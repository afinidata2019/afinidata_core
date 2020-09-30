from groups.models import Group
from django import forms


class GroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())


class CreateProgramForm(forms.Form):
    name = forms.CharField(max_length=255)
    age_range = forms.MultipleChoiceField(choices=((1, '0 to 3 months old'), (2, '4 to 6 months old'),
                                                   (1, '7 to 9 months old'), (2, '10 to 12 months old'),
                                                   (1, '13 to 18 months old'), (2, '19 to 24 months old'),
                                                   (1, '25 to 36 months old'), (2, '37 to 48 months old'),
                                                   (1, '49 to 60 months old'), (2, '61 to 72 months old'),
                                                   (1, 'Pregnancy')),
                                          widget=forms.CheckboxSelectMultiple)
    languages = forms.MultipleChoiceField(choices=((0, 'English'), (0, 'Spanish'), (0, 'Arabic')),
                                          widget=forms.CheckboxSelectMultiple)
