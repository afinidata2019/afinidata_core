from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from messenger_users.models import User, UserData
from attributes.models import Attribute
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from posts.models import Interaction
from articles.models import Interaction as ArticleInteraction
from django.contrib import messages
from messenger_users import forms
from dateutil.parser import parse
from user_sessions.models import Session, Field, Message, Reply, Interaction as SessionInteraction


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
        replies = SessionInteraction.objects.filter(user_id=self.object.pk, type='quick_reply').order_by('-id')
        for reply in replies:
            rep = dict()
            field = Field.objects.filter(id=reply.field_id).first()
            question_field = Field.objects.filter(session_id=field.session_id, position=field.position - 1).last()
            rep['question'] = Message.objects.filter(field_id=question_field.id).order_by('id').last().text
            rep['session'] = Session.objects.get(id=reply.session_id)
            answer = Reply.objects.filter(field_id=field.id, value=reply.value)
            if answer.exists():
                rep['answer'] = answer.first().label
                rep['attribute'] = answer.first().attribute
            else:
                rep['answer'] = reply.text or ''
                rep['attribute'] = Reply.objects.filter(field_id=field.id).first().attribute
            Attribute.objects.filter(name=rep['attribute']).first()
            rep['value'] = reply.value or 0
            rep['response'] = reply.created_at
            quick_replies.append(rep)
        c['quick_replies'] = quick_replies
        return c


class UserInteractionsView(PermissionRequiredMixin, DetailView):
    permission_required = 'messenger_users.view_user'
    model = User
    pk_url_kwarg = 'id'
    template_name = 'messenger_users/interactions_detail.html'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(UserInteractionsView, self).get_context_data()
        c['post_interactions'] = self.object.get_post_interactions()[:20]
        c['article_interactions'] = self.object.get_article_interactions()[:20]
        c['session_interactions'] = self.object.get_session_interactions()[:20]
        return c


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
        return user.get_session_interactions()


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
                        print(data, user_form.data[data])
                        user.userdata_set.create(data_key=data, data_value=user_form.data[data])

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
        form.instance.entity_id = 1
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
                    user.userdata_set.create(data_key=data, data_value=request.POST[data])
                    c = c + 1
        messages.success(request, 'Added %s items in data for %s' % (c, user))
        return redirect('messenger_users:user', id=user.pk)
