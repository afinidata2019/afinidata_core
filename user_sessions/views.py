import os
import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, RedirectView, View
from rest_framework.response import Response
from rest_framework.views import APIView
from user_sessions import models, forms
from attributes.models import Attribute
from entities.models import Entity
from instances.models import AttributeValue
from messenger_users.models import UserData
from areas.models import Area
from topics.models import Topic
from programs.models import Program
from user_sessions.serializers import FieldSerializer



class SessionListView(PermissionRequiredMixin, ListView):
    permission_required = 'user_sessions.view_session'
    model = models.Session
    context_object_name = 'sessions'
    paginate_by = 15

    def get_queryset(self):
        try:
            params = dict()
            if self.request.GET.get('session_id'):
                params['id'] = self.request.GET['session_id']
            if self.request.GET.get('name'):
                params['name__icontains'] = self.request.GET['name']
            if self.request.GET.get('min_range'):
                params['min'] = self.request.GET['min_range']
            if self.request.GET.get('max_range'):
                params['max'] = self.request.GET['max_range']
            if self.request.GET.get('programs'):
                params['programs'] = self.request.GET['programs']
            if self.request.GET.get('types'):
                params['session_type'] = self.request.GET['types']
            if self.request.GET.get('topics'):
                params['areas__topic'] = self.request.GET['topics']
            if self.request.GET.get('areas'):
                params['areas'] = self.request.GET['areas']
            if self.request.GET.get('services'):
                urls = models.Service.objects.filter(available_service_id=self.request.GET['services'])
                params['id__in'] = [service.field.session.id for service in urls]
            if self.request.GET.get('set_attributes'):
                set_attributes = models.SetAttribute.objects.filter(attribute_id=self.request.GET['set_attributes'])
                params['id__in'] = [set_attribute.field.session.id for set_attribute in set_attributes]
            if self.request.GET.get('bots'):
                params['id__in'] = [x.session_id for x in models.BotSessions.objects.filter(bot_id=self.request.GET['bots'])]
            if self.request.GET.get('subscribe_sequence'):
                params['id__in'] = [x.session_id for x in models.AssignSequence.objects.filter(sequence_id=self.request.GET['subscribe_sequence'])]
            if self.request.GET.get('unsubscribe_sequence'):
                params['id__in'] = [x.session_id for x in models.UnsubscribeSequence.objects.filter(sequence_id=self.request.GET['unsubscribe_sequence'])]
            return models.Session.objects.filter(**params)
        except:
            return models.Session.objects.all()

    def get_context_data(self, **kwargs):
        c = super(SessionListView, self).get_context_data()
        get_copy = self.request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        c['get_params'] = parameters
        sessions = models.Session.objects.all().order_by('-session_type', 'name')
        c['programs_list'] = Program.objects.all().order_by('name')
        bots_list = []
        response = requests.get(os.getenv("WEBHOOK_DOMAIN_URL") + '/api/0.1/bots/')
        if response.status_code == 200:
            bots_list = [dict(id=x['id'], name=x['name']) for x in response.json()['results']]
        c['bots_list'] = bots_list
        sequence_list = []
        response = requests.get(os.getenv("HOTTRIGGERS_DOMAIN_URL") + '/api/0.1/sequences/')
        if response.status_code == 200:
            sequence_list = [dict(id=x['id'], name=x['name']) for x in response.json()['results']]
        c['sequence_list'] = sequence_list
        c['types_list'] = models.SessionType.objects.all().order_by('name')
        c['topics_list'] = Topic.objects.all().order_by('name')
        c['areas_list'] = Area.objects.all().order_by('name')
        c['services_list'] = [dict(id=x.id, name=x.name) for x in models.AvailableService.objects.all()]
        c['set_attributes_list'] = Attribute.objects.\
            filter(id__in=[x['attribute_id'] for x in models.SetAttribute.objects.values('attribute_id').distinct()])

        c['programs'] = ''
        c['bots'] = ''
        c['subscribe_sequence'] = ''
        c['unsubscribe_sequence'] = ''
        c['types'] = ''
        c['topics'] = ''
        c['areas'] = ''
        c['services'] = ''
        c['set_attributes'] = ''
        params = dict()
        if self.request.GET.get('name'):
            params['name__icontains'] = self.request.GET['name']
            c['name'] = self.request.GET['name']
        if self.request.GET.get('session_id'):
            params['id'] = self.request.GET['session_id']
            c['session_id'] = self.request.GET['session_id']
        if self.request.GET.get('min_range'):
            params['min'] = self.request.GET['min_range']
            c['min_range'] = self.request.GET['min_range']
        if self.request.GET.get('max_range'):
            params['max'] = self.request.GET['max_range']
            c['max_range'] = self.request.GET['max_range']
        if self.request.GET.get('programs'):
            params['programs'] = self.request.GET['programs']
            c['programs'] = int(self.request.GET['programs'])
        if self.request.GET.get('bots'):
            params['id__in'] = [x.session_id for x in models.BotSessions.objects.filter(bot_id=self.request.GET['bots'])]
            c['bots'] = int(self.request.GET['bots'])
        if self.request.GET.get('subscribe_sequence'):
            params['id__in'] = [x.session_id for x in models.AssignSequence.objects.filter(sequence_id=self.request.GET['subscribe_sequence'])]
            c['subscribe_sequence'] = int(self.request.GET['subscribe_sequence'])
        if self.request.GET.get('unsubscribe_sequence'):
            params['id__in'] = [x.session_id for x in models.UnsubscribeSequence.objects.filter(sequence_id=self.request.GET['unsubscribe_sequence'])]
            c['unsubscribe_sequence'] = int(self.request.GET['unsubscribe_sequence'])
        if self.request.GET.get('types'):
            params['session_type'] = self.request.GET['types']
            c['types'] = int(self.request.GET['types'])
        if self.request.GET.get('topics'):
            params['areas__topic'] = self.request.GET['topics']
            c['topics'] = int(self.request.GET['topics'])
        if self.request.GET.get('areas'):
            params['areas'] = self.request.GET['areas']
            c['areas'] = int(self.request.GET['areas'])
        if self.request.GET.get('services'):
            urls = models.Service.objects.filter(available_service_id=self.request.GET['services'])
            params['id__in'] = [service.field.session.id for service in urls]
            c['services'] = self.request.GET['services']
        if self.request.GET.get('set_attributes'):
            set_attributes = models.SetAttribute.objects.filter(attribute_id=self.request.GET['set_attributes'])
            params['id__in'] = [set_attribute.field.session.id for set_attribute in set_attributes]
            c['set_attributes'] = int(self.request.GET['set_attributes'])
        sessions = sessions.filter(**params)
        for session in c['sessions']:
            session.type = session.session_type.name
            session.topics = ', '.join(set([area.topic.name for area in session.areas.all() if area.topic]))
            session.areas_list = ', '.join([area.name for area in session.areas.all()])
            session.programs_list = ', '.join([program.name.replace('Afini ', '') for program in session.programs.all()])
        c['total'] = sessions.count()
        return c


class TestSessionView(PermissionRequiredMixin, ListView):
    model = models.Session
    permission_required = 'user_sessions.view_session'
    login_url = reverse_lazy('pages:login')
    permission_denied_message = 'Unauthorized'
    template_name = 'user_sessions/test_sessions.html'


class ReplyCorrectionListView(PermissionRequiredMixin, ListView):
    permission_required = 'user_sessions.view_session'
    model = models.Interaction
    paginate_by = 30
    template_name = 'user_sessions/reply_correction_list.html'

    def get_queryset(self):
        qs = super(ReplyCorrectionListView, self).get_queryset().filter(type='quick_reply').\
            exclude(text__isnull=True).filter(value__isnull=True).order_by('-id')
        for interaction in qs:
            interaction.attribute = ''
            interaction.question = ''
            reply = models.Reply.objects.filter(field_id=interaction.field_id)
            if reply.exists():
                interaction.attribute = reply.last().attribute
            field = models.Field.objects.get(id=interaction.field_id)
            question_field = models.Field.objects.filter(session_id=interaction.session_id, position=field.position-1)
            if question_field.exists():
                message = models.Message.objects.filter(field_id=question_field.last().id)
                if message.exists():
                    interaction.question = message.last().text
        return qs


class ReplyCorrectionView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.view_session'
    login_url = reverse_lazy('pages:login')
    model = models.Interaction
    pk_url_kwarg = 'interaction_id'
    form_class = forms.InteractionForm
    template_name = 'user_sessions/reply_correction.html'

    def get_success_url(self):
        messages.success(self.request, 'El atributo fue actualizado.')
        return reverse_lazy('sessions:nlu_correction_list')

    def get_context_data(self, **kwargs):
        c = super(ReplyCorrectionView, self).get_context_data()
        reply = models.Reply.objects.filter(field_id=self.object.field_id)
        if reply.exists():
            c['replies'] = models.Reply.objects.exclude(attribute__isnull=True).\
                filter(attribute=reply.last().attribute).values('value', 'label').distinct()
        else:
            c['replies'] = []
        c['action'] = 'Editar'
        return c

    def form_valid(self, form):
        self.object.value = form.cleaned_data.get('options')
        self.object.save()
        user_attributes = [x.id for x in Entity.objects.get(id=4).attributes.all()] \
                              + [x.id for x in Entity.objects.get(id=5).attributes.all()]# caregiver or professional
        instance_attributes = [x.id for x in Entity.objects.get(id=1).attributes.all()] \
                              + [x.id for x in Entity.objects.get(id=2).attributes.all()]  # child or pregnant
        attribute = Attribute.objects.filter(name=form.cleaned_data.get('attribute'))
        if attribute.exists():
            if attribute.filter(id__in=user_attributes).exists():
                UserData.objects.create(user_id=self.object.user_id,
                                        attribute_id=attribute.last().id,
                                        data_key=attribute.last().name,
                                        data_value=self.object.value)
            if attribute.filter(id__in=instance_attributes).exists():
                AttributeValue.objects.create(instance_id=self.object.instance_id,
                                              attribute_id=attribute.last().id,
                                              value=self.object.value)
        return super(ReplyCorrectionView, self).form_valid(form)


class SessionDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'user_sessions.view_session'
    model = models.Session
    pk_url_kwarg = 'session_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(SessionDetailView, self).get_context_data()
        c['fields'] = self.object.field_set.order_by('position')
        is_condition = False
        for field in c['fields']:
            if is_condition:
                field.padding = 1
            else:
                field.padding = 0
            is_condition = (field.field_type == 'condition')
        c['last_field'] = c['fields'].last()
        c['type'] = self.object.session_type.name
        c['topics'] = ', '.join(set([area.topic.name for area in self.object.areas.all() if area.topic]))
        c['areas_list'] = ', '.join([area.name for area in self.object.areas.all()])
        c['programs_list'] = ', '.join([program.name.replace('Afini ', '') for program in self.object.programs.all()])
        c['entities_list'] = ', '.join([entity.name for entity in self.object.entities.all()])
        c['licences_list'] = ', '.join([user_license.name for user_license in self.object.licences.all()])
        inbounds = []
        inbounds = inbounds + [user_input.field.session.id for user_input
                               in models.UserInput.objects.filter(session_id=self.object.id)
                               if user_input.field]
        inbounds = inbounds + [reply.field.session.id for reply
                               in models.Reply.objects.filter(session_id=self.object.id)
                               if reply.field]
        inbounds = inbounds + [redirect.field.session.id for redirect
                               in models.RedirectSession.objects.filter(session_id=self.object.id)
                               if redirect.field]
        if models.Session.objects.filter(id__in=inbounds).exists():
            c['inbounds'] = models.Session.objects.filter(id__in=inbounds)
        outbounds = []
        outbounds = outbounds + [user_input.session.id for user_input
                                 in models.UserInput.objects.filter(field__in=self.object.field_set.all())
                                 if user_input.session]
        outbounds = outbounds + [reply.session.id for reply
                                 in models.Reply.objects.filter(field__in=self.object.field_set.all())
                                 if reply.session]
        outbounds = outbounds + [redirect.session.id for redirect
                                 in models.RedirectSession.objects.filter(field__in=self.object.field_set.all())
                                 if redirect.session]
        if models.Session.objects.filter(id__in=outbounds).exists():
            c['outbounds'] = models.Session.objects.filter(id__in=outbounds)
        if models.BotSessions.objects.filter(session_id=self.object.pk).exists():
            c['bot_sessions'] = models.BotSessions.objects.filter(session_id=self.object.pk)
        return c


class SessionCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_session'
    form_class = forms.SessionForm
    template_name = 'user_sessions/session_form.html'

    def get_context_data(self, **kwargs):
        c = super(SessionCreateView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has created." % self.object.pk)
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.object.pk))


@csrf_exempt
def set_intents(request):
    session = get_object_or_404(models.Session, id=request.POST.get('session'))
    intents = models.Intent.objects.all().filter(session__id=session.id)
    intents.delete()

    for intent_id in request.POST.getlist('intents'):
        intent = models.Intent.objects.create(session=session, intent_id=intent_id)

    return redirect('/sessions/{0}/edit'.format(session.pk))


class SessionUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_session'
    model = models.Session
    pk_url_kwarg = 'session_id'
    form_class = forms.SessionForm

    def get_context_data(self, **kwargs):
        c = super(SessionUpdateView, self).get_context_data()
        c['action'] = 'Edit'

        session = get_object_or_404(models.Session, id=self.kwargs['session_id'])
        intents = list(models.Intent.objects.values_list('intent_id', flat=True).filter(session__id=self.kwargs['session_id']))
        fintent = forms.IntentForm(initial={'session': session, 'intents': intents})
        c['intents'] = fintent

        return c

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has updated." % self.object.pk)
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.object.pk))


class SessionDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_session'
    model = models.Session
    pk_url_kwarg = 'session_id'

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has deleted." % self.object.pk)
        return reverse_lazy('sessions:session_list')


class FieldCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_field'
    model = models.Field
    fields = ('field_type', )

    def get_context_data(self, **kwargs):
        c = super(FieldCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        return c

    def form_valid(self, form):
        session = models.Session.objects.get(id=self.kwargs['session_id'])
        form.instance.session_id = self.kwargs['session_id']
        form.instance.position = session.field_set.count()
        return super(FieldCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Field added to session.')
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class FieldDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.add_field'
    model = models.Field
    pk_url_kwarg = 'field_id'

    def get_success_url(self):
        fields = self.object.session.field_set.filter(position__gt=self.object.position)
        for field in fields:
            field.position = field.position - 1
            field.save()
        messages.success(self.request, "Field has been deleted.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class FieldUpView(PermissionRequiredMixin, RedirectView):
    permission_required = 'user_sessions.change_field'
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        field = models.Field.objects.get(id=self.kwargs['field_id'])
        top_field = field.session.field_set.get(position=(field.position - 1))
        field.position = field.position - 1
        top_field.position = top_field.position + 1
        field.save()
        top_field.save()
        messages.success(self.request, "Changed position for fields.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class FieldDownView(PermissionRequiredMixin, RedirectView):
    permission_required = 'user_sessions.change_field'
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        field = models.Field.objects.get(id=self.kwargs['field_id'])
        bottom_field = field.session.field_set.get(position=(field.position + 1))
        field.position = field.position + 1
        bottom_field.position = bottom_field.position - 1
        field.save()
        bottom_field.save()
        messages.success(self.request, "Changed position for fields.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class MessageCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_message'
    model = models.Message
    fields = ('text', )

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(MessageCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        c = super(MessageCreateView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        if c['field'].field_type == 'one_time_notification':
            c['field_maxlength'] = 65
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, "Message added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class MessageEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_message'
    model = models.Message
    fields = ('text', )
    pk_url_kwarg = 'message_id'

    def get_context_data(self, **kwargs):
        c = super(MessageEditView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        if c['field'].field_type == 'one_time_notification':
            c['field_maxlength'] = 65
        c['action'] = 'Update'
        return c

    def get_success_url(self):
        messages.success(self.request, "Message changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class MessageDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_message'
    model = models.Message
    pk_url_kwarg = 'message_id'

    def get_success_url(self):
        messages.success(self.request, "Message deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class UserInputCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_userinput'
    form_class = forms.UserInputForm
    template_name = 'user_sessions/userinput_form.html'

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(UserInputCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        c = super(UserInputCreateView, self).get_context_data()
        c['parent_session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, "UserInput added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class UserInputEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_userinput'
    model = models.UserInput
    pk_url_kwarg = 'userinput_id'
    form_class = forms.UserInputForm

    def get_context_data(self, **kwargs):
        c = super(UserInputEditView, self).get_context_data()
        c['parent_session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        c['action'] = 'Update'
        return c

    def get_success_url(self):
        messages.success(self.request, "UserInput changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class UserInputDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_userinput'
    model = models.UserInput
    pk_url_kwarg = 'userinput_id'

    def get_success_url(self):
        messages.success(self.request, "UserInput deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ReplyCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_reply'
    model = models.Reply
    fields = ('label', 'attribute', 'value', 'redirect_block', 'session', 'position')

    def get_context_data(self, **kwargs):
        c = super(ReplyCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['parent_session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(ReplyCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Reply added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ButtonCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_button'
    model = models.Button
    fields = ('button_type', 'title', 'url', 'block_names')

    def get_context_data(self, **kwargs):
        c = super(ButtonCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        form.instance.session_id = self.kwargs['session_id']
        return super(ButtonCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Button added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ReplyEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_reply'
    model = models.Reply
    fields = ('label', 'attribute', 'value', 'redirect_block', 'session', 'position')
    pk_url_kwarg = 'reply_id'

    def get_context_data(self, **kwargs):
        c = super(ReplyEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['parent_session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Reply changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ButtonEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_button'
    model = models.Button
    fields = ('button_type', 'title', 'url', 'block_names')
    pk_url_kwarg = 'button_id'

    def get_context_data(self, **kwargs):
        c = super(ButtonEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Button changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ReplyDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_reply'
    model = models.Reply
    pk_url_kwarg = 'reply_id'

    def get_context_data(self, **kwargs):
        c = super(ReplyDeleteView, self).get_context_data()
        c['parent_session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Reply deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ButtonDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_button'
    model = models.Button
    pk_url_kwarg = 'button_id'

    def get_context_data(self, **kwargs):
        c = super(ButtonDeleteView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Button deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class SetAttributeCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_setattribute'
    model = models.SetAttribute
    form_class = forms.SetAttributeForm

    def get_context_data(self, **kwargs):
        c = super(SetAttributeCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        form.instance.session_id = self.kwargs['session_id']
        return super(SetAttributeCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "SetAttribute added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class SetAttributeEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_setattribute'
    model = models.SetAttribute
    pk_url_kwarg = 'setattribute_id'
    form_class = forms.SetAttributeForm

    def get_context_data(self, **kwargs):
        c = super(SetAttributeEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "SetAttribute changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class SetAttributeDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_setattribute'
    model = models.SetAttribute
    pk_url_kwarg = 'setattribute_id'

    def get_context_data(self, **kwargs):
        c = super(SetAttributeDeleteView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "SetAttribute deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ConditionCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_condition'
    model = models.Condition
    fields = ('attribute', 'condition', 'value')

    def get_context_data(self, **kwargs):
        c = super(ConditionCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        form.instance.session_id = self.kwargs['session_id']
        return super(ConditionCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Condition added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ConditionEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_condition'
    pk_url_kwarg = 'condition_id'
    model = models.Condition
    fields = ('attribute', 'condition', 'value')

    def get_context_data(self, **kwargs):
        c = super(ConditionEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Condition changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ConditionDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_condition'
    model = models.Condition
    pk_url_kwarg = 'condition_id'

    def get_context_data(self, **kwargs):
        c = super(ConditionDeleteView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Condition deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectBlockCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_redirectblock'
    model = models.RedirectBlock
    fields = ('block', )

    def get_context_data(self, **kwargs):
        c = super(RedirectBlockCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(RedirectBlockCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Redirect Block added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectBlockEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_redirectblock'
    model = models.RedirectBlock
    fields = ('block', )
    pk_url_kwarg = 'block_id'

    def get_context_data(self, **kwargs):
        c = super(RedirectBlockEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Redirect Block changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectBlockDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_redirectblock'
    model = models.RedirectBlock
    pk_url_kwarg = 'block_id'

    def get_success_url(self):
        messages.success(self.request, "Redirect Block has deleted.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ServiceCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_service'
    form_class = forms.ServiceSessionForm
    template_name = 'user_sessions/serviceparam_form.html'

    def get_context_data(self, **kwargs):
        c = super(ServiceCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        form.instance.save()
        for param in form.instance.available_service.suggested_params.split(','):
            print(param)
            p = models.ServiceParam(service=form.instance, parameter=param, value='')
            p.save()
            form.instance.serviceparam_set.add(p)
        return super(ServiceCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Service added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ServiceEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_service'
    form_class = forms.ServiceSessionForm
    model = models.Service
    pk_url_kwarg = 'service_id'

    def get_context_data(self, **kwargs):
        c = super(ServiceEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Service changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ServiceDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_service'
    model = models.Service
    pk_url_kwarg = 'service_id'

    def get_success_url(self):
        messages.success(self.request, "Service has deleted.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ServiceParamCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_serviceparam'
    model = models.ServiceParam
    fields = ('parameter', 'value')

    def form_valid(self, form):
        form.instance.service_id = models.Service.objects.get(field__id=self.kwargs['field_id']).id
        return super(ServiceParamCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        c = super(ServiceParamCreateView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        c['service'] = models.Service.objects.get(field__id=self.kwargs['field_id'])
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, "Service parameter added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ServiceParamEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_serviceparam'
    model = models.ServiceParam
    fields = ('parameter', 'value')
    pk_url_kwarg = 'serviceparam_id'

    def get_context_data(self, **kwargs):
        c = super(ServiceParamEditView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        c['service'] = models.Service.objects.get(field__id=self.kwargs['field_id'])
        c['action'] = 'Update'
        return c

    def get_success_url(self):
        messages.success(self.request, "Service parameter changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ServiceParamDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_serviceparam'
    model = models.ServiceParam
    pk_url_kwarg = 'serviceparam_id'

    def get_success_url(self):
        messages.success(self.request, "Service parameter deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectSessionCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_redirectsession'
    model = models.RedirectSession
    fields = ('session', 'position')

    def get_context_data(self, **kwargs):
        c = super(RedirectSessionCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(RedirectSessionCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Redirect Session added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectSessionEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_redirectsession'
    model = models.RedirectSession
    fields = ('session', 'position')
    pk_url_kwarg = 'redirectsession_id'

    def get_context_data(self, **kwargs):
        c = super(RedirectSessionEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Redirect Session changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectSessionDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_redirectsession'
    model = models.RedirectSession
    pk_url_kwarg = 'redirectsession_id'

    def get_success_url(self):
        messages.success(self.request, "Redirect Session has deleted.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class AssignSequenceCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_assignsequence'
    template_name = 'user_sessions/assignsequence_form.html'
    form_class = forms.SubscribeSequenceSessionForm

    def get_context_data(self, **kwargs):
        c = super(AssignSequenceCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(AssignSequenceCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Assign to Sequence added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class AssignSequenceEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_assignsequence'
    template_name = 'user_sessions/assignsequence_form.html'
    form_class = forms.SubscribeSequenceSessionForm
    model = models.AssignSequence
    pk_url_kwarg = 'assignsequence_id'

    def get_context_data(self, **kwargs):
        c = super(AssignSequenceEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Assign to Sequence changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class AssignSequenceDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_assignsequence'
    model = models.AssignSequence
    pk_url_kwarg = 'assignsequence_id'

    def get_success_url(self):
        messages.success(self.request, "Assign to Sequence has deleted.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class UnsubscribeSequenceCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_unsubscribesequence'
    template_name = 'user_sessions/unsubscribesequence_form.html'
    form_class = forms.UnsubscribeSequenceSessionForm

    def get_context_data(self, **kwargs):
        c = super(UnsubscribeSequenceCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(UnsubscribeSequenceCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Unsubscribe to Sequence added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class UnsubscribeSequenceEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_unsubscribesequence'
    template_name = 'user_sessions/unsubscribesequence_form.html'
    form_class = forms.UnsubscribeSequenceSessionForm
    model = models.UnsubscribeSequence
    pk_url_kwarg = 'unsubscribesequence_id'

    def get_context_data(self, **kwargs):
        c = super(UnsubscribeSequenceEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Unsubscribe to Sequence changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class UnsubscribeSequenceDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_unsubscribesequence'
    model = models.UnsubscribeSequence
    pk_url_kwarg = 'unsubscribesequence_id'

    def get_success_url(self):
        messages.success(self.request, "Unsubscribe to Sequence has deleted.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class AddBotSessionView(LoginRequiredMixin, View):
    login_url = reverse_lazy('pages:login')

    def get(self, request, *args, **kwargs):
        form = forms.BotSessionForm()

        return render(request, 'user_sessions/session_form.html', dict(
            form=form,
            action='Set Bot to',
            #api_endpoint=os.getenv("WEBHOOK_DOMAIN_URL") + '/api/0.1/bots/'
        ))

    def post(self, request, *args, **kwargs):
        session = get_object_or_404(models.Session, id=kwargs['session_id'])
        form = forms.BotSessionForm(request.POST)

        if form.is_valid():
            messages.success(request, 'Session has been added to bot')
            bot_session = models.BotSessions.objects.\
                filter(bot_id=request.POST['bot_id'],
                       session_type=request.POST['session_type'])
            if bot_session.exists():
                bot_session = bot_session.last()
                bot_session.session = session
                bot_session.save()
            else:
                models.BotSessions.objects.create(bot_id=request.POST['bot_id'],
                                                  session_type=request.POST['session_type'],
                                                  session=session)
            return redirect('sessions:session_detail', session_id=session.pk)
        else:
            messages.success(request, 'Invalid params.')
            return redirect('sessions:session_detail', session_id=session.pk)


""""
    Api view para data detail session
    @author: jose quintero
"""
class FieldsData(APIView):

    def get_object(self, pk):
        try:
            return models.Field.objects.filter(session_id=pk).order_by('position')
        except models.Field.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        fields = self.get_object(pk)
        serializer = FieldSerializer(fields, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        try:
            data = request.data

            for val in data['fields']:
                f = models.Field.objects.get(pk=val['id'])
                f.position = val['position']
                f.save()

            return JsonResponse({ 'ok': True, 'message': "success" })

        except DoesNotExist:
            raise Http404
        except Exception as err:
            return JsonResponse({ 'ok': False, 'message': str(err) })
