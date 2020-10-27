from utilities.models import InteractionInstanceMigrations
from messenger_users.models import Child, User, UserData, ChildData
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from instances.models import Instance, Response, AttributeValue, InstanceAssociationUser
from milestones.models import Milestone
from languages.models import MilestoneTranslation
from django.http import JsonResponse
from posts.models import Interaction
from entities.models import Entity
from groups.models import Group, MilestoneRisk
from programs.models import Attributes as ProgramAttribute
from user_sessions.models import Reply, Interaction as SessionInteraction
from django.http import Http404
from bots.models import Bot
from utilities import forms
import boto3
import os
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from django.db.models import Max
from django.db.models import Q
import json


@method_decorator(csrf_exempt, name='dispatch')
class GroupAssignationsView(View):

    def get(self, request, *args, **kwargs):
        return Http404()

    def post(self, request):
        form = forms.GroupForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            program = group.programs.last()
            assigns = group.assignationmessengeruser_set.all()
            group_users = set([a.messenger_user_id for a in assigns])
            if 'pag' in self.request.POST:
                pag = int(self.request.POST['pag'])
            else:
                pag = 0
            if 'all' in self.request.POST:
                group_instances = InstanceAssociationUser.objects.filter(user_id__in=group_users).all()
            if 'attribute_id' in self.request.POST:
                program_attribute = ProgramAttribute.objects.get(id=self.request.POST['attribute_id'])
                group_instances = InstanceAssociationUser.objects.filter(user_id__in=group_users).all()
                last_attributes = AttributeValue.objects.\
                    filter(instance__id__in=[x.instance.id for x in group_instances],
                           attribute=program_attribute.attribute). \
                    values('instance__id').annotate(max_id=Max('id'))
                risk_count_instance = AttributeValue.objects.filter(id__in=[x['max_id'] for x in last_attributes],
                                                                    value__lte=program_attribute.threshold). \
                    values('instance__id').distinct()
                if risk_count_instance.count() > 0:
                    group_instances = InstanceAssociationUser.objects.\
                        filter(instance_id__in=[x['instance__id'] for x in risk_count_instance]).all()
                else:
                    last_attributes = UserData.objects.filter(user__id__in=group_users,
                                                              attribute_id=program_attribute.attribute.id). \
                        values('user__id').annotate(max_id=Max('id'))
                    risk_count_user = UserData.objects.filter(id__in=[x['max_id'] for x in last_attributes],
                                                              data_value__lte=program_attribute.threshold). \
                        values('user__id').distinct()
                    group_instances = InstanceAssociationUser.objects. \
                        filter(user_id__in=[x['user__id'] for x in risk_count_user]).all()
            if 'milestone_id' in self.request.POST:
                group_instances = set([])
                for assignation in assigns:
                    for instance in assignation.get_messenger_user().get_instances():
                        try:
                            age = relativedelta(datetime.datetime.now(),
                                                parse(instance.get_attribute_value(191).value))# birthday
                            months = 0
                            if age.months:
                                months = age.months
                            if age.years:
                                months = months + (age.years * 12)
                        except:
                            months = 0
                        risks = [r.milestone_id for r in MilestoneRisk.objects.\
                            filter(milestone_id=self.request.POST['milestone_id'], value__lte=months)]
                        if len(risks) > 0:
                            last_responses = instance.response_set.filter(milestone_id__in=risks).\
                                values('milestone_id').annotate(max_id=Max('id'))
                            responses = instance.response_set.filter(response__in=['failed', 'dont-know'],
                                                                     id__in=[x['max_id'] for x in last_responses])
                            if responses.exists():
                                group_instances = group_instances.union(set([instance.id]))
                group_instances = InstanceAssociationUser.objects.filter(instance_id__in=group_instances).all()
            if 'name' in self.request.POST:
                group_instances = InstanceAssociationUser.objects.filter(user_id__in=group_users).all()
                if self.request.POST['name'] != '':
                    instances = Instance.objects.filter(id__in=[x.instance.id for x in group_instances],
                                                        name__icontains=str(self.request.POST['name']))
                    usuarios = User.objects.filter(id__in=group_users).\
                        filter(Q(first_name__icontains=str(self.request.POST['name'])) |
                               Q(last_name__icontains=str(self.request.POST['name'])))
                    group_instances = InstanceAssociationUser.objects.\
                        filter(Q(instance_id__in=instances) | Q(user_id__in=[x.id for x in usuarios]))
            if 'months' in self.request.POST:
                try:
                    query = Q()
                    now = datetime.datetime.now()
                    for rango in self.request.POST['months'].split(','):
                        date1 = now + relativedelta(months=-int(rango.split('_')[1])-1)
                        date2 = now + relativedelta(months=-int(rango.split('_')[0]))
                        query = query | Q(value__gte=date1, value__lte=date2)
                    instance_attributes = AttributeValue.objects. \
                        filter(instance_id__in=[x.instance.id for x in group_instances],
                               attribute_id=191).filter(query)
                    group_instances = group_instances.\
                        filter(instance__id__in=[x.instance_id for x in instance_attributes])
                except:
                    group_instances = group_instances
            if 'attribute_id' in self.request.POST or 'milestone_id' in self.request.POST\
                    or 'name' in self.request.POST or 'months' in self.request.POST\
                    or 'all' in self.request.POST:
                instances_data = []
                for assoc in group_instances.order_by('-id')[20*pag:20*(pag + 1)]:
                    if assoc.instance.get_attribute_value(191):  # birthday
                        try:
                            birthday = parse(assoc.instance.get_attribute_value(191).value).strftime('%d/%m/%Y')
                        except:
                            birthday = assoc.instance.get_attribute_value(191).value
                    else:
                        birthday = '---'
                    if assoc.user.userdata_set.filter(attribute_id=13).exists():  # telefono
                        telefono = assoc.user.userdata_set.filter(attribute_id=13).last().data_value
                    else:
                        telefono = '---'
                    if assoc.user.userdata_set.filter(attribute_id=190).exists():  # direccion
                        direccion = assoc.user.userdata_set.filter(attribute_id=190).last().data_value
                    else:
                        direccion = '---'
                    try:
                        age = relativedelta(datetime.datetime.now(), parse(assoc.instance.get_attribute_value(191).value))
                        months = ''
                        if age.months:
                            months = str(age.months) + ' meses'
                        if age.years:
                            if age.years == 1:
                                months = str(age.years) + ' año ' + months
                            else:
                                months = str(age.years) + ' años ' + months
                    except:
                        months = 0
                    risks = [r.milestone_id for r in MilestoneRisk.objects.filter(value__lte=months)]
                    responses = instance.response_set.filter(response='failed', milestone_id__in=risks)
                    if responses.exists():
                        milestones_count = milestones_count + 1
                    for response in responses:
                        if response.milestone_id in milestones:
                            milestones[response.milestone_id].append(response.instance.id)
                        else:
                            milestones[response.milestone_id] = [response.instance.id]
            milestones_data = []
            for milestone in milestones:
                y_label = "Cases"
                if len(milestones[milestone]) == 1:
                    y_label = "Case"
                milestones_data.append(dict(y=len(milestones[milestone]), y_label=y_label,
                                            label=MilestoneTranslation.objects.get(language_id=2,
                                                                                   milestone_id=milestone).name,
                                            instances=milestones[milestone]))
            if len(milestones_data) == 0:
                milestones_data = [dict(y=0, label='No children with development risk')]

            # Count cases of risk attributes
            program = group.programs.last()
            factores_riesgo = []
            for attributes_type in program.attributetype_set.all():
                factores_riesgo_data = []
                factores_riesgo_count = set([])
                for program_attribute in attributes_type.attributes_set.all():
                    risk_count = 0
                    for attributes_type in program.attributetype_set.all():
                        for program_attribute in attributes_type.attributes_set.all():
                            last_attributes = AttributeValue.objects.filter(instance=assoc.instance,
                                                                            attribute=program_attribute.attribute). \
                                values('attribute__id').annotate(max_id=Max('id'))
                            risk_count = risk_count + AttributeValue.objects.filter(
                                id__in=[x['max_id'] for x in last_attributes],
                                value__lte=program_attribute.threshold). \
                                values('instance__id').distinct().count()
                            last_attributes = UserData.objects.filter(user=assoc.user,
                                                                      attribute=program_attribute.attribute). \
                                values('user__id', 'attribute_id').annotate(max_id=Max('id'))
                            risk_count = risk_count + \
                                         UserData.objects.filter(id__in=[x['max_id'] for x in last_attributes],
                                                                 data_value__lte=program_attribute.threshold). \
                                             values('user__id').distinct().count()
                    if risk_count == 0:
                        risk = 0
                    elif risk_count < 4:
                        risk = 1
                    else:
                        risk = 2
                    try:
                        username = assoc.user.first_name + ' ' + assoc.user.last_name
                    except:
                        username = ''
                    instance_data = dict(id=assoc.instance.id,
                                         name=assoc.instance.name,
                                         username=username,
                                         user_id=assoc.user.id,
                                         image="child_user_" + str((assoc.instance.id % 10) + 1) + ".jpg",
                                         months=months,
                                         birthdate=birthday,
                                         tel=telefono,
                                         dir=direccion,
                                         risk=risk)
                    instances_data.append(instance_data)
                return JsonResponse(dict(data=sorted(instances_data, key=lambda k: k['risk'], reverse=True),
                                         total=group_instances.count()))
            else:
                lang = program.languages.last()
                if lang.name == 'en':
                    label_caso = 'Case'
                    label_casos = 'Cases'
                    label_nohay = 'No children with development risks'
                else:
                    label_caso = 'Caso'
                    label_casos = 'Casos'
                    label_nohay = 'No hay niños con riesgos de desarrollo'
                # Count Sent activities
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
                                                parse(instance.get_attribute_value(191).value))# birthday
                            months = 0
                            if age.months:
                                months = age.months
                            if age.years:
                                months = months + (age.years * 12)
                        except:
                            months = 0
                        risks = [r.milestone_id for r in MilestoneRisk.objects.filter(value__lte=months)]
                        last_responses = instance.response_set.filter(milestone_id__in=risks).values('milestone_id').\
                            annotate(max_id=Max('id'))
                        responses = instance.response_set.filter(response__in=['failed', 'dont-know'],
                                                                 id__in=[x['max_id'] for x in last_responses])
                        if responses.exists():
                            milestones_count = milestones_count + 1
                        for response in responses:
                            if response.milestone_id in milestones:
                                milestones[response.milestone_id].append(instance.id)
                            else:
                                milestones[response.milestone_id] = [instance.id]
                milestones_data = []
                for milestone in milestones:
                    y_label = label_casos
                    if len(milestones[milestone]) == 1:
                        y_label = label_caso
                    milestones_data.append(dict(y=len(milestones[milestone]), y_label=y_label,
                                                label=MilestoneTranslation.objects.get(language_id=lang.id,
                                                                                       milestone_id=milestone).name,
                                                instances=milestones[milestone], milestone_id=milestone))
                if len(milestones_data) == 0:
                    milestones_data = [dict(y=0, label=label_nohay)]

                # Count cases of risk attributes
                factores_riesgo = []
                for attributes_type in program.attributetype_set.all():
                    factores_riesgo_data = []
                    factores_riesgo_count = set([])
                    for program_attribute in attributes_type.attributes_set.all():
                        risk_count = 0
                        last_attributes = AttributeValue.objects.filter(instance__id__in=group_instances,
                                                                        attribute=program_attribute.attribute). \
                            values('instance__id', 'attribute__id').annotate(max_id=Max('id'))
                        risk_count_instance = AttributeValue.objects.filter(id__in=[x['max_id'] for x in last_attributes],
                                                                            value__lte=program_attribute.threshold). \
                            values('instance__id').distinct()
                        if risk_count_instance.count() > 0:
                            factores_riesgo_count = factores_riesgo_count.union(set([x['instance__id']
                                                                                     for x in risk_count_instance]))
                            risk_count = risk_count_instance.count()
                            instance_list = [x['instance__id'] for x in risk_count_instance]
                        else:
                            last_attributes = UserData.objects.filter(user__id__in=group_users,
                                                                      attribute_id=program_attribute.attribute.id). \
                                values('user__id', 'attribute_id').annotate(max_id=Max('id'))
                            risk_count_user = UserData.objects.filter(id__in=[x['max_id'] for x in last_attributes],
                                                                      data_value__lte=program_attribute.threshold). \
                                values('user__id').distinct()
                            factores_riesgo_count = factores_riesgo_count.union(set([x['user__id']*1000000
                                                                                     for x in risk_count_user]))
                            risk_count = risk_count_user.count()
                            associations = InstanceAssociationUser.objects.\
                                filter(user_id__in=[x['user__id'] for x in risk_count_user])
                            instance_list = [association.instance.id for association in associations]
                        y_label = label_casos
                        if risk_count == 1:
                            y_label = label_caso
                        factores_riesgo_data.append(dict(y=risk_count, y_label=y_label, label=program_attribute.label,
                                                         program_attribute_id=program_attribute.id,
                                                         instances=instance_list))
                    factores_riesgo.append(dict(id=attributes_type.id, name=attributes_type.name,
                                                factores_riesgo=factores_riesgo_data, total=len(factores_riesgo_count)))
                children = InstanceAssociationUser.objects.filter(
                    user_id__in=[u.messenger_user_id for u in group.assignationmessengeruser_set.all()]).count()
                '''for assign in self.object.assignationmessengeruser_set.all():
                            data = User.objects.get(id=assign.messenger_user_id).get_instances().filter(entity_id=1)
                            children = children + data.count()
                            assignations = assignations + Interaction.objects.filter(user_id=assign.messenger_user_id,
                                                                                     type='dispatched').count()'''
                return JsonResponse(dict(data=dict(count=count, children=children), milestones=milestones_data,
                                         milestones_count=milestones_count, factores_riesgo=factores_riesgo))
        return JsonResponse(dict(data=dict(count=0)))


@method_decorator(csrf_exempt, name='dispatch')
class GroupInstanceCardView(View):
    def get(self, request, *args, **kwargs):
        return Http404()

    def post(self, request):
        group = Group.objects.get(id=int(self.request.POST['group_id']))
        program = group.programs.last()
        instance = Instance.objects.get(id=int(self.request.POST['instance_id']))
        user = User.objects.get(id=int(self.request.POST['user_id']))
        factores = []
        if self.request.POST['type'] == 'user':
            entities_attributes = [x.id for x in Entity.objects.get(id=4).attributes.all()]\
                                  + [x.id for x in Entity.objects.get(id=5).attributes.all()]# caregiver or professional
        else:
            entities_attributes = [x.id for x in Entity.objects.get(id=1).attributes.all()] \
                                  + [x.id for x in Entity.objects.get(id=2).attributes.all()] # child or pregnant
        for attributes_type in program.attributetype_set.all():
            factores_riesgo = []
            for program_attribute in attributes_type.attributes_set.filter(attribute__in=entities_attributes):
                if self.request.POST['type'] == 'user':
                    attributevalue = UserData.objects.\
                        filter(user=user, attribute_id=program_attribute.attribute_id).order_by('-id')
                else:
                    attributevalue = AttributeValue.objects. \
                        filter(instance=instance, attribute_id=program_attribute.attribute_id).order_by('-id')
                # Obtener solo los fields que tiene ese atribto
                fields = [x.field_id for x in Reply.objects.filter(attribute=program_attribute.attribute.name)]
                # Filtrar las interacciones de la instancia con dichos fields
                interactions = SessionInteraction.objects.filter(instance_id=instance.id,
                                                                 field_id__in=fields,
                                                                 type='quick_reply').order_by('-id')
                # Conjunto de posibles respuestas
                if interactions.exists():
                    interaction = interactions.first()  # Obtener la ultima sesion
                    possible_replies = [dict(value=r.value, label=r.label)
                                        for r in Reply.objects.filter(attribute=program_attribute.attribute.name,
                                                                      field_id=interaction.field_id).order_by('-id')]
                else:
                    possible_replies = [dict(value=r['value'], label=r['label'])
                                        for r in Reply.objects.filter(attribute=program_attribute.attribute.name). \
                                            values('value', 'label').distinct()]
                if attributevalue.exists():
                    attribute = attributevalue.first()
                    if self.request.POST['type'] == 'user':
                        attribute.value = attribute.data_value
                    fields = [x.field_id for x in Reply.objects.filter(attribute=attribute.attribute.name)]
                    interactions = SessionInteraction.objects.filter(instance_id=instance.id,
                                                                     field_id__in=fields,
                                                                     type='quick_reply').order_by('-id')
                    if interactions.exists():
                        interaction = interactions.first()
                        reply = Reply.objects.filter(attribute=attribute.attribute.name, field_id=interaction.field_id,
                                                     value=interaction.value).order_by('-id')
                        if reply.exists():
                            value = reply.first().label
                            if reply.first().value.isnumeric():
                                if float(reply.first().value) <= program_attribute.threshold:
                                    risk = 1
                                else:
                                    risk = 0
                            else:
                                -1
                        else:
                            value = attribute.value
                            if value.isnumeric():
                                if float(value) <= program_attribute.threshold:
                                    risk = 1
                                else:
                                    risk = 0
                            else:
                                risk = -1
                    else:
                        reply_value = Reply.objects.filter(attribute=attribute.attribute.name, value=attribute.value)
                        if reply_value.exists():
                            value = reply_value.first().label
                        else:
                            value = attribute.value
                        if attribute.value.isnumeric():
                            if float(attribute.value) <= program_attribute.threshold:
                                risk = 1
                            else:
                                risk = 0
                        else:
                            risk = -1
                else:
                    value = 'Sin responder'
                    risk = -1
                factores_riesgo.append(dict(name=program_attribute.label,
                                            program_attribute_id=program_attribute.id,
                                            options=possible_replies,
                                            value=value,
                                            threshold=program_attribute.threshold,
                                            risk=risk))
            if len(factores_riesgo) > 0:
                factores.append(dict(attributes_type_id=attributes_type.id, name=attributes_type.name,
                                     program_attributes=factores_riesgo))
        if self.request.POST['type'] == 'user':
            observaciones = UserData.objects.filter(user=user, attribute_id=252).order_by('-id')
            if observaciones.exists():
                observaciones = observaciones[0].data_value
            else:
                observaciones = ''
            seguimiento = UserData.objects.filter(user=user, attribute_id=253).order_by('-id')
            if seguimiento.exists():
                seguimiento = seguimiento[0].data_value
            else:
                seguimiento = ''
            try:
                name = user.first_name + ' ' + user.last_name
            except:
                name = ''
        else:
            observaciones = AttributeValue.objects.filter(instance=instance, attribute_id=252).order_by('-id')
            if observaciones.exists():
                observaciones = observaciones[0].value
            else:
                observaciones = ''
            seguimiento = AttributeValue.objects.filter(instance=instance, attribute_id=253).order_by('-id')
            if seguimiento.exists():
                seguimiento = seguimiento[0].value
            else:
                seguimiento = ''
            name = instance.name
        return JsonResponse(dict(attributes_types=factores,
                                 name=name,
                                 image="child_user_" + str((instance.id % 10) + 1) + ".jpg",
                                 observaciones=observaciones,
                                 seguimiento=seguimiento))


@method_decorator(csrf_exempt, name='dispatch')
class GroupInstanceCardSaveView(View):
    def get(self, request, *args, **kwargs):
        return Http404()

    def post(self, request):
        try:
            instance = Instance.objects.get(id=int(self.request.POST['instance_id']))
            user = User.objects.get(id=int(self.request.POST['user_id']))
            data = json.loads(self.request.POST['attributes'])
            if self.request.POST['type'] == 'user':
                for key in data:
                    program_attribute = ProgramAttribute.objects.get(id=key)
                    UserData.objects.create(user=user, data_key=program_attribute.attribute.name,
                                            attribute=program_attribute.attribute,
                                            data_value=data[key])
            else:
                for key in data:
                    program_attribute = ProgramAttribute.objects.get(id=key)
                    AttributeValue.objects.create(instance=instance, attribute=program_attribute.attribute,
                                                  value=data[key])
            if 'observaciones' in self.request.POST:
                AttributeValue.objects.create(instance=instance, attribute_id=252,
                                              value=self.request.POST['observaciones'])#observaciones
            if 'seguimiento' in self.request.POST:
                AttributeValue.objects.create(instance=instance, attribute_id=253,
                                              value=self.request.POST['seguimiento'])#seguimiento
            return JsonResponse(dict(status="done"))
        except:
            return JsonResponse(dict(status="failed"))


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
