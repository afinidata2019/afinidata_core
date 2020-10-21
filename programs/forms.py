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
    paternidad_responsiva = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=3),
                                                          widget=forms.CheckboxSelectMultiple())
    cuidado_del_cuidador = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=4),
                                                              widget=forms.CheckboxSelectMultiple())
    nutricion = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=5),
                                               widget=forms.CheckboxSelectMultiple())
    seguridad = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=6),
                                            widget=forms.CheckboxSelectMultiple())
    desarrollo_infantil_y_aprendizaje_inicial = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(topic_id=1),
                                                                    widget=forms.CheckboxSelectMultiple())
