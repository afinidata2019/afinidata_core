from messenger_users.models import User
from instances.models import Instance
from bots.models import Bot
from django import forms


class SearchUserForm(forms.Form):
    bot = forms.ModelChoiceField(queryset=Bot.objects.all(), required=False)
    id = forms.IntegerField(min_value=User.objects.all().first().pk, max_value=2000000,
                            required=False)
    name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)


class AfinidataUserForm(forms.ModelForm):
    bot_id = forms.ChoiceField(choices=((1, 'Afini Pilot'), (2, 'Afini AUE')))
    tipo_de_licencia = forms.CharField(max_length=50)
    user_type = forms.ChoiceField(choices=(('caregiver', 'caregiver'), ('professional', 'professional'),
                                           ('pregnant', 'pregnant'), ('influencer', 'influencer')))
    user_rol = forms.ChoiceField(choices=(('👩 soy su mamá/papá', '👩 soy su mamá/papá'),
                                          ('🏫trabajo con niños', '🏫trabajo con niños')))
    Pais = forms.CharField(max_length=20)
    childMonths = forms.IntegerField()
    user_reg = forms.ChoiceField(choices=(('registered', 'registered'), ('unregistered', 'unregistered')))
    Premium = forms.CharField(max_length=10)
    user_locale = forms.CharField(max_length=10)
    childtype = forms.ChoiceField(choices=(('onlychild', 'onlychild'), ('multichild', 'multichild')))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'channel_id')


class AfinidataChildForm(forms.ModelForm):
    birthday = forms.CharField(max_length=20)

    class Meta:
        model = Instance
        fields = ('name',)
