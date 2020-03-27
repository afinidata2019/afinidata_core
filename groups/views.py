from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from groups import models


class GroupListView(PermissionRequiredMixin, ListView):
    model = models.Group
    permission_required = 'groups.view_group'
    paginate_by = 30
    login_url = reverse_lazy('pages:login')
    permission_denied_message = 'Unauthorized'


class GroupView(PermissionRequiredMixin, DetailView):
    model = models.Group
    permission_required = 'groups.view_group'
    pk_url_kwarg = 'group_id'
    login_url = reverse_lazy('pages:login')
    permission_denied_message = 'Unauthorized'

    def get_context_data(self, **kwargs):
        c = super(GroupView, self).get_context_data()
        c['last_assignations'] = self.object.assignationmessengeruser_set.all()[:5]
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
