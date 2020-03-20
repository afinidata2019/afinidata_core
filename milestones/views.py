from django.views.generic import DetailView, UpdateView, ListView, CreateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from milestones.models import Milestone
from django.urls import reverse_lazy
from django.contrib import messages


class HomeView(PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('pages:login')
    permission_required = 'milestones.view_milestone'
    model = Milestone
    context_object_name = 'milestones'
    paginate_by = 50


class MilestoneView(PermissionRequiredMixin, DetailView):
    permission_required = 'milestones.view_milestone'
    login_url = reverse_lazy('pages:login')
    model = Milestone
    pk_url_kwarg = 'milestone_id'


class EditMilestoneView(PermissionRequiredMixin, UpdateView):
    login_url = reverse_lazy('pages:login')
    permission_required = 'milestones.add_milestone'
    model = Milestone
    fields = ('name', 'code', 'second_code', 'area', 'value', 'secondary_value', 'source', 'description')
    pk_url_kwarg = 'milestone_id'
    context_object_name = 'milestone'

    def get_success_url(self):
        messages.success(self.request, 'Milestone with Code: "%s" has been updated.' % self.object.code)
        return reverse_lazy('milestones:milestone', kwargs={'id': self.object.pk})

    def get_context_data(self, **kwargs):
        c = super(EditMilestoneView, self).get_context_data()
        c['action'] = 'Edit'
        return c


class NewMilestoneView(PermissionRequiredMixin, CreateView):
    login_url = reverse_lazy('pages:login')
    permission_required = 'milestones.change_milestone'
    model = Milestone
    fields = ('name', 'code', 'second_code', 'area', 'value', 'secondary_value', 'source', 'description')

    def get_success_url(self):
        messages.success(self.request, 'Milestone with Code: "%s" has been created.' % self.object.code)
        return reverse_lazy('milestones:milestone', kwargs={'id': self.object.pk})

    def get_context_data(self, **kwargs):
        c = super(NewMilestoneView, self).get_context_data()
        c['action'] = 'Create'
        return c


class DeleteMilestoneView(PermissionRequiredMixin, DeleteView):
    login_url = reverse_lazy('pages:login')
    template_name = 'milestones/milestone_form.html'
    permission_required = 'milestones.delete_milestone'
    model = Milestone
    pk_url_kwarg = 'milestone_id'

    def get_context_data(self, **kwargs):
        c = super(DeleteMilestoneView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete milestone with name: "%s"' % self.object.name
        return c

    def get_success_url(self):
        messages.success(self.request, 'Milestone with Code: "%s" has been deleted.' % self.object.code)
        return reverse_lazy('milestones:index')
