from django import forms
from user_sessions import models
from attributes.models import Attribute
from areas.models import Area
from programs.models import Program
from entities.models import Entity
from licences.models import License
import requests
import os


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
        response = requests.get(os.getenv("WEBHOOK_DOMAIN_URL") + '/api/0.1/bots/')
        if response.status_code == 200:
            self.fields['bot_id'].choices = [ (x['id'], x['name']) for x in response.json()['results']]

    # response = requests.get(os.getenv("WEBHOOK_DOMAIN_URL") + '/api/0.1/bots/')
    # if response.status_code == 200:
    #     for bot in response.json()['results']:
    #         bots_list.append((bot['id'], bot['name']))

    bot_id = forms.ChoiceField(choices=tuple(bots_list))
    session_type = forms.ChoiceField(choices=(('welcome', 'Welcome'), ('default', 'Default')))
