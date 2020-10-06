from django import forms
from user_sessions import models
from attributes.models import Attribute
from areas.models import Area
from programs.models import Program
from entities.models import Entity
from licences.models import License


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
                                            ('date', 'Date')), required=False)
    attribute = forms.ModelChoiceField(queryset=Attribute.objects.all().order_by('name'))
    session = forms.ModelChoiceField(queryset=models.Session.objects.filter(session_type=9), required=False)

    class Meta:
        model = models.UserInput
        fields = ('text', 'validation', 'attribute', 'session')
