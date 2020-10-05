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
