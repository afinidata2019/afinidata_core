from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, RedirectView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from user_sessions import models, forms
from attributes.models import Attribute
from entities.models import Entity
from instances.models import AttributeValue
from messenger_users.models import UserData
from areas.models import Area
from topics.models import Topic
from programs.models import Program


class SessionListView(PermissionRequiredMixin, ListView):
    permission_required = 'user_sessions.view_session'
    model = models.Session
    context_object_name = 'sessions'
    paginate_by = 15

    def get_queryset(self):
        try:
            params = dict()
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
        c['types_list'] = models.SessionType.objects.all().order_by('name')
        c['topics_list'] = Topic.objects.all().order_by('name')
        c['areas_list'] = Area.objects.all().order_by('name')
        c['programs'] = ''
        c['types'] = ''
        c['topics'] = ''
        c['areas'] = ''
        params = dict()
        if self.request.GET.get('name'):
            params['name__icontains'] = self.request.GET['name']
            c['name'] = self.request.GET['name']
        if self.request.GET.get('min_range'):
            params['min'] = self.request.GET['min_range']
            c['min_range'] = self.request.GET['min_range']
        if self.request.GET.get('max_range'):
            params['max'] = self.request.GET['max_range']
            c['max_range'] = self.request.GET['max_range']
        if self.request.GET.get('programs'):
            params['programs'] = self.request.GET['programs']
            c['programs'] = int(self.request.GET['programs'])
        if self.request.GET.get('types'):
            params['session_type'] = self.request.GET['types']
            c['types'] = int(self.request.GET['types'])
        if self.request.GET.get('topics'):
            params['areas__topic'] = self.request.GET['topics']
            c['topics'] = int(self.request.GET['topics'])
        if self.request.GET.get('areas'):
            params['areas'] = self.request.GET['areas']
            c['areas'] = int(self.request.GET['areas'])
        sessions = sessions.filter(**params)
        for session in c['sessions']:
            session.type = session.session_type.name
            session.topics = ', '.join(set([area.topic.name for area in session.areas.all() if area.topic]))
            session.areas_list = ', '.join([area.name for area in session.areas.all()])
            session.programs_list = ', '.join([program.name.replace('Afini ', '') for program in session.programs.all()])
        c['total'] = sessions.count()
        return c


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


class SessionUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_session'
    model = models.Session
    pk_url_kwarg = 'session_id'
    form_class = forms.SessionForm

    def get_context_data(self, **kwargs):
        c = super(SessionUpdateView, self).get_context_data()
        c['action'] = 'Edit'
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
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
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
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
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
    fields = ('label', 'attribute', 'value', 'redirect_block')

    def get_context_data(self, **kwargs):
        c = super(ReplyCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        form.instance.session_id = self.kwargs['session_id']
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
    fields = ('label', 'attribute', 'value', 'redirect_block')
    pk_url_kwarg = 'reply_id'

    def get_context_data(self, **kwargs):
        c = super(ReplyEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
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
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
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


class RedirectSessionCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_redirectsession'
    model = models.RedirectSession
    fields = ('session', )

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
    fields = ('session',)
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
