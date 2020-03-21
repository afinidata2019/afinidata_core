from django.views.generic import ListView, View, DetailView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from messenger_users.models import User, UserData
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib import messages
from messenger_users import forms
import os


class HomeView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('pages:login')
    paginate_by = 30
    model = User

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(HomeView, self).get_context_data()
        c['form'] = forms.SearchUserForm(self.request.GET or None)
        c['get_params'] = self.request.GET.copy()
        if 'page' in c['get_params']:
            del c['get_params']['page']
        c['get_params'] = c['get_params'].urlencode()
        return c

    def get_queryset(self):
        queryset = super(HomeView, self).get_queryset()
        form = forms.SearchUserForm(self.request.GET or None)
        if form.is_valid():
            if 'id' in form.data:
                if form.cleaned_data['id']:
                    queryset = queryset.filter(id=form.cleaned_data['id'])
            if 'bot' in form.data:
                if form.cleaned_data['bot']:
                    queryset = queryset.filter(bot_id=form.cleaned_data['bot'].pk)
            if 'name' in form.data:
                if form.cleaned_data['name']:
                    queryset = queryset.filter(first_name__contains=form.cleaned_data['name'])
            if 'last_name' in form.data:
                if form.cleaned_data['last_name']:
                    queryset = queryset.filter(last_name__contains=form.cleaned_data['last_name'])
        return queryset


class ByGroupView(LoginRequiredMixin, ListView):
    template_name = 'messenger_users/by_group.html'
    login_url = reverse_lazy('pages:login')
    context_object_name = 'users'
    paginate_by = 300
    model = User

    def get_queryset(self):
        return User.objects.filter(userdata__data_key='AB_group', userdata__data_value=self.kwargs['group'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ByGroupView, self).get_context_data(**kwargs)
        context['total'] = User.objects.filter(userdata__data_key='AB_group',
                                               userdata__data_value=self.kwargs['group']).count()
        months_group = set(item.data_value for item in UserData.objects.filter(data_key='months_group')
                           .order_by('data_value'))
        context['months_groups'] = months_group
        print(context)
        return context


class UserView(LoginRequiredMixin, DetailView):
    model = User
    pk_url_kwarg = 'id'
    login_url = reverse_lazy('pages:login')


class EditAttributeView(LoginRequiredMixin, UpdateView):
    model = UserData
    pk_url_kwarg = 'attribute_id'
    fields = ('data_value',)
    template_name = 'messenger_users/data_edit.html'
    context_object_name = 'data'
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'

    def get_object(self, queryset=None):
        object = get_object_or_404(UserData, user_id=self.kwargs['id'], id=self.kwargs['attribute_id'])
        return object

    def form_valid(self, form):
        data = form.save()
        messages.success(self.request, 'Attribute with name: %s has been updated' % data.data_key)
        return redirect('messenger_users:user', id=self.kwargs['id'])


class DeleteAttributeView(LoginRequiredMixin, DeleteView):
    model = UserData
    pk_url_kwarg = 'attribute_id'
    template_name = 'messenger_users/data_delete.html'
    context_object_name = 'data'
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy('messenger_users:index')

    def get_object(self, queryset=None):
        object = get_object_or_404(UserData, user_id=self.kwargs['id'], id=self.kwargs['attribute_id'])
        return object
