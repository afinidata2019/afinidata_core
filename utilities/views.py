from utilities.models import InteractionInstanceMigrations
from messenger_users.models import Child, User, UserData, ChildData
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from instances.models import Instance, Response, AttributeValue
from milestones.models import Milestone
from django.http import JsonResponse
from posts.models import Interaction
from entities.models import Entity
from groups.models import Group, MilestoneRisk
from django.http import Http404
from bots.models import Bot
from utilities import forms
import boto3
import os
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from django.db.models import Count


@method_decorator(csrf_exempt, name='dispatch')
class GroupAssignationsView(View):

    def get(self, request, *args, **kwargs):
        return Http404()

    def post(self, request):
        form = forms.GroupForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            assigns = group.assignationmessengeruser_set.all()
            # Count Sent activities
            group_users = set([a.messenger_user_id for a in assigns])
            count = Interaction.objects.filter(user_id__in=group_users,
                                               type='dispatched').count()

            # Count Cases of risk in Development through risk milestones
            group_instances = set([])
            milestones = dict()
            milestones_count = 0
            for assignation in assigns:
                assignation.instances = assignation.get_messenger_user().get_instances()
                for instance in assignation.instances:
                    group_instances = group_instances.union(set([instance.id]))
                    try:
                        age = relativedelta(datetime.datetime.now(),
                                            parse(instance.get_attribute_values('birthday').value))
                        months = 0
                        if age.months:
                            months = age.months
                        if age.years:
                            months = months + (age.years * 12)
                    except:
                        months = 0
                    risks = [r.milestone_id for r in MilestoneRisk.objects.filter(value__lte=months)]
                    responses = instance.response_set.filter(response='failed', milestone_id__in=risks)
                    if responses.exists():
                        milestones_count = milestones_count + 1
                    for response in responses:
                        if response.milestone_id in milestones:
                            milestones[response.milestone_id] = milestones[response.milestone_id] + 1
                        else:
                            milestones[response.milestone_id] = 1
            milestones_data = []
            for milestone in milestones:
                y_label = "Casos"
                if milestones[milestone] == 1:
                    y_label = "Caso"
                milestones_data.append(dict(y=milestones[milestone], y_label=y_label,
                                            label=Milestone.objects.get(id=milestone).name))
            if len(milestones_data) == 0:
                milestones_data = [dict(y=0, label='No hay niños con riesgos de desarrollo')]

            # Count cases of risk attributes
            program = group.programs.last()
            factores_riesgo = []
            for attributes_type in program.attributetype_set.all():
                factores_riesgo_data = []
                factores_riesgo_count = set([])
                for attribute in attributes_type.attributes_set.all():
                    risk_count = 0
                    risk_count_instance = AttributeValue.objects.filter(instance__id__in=group_instances,
                                                                        attribute=attribute.attribute,
                                                                        value__lte=attribute.threshold).\
                        values('instance__id').distinct()
                    if risk_count_instance.count() > 0:
                        factores_riesgo_count = factores_riesgo_count.union(set([x['instance__id']
                                                                                 for x in risk_count_instance]))
                        risk_count = risk_count_instance.count()
                    else:
                        risk_count_user = UserData.objects.filter(user__id__in=group_users,
                                                                  data_key=attribute.attribute.name,
                                                                  data_value__lte=attribute.threshold).\
                            values('user__id').distinct().count()
                        risk_count = risk_count_user
                    y_label = "Casos"
                    if risk_count == 1:
                        y_label = "Caso"
                    factores_riesgo_data.append(dict(y=risk_count, y_label=y_label, label=attribute.label))
                factores_riesgo.append(dict(id=attributes_type.id, name=attributes_type.name,
                                            factores_riesgo=factores_riesgo_data, total=len(factores_riesgo_count)))
            return JsonResponse(dict(data=dict(count=count), milestones=milestones_data,
                                     milestones_count=milestones_count, factores_riesgo=factores_riesgo))
        return JsonResponse(dict(data=dict(count=0)))


class TranslateView(View):

    def get(self, request, *args, **kwargs):
        region = os.getenv('region')
        translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
        result = translate.translate_text(Text="Hello, World",
                                          SourceLanguageCode="en", TargetLanguageCode="es")
        print('TranslatedText: ' + result.get('TranslatedText'))
        return JsonResponse(dict(h='w'))


class GetChildrenView(LoginRequiredMixin, TemplateView):
    template_name = 'utilities/get_children.html'

    def get_context_data(self, **kwargs):
        context = super(GetChildrenView, self).get_context_data()
        context['children'] = Child.objects.all()
        entity = Entity.objects.get(name='Niño')
        bot = Bot.objects.get(name='Afinibot')
        context['created'] = 0
        for child in context['children']:
            if Instance.objects.filter(user_id=child.parent_user_id).count() == 0:
                instance = Instance.objects.create(bot=bot, entity=entity, user_id=child.parent_user_id,
                                                   name=child.name)
                context['created'] = context['created'] + 1
                print(instance)
                print(context['created'])
        return context


class GetChildrenMilestonesView(LoginRequiredMixin, TemplateView):
    template_name = 'utilities/get_children_milestones.html'

    def get_context_data(self, **kwargs):
        context = super(GetChildrenMilestonesView, self).get_context_data()
        context['created'] = 0
        for instance in Instance.objects.all():
            parent = User.objects.get(id=instance.user_id)
            child_data = ChildData.objects\
                .filter(child__parent_user=parent,
                        data_key__in=[milestone.second_code for milestone in Milestone.objects.all()],
                        data_value__in=['Completado', 'done', 'Si lo hace'])
            parent_data = parent.userdata_set.filter(
                data_key__in=[milestone.second_code for milestone in Milestone.objects.all()],
                data_value__in=['Completado', 'done', 'Si lo hace'])

            negative_child_data = ChildData.objects\
                .filter(child__parent_user=parent,
                        data_key__in=[milestone.second_code for milestone in Milestone.objects.all()],
                        data_value__in=['Todavía no'])

            negative_parent_data = parent.userdata_set.filter(
                data_key__in=[milestone.second_code for milestone in Milestone.objects.all()],
                data_value__in=['Todavía no'])

            if negative_child_data.count() > 0:
                for data in negative_child_data:
                    response = Response.objects.create(instance=instance,
                                                       milestone=Milestone.objects.get(second_code=data.data_key),
                                                       response='failed',
                                                       created_at=data.timestamp)
                    print(response)
                    context['created'] = context['created'] + 1

            if negative_parent_data.count() > 0:
                for data in negative_parent_data:
                    response = Response.objects.create(instance=instance,
                                                       milestone=Milestone.objects.get(second_code=data.data_key),
                                                       response='failed',
                                                       created_at=data.created)
                    print(response)
                    context['created'] = context['created'] + 1

            if parent_data.count() > 0:
                for data in parent_data:
                    if instance.response_set.filter(milestone__second_code=data.data_key, response='done').count() < 1:
                        response = Response.objects.create(instance=instance,
                                                           milestone=Milestone.objects.get(second_code=data.data_key),
                                                           response='done',
                                                           created_at=data.created)
                        print(instance.pk, response.milestone, response.response)
                        context['created'] = context['created'] + 1

            if child_data.count() > 0:
                print(instance.pk)
                for data in child_data:
                    if instance.response_set.filter(milestone__second_code=data.data_key, response='done').count() < 1:
                        response = Response.objects.create(instance=instance,
                                                           milestone=Milestone.objects.get(second_code=data.data_key),
                                                           response='done',
                                                           created_at=data.timestamp)
                        print(instance.pk, response.milestone, response.response)
                        context['created'] = context['created'] + 1

        return context


class GetChildrenInteractionsView(LoginRequiredMixin, TemplateView):
    template_name = 'utilities/get_children_interactions.html'

    def get_context_data(self, **kwargs):
        context = super(GetChildrenInteractionsView, self).get_context_data()
        last_data_id = 0
        last_register_id = 0
        qty_register = 0
        migrations = InteractionInstanceMigrations.objects.all()
        query_data = None

        if migrations.count() > 0:
            query_data = Interaction.objects.filter(id__gt=migrations.last().last_register_id)
        else:
            query_data = Interaction.objects.all()

        for instance in Instance.objects.all():
            interactions = query_data.filter(user_id=instance.user_id, type__in=['dispatched', 'session'],
                                             post_id__isnull=False)
            for interaction in interactions:
                post_interaction = instance.postinteraction_set\
                    .create(post_id=interaction.post_id, type=interaction.type, value=interaction.value,
                            created_at=interaction.created_at)
                last_data_id = post_interaction.pk
                last_register_id = interaction.pk
                qty_register = qty_register + 1
                print(post_interaction)

        context['data_migration'] = InteractionInstanceMigrations.objects\
            .create(last_register_id=last_register_id, last_data_id=last_data_id, qty_register=qty_register)

        return context


class CreateProgramDemoView(TemplateView):
    template_name = 'utilities/create_program.html'

    def get_context_data(self, **kwargs):
        c = super(CreateProgramDemoView, self).get_context_data(**kwargs)
        c['form'] = forms.CreateProgramForm()
        return c


class NewProgramDemoView(TemplateView):
    template_name = 'utilities/new_program.html'


class EditLevelDemoView(TemplateView):
    template_name = 'utilities/edit_level.html'


class CognitiveExampleView(TemplateView):
    template_name = 'utilities/example_area.html'

    def get_context_data(self, **kwargs):
        c = super(CognitiveExampleView, self).get_context_data(**kwargs)
        c['uri'] = 'https://afinicontent.com/boxes-boxes-boxes/'
        c['area'] = 'Cognitive and Language Activity'
        return c
