from messenger_users.models import User
from programs.models import Program
from django import forms
from groups import models


class ExchangeCodeForm(forms.Form):
    code = forms.ModelChoiceField(queryset=models.Code.objects.filter(available=True), to_field_name='code')
    messenger_user_id = forms.ModelChoiceField(User.objects.all())


class AddProgramForm(forms.Form):
    program = forms.ModelChoiceField(queryset=Program.objects.all())
