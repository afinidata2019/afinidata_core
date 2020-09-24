from groups.models import Group
from django import forms


class GroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())
