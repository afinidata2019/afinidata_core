from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, View
from instances.models import Instance, AttributeValue, Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from messenger_users.models import User
from milestones.models import Milestone
from attributes.models import Attribute
from areas.models import Area, Section
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from levels.models import Level
from instances import forms
import requests


class HomeView(LoginRequiredMixin, ListView):
    model = Instance
    paginate_by = 30
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data()
        print(self.paginator_class)
        return context


class InstanceView(LoginRequiredMixin, DetailView):
    model = Instance
    pk_url_kwarg = 'id'
    login_url = reverse_lazy('pages:login')


class NewInstanceView(LoginRequiredMixin, CreateView):
    model = Instance
    form_class = forms.InstanceModelForm
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(NewInstanceView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def form_valid(self, form):
        users = User.objects.filter(id=form.cleaned_data['user_id'])
        if not users.count() > 0:
            form.add_error('user_id', 'User ID is not valid')
            messages.error(self.request, 'User ID is not valid')
            return super(NewInstanceView, self).form_invalid(form)
        
        return super(NewInstanceView, self).form_valid(form)

    def get_success_url(self):
        self.object.instanceassociationuser_set.create(user_id=self.request.POST['user_id'])
        messages.success(self.request, 'Instance with name: "%s" has been created.' % self.object.name)
        return reverse_lazy('instances:instance', kwargs={'id': self.object.pk})


class EditInstanceView(LoginRequiredMixin, UpdateView):
    model = Instance
    fields = ('name',)
    pk_url_kwarg = 'id'
    context_object_name = 'instance'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(EditInstanceView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Instance with name "%s" has been updated.' % self.object.name)
        return reverse_lazy('instances:instance', kwargs={'id': self.object.pk})


class DeleteInstanceView(LoginRequiredMixin, DeleteView):
    model = Instance
    template_name = 'instances/instance_form.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('instances:index')
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(DeleteInstanceView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete instance with name: "%s"?' % self.object.name
        return c
    
    def get_success_url(self):
        messages.success(self.request, 'Instance with name: "%s" has been deleted.' % self.object.name)
        return super(DeleteInstanceView, self).get_success_url()


class AddAttributeToInstance(LoginRequiredMixin, View):

    login_url = reverse_lazy('pages:login')

    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(Instance, id=kwargs['id'])
        exclude_arr = [item.pk for item in instance.attributes.all()]
        queryset = instance.entity.attributes.all().exclude(id__in=exclude_arr)
        form = forms.InstanceAttributeValueForm(request.GET or None, queryset=queryset)
        return render(self.request, 'instances/add_attribute_value.html', dict(form=form))

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(Instance, id=kwargs['id'])
        attribute = get_object_or_404(instance.entity.attributes, id=request.POST['attribute'])
        if attribute:
            queryset = instance.entity.attributes.filter(id=request.POST['attribute'])
        form = forms.InstanceAttributeValueForm(request.POST, queryset=queryset)

        if form.is_valid():
            attr = AttributeValue.objects.create(instance=instance, attribute=attribute, value=request.POST['value'])
            print(attr)
            messages.success(request, 'Attribute has been added to instance')
            return redirect('instances:instance', id=kwargs['id'])

        return JsonResponse(dict(hello='world'))


class InstanceSectionView(LoginRequiredMixin, View):
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(Instance, id=kwargs['id'])
        exclude_arr = [item.pk for item in instance.areas.all()]
        queryset = Area.objects.all().exclude(id__in=exclude_arr)
        form = forms.InstanceSectionForm(None, queryset=queryset)
        return render(request, 'instances/section_to_instance.html', dict(form=form))

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(Instance, id=kwargs['id'])
        queryset = Area.objects.filter(id=request.POST['area'])
        form = forms.InstanceSectionForm(request.POST, queryset=queryset)

        if form.is_valid():
            level = Level.objects.get(max__gte=int(request.POST['value_to_init']),
                                      min__lte=int(request.POST['value_to_init']))
            area = get_object_or_404(Area, id=request.POST['area'])
            section = get_object_or_404(Section, level=level, area=area)
            instance_section = InstanceSection.objects.create(value_to_init=request.POST['value_to_init'],
                                                              section=section,
                                                              instance=instance,
                                                              area=area)
            print(instance_section)
            messages.success(request, 'Instance has been added to section "%s".' % section.name)
            return redirect('instances:instance', id=instance.pk)


class Evaluator(View):

    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(Instance, id=kwargs['id'])
        area = get_object_or_404(Area, id=int(request.GET['area']))
        section = get_object_or_404(Section, instance=instance, area=area)
        last_milestones = Milestone.objects.filter(area=area,
                                                   value__gte=section.level.min,
                                                   value__lte=section.level.max).order_by('-value', '-created_at')[:3]

        last_milestones_ids = [milestone.pk for milestone in last_milestones]

        instance_responses = Response.objects.filter(instance=instance,
                                                     created_at__gte=(datetime.now() - timedelta(days=30)),
                                                     milestone__value__gte=section.level.min,
                                                     milestone__value__lte=section.level.max)

        for response in instance_responses:
            print(response.pk, response.response, response.milestone.id)

        if instance_responses.count() <= 0:
            return JsonResponse(dict(status='done', data=dict(up=False, down=False,
                                                              message='Instance not change section')))

        search_responses = instance_responses.filter(milestone_id__in=last_milestones_ids)\
            .order_by('-milestone_id', '-id')
        for response in search_responses:
            print(response.pk, response.response, response.milestone.id)

        if len(last_milestones_ids) <= 0:
            return JsonResponse(dict(status='done', data=dict(up=False, down=False,
                                                              message='Instance not change section')))
        print(search_responses.filter(milestone_id=last_milestones_ids[0]).count())
        if search_responses.filter(milestone_id=last_milestones_ids[0]).count() > 0:
            debug_responses = search_responses.filter(milestone_id=last_milestones_ids[0])

            for response in debug_responses:
                print(response.pk, response.response, response.milestone.id)

            if search_responses.count() >= 3:
                print(search_responses.count())
                instance_has_up = True

                for milestone in last_milestones:
                    milestone_init = False
                    responses = search_responses.filter(milestone__id=milestone.pk)
                    for response in responses:
                        if response.response == 'true':
                            milestone_init = True
                    print(milestone.pk, milestone_init, responses.count())

                    if not milestone_init:
                        instance_has_up = False

                if instance_has_up:
                    attribute_name = "%s__has__up" % area.name
                    attribute = Attribute.objects.update_or_create(name=attribute_name,
                                                                   defaults=dict(name=attribute_name, type='boolean'))
                    attribute = attribute[0]
                    instance.entity.attributes.add(attribute)
                    attribute_value = AttributeValue.objects.update_or_create(instance=instance,
                                                                              attribute=attribute,
                                                                              defaults=dict(value=True))
                    return JsonResponse(dict(status='done', data=dict(message='Instance must be up section.',
                                                                      up=True, down=False)))

                if not instance_has_up:
                    return JsonResponse(dict(status='done', data=dict(message='Instance not change section.',
                                                                      up=False,
                                                                      down=False)))
            else:
                return JsonResponse(dict(status='done', data=dict(message='Instance not change section.',
                                                                  up=False, down=False)))

        print('not in last milestones')

        first_milestones = Milestone.objects.filter(area=area,
                                                    value__gte=section.level.min,
                                                    value__lte=section.level.max).order_by('value', 'created_at')[:3]
        first_milestones_ids = [milestone.pk for milestone in first_milestones]
        search_responses = instance_responses.filter(milestone_id__in=first_milestones_ids)\
            .order_by('milestone_id', 'id')
        for response in search_responses:
            print(response.pk, response.response, response.milestone.id)

        if search_responses.filter(milestone_id=first_milestones_ids[0], response='false').count() > 0:
            instance_has_down = True
            index = 0
            while instance_has_down:
                if search_responses[index].response == 'true':
                    instance_has_down = False
                index = index + 1
                if index == search_responses.count():
                    break

            if instance_has_down:
                change_level_number = section.level.min - 1
                try:
                    new_section = Section.objects.get(level__max__gte=change_level_number,
                                                      level__min__lte=change_level_number,
                                                      area=area)
                    attribute = Attribute.objects.update_or_create(name="%s__has__descended" % area.name,
                                                                   defaults=dict(type='string'))
                    attribute = attribute[0]
                    instance.entity.attributes.add(attribute)
                    instance.attributevalue_set.create(attribute=attribute,
                                                       value='instance: %s descended of %s (%s) to %s (%s). date: %s' %
                                                             (instance.name, section.name, section.pk, new_section.name,
                                                              new_section.pk, datetime.now()))
                    actual_section_to_instance = InstanceSection.objects.get(instance=instance,
                                                                             section=section)
                    print(actual_section_to_instance)
                    actual_section_to_instance.delete()
                    new_section_to_instance = InstanceSection.objects.create(instance=instance, section=new_section,
                                                                             area=area,
                                                                             value_to_init=change_level_number)
                    print(new_section_to_instance)
                    return JsonResponse(dict(status='done', data=dict(message='Instance down section',
                                                                      up=False, down=True)))
                except Exception as e:
                    return JsonResponse(dict(status='error', error='%s' % str(e)))

        return JsonResponse(dict(status='done', data=dict(message='Instance not change section',
                                                          up=False, down=False)))


@csrf_exempt
def up_instance(request, id):

    if request.method == 'GET':
        return JsonResponse(dict(status='error', error='Invalid method'))

    try:
        instance = Instance.objects.get(id=id)
        area = Area.objects.get(id=request.POST['area'])
        attribute = instance.attributevalue_set.get(attribute__name="%s__has__up" % area.name)
    except Exception as e:
        return JsonResponse(dict(status='error', error='Invalid params. %s' % e))

    if attribute.value != 'True':
        return JsonResponse(dict(status='done', data=dict(message='Instance not qualified to up in area')))

    instance_section = instance.instancesection_set.get(area=area)
    new_value_to_init = instance_section.section.level.max + 2
    new_section = Section.objects.get(level__min__lte=new_value_to_init, level__max__gte=new_value_to_init, area=area)
    new_instance_section = instance.instancesection_set.update_or_create(area=area, defaults=dict(
        section=new_section,
        value_to_init=new_value_to_init
    ))
    print(new_instance_section)
    attribute.delete()
    return JsonResponse(dict(
        status='done',
        data=dict(
            message='Instance: %s has up to section: %s' % (instance.name, new_section.name)
        )
    ))


class GetActivityView(View):

    def get(self, request, *args, **kwargs):

        try:
            instance = Instance.objects.get(id=kwargs['id'])
            area = Area.objects.get(id=request.GET['area'])
            user = User.objects.get(id=instance.user_id)
            section = instance.sections.get(area=area)
        except Exception as e:
            return JsonResponse(dict(status='error', error='Invalid params. %s' % e))

        value = section.level.min + 1
        request_uri = "%s/posts/by_limit/?area_id=%s&value=%s&username=%s" % (settings.CONTENT_MANAGER_URL,
                                                                              area.pk, value, user.username)

        r = requests.get(request_uri)
        response = r.json()

        print(response)
        return JsonResponse(response)
