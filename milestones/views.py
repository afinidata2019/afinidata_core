from django.views.generic import DetailView, UpdateView, ListView, CreateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from milestones.models import Milestone
from django.urls import reverse_lazy
from django.contrib import messages
from milestones import forms


class HomeView(PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('pages:login')
    permission_required = 'milestones.view_milestone'
    model = Milestone
    context_object_name = 'milestones'
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(HomeView, self).get_context_data()
        c['form'] = forms.MilestoneSearchForm(self.request.GET or None)
        c['get_params'] = self.request.GET.copy()
        if 'page' in c['get_params']:
            del c['get_params']['page']
        c['get_params'] = c['get_params'].urlencode()
        return c

    def get_queryset(self):
        qs = super(HomeView, self).get_queryset()
        form = forms.MilestoneSearchForm(self.request.GET or None)
        if form.is_valid():
            if 'area' in form.data:
                if form.data['area']:
                    qs = qs.filter(area__name=form.data['area'])
            if 'code' in form.data:
                if form.data['code']:
                    qs = qs.filter(code=form.data['code'])
            if 'second_code' in form.data:
                if form.data['second_code']:
                    qs = qs.filter(second_code=form.data['second_code'])
        return qs


class MilestoneView(PermissionRequiredMixin, DetailView):
    permission_required = 'milestones.view_milestone'
    login_url = reverse_lazy('pages:login')
    model = Milestone
    pk_url_kwarg = 'milestone_id'


class EditMilestoneView(PermissionRequiredMixin, UpdateView):
    login_url = reverse_lazy('pages:login')
    permission_required = 'milestones.add_milestone'
    model = Milestone
    fields = ('name', 'code', 'second_code', 'areas', 'value', 'secondary_value', 'source', 'description')
    pk_url_kwarg = 'milestone_id'
    context_object_name = 'milestone'

    def get_success_url(self):
        messages.success(self.request, 'Milestone with Code: "%s" has been updated.' % self.object.code)
        return reverse_lazy('milestones:milestone', kwargs={'milestone_id': self.object.pk})

    def get_context_data(self, **kwargs):
        c = super(EditMilestoneView, self).get_context_data()
        c['action'] = 'Edit'
        return c


class NewMilestoneView(PermissionRequiredMixin, CreateView):
    login_url = reverse_lazy('pages:login')
    permission_required = 'milestones.change_milestone'
    model = Milestone
    fields = ('name', 'code', 'second_code', 'areas', 'value', 'secondary_value', 'source', 'description')

    def get_success_url(self):
        messages.success(self.request, 'Milestone with Code: "%s" has been created.' % self.object.code)
        return reverse_lazy('milestones:milestone', kwargs={'milestone_id': self.object.pk})

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
