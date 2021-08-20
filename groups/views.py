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
from programs.models import Program
import datetime
from dateutil.parser import parse
from django.db.models import Max
import threading


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
    permission_required = 'groups.view_all_groups'
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


class CreateGroupView(PermissionRequiredMixin, CreateView):
    model = models.Group
    permission_required = 'groups.add_group'
    form_class = forms.CreateGroup
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(CreateGroupView, self).get_context_data()
        c['action'] = 'Crear'
        return c

    def get_form(self, form_class=None):
        form = super(CreateGroupView, self).get_form(form_class=forms.CreateGroup)
        if not self.request.user.is_superuser:
            form.fields['program'].queryset = self.request.user.program_set.all()
        return form


    def get_success_url(self):
        self.object.rolegroupuser_set.create(user=self.request.user, role='administrator')
        self.object.botassignation_set.create(user=self.request.user, bot_id=self.request.POST['bot'])
        program = Program.objects.get(id=self.request.POST['program'])
        self.object.programs.add(program)
        messages.success(self.request, 'Grupo con nombre: "%s" ha sido creado.' % self.object.name)
        return reverse_lazy('groups:group', kwargs={'group_id': self.object.pk})


def change_users_license(group):
    print(group)
    for a in group.assignationmessengeruser_set.all():
        a.user.license = group.license
        a.user.save()
        print(a.user.license)


class EditGroupView(PermissionRequiredMixin, UpdateView):
    model = models.Group
    permission_required = 'groups.change_group'
    fields = ('name', 'parent', 'country', 'region', 'license')
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'group_id'

    def get_context_data(self, **kwargs):
        c = super(EditGroupView, self).get_context_data()
        c['action'] = 'Editar'
        return c

    def get_success_url(self):
        x = threading.Thread(target=change_users_license, args=(self.object, ))
        x.start()
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


class AddBotView(PermissionRequiredMixin, CreateView):
    template_name = 'groups/add_bot.html'
    permission_required = 'groups.change_group'
    model = models.BotAssignation
    fields = ('bot',)

    def form_valid(self, form):
        form.instance.group_id = self.kwargs['group_id']
        form.instance.user = self.request.user
        return super(AddBotView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Bot added to group')
        return reverse_lazy('groups:group', kwargs={'group_id': self.kwargs['group_id']})

    def get_context_data(self, **kwargs):
        c = super(AddBotView, self).get_context_data(**kwargs)
        c['group'] = models.Group.objects.get(id=self.kwargs['group_id'])
        return c
