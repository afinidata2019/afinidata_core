from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from attributes.models import Attribute
from django.urls import reverse_lazy
from django.contrib import messages


class AttributesView(PermissionRequiredMixin, ListView):
    permission_required = 'attributes.view_all_attributes'
    login_url = reverse_lazy('pages:login')
    model = Attribute
    paginate_by = 5


class NewAttributeView(PermissionRequiredMixin, CreateView):
    permission_required = 'attributes.add_attribute'
    model = Attribute
    fields = ('name', 'type')
    login_url = reverse_lazy('pages:login')

    def get_success_url(self):
        messages.success(self.request, 'Attribute with name: %s has been created.' % self.object.name)
        return reverse_lazy('attributes:attribute_detail', kwargs={'attribute_id': self.object.pk})

    def get_context_data(self, **kwargs):
        c = super(NewAttributeView, self).get_context_data()
        c['action'] = 'Create'
        return c


class AttributeView(PermissionRequiredMixin, DetailView):
    permission_required = 'attributes.view_attribute'
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'attribute_id'
    model = Attribute


class EditAttributeView(PermissionRequiredMixin, UpdateView):
    permission_required = 'attributes.change_attribute'
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'attribute_id'
    fields = ('name', 'type')
    model = Attribute

    def get_success_url(self):
        messages.success(self.request, 'Attribute with name "%s" has been updated.' % self.object.name)
        return reverse_lazy('attributes:attribute_detail', kwargs={'attribute_id': self.object.pk})

    def get_context_data(self, **kwargs):
        c = super(EditAttributeView, self).get_context_data()
        c['action'] = 'Edit'
        return c


class DeleteAttributeView(PermissionRequiredMixin, DeleteView):
    permission_required = 'attributes.delete_attribute'
    template_name = 'attributes/attribute_form.html'
    model = Attribute
    pk_url_kwarg = 'attribute_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(DeleteAttributeView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete attribute with name: "%s"?' % self.object.name
        return c

    def get_success_url(self):
        messages.success(self.request, 'Attribute with name "%s" has been deleted.' % self.object.name)
        return reverse_lazy('attributes:attribute_list')
