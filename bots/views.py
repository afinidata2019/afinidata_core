from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from messenger_users.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from bots.models import Bot


class HomeView(PermissionRequiredMixin, ListView):
    permission_required = 'bots.view_all_bots'
    model = Bot
    paginate_by = 10
    context_object_name = 'bots'
    login_url = reverse_lazy('pages:login')


class BotView(LoginRequiredMixin, DetailView):
    model = Bot
    pk_url_kwarg = 'bot_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(BotView, self).get_context_data()
        users = User.objects.filter(bot_id=self.kwargs['bot_id'])
        registered = set(user.pk for user in users.filter(userdata__data_key='user_reg',
                                                          userdata__data_value='registered'))
        unregistered = set(user.pk for user in users.filter(userdata__data_key='user_reg',
                                                            userdata__data_value='unregistered')
                           .exclude(id__in=registered))
        with_licence = set(user.pk for user in users.filter(userdata__data_key='tipo_de_licencia'))
        with_rol = set(user.pk for user in users.filter(userdata__data_key='user_rol'))
        with_cname = set(user.pk for user in users.filter(userdata__data_key='childName'))
        with_cdob = set(user.pk for user in users.filter(userdata__data_key='childDOB'))
        with_cdobi = set(user.pk for user in users.filter(userdata__data_key='childDOBinput'))
        with_country = set(user.pk for user in users.filter(userdata__data_key='Pais'))
        c['users'] = users
        c['registered'] = len(registered)
        c['unregistered'] = len(unregistered)
        c['whitout_reg'] = users.count() - (len(registered) + len(unregistered))
        c['with_licence'] = len(with_licence)
        c['without_licence'] = users.count() - len(with_licence)

        return c


class CreateBotView(LoginRequiredMixin, CreateView):
    model = Bot
    fields = ('name', 'description')
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(CreateBotView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Bot with name: %s has been created.' % self.object.name)
        return reverse_lazy('bots:bot_detail', kwargs={'bot_id': self.object.pk})


class UpdateBotView(LoginRequiredMixin, UpdateView):
    model = Bot
    fields = ('name', 'description')
    pk_url_kwarg = 'bot_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(UpdateBotView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Bot with name: %s has been updated.' % self.object.name)
        return reverse_lazy('bots:bot', kwargs={'id': self.object.pk})


class DeleteBotView(LoginRequiredMixin, DeleteView):
    model = Bot
    template_name = 'bots/bot_form.html'
    pk_url_kwarg = 'bot_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(DeleteBotView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete bot with name: "%s"' % self.object.name
        return c

    def get_success_url(self):
        messages.success(self.request, 'Bot with name "%s" has been deleted.' % self.object.name)
        return reverse_lazy('bots:bot_list')


class UserGroupBotsView(PermissionRequiredMixin, ListView):
    permission_required = 'bots.view_user_bots'
    login_url = reverse_lazy('pages:login')
    context_object_name = 'bots'
    paginate_by = 10
    model = Bot

    def get_queryset(self):
        qs = super(UserGroupBotsView, self).get_queryset()
        qs = qs.filter(botassignation__group_id__in=[group.group_id for group in
                                                               self.request.user.rolegroupuser_set.all()])
        return qs
