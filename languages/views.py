from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
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
        l = Language.objects.all().last()
        c['form'].fields['redirect'].queryset = Language.objects\
            .exclude(id__in=[self.object.pk] + [item.pk for item in self.object.language_set.all()])
        c['form'].fields['redirect'].required = False
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Language with name: "%s" has been updated.' % self.object.name)
        return reverse_lazy('languages:language_detail', kwargs=dict(language_id=self.object.pk))


class LanguageCodeListView(PermissionRequiredMixin, ListView):
    permission_required = 'languages.view_languagecode'
    model = LanguageCode
    login_url = reverse_lazy('pages:login')
    paginate_by = 20

    def get_queryset(self):
        qs = super(LanguageCodeListView, self).get_queryset()
        qs.filter(language_id=self.kwargs['language_id'])
        return qs


class LanguageCodeView(PermissionRequiredMixin, DetailView):
    permission_required = 'languages.view_languagecode'
    model = LanguageCode
    pk_url_kwarg = 'language_code_id'
    login_url = reverse_lazy('pages:login')


class LanguageCodeCreateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'languages.add_languagecode'
    model = LanguageCode
    login_url = reverse_lazy('pages:login')


class LanguageCodeEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'languages.change_languagecode'
    model = LanguageCode
    pk_url_kwarg = 'language_code_id'
    login_url = reverse_lazy('pages:login')


class LanguageCodeDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'languages.delete_languagecode'
    model = LanguageCode
    pk_url_kwarg = 'language_code_id'
    login_url = reverse_lazy('pages:login')
