from django.shortcuts import get_object_or_404, redirect
from levels.models import Level
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


class ListLevelView(LoginRequiredMixin, ListView):
    model = Level
    context_object_name = 'levels'
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'


class LevelView(LoginRequiredMixin, TemplateView):
    template_name = 'levels/level.html'
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        level = get_object_or_404(Level, id=kwargs['id'])
        return dict(level=level)


class CreateLevelView(LoginRequiredMixin, CreateView):
    model = Level
    template_name = 'levels/new.html'
    fields = ('name', 'min', 'max')
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        level = form.save()
        messages.success(self.request, 'Level with name: "%s" has been created' % level.name)
        return redirect('levels:index')


class UpdateLevelView(LoginRequiredMixin, UpdateView):
    template_name = 'levels/edit.html'
    model = Level
    fields = ('name', 'min', 'max')
    pk_url_kwarg = 'id'
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        level = form.save()
        messages.success(self.request, 'Level with name %s has been updated' % level.name)
        return redirect('levels:index')
