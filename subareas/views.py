from django.views.generic import UpdateView, ListView, DetailView, DeleteView, CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from subareas.models import Subarea


class HomeView(PermissionRequiredMixin, ListView):
    permission_required = 'subareas.view_all_subareas'
    login_url = reverse_lazy('pages:login')
    paginate_by = 10
    model = Subarea


class EditSubareaView(PermissionRequiredMixin, UpdateView):
    permission_required = 'subareas.change_subarea'
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description')
    pk_url_kwarg = 'subarea_id'
    model = Subarea

    def get_context_data(self, **kwargs):
        c = super(EditSubareaView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Subarea with name: %s has been updated.' % self.object.name)
        return reverse_lazy('subareas:subarea_detail', kwargs=dict(subarea_id=self.object.pk))


class SubareaView(PermissionRequiredMixin, DetailView):
    permission_required = 'subareas.view_subarea'
    login_url = reverse_lazy('pages:login')
    context_object_name = 'subarea'
    pk_url_kwarg = 'subarea_id'
    model = Subarea


class NewSubareaView(PermissionRequiredMixin, CreateView):
    permission_required = 'subareas.add_subarea'
    model = Subarea
    fields = ('name', 'description')
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(NewSubareaView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Subarea with name: %s has been created.' % self.object.name)
        return reverse_lazy('subareas:subarea_detail', kwargs=dict(subarea_id=self.object.pk))


class DeleteSubareaView(PermissionRequiredMixin, DeleteView):
    permission_required = 'subareas.delete_subarea'
    template_name = 'subareas/subarea_form.html'
    model = Subarea
    pk_url_kwarg = 'subarea_id'
    login_url = reverse_lazy('pages:login')

    def get_success_url(self):
        messages.success(self.request, 'Subarea with name: %s has been deleted.' % self.object.name)
        return reverse_lazy('subareas:subarea_list')

    def get_context_data(self, **kwargs):
        c = super(DeleteSubareaView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete subarea with name: "%s"?' % self.object.name
        return c
