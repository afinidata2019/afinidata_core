import os
import requests
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from messenger_users.models import User, UserData, UserChannel
from django.db import connection
from channels.models import Channel
from attributes.models import Attribute
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from posts.models import Interaction
from articles.models import Interaction as ArticleInteraction
from django.contrib import messages
from messenger_users import forms
from dateutil.parser import parse
from user_sessions.models import Session, Field, Message, Reply, UserInput, Interaction as SessionInteraction
from bots.models import UserInteraction
from groups.models import AssignationMessengerUser
from django.db.models import Max


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
    def get_context_data(self, **kwargs):
        c = super(UserView, self).get_context_data()
        quick_replies = []
        replies = SessionInteraction.objects.filter(user_id=self.object.pk,
                                                    type__in=['quick_reply', 'user_input']).order_by('-id')
        assignations = AssignationMessengerUser.objects.filter(user_id=self.object.pk)
        if assignations:
            c['assignations'] = assignations
        for reply in replies:
            rep = dict()
            field = Field.objects.filter(id=reply.field_id).first()
            rep['session'] = Session.objects.get(id=reply.session_id)
            rep['response'] = reply.created_at
            if reply.type == 'quick_reply':
                qfs = Field.objects.filter(session_id=field.session_id, position=field.position - 1)
                if qfs.exists():
                    question_field = qfs.last()
                    qns = Message.objects.filter(field_id=question_field.id).order_by('id')
                    if qns.exists():
                        rep['question'] = qns.last().text
                answer = Reply.objects.filter(field_id=field.id, value=reply.value)
                if answer.exists():
                    rep['answer'] = answer.first().label
                    rep['attribute'] = answer.first().attribute
                else:
                    rep['answer'] = reply.text or ''
                    rep['attribute'] = Reply.objects.filter(field_id=field.id).first().attribute
                Attribute.objects.filter(name=rep['attribute']).first()
                rep['value'] = reply.value or 0
            elif reply.type == 'user_input':
                rep['question'] = UserInput.objects.filter(field_id=field.id).first().text
                rep['answer'] = reply.text
                rep['value'] = ''
                rep['attribute'] = UserInput.objects.filter(field_id=field.id).first().attribute.name
            quick_replies.append(rep)
        c['quick_replies'] = quick_replies
        user_channel = UserChannel.objects.filter(user_id=self.object.pk)
        if user_channel.exists():
            c['bot_id'] = user_channel.last().bot_id
            c['channel'] = user_channel.last().channel_id
            channel = Channel.objects.filter(id=user_channel.last().channel_id)
            if channel.exists():
                c['channel'] = channel.last().name
        else:
            c['bot_id'] = ''
            c['channel'] = ''
        return c


class DeleteUserView(PermissionRequiredMixin, DeleteView):
    permission_required = 'messenger_users.delete_user'
    model = User
    template_name = 'messenger_users/user_form.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('messenger_users:index')
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(DeleteUserView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = '¿Estás segura de eliminar el usuario con nombre: "%s %s", ID: %s?' %\
                              (self.object.first_name, self.object.last_name, self.object.id)
        return c

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        # Delete live chat history
        for user_channel in self.object.userchannel_set.all():
            user_channel.livechat_set.all().delete()
            user_channel.interaction_set.all().delete()
        with connection.cursor() as cursor:
            # Delete instances
            cursor.execute("delete from instances_attributevalue where instance_id in (select instance_id from instances_instanceassociationuser where user_id = %s);", [self.object.id])
            cursor.execute("delete from instances_response where instance_id in (select instance_id from instances_instanceassociationuser where user_id = %s);", [self.object.id])
            cursor.execute("delete from user_sessions_interaction where instance_id in (select instance_id from instances_instanceassociationuser where user_id = %s);", [self.object.id])
            cursor.execute("delete from instances_postinteraction where instance_id in (select instance_id from instances_instanceassociationuser where user_id =%s);", [self.object.id])
            cursor.execute("delete from instances_instance_sessions where instance_id in (select instance_id from instances_instanceassociationuser where user_id = %s);", [self.object.id])
            cursor.execute("delete from instances_instanceassociationuser where user_id = %s", [self.object.id])
            cursor.execute("delete from instances_instance where id in (select instance_id from instances_instanceassociationuser where user_id = %s);", [self.object.id])
            # Delete user data/interactions
            cursor.execute("delete from messenger_users_userdata where user_id = %s;", [self.object.id])
            cursor.execute("delete from bots_userinteraction where user_id = %s;", [self.object.id])
            cursor.execute("delete from user_sessions_interaction where user_id = %s;", [self.object.id])
            cursor.execute("delete from messenger_users_userchannel where user_id = %s;", [self.object.id])
            cursor.execute("delete from articles_articlefeedback where user_id = %s;", [self.object.id])
            cursor.execute("delete from messenger_users_childdata where child_id in (select id from messenger_users_child where parent_user_id = %s);",[self.object.id])
            cursor.execute("delete from groups_assignationmessengeruser where messenger_user_id = %s;", [self.object.id])
            cursor.execute("delete from messenger_users_child where parent_user_id = %s;", [self.object.id])
            cursor.execute("delete from messenger_users_referral where user_opened_id = %s;", [self.object.id])
            cursor.execute("delete from messenger_users_useractivitylog where user_id = %s;", [self.object.id])
            cursor.execute("delete from messenger_users_useractivity where user_id = %s;", [self.object.id])
            cursor.execute("delete from messenger_users_child where parent_user_id = %s;", [self.object.id])
        return super(DeleteUserView, self).delete(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Usuario con nombre: "%s %s" fue eliminado.' %
                         (self.object.first_name, self.object.last_name))
        return super(DeleteUserView, self).get_success_url()


class UserInteractionsView(PermissionRequiredMixin, DetailView):
    permission_required = 'messenger_users.view_user'
    model = User
    pk_url_kwarg = 'id'
    template_name = 'messenger_users/interactions_detail.html'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(UserInteractionsView, self).get_context_data()
        c['bot_interactions'] = UserInteraction.objects.filter(user=self.object)[:20]
        c['post_interactions'] = self.object.get_post_interactions()[:20]
        c['article_interactions'] = self.object.get_article_interactions()[:20]
        c['session_interactions'] = SessionInteraction.objects.filter(user=self.object).order_by('-id')[:20]
        return c


class UserBotInteractionListView(PermissionRequiredMixin, ListView):
    permission_required = 'messenger_users.view_user'
    model = UserInteraction
    paginate_by = 30
    template_name = 'messenger_users/bot_interaction_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(UserBotInteractionListView, self).get_context_data(object_list=None, **kwargs)
        c['user'] = User.objects.get(id=self.kwargs['id'])
        return c

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['id'])
        return UserInteraction.objects.filter(user=user)


class UserPostInteractionListView(PermissionRequiredMixin, ListView):
    permission_required = 'messenger_users.view_user'
    model = Interaction
    paginate_by = 30
    template_name = 'messenger_users/post_interaction_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(UserPostInteractionListView, self).get_context_data(object_list=None, **kwargs)
        c['user'] = User.objects.get(id=self.kwargs['id'])
        return c

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['id'])
        return user.get_post_interactions()


class UserArticleInteractionListView(PermissionRequiredMixin, ListView):
    permission_required = 'messenger_users.view_user'
    model = ArticleInteraction
    paginate_by = 30
    template_name = 'messenger_users/article_interaction_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(UserArticleInteractionListView, self).get_context_data(object_list=None, **kwargs)
        c['user'] = User.objects.get(id=self.kwargs['id'])
        return c

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['id'])
        return user.get_article_interactions()


class UserSessionInteractionListView(PermissionRequiredMixin, ListView):
    permission_required = 'messenger_users.view_user'
    model = SessionInteraction
    paginate_by = 30
    template_name = 'messenger_users/session_interaction_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(UserSessionInteractionListView, self).get_context_data(object_list=None, **kwargs)
        c['user'] = User.objects.get(id=self.kwargs['id'])
        return c

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['id'])
        return SessionInteraction.objects.filter(user=user).order_by('-id')


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


class UserLastDataListView(PermissionRequiredMixin, ListView):
    permission_required = 'messenger_users.add_userdata'
    template_name = 'messenger_users/userlastdata_list.html'
    model = UserData
    paginate_by = 30

    def get_queryset(self):
        qs = super(UserLastDataListView, self).get_queryset().filter(user_id=self.kwargs['user_id'])
        last_attributes = qs.values('attribute__id').annotate(max_id=Max('id'))
        qs = qs.filter(id__in=[x['max_id'] for x in last_attributes]).order_by('-created')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(UserLastDataListView, self).get_context_data()
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
        userdata = form.save()
        attribute, created = Attribute.objects.get_or_create(name=userdata.data_key)
        userdata.attribute = attribute
        return super(UserDataCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'El atributo: "%s" con valor "%s" del usuario: "%s" se ha creado.' % (
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
        messages.success(self.request, 'El atributo: "%s" con valor "%s" del usuario: "%s" se ha actualizado.' % (
            self.object.data_key, self.object.data_value, self.object.user
        ))
        return reverse_lazy('messenger_users:user_last_data_list', kwargs=dict(user_id=self.object.user_id))


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


class CreateAfinidataUser(PermissionRequiredMixin, TemplateView):
    permission_required = 'messenger_users.add_user'
    template_name = 'messenger_users/afinidata_user_form.html'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(CreateAfinidataUser, self).get_context_data()
        c['form'] = forms.AfinidataUserForm(self.request.POST or None)
        return c

    def post(self, request, *args, **kwargs):
        user_form = forms.AfinidataUserForm(self.request.POST)
        if user_form.is_valid():
            user_form.instance.last_channel_id = user_form.data['channel_id']
            user_form.instance.username = user_form.data['channel_id']
            user_form.instance.backup_key = user_form.data['channel_id']
            user = user_form.save()
            if user:
                messages.success(request, 'User with name: "%s" has been created.' % user)
                for data in user_form.data:
                    if data not in ['first_name', 'last_name', 'channel_id', 'bot_id', 'name', 'birthday',
                                    'csrfmiddlewaretoken']:
                        attribute, created = Attribute.objects.get_or_create(name=data)
                        user.userdata_set.create(data_key=data, data_value=user_form.data[data],
                                                 attribute_id=attribute.id)

                return redirect('messenger_users:want_add_child', user_id=user.pk)
            else:
                messages.error('An error ocurred and the user has not been created, try again.')
        else:
            messages.error(request, 'Check again the data for user.')

        return super(CreateAfinidataUser, self).get(request)


class WantAddChildView(PermissionRequiredMixin, TemplateView):
    permission_required = 'messenger_users.add_user'
    template_name = 'messenger_users/afinidata_want_add_child.html'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(WantAddChildView, self).get_context_data()
        c['ms_user'] = User.objects.get(id=self.kwargs['user_id'])
        return c


class AddChildView(PermissionRequiredMixin, CreateView):
    form_class = forms.AfinidataChildForm
    permission_required = 'instances.add_instance'
    template_name = 'messenger_users/add_child_form.html'

    def get_context_data(self, **kwargs):
        c = super(AddChildView, self).get_context_data()
        c['ms_user'] = User.objects.get(id=self.kwargs['user_id'])
        return c

    def form_valid(self, form):
        return super(AddChildView, self).form_valid(form)

    def get_success_url(self):
        user = User.objects.get(id=self.kwargs['user_id'])
        self.object.instanceassociationuser_set.create(user_id=user.pk)
        self.object.attributevalue_set.create(attribute=Attribute.objects.get(name='birthday'),
                                              value=parse(self.request.POST['birthday'], dayfirst=True))
        messages.success(self.request, 'The child with name "%s" has been created for user "%s".' % (
            self.object.name,
            user
        ))
        return reverse_lazy('messenger_users:want_add_child', kwargs=dict(user_id=user.pk))


class AddUserInitialData(PermissionRequiredMixin, TemplateView):
    template_name = 'messenger_users/userdata_form.html'
    permission_required = 'messenger_users.add_userdata'

    def get_context_data(self, **kwargs):
        c = super(AddUserInitialData, self).get_context_data()
        c['ms_user'] = User.objects.get(id=self.kwargs['user_id'])
        c['action'] = 'Add Initial'
        c['form'] = forms.InitialUserForm(self.request.POST or None)
        return c

    def post(self, request, **kwargs):
        user = User.objects.get(id=kwargs['user_id'])
        c = 0
        for data in request.POST:
            if data not in ['csrfmiddlewaretoken']:
                if request.POST[data]:
                    attribute, created = Attribute.objects.get_or_create(name=data)
                    user.userdata_set.create(data_key=data, data_value=request.POST[data],
                                             attribute_id=attribute.id)
                    c = c + 1
        messages.success(request, 'Added %s items in data for %s' % (c, user))
        return redirect('messenger_users:user', id=user.pk)
