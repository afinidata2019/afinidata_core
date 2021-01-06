from messenger_users.models import User
from instances.models import Instance
from bots.models import Bot
from entities.models import Entity
from django import forms


class SearchUserForm(forms.Form):
    bot = forms.ModelChoiceField(queryset=Bot.objects.all(), required=False)
    id = forms.IntegerField(min_value=1, max_value=2000000,
                            required=False)
    name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)


class AfinidataUserForm(forms.ModelForm):
    bot_id = forms.ChoiceField(choices=((1, 'Afini Pilot'), (2, 'Afini AUE')))
    tipo_de_licencia = forms.ChoiceField(required=False, choices=(('', '--'), ('free', 'free'),
                                                                  ('patrocinado', 'patrocinado'),
                                                                  ('premium', 'premium'),
                                                                  ('trial_premium', 'trial_premium')))
    user_type = forms.ChoiceField(required=False, choices=(('', '--'), ('caregiver', 'caregiver'),
                                                           ('professional', 'professional'), ('pregnant', 'pregnant'),
                                                           ('influencer', 'influencer')))
    user_rol = forms.ChoiceField(required=False, choices=(('', '--'), ('👩 soy su mamá/papá', '👩 soy su mamá/papá'),
                                                          ('🏫trabajo con niños', '🏫trabajo con niños')))
    Pais = forms.CharField(max_length=20, required=False)
    childMonths = forms.IntegerField(required=False)
    chilDOB = forms.CharField(required=False, label='childDOB')
    user_reg = forms.ChoiceField(required=False, choices=(('', '--'), ('registered', 'registered'),
                                                          ('unregistered', 'unregistered')))
    Premium = forms.ChoiceField(choices=(('true', 'true'),))
    user_locale = forms.ChoiceField(required=False, choices=(('', '--'), ('en_US', 'en_US'), ('es_LA', 'es_LA')))
    childtype = forms.ChoiceField(required=False, choices=(('', '--'), ('onlychild', 'onlychild'),
                                                           ('multichild', 'multichild')))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'channel_id')


class AfinidataChildForm(forms.ModelForm):
    birthday = forms.CharField(max_length=20)
    entity = forms.ModelChoiceField(queryset=Entity.objects.filter(id__in=[1, 2]))

    class Meta:
        model = Instance
        fields = ('name', 'birthday', 'entity')


class InitialUserForm(forms.Form):
    tipo_de_licencia = forms.ChoiceField(required=False, choices=(('', '--'), ('free', 'free'),
                                                                  ('patrocinado', 'patrocinado'),
                                                                  ('premium', 'premium'),
                                                                  ('trial_premium', 'trial_premium')))
    user_type = forms.ChoiceField(choices=(('', '--'), ('caregiver', 'caregiver'), ('professional', 'professional'),
                                           ('pregnant', 'pregnant'), ('influencer', 'influencer')), required=False)
    user_rol = forms.ChoiceField(choices=(('', '--'), ('👩 soy su mamá/papá', '👩 soy su mamá/papá'),
                                          ('🏫trabajo con niños', '🏫trabajo con niños')), required=False)
    Pais = forms.CharField(max_length=20, required=False)
    childMonths = forms.IntegerField(required=False)
    chilDOB = forms.CharField(required=False, label='childDOB')
    user_reg = forms.ChoiceField(choices=(('', '--'), ('registered', 'registered'), ('unregistered', 'unregistered')),
                                 required=False)
    Premium = forms.CharField(max_length=10, required=False)
    user_locale = forms.ChoiceField(required=False, choices=(('', '--'), ('en_US', 'en_US'), ('es_LA', 'es_LA')))
    childtype = forms.ChoiceField(choices=(('', '--'), ('onlychild', 'onlychild'), ('multichild', 'multichild'))
                                  , required=False)
