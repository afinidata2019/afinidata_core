from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from messenger_users.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from groups import models


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
        children = 0
        for assign in self.object.assignationmessengeruser_set.all():
            data = User.objects.get(id=assign.messenger_user_id).get_instances().filter(entity_id=1).count()
            children = children + data
        c['children'] = children
        return c


class CreateGroupView(PermissionRequiredMixin, CreateView):
    model = models.Group
    permission_required = 'groups.add_group'
    fields = ('name',)
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(CreateGroupView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Group with name: "%s" has been created.' % self.object.name)
        print(self.object.pk, self.object.name)
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
