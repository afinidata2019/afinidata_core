from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, CreateView, DeleteView, View, ListView, DetailView
from entities.models import Entity
from attributes.models import Attribute
from django.urls import reverse_lazy
from django.http import JsonResponse
from entities.forms import EntityAttributeForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'entities/index.html'
    model = Entity
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'
    context_object_name = 'entities'


class EntityView(LoginRequiredMixin, DetailView):
    template_name = 'entities/entity.html'
    model = Entity
    pk_url_kwarg = 'id'
    context_object_name = 'entity'
    login_url = reverse_lazy('pages:login')


class NewEntityView(LoginRequiredMixin, CreateView):
    model = Entity
    template_name = 'entities/new.html'
    fields = ('name', 'description')
    context_object_name = 'entity'
    login_url = reverse_lazy('pages:login')

    def form_valid(self, form):
        entity = form.save()
        messages.success(self.request, 'Entity with name: %s has been created.' % entity.name)
        return redirect('entities:index')


class EditEntityView(LoginRequiredMixin, UpdateView):
    model = Entity
    fields = ('name', 'description')
    template_name = 'entities/edit.html'
    pk_url_kwarg = 'id'
    context_object_name = 'entity'
    login_url = reverse_lazy('pages:login')

    def form_valid(self, form):
        entity = form.save()
        messages.success(self.request, 'Entity with name: %s has been updated.' % entity.name)
        return redirect('entities:edit', entity.pk)


class DeleteEntityView(LoginRequiredMixin, DeleteView):
    model = Entity
    template_name = 'entities/delete.html'
    pk_url_kwarg = 'id'
    login_url = reverse_lazy('pages:login')
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy('entities:index')


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
