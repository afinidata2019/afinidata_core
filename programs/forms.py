from areas.models import Area
from programs import models
from django import forms


class GroupProgramForm(forms.ModelForm):

    class Meta:
        model = models.Program
        fields = ('name', 'languages', 'levels')
        widgets = dict(
            languages=forms.CheckboxSelectMultiple(),
            levels=forms.CheckboxSelectMultiple()
        )
        labels = {
            "name": "Nombre",
            "languages": "Lenguajes",
            "levels": "Niveles"
        }


class GroupProgramAreasForm(forms.Form):
    salud = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=2),
                                            widget=forms.CheckboxSelectMultiple())
    encargado_responsable = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=3),
                                                          widget=forms.CheckboxSelectMultiple())
    salud_del_encargado = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=4),
                                                              widget=forms.CheckboxSelectMultiple())
    nutricion = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=5),
                                               widget=forms.CheckboxSelectMultiple())
    seguridad = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=6),
                                            widget=forms.CheckboxSelectMultiple())
    desarrollo_y_estimulacion_temprana = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=1),
                                                                    widget=forms.CheckboxSelectMultiple())
