from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from languages.models import Language, LanguageCode
from django.urls import reverse_lazy
from django.contrib import messages


class LanguageListView(PermissionRequiredMixin, ListView):
    model = Language
    permission_required = 'languages.view_language'
    paginate_by = 1
    login_url = reverse_lazy('pages:login')


class LanguageView(PermissionRequiredMixin, DetailView):
    model = Language
    permission_required = 'languages.view_language'
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'language_id'


class LanguageCreateView(PermissionRequiredMixin, CreateView):
    model = Language
    permission_required = 'languages.add_language'
    fields = ('name', 'description', 'available', 'redirect')
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(LanguageCreateView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Language with name: "%s" has been created.' % self.object.name)
        return reverse_lazy('languages:language_detail', kwargs=dict(language_id=self.object.pk))


class LanguageEditView(PermissionRequiredMixin, UpdateView):
    model = Language
    permission_required = 'languages.add_language'
    fields = ('description', 'available', 'redirect')
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'language_id'

    def get_context_data(self, **kwargs):
        c = super(LanguageEditView, self).get_context_data(**kwargs)
        c['form'].fields['redirect'].queryset = Language.objects.exclude(id=self.object.pk)
        c['form'].fields['redirect'].required = False
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Language with name: "%s" has been updated.' % self.object.name)
        return reverse_lazy('languages:language_detail', kwargs=dict(language_id=self.object.pk))
