from areas.models import Area
from programs import models
from django import forms


class GroupProgramForm(forms.ModelForm):

    class Meta:
        model = models.Program
        fields = ('name', 'description', 'languages', 'levels')
        widgets = dict(
            languages=forms.CheckboxSelectMultiple(),
            levels=forms.CheckboxSelectMultiple()
        )


class GroupProgramAreasForm(forms.Form):
    health = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=2),
                                            widget=forms.CheckboxSelectMultiple())
    responsive_caregiver = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=3),
                                                          widget=forms.CheckboxSelectMultiple())
    caring_for_the_caregiver = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=4),
                                                              widget=forms.CheckboxSelectMultiple())
    nutrition = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=5),
                                               widget=forms.CheckboxSelectMultiple())
    safety = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=6),
                                            widget=forms.CheckboxSelectMultiple())
    development_and_early_learning = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=1),
                                                                    widget=forms.CheckboxSelectMultiple())
