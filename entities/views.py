from django.views.generic import UpdateView, CreateView, DeleteView, View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from entities.forms import EntityAttributeForm
from attributes.models import Attribute
from django.urls import reverse_lazy
from django.contrib import messages
from entities.models import Entity


class HomeView(PermissionRequiredMixin, ListView):
    permission_required = 'entities.view_all_entities'
    model = Entity
    login_url = reverse_lazy('pages:login')


class EntityView(PermissionRequiredMixin, DetailView):
    permission_required = 'entities.view_entity'
    model = Entity
    pk_url_kwarg = 'entity_id'
    login_url = reverse_lazy('pages:login')


class NewEntityView(PermissionRequiredMixin, CreateView):
    permission_required = 'entities.add_entity'
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description')
    model = Entity

    def get_context_data(self, **kwargs):
        c = super(NewEntityView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Entity with name: %s has been created.' % self.object.name)
        return reverse_lazy('entities:entity_detail', kwargs=dict(entity_id=self.object.pk))


class EditEntityView(PermissionRequiredMixin, UpdateView):
    permission_required = 'entities.change_entity'
    model = Entity
    fields = ('name', 'description')
    pk_url_kwarg = 'entity_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(EditEntityView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Entity with name: %s has been updated.' % self.object.name)
        return reverse_lazy('entities:entity_detail', kwargs=dict(entity_id=self.object.pk))


class DeleteEntityView(PermissionRequiredMixin, DeleteView):
    permission_required = 'entities.delete_entity'
    template_name = 'entities/entity_form.html'
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'entity_id'
    model = Entity

    def get_context_data(self, **kwargs):
        c = super(DeleteEntityView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete entity with name: "%s"?' % self.object.name
        return c

    def get_success_url(self):
        messages.success(self.request, 'Entity with name: %s has been deleted.' % self.object.name)
        return reverse_lazy('entities:entity_list')


class AddAttributeToEntityView(LoginRequiredMixin, View):
    login_url = reverse_lazy('pages:login')

    def get(self, request, *args, **kwargs):
        entity = get_object_or_404(Entity, id=kwargs['id'])
        exclude_arr = [item.pk for item in entity.attributes.all()]
        queryset = Attribute.objects.all().exclude(id__in=exclude_arr)
        form = EntityAttributeForm(request.POST or None, queryset=queryset)
        return render(request, 'entities/new.html', dict(form=form, action='Set attribute to'))

    def post(self, request, *args, **kwargs):

        entity = get_object_or_404(Entity, id=kwargs['id'])
        queryset = Attribute.objects.filter(id=request.POST['attribute'])
        form = EntityAttributeForm(request.POST, queryset=queryset)

        if form.is_valid():
            attribute = Attribute.objects.get(id=request.POST['attribute'])
            entity.attributes.add(attribute)
            messages.success(request, 'Attribute has been added to entity')
            return redirect('entities:entity', id=entity.pk)
        else:
            messages.success(request, 'Invalid params.')
            return redirect('entities:entity', id=entity.pk)
