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
        print(queryset.count())
        form = forms.SearchUserForm(self.request.GET or None)
        user = User.objects.all().last()
        if form.is_valid():
            if form.cleaned_data['id']:
                queryset = queryset.filter(id=form.cleaned_data['id'])
            if form.cleaned_data['bot']:
                queryset = queryset.filter(bot_id=form.cleaned_data['bot'].pk)
            if form.cleaned_data['name']:
                queryset = queryset.filter(first_name__contains=form.cleaned_data['name'])
            if form.cleaned_data['last_name']:
                queryset = queryset.filter(last_name__contains=form.cleaned_data['last_name'])
                print(queryset.count())
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


class UserCaptchaView(View):

    def get(self, request):

        try:
            username = request.GET['username']
            user = User.objects.get(username=username)
            api_key = request.GET['api_key']
        except Exception as e:
            return JsonResponse(dict(status='error', error='Invalid params.'))

        if api_key != os.getenv('CORE_QUEST_KEY'):
            return JsonResponse(dict(status='error', error='Invalid params.'))

        captcha = '00%sCHF' % user.id

        return JsonResponse(dict(
            set_attributes=dict(
                captcha=captcha,
                core_message='Captcha for user %s is %s' % (user.username, captcha)
            ),
            messages=[]
        ))


class VerifyUserCaptchaView(View):

    def get(self, request):

        try:
            user = User.objects.get(username=request.GET['username'])
            response = str(request.GET['response'])
            api_key = request.GET['api_key']
        except Exception as e:
            return JsonResponse(dict(status='error', error='Invalid params.'))

        if api_key != os.getenv('CORE_QUEST_KEY'):
            return JsonResponse(dict(status='error', error='Invalid params.'))

        captcha = '00%sCHF' % user.id

        if response == captcha:
            valid_captcha = True
            core_message = 'Captcha valid'
        else:
            valid_captcha = False
            core_message = 'Captcha invalid'

        return JsonResponse(dict(
            set_attributes=dict(
                valid_captcha=valid_captcha,
                core_message=core_message
            ),
            messages=[]
        ))


class DataView(View):

    def get(self, request):
        try:
            admin = request.GET['admin']
            password = request.GET['password']
            username = request.GET['username']
            user = User.objects.get(username=username)
        except Exception as e:
            return JsonResponse(dict(status='error', error='invalid params'))

        if admin != os.getenv('CORE_ADMIN_ADMIN') or password != os.getenv('CORE_ADMIN_PASSWORD'):
            return HttpResponse('Admin o contraseña incorrecta')

        dataset = user.userdata_set.all()

        text = 'Data for %s is: \n' % user.username

        for item in dataset:
            text = text + "%s: %s \n" % (item.data_key, item.data_value)
        return HttpResponse(text)


class DeleteByUsernameView(LoginRequiredMixin, View):
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        return render(request, 'messenger_users/username.html', {})

    def post(self, request):
        user = get_object_or_404(User, username=request.POST['username'])
        user.delete()
        return redirect('messenger_users:index')


@csrf_exempt
def set_attributes_for_user(request, id):

    if request.method == 'GET':
        return JsonResponse(dict(status='error', error='Invalid method.'))

    try:
        user = User.objects.get(id=id)
    except Exception as e:
        return JsonResponse(dict(status='error', error='invalid params.'))

    for data_key in request.POST:
        data_value = request.POST[data_key]
        new_data = UserData.objects.update_or_create(user=user, data_key=data_key, defaults=dict(
            data_value=data_value
        ))
        print(new_data)
    return JsonResponse(dict(hello='world'))


class SetRandomPostGroupForUser(View):

    def get(self, request, *args, **kwargs):

        data_key = 'AB_group'
        try:
            user = User.objects.get(id=kwargs['id'])
            group = user.userdata_set.get(data_key='months_group')
        except Exception as e:
            return JsonResponse(dict(status='error', error='Invalid params.'))

        try:
            posts_group = user.userdata_set.get(data_key=data_key)
            print(posts_group)
            return JsonResponse(dict(status='error', error='user has AB group'))
        except Exception as e:
            print(e)
            print('Pass here!')
            pass

        users = User.objects.filter(userdata__data_key='months_group', userdata__data_value=group)\
            .exclude(id=user.pk).order_by('-id')[:1]

        if users.count() == 0:
            print('not users in group')
            posts_group = user.userdata_set.update_or_create(data_key=data_key, defaults=dict(data_value='A'))[0]
            print(posts_group)

        else:
            print('has more users')
            print(users)
            last_user = users.first()
            last_user_group = UserData.objects.get(user=last_user, data_key=data_key)
            new_group = 'A'
            if last_user_group.data_value == 'A':
                new_group = 'B'
            elif last_user_group.data_value == 'B':
                new_group = 'C'
            print(new_group)
            posts_group = user.userdata_set.create(data_key=data_key, data_value=new_group)
            print(posts_group)

        return JsonResponse(dict(status='done',
                                 data=dict(data_key=data_key, data_value=posts_group.data_value, user_id=user.pk),
                                 set_attributes=dict(
                                    AB_group=posts_group.data_value
                                 ),
                                 messages=[]))


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


class GetIDByUsernameView(View):

    def get(self, request):
        try:
            api_key = request.GET['api_key']
            username = request.GET['username']
            user = User.objects.get(username=username)
            print(user)
            print(os.getenv('CORE_QUEST_KEY'))
        except Exception as e:
            print(str(e))
            return JsonResponse(dict(status='error', error="Invalid params."))


class AssignMonthsGroupView(View):

    def get(self, request, *args, **kwargs):
        try:
            months = int(request.GET['months'])
            user = User.objects.get(id=kwargs['id'])
        except Exception as e:
            return JsonResponse(dict(status='error', error='Invalid params'))

        groups_array = [
            {'min': 0, 'max': 2, 'group_name': '0-2'},
            {'min': 3, 'max': 5, 'group_name': '3-5'},
            {'min': 6, 'max': 8, 'group_name': '6-8'},
            {'min': 9, 'max': 11, 'group_name': '9-11'},
            {'min': 12, 'max': 14, 'group_name': '12-14'},
            {'min': 15, 'max': 17, 'group_name': '15-17'},
            {'min': 18, 'max': 20, 'group_name': '18-20'},
            {'min': 21, 'max': 23, 'group_name': '21-23'},
            {'min': 24, 'max': 26, 'group_name': '24-26'},
            {'min': 27, 'max': 29, 'group_name': '27-29'},
            {'min': 30, 'max': 32, 'group_name': '30-32'},
            {'min': 33, 'max': 35, 'group_name': '33-35'},
            {'min': 36, 'max': 38, 'group_name': '36-38'},
            {'min': 39, 'max': 41, 'group_name': '39-41'},
            {'min': 42, 'max': 44, 'group_name': '42-44'},
            {'min': 45, 'max': 47, 'group_name': '45-47'},
            {'min': 48, 'max': 50, 'group_name': '48-50'},
            {'min': 51, 'max': 53, 'group_name': '51-53'},
            {'min': 54, 'max': 56, 'group_name': '54-56'},
            {'min': 57, 'max': 59, 'group_name': '57-59'},
            {'min': 60, 'max': 62, 'group_name': '60-62'},
            {'min': 63, 'max': 65, 'group_name': '63-65'},
            {'min': 66, 'max': 68, 'group_name': '66-68'},
            {'min': 69, 'max': 71, 'group_name': '69-71'},
            {'min': 72, 'max': 74, 'group_name': '72-74'},
            {'min': 75, 'max': 77, 'group_name': '75-77'},
            {'min': 78, 'max': 80, 'group_name': '78-80'},
            {'min': 81, 'max': 83, 'group_name': '81-83'},
            {'min': 84, 'max': 2000, 'group_name': '>= 84'}
        ]

        if months > 0:
            item = [item for item in groups_array if item['min'] <= months <= item['max']][0]
        else:
            item = {'group_name': '<= 0'}

        print(item['group_name'])

        try:
            group = user.userdata_set.get(data_key='months_group')
            return JsonResponse(dict(
                set_attributes=dict(
                    months_group=group.data_value
                ),
                messages=[]
            ))
        except Exception as e:
            print(e)
            pass

        group = user.userdata_set.update_or_create(data_key='months_group',
                                                   defaults=dict(data_value=item['group_name']))[0]

        return JsonResponse(dict(
            set_attributes=dict(
                months_group=group.data_value
            ),
            messages=[]
        ))


class SetUserChannelID(View):

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['id'])
        try:
            channel_id = request.GET['channel_id']
        except Exception as e:
            return JsonResponse(dict(
                set_attributes=dict(
                    set_channel_id=False
                ),
                messages=[]
            ))
        user.channel_id = channel_id
        user.save()

        return JsonResponse(dict(
            set_attributes=dict(
                set_channel_id=True
            ),
            messages=[]
        ))
