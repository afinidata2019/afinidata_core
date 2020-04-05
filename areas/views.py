from django.views.generic import UpdateView, ListView, DetailView, DeleteView, CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from areas.models import Area


class HomeView(PermissionRequiredMixin, ListView):
    permission_required = 'areas.view_all_areas'
    login_url = reverse_lazy('pages:login')
    paginate_by = 10
    model = Area


class EditAreaView(PermissionRequiredMixin, UpdateView):
    permission_required = 'areas.change_area'
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description', 'background_color', 'point_color', 'another_color')
    pk_url_kwarg = 'area_id'
    model = Area

    def get_context_data(self, **kwargs):
        c = super(EditAreaView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Area with name: %s has been updated.' % self.object.name)
        return reverse_lazy('areas:area_detail', kwargs=dict(area_id=self.object.pk))


class AreaView(PermissionRequiredMixin, DetailView):
    permission_required = 'areas.view_area'
    login_url = reverse_lazy('pages:login')
    context_object_name = 'area'
    pk_url_kwarg = 'area_id'
    model = Area


class NewAreaView(PermissionRequiredMixin, CreateView):
    permission_required = 'areas.add_area'
    model = Area
    fields = ('name', 'description', 'background_color', 'point_color', 'another_color')
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(NewAreaView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Area with name: %s has been created.' % self.object.name)
        return reverse_lazy('areas:area_detail', kwargs=dict(area_id=self.object.pk))


class DeleteAreaView(PermissionRequiredMixin, DeleteView):
    permission_required = 'areas.delete_area'
    template_name = 'areas/area_form.html'
    model = Area
    pk_url_kwarg = 'area_id'
    login_url = reverse_lazy('pages:login')

    def get_success_url(self):
        messages.success(self.request, 'Area with name: %s has been deleted.' % self.object.name)
        return reverse_lazy('areas:area_list')

    def get_context_data(self, **kwargs):
        c = super(DeleteAreaView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete area with name: "%s"?' % self.object.name
        return c
