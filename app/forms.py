from instances.models import Instance
from entities.models import Entity
from areas.models import Area
from app.models import User
from django import forms


class LoginForm(forms.Form):
    identifier = forms.ModelChoiceField(queryset=User.objects.all(), to_field_name='identifier')
    password = forms.CharField(max_length=50)


class GetInstancesForm(forms.Form):
    entity = forms.ModelChoiceField(queryset=Entity.objects.all())


class GetActivitiesForm(forms.Form):
    instance = forms.ModelChoiceField(queryset=Instance.objects.all())
    area = forms.ModelChoiceField(queryset=Area.objects.all())
