from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from messenger_users.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from bots import models


class HomeView(PermissionRequiredMixin, ListView):
    permission_required = 'bots.view_all_bots'
    model = models.Bot
    paginate_by = 10
    context_object_name = 'bots'
    login_url = reverse_lazy('pages:login')


class BotView(LoginRequiredMixin, DetailView):
    model = models.Bot
    pk_url_kwarg = 'bot_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(BotView, self).get_context_data()
        users = User.objects.filter(bot_id=self.kwargs['bot_id'])
        total = users.count()
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
        with_premium = set(user.pk for user in users.filter(userdata__data_key='premium'))
        c['users'] = users
        c['registered'] = len(registered)
        c['unregistered'] = len(unregistered)
        c['whitout_reg'] = total - (len(registered) + len(unregistered))
        c['with_licence'] = len(with_licence)
        c['without_licence'] = total - c['with_licence']
        c['with_rol'] = len(with_rol)
        c['without_rol'] = total - c['with_rol']
        c['with_name'] = len(with_cname)
        c['without_name'] = total - c['with_name']
        c['with_cdob'] = len(with_cdob)
        c['without_cdob'] = total - c['with_cdob']
        c['with_cdobi'] = len(with_cdobi)
        c['without_cdobi'] = total - c['with_cdobi']
        c['with_country'] = len(with_country)
        c['without_country'] = total - c['with_country']
        c['with_premium'] = len(with_premium)
        c['without_premium'] = total - c['with_premium']

        return c


class CreateBotView(LoginRequiredMixin, CreateView):
    model = models.Bot
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
    model = models.Bot
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
    model = models.Bot
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
    model = models.Bot

    def get_queryset(self):
        qs = super(UserGroupBotsView, self).get_queryset()
        qs = qs.filter(botassignation__group_id__in=[group.group_id for group in
                                                               self.request.user.rolegroupuser_set.all()])
        return qs


class BotInteractionListView(PermissionRequiredMixin, ListView):
    permission_required = 'bots.view_interaction'
    login_url = reverse_lazy('pages:login')
    model = models.Interaction
    paginate_by = 10


class BotInteractionDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'bots.view_interaction'
    login_url = reverse_lazy('pages:login')
    model = models.Interaction
    pk_url_kwarg = 'interaction_id'


class CreateBotInteractionView(PermissionRequiredMixin, CreateView):
    permission_required = 'bots.add_interaction'
    login_url = reverse_lazy('pages:login')
    model = models.Interaction
    fields = ('name', 'description')

    def get_context_data(self, **kwargs):
        c = super(CreateBotInteractionView, self).get_context_data(**kwargs)
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'The interaction "%s" has been created.' % self.object.name)
        return reverse_lazy('bot_interactions:bot_interaction_detail', kwargs={'interaction_id': self.object.pk})


class UpdateBotInteractionView(PermissionRequiredMixin, UpdateView):
    permission_required = 'bots.change_interaction'
    login_url = reverse_lazy('pages:login')
    model = models.Interaction
    fields = ('name', 'description')
    pk_url_kwarg = 'interaction_id'

    def get_context_data(self, **kwargs):
        c = super(UpdateBotInteractionView, self).get_context_data(**kwargs)
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'The interaction "%s" has been updated.' % self.object.name)
        return reverse_lazy('bot_interactions:bot_interaction_detail', kwargs={'interaction_id': self.object.pk})
