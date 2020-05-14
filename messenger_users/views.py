from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import  PermissionRequiredMixin
from messenger_users.models import User, UserData
from django.urls import reverse_lazy
from django.contrib import messages
from messenger_users import forms


class HomeView(PermissionRequiredMixin, ListView):
    permission_required = 'messenger_users.view_all_messenger_users'
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


class UserView(PermissionRequiredMixin, DetailView):
    permission_required = 'messenger_users.view_user'
    model = User
    pk_url_kwarg = 'id'
    login_url = reverse_lazy('pages:login')


class UserDataListView(PermissionRequiredMixin, ListView):
    permission_required = 'messenger_users.view_userdata'
    model = UserData
    paginate_by = 30

    def get_queryset(self):
        qs = super(UserDataListView, self).get_queryset()
        qs = qs.filter(user_id=self.kwargs['user_id']).order_by('-created')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(UserDataListView, self).get_context_data()
        ctx['user'] = User.objects.get(id=self.kwargs['user_id'])
        return ctx


class UserDataCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'messenger_users.add_userdata'
    model = UserData
    fields = ('data_key', 'data_value')

    def get_context_data(self, **kwargs):
        c = super(UserDataCreateView, self).get_context_data()
        c['ms_user'] = User.objects.get(id=self.kwargs['user_id'])
        c['action'] = 'Create'
        return c

    def form_valid(self, form):
        form.instance.user_id = self.kwargs['user_id']
        return super(UserDataCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'User data with key: "%s" with data "%s" for user: "%s" has been created.' % (
            self.object.data_key, self.object.data_value, self.object.user
        ))
        return reverse_lazy('messenger_users:user', kwargs=dict(id=self.object.user_id))


class UserDataUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'messenger_users.change_userdata'
    model = UserData
    fields = ('data_value', )
    template_name = 'messenger_users/userdata_edit_form.html'
    pk_url_kwarg = 'userdata_id'

    def get_context_data(self, **kwargs):
        c = super(UserDataUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'User data with key: "%s" with data "%s" for user: "%s" has been updated.' % (
            self.object.data_key, self.object.data_value, self.object.user
        ))
        return reverse_lazy('messenger_users:user', kwargs=dict(id=self.object.user_id))


class UserDataDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'messenger_users.delete_userdata'
    model = UserData
    template_name = 'messenger_users/userdata_delete_form.html'
    pk_url_kwarg = 'userdata_id'

    def get_context_data(self, **kwargs):
        c = super(UserDataDeleteView, self).get_context_data()
        c['action'] = 'Delete'
        return c

    def get_success_url(self):
        messages.success(self.request, 'User data with key: "%s" with data "%s" for user: "%s" has been deleted.' % (
            self.object.data_key, self.object.data_value, self.object.user
        ))
        return reverse_lazy('messenger_users:user', kwargs=dict(id=self.object.user_id))
