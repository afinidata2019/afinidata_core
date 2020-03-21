from milestones.models import Milestone
from areas.models import Area
from django import forms


class MilestoneSearchForm(forms.Form):
    code = forms.ModelChoiceField(queryset=Milestone.objects.all().only('code'), widget=forms.TextInput, to_field_name='code',
                                  required=False)
    second_code = forms.ModelChoiceField(queryset=Milestone.objects.all().only('second_code'), widget=forms.TextInput,
                                         to_field_name='second_code', required=False)
    area = forms.ModelChoiceField(queryset=Area.objects.all(), to_field_name='name', required=False)

