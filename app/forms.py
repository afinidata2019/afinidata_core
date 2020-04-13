from app.models import User
from django import forms


class LoginForm(forms.Form):
    identifier = forms.ModelChoiceField(queryset=User.objects.all(), to_field_name='identifier')
    password = forms.CharField(max_length=50)
