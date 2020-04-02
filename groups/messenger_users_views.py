from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, CreateView, DeleteView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from django.contrib import messages
from groups import models


class AddMessengerUserView(PermissionRequiredMixin, CreateView):
    permission_required = 'groups.add_assignationmessengeruser'
    model = models.AssignationMessengerUser
    fields = ('messenger_user_id',)

    def get_context_data(self, **kwargs):
        c = super(AddMessengerUserView, self).get_context_data()
        c['action'] = 'Add'
        c['group'] = get_object_or_404(models.Group, id=self.kwargs['group_id'])
        return c

    def form_valid(self, form):
        form.instance.group = get_object_or_404(models.Group, id=self.kwargs['group_id'])
        return super(AddMessengerUserView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Messenger User: "%s %s" has been added to group.' %
                         (self.object.get_messenger_user().get_first_name(),
                          self.object.get_messenger_user().get_last_name()))
        return reverse_lazy('groups:group', kwargs={'group_id': self.object.group.pk})


class RemoveMessengerUserView(PermissionRequiredMixin, DeleteView):
    permission_required = 'groups.delete_assignationmessengeruser'
    model = models.AssignationMessengerUser
    pk_url_kwarg = 'assignation_id'
    template_name = 'groups/group_form.html'

    def get_context_data(self, **kwargs):
        c = super(RemoveMessengerUserView, self).get_context_data()
        c['action'] = 'Remove User to'
        c['delete_message'] = 'Are you sure to remove association with user "%s" to group: %s?' % (
            "%s %s" % (self.object.get_messenger_user().first_name, self.object.get_messenger_user().last_name),
            self.object.group.name
        )
        return c

    def get_success_url(self):
        messages.success(self.request,
                         'User with ID: "%s" has been removed to group.' % self.object.get_messenger_user().pk)
        return reverse_lazy('groups:group', kwargs=dict(group_id=self.object.group_id))
