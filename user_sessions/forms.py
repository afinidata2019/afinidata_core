from django import forms
from user_sessions import models
from attributes.models import Attribute
from areas.models import Area
from programs.models import Program
from entities.models import Entity
from licences.models import License
import requests
import os
import json


class SessionForm(forms.ModelForm):
    permission_required = 'user_sessions.add_session'
    areas = forms.ModelMultipleChoiceField(
        queryset=Area.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    programs = forms.ModelMultipleChoiceField(
        queryset=Program.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    entities = forms.ModelMultipleChoiceField(
        queryset=Entity.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    licences = forms.ModelMultipleChoiceField(
        queryset=License.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    class Meta:
        model = models.Session
        fields = ('name', 'min', 'max', 'session_type', 'areas', 'programs', 'entities', 'licences')


class UserInputForm(forms.ModelForm):
    validation = forms.ChoiceField(choices=(('', '---------'), ('phone', 'Phone'), ('email', 'Email'),
                                            ('date', 'Date'), ('number', 'Number')), required=False)
    attribute = forms.ModelChoiceField(queryset=Attribute.objects.all().order_by('name'))
    session = forms.ModelChoiceField(queryset=models.Session.objects.all().order_by('name'), required=False)

    class Meta:
        model = models.UserInput
        fields = ('text', 'validation', 'attribute', 'session', 'position')


class SetAttributeForm(forms.ModelForm):
    attribute = forms.ModelChoiceField(queryset=Attribute.objects.all().order_by('name'))

    class Meta:
        model = models.SetAttribute
        fields = ('attribute', 'value')


class ConditionForm(forms.ModelForm):
    attribute = forms.ModelChoiceField(queryset=Attribute.objects.all().order_by('name'))

    class Meta:
        model = models.Condition
        fields = ('attribute', 'condition', 'value')


class RedirectSessionForm(forms.ModelForm):
    session = forms.ModelChoiceField(queryset=models.Session.objects.all().order_by('name'))

    class Meta:
        model = models.RedirectSession
        fields = ('session', )


class ServiceSessionForm(forms.ModelForm):
    available_service = forms.ModelChoiceField(queryset=models.AvailableService.objects.all().order_by('name'))

    class Meta:
        model = models.Service
        fields = ('available_service', )


class IntentForm(forms.Form):
    OPTIONS = []
    service_response = requests.get(os.getenv('NLU_API') + '/intents/?options=True').json()
    if 'count' in service_response and service_response['count'] > 0:
        OPTIONS = [ (intent['id'], intent['name']) for intent in service_response['results'] ]
    
    intents = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OPTIONS)
    session =  forms.ModelChoiceField(widget = forms.HiddenInput(), queryset=models.Session.objects.all())


class InteractionForm(forms.ModelForm):
    session_name = forms.CharField()
    question = forms.CharField()
    attribute = forms.CharField()
    options = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(InteractionForm, self).__init__(*args, **kwargs)
        choices = []
        for rep in models.Reply.objects.exclude(attribute__isnull=True). \
                filter(field_id=self.instance.field_id).values('value', 'label', 'attribute').distinct():
            choices.append((rep['value'], rep['label']))
            self.fields['attribute'].initial = rep['attribute']
        self.fields['options'].choices = choices
        self.fields['session_name'].initial = models.Session.objects.get(id=self.instance.session_id).name
        self.fields['question'].initial = ''
        field = models.Field.objects.get(id=self.instance.field_id)
        question_field = models.Field.objects.filter(session_id=self.instance.session_id, position=field.position - 1)
        if question_field.exists():
            message = models.Message.objects.filter(field_id=question_field.last().id)
            if message.exists():
                self.fields['question'].initial = message.last().text
        self.fields['session_name'].widget.attrs['readonly'] = True
        self.fields['question'].widget.attrs['readonly'] = True
        self.fields['attribute'].widget.attrs['readonly'] = True
        self.fields['text'].widget.attrs['readonly'] = True
        self.fields['session_name'].label = 'Sesion'
        self.fields['question'].label = 'Pregunta'
        self.fields['attribute'].label = 'Atributo'
        self.fields['text'].label = 'Respuesta del usuario'
        self.fields['options'].label = 'Opciones válidas'

    class Meta:
        fields = ('session_name', 'question', 'attribute', 'text', 'options')
        model = models.Interaction


class BotSessionForm(forms.Form):
    bots_list = []

    def __init__(self, *args, **kwargs):
        super(BotSessionForm, self).__init__(*args, **kwargs)
        response = requests.get(os.getenv("WEBHOOK_API") + '/bots/')
        if response.status_code == 200:
            self.fields['bot_id'].choices = [(x['id'], x['name']) for x in response.json()['results']]

    bot_id = forms.ChoiceField(choices=tuple(bots_list))
    session_type = forms.ChoiceField(choices=(('welcome', 'Welcome'), ('default', 'Default')))


class SubscribeSequenceSessionForm(forms.ModelForm):
    sequences_list = []

    def __init__(self, *args, **kwargs):
        super(SubscribeSequenceSessionForm, self).__init__(*args, **kwargs)
        response = requests.get(os.getenv("HOTTRIGGERS_API") + '/sequences/?has_triggers=True')
        if response.status_code == 200:
            self.fields['sequence_id'].choices = [(x['id'], x['name']) for x in response.json()['results']]

    sequence_id = forms.ChoiceField(choices=tuple(sequences_list))

    class Meta:
        model = models.AssignSequence
        fields = ('sequence_id', 'start_position')


class UnsubscribeSequenceSessionForm(forms.ModelForm):
    sequences_list = []

    def __init__(self, *args, **kwargs):
        super(UnsubscribeSequenceSessionForm, self).__init__(*args, **kwargs)
        response = requests.get(os.getenv("HOTTRIGGERS_API") + '/sequences/')
        if response.status_code == 200:
            self.fields['sequence_id'].choices = [(x['id'], x['name']) for x in response.json()['results']]

    sequence_id = forms.ChoiceField(choices=tuple(sequences_list))

    class Meta:
        model = models.UnsubscribeSequence
        fields = ('sequence_id', )


class ReplyCreateForm(forms.ModelForm):
    attribute = forms.ModelChoiceField(queryset=Attribute.objects.all().order_by('name'), required=False)
    
    class Meta:
        model = models.Reply
        fields = ('label', 'attribute', 'value', 'redirect_block', 'session', 'position')

