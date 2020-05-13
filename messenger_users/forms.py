from messenger_users.models import User
from bots.models import Bot
from django import forms


class SearchUserForm(forms.Form):
    bot = forms.ModelChoiceField(queryset=Bot.objects.all(), required=False)
    id = forms.IntegerField(min_value=User.objects.all().first().pk, max_value=2000000,
                            required=False)
    name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
