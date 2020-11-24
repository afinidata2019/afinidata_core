from messenger_users.models import User
from programs.models import Program
from bots.models import Bot
from django import forms
from groups import models


class ExchangeCodeForm(forms.Form):
    code = forms.ModelChoiceField(queryset=models.Code.objects.filter(available=True), to_field_name='code')
    messenger_user_id = forms.ModelChoiceField(User.objects.all())


class AddProgramForm(forms.Form):
    program = forms.ModelChoiceField(queryset=Program.objects.all())


class CreateGroup(forms.ModelForm):
    program = forms.ModelChoiceField(queryset=Program.objects.all())
    bot = forms.ModelChoiceField(queryset=Bot.objects.all())

    class Meta:
        model = models.Group
        fields = ('name', 'parent', 'country', 'region', 'license')
