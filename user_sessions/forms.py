from django import forms
from user_sessions import models
from attributes.models import Attribute


class UserInputForm(forms.ModelForm):
    validation = forms.ChoiceField(choices=(('', '---------'), ('phone', 'Phone'), ('email', 'Email'),
                                            ('date', 'Date')), required=False)
    attribute = forms.ModelChoiceField(queryset=Attribute.objects.all().order_by('name'))
    session = forms.ModelChoiceField(queryset=models.Session.objects.filter(session_type=9), required=False)

    class Meta:
        model = models.UserInput
        fields = ('text', 'validation', 'attribute', 'session')
