from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from languages.models import Language, LanguageCode
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages


class LanguageListView(PermissionRequiredMixin, ListView):
    model = Language
    permission_required = 'languages.view_language'
    paginate_by = 20
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

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(LanguageCodeListView, self).get_context_data()
        c['language'] = get_object_or_404(Language, id=self.kwargs['language_id'])
        print(c)
        return c


class LanguageCodeView(PermissionRequiredMixin, DetailView):
    permission_required = 'languages.view_languagecode'
    model = LanguageCode
    pk_url_kwarg = 'language_code_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(LanguageCodeView, self).get_context_data()
        c['language'] = get_object_or_404(Language, id=self.kwargs['language_id'])
        return c


class LanguageCodeCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'languages.add_languagecode'
    model = LanguageCode
    login_url = reverse_lazy('pages:login')
    fields = ('code', 'description')

    def get_context_data(self, **kwargs):
        c = super(LanguageCodeCreateView, self).get_context_data()
        c['language'] = get_object_or_404(Language, id=self.kwargs['language_id'])
        c['action'] = 'Create'
        return c

    def form_valid(self, form):
        language = get_object_or_404(Language, id=self.kwargs['language_id'])
        form.instance.language = language
        return super(LanguageCodeCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Language code: "%s" for language: "%s" has been added.' % (
            self.object.code, self.object.language.name
        ))
        return reverse_lazy('languages:language_code',
                            kwargs=dict(
                                language_id=self.object.language_id,
                                language_code_id=self.object.pk
                            ))


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
