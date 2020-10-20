from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from instances.models import InstanceAssociationUser
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from messenger_users.models import UserData
from django.urls import reverse_lazy
from django.contrib import messages
from groups import models, forms
from instances.models import AttributeValue
import datetime
from dateutil.parser import parse
from django.db.models import Max


class GroupListView(PermissionRequiredMixin, ListView):
    model = models.Group
    permission_required = 'groups.view_all_groups'
    paginate_by = 30
    login_url = reverse_lazy('pages:login')
    permission_denied_message = 'Unauthorized'


class MyGroupsListView(PermissionRequiredMixin, ListView):
    model = models.Group
    permission_required = 'groups.view_user_groups'
    paginate_by = 30
    login_url = reverse_lazy('pages:login')

    def get_queryset(self):
        qs = super(MyGroupsListView, self).get_queryset()
        qs = qs.filter(rolegroupuser__user=self.request.user)
        return qs


class GroupView(PermissionRequiredMixin, DetailView):
    model = models.Group
    permission_required = 'groups.view_group'
    pk_url_kwarg = 'group_id'
    login_url = reverse_lazy('pages:login')
    permission_denied_message = 'Unauthorized'

    def get_context_data(self, **kwargs):
        c = super(GroupView, self).get_context_data()
        c['last_assignations'] = self.object.assignationmessengeruser_set.all().order_by('-id')[:5]
        print(self.object.programs.all())
        children = 0
        assignations = 0
        assigns = InstanceAssociationUser.objects.filter(
            user_id__in=[u.messenger_user_id for u in self.object.assignationmessengeruser_set.all()])
        '''for assign in self.object.assignationmessengeruser_set.all():
            data = User.objects.get(id=assign.messenger_user_id).get_instances().filter(entity_id=1)
            children = children + data.count()
            assignations = assignations + Interaction.objects.filter(user_id=assign.messenger_user_id,
                                                                     type='dispatched').count()'''
        c['children'] = assigns.count()
        c['assignations'] = assignations
        return c


class GroupDashboardView(PermissionRequiredMixin, DetailView):
    model = models.Group
    permission_required = 'groups.view_group'
    pk_url_kwarg = 'group_id'
    login_url = reverse_lazy('pages:login')
    permission_denied_message = 'Unauthorized'
    template_name = 'groups/group_dashboard.html'

    def get_context_data(self, **kwargs):
        c = super(GroupDashboardView, self).get_context_data()
        c['last_assignations'] = self.object.assignationmessengeruser_set.all().order_by('-id')[:10]
        if self.object.programs.exists():
            c['attribute_types'] = self.object.programs.last().attributetype_set.all()
            program = self.object.programs.last()
        else:
            c['attribute_types'] = []
            program = None
        for assignation in c['last_assignations']:
            user = assignation.user
            assignation.instances = user.get_instances()
            for instance in assignation.instances:
                risk_count = 0
                if program:
                    for attributes_type in program.attributetype_set.all():
                        for program_attribute in attributes_type.attributes_set.all():
                            last_attributes = AttributeValue.objects.filter(instance=instance,
                                                                            attribute=program_attribute.attribute). \
                                values('attribute__id').annotate(max_id=Max('id'))
                            risk_count = risk_count + AttributeValue.objects.filter(
                                id__in=[x['max_id'] for x in last_attributes],
                                value__lte=program_attribute.threshold). \
                                values('instance__id').distinct().count()
                            last_attributes = UserData.objects.filter(user=user,
                                                                      attribute=program_attribute.attribute). \
                                values('user__id', 'attribute_id').annotate(max_id=Max('id'))
                            risk_count = risk_count + \
                                         UserData.objects.filter(id__in=[x['max_id'] for x in last_attributes],
                                                                 data_value__lte=program_attribute.threshold).\
                                             values('user__id').distinct().count()
                if risk_count == 0:
                    instance.risk = 0
                elif risk_count < 4:
                    instance.risk = 1
                else:
                    instance.risk = 2
                if instance.get_attribute_value(191):  # birthday
                    try:
                        instance.birthday = parse(instance.get_attribute_value(191).value).strftime('%d/%m/%Y')
                    except:
                        instance.birthday = instance.get_attribute_value(191).value
                else:
                    instance.birthday = '---'
                if user.userdata_set.filter(attribute_id=13).exists():  # telefono
                    instance.telefono = user.userdata_set.filter(attribute_id=13).last().data_value
                else:
                    instance.telefono = '---'
                if user.userdata_set.filter(attribute_id=190).exists():  # direccion
                    instance.direccion = user.userdata_set.filter(attribute_id=190).last().data_value
                else:
                    instance.direccion = '---'
                try:
                    age = relativedelta(datetime.datetime.now(), parse(instance.get_attribute_value(191).value))
                    months = ''
                    if age.months:
                        months = str(age.months) + ' meses'
                    if age.years:
                        if age.years == 1:
                            months = str(age.years) + ' año ' + months
                        else:
                            months = str(age.years) + ' años ' + months
                except:
                    months = '---'
                instance.months = months
                instance.image = "images/child_user_" + str((instance.id % 10) + 1) + ".jpg"
        try:
            c['ref'] = "m.me/afinidatatutor?ref=" + self.object.code_set.all().last().code
        except:
            c['ref'] = "m.me/afinidatatutor?ref="
        return c


class CreateGroupView(PermissionRequiredMixin, CreateView):
    model = models.Group
    permission_required = 'groups.add_group'
    fields = ('name', 'parent')
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(CreateGroupView, self).get_context_data()
        c['action'] = 'Crear'
        return c

    def get_success_url(self):
        self.object.rolegroupuser_set.create(user=self.request.user, role='administrator')
        messages.success(self.request, 'Grupo con nombre: "%s" ha sido creado.' % self.object.name)
        return reverse_lazy('groups:group', kwargs={'group_id': self.object.pk})


class EditGroupView(PermissionRequiredMixin, UpdateView):
    model = models.Group
    permission_required = 'groups.change_group'
    fields = ('name', 'parent')
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'group_id'

    def get_context_data(self, **kwargs):
        c = super(EditGroupView, self).get_context_data()
        c['action'] = 'Editar'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Grupo con nombre: "%s" ha sido editado.' % self.object.name)
        return reverse_lazy('groups:group', kwargs={'group_id': self.object.pk})


class MessengerUsersListView(PermissionRequiredMixin, ListView):
    model = models.AssignationMessengerUser
    permission_required = 'groups.view_assignationmessengeruser'
    login_url = reverse_lazy('pages:login')
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(MessengerUsersListView, self).get_context_data()
        c['group'] = get_object_or_404(models.Group, id=self.kwargs['group_id'])
        c['count'] = self.get_queryset().count()
        return c

    def get_queryset(self):
        qs = super(MessengerUsersListView, self).get_queryset()
        qs = qs.filter(group_id=self.kwargs['group_id']).order_by('-pk')
        return qs


class AddProgramView(PermissionRequiredMixin, CreateView):
    template_name = 'groups/add_program.html'
    permission_required = 'groups.change_group'
    model = models.ProgramAssignation
    fields = ('program',)

    def get_context_data(self, **kwargs):
        c = super(AddProgramView, self).get_context_data(**kwargs)
        c['group'] = models.Group.objects.get(id=self.kwargs['group_id'])
        return c

    def get_form(self, form_class=None):
        form = super(AddProgramView, self).get_form(form_class=None)
        form.fields['program'].queryset = self.request.user.program_set.all()
        return form

    def form_valid(self, form):
        form.instance.group_id = self.kwargs['group_id']
        form.instance.user = self.request.user
        return super(AddProgramView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Program added to group')
        return reverse_lazy('groups:group', kwargs={'group_id': self.kwargs['group_id']})
