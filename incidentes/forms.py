from django import forms
from .models import Incidente


class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = [
            "titulo",
            "descripcion",
            "categoria",
            "severidad",
            "direccion",
            "latitud",
            "longitud",
            "fecha_ocurrencia",
        ]
        widgets = {
            "fecha_ocurrencia": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "latitud": forms.NumberInput(attrs={"step": "any", "readonly": "readonly"}),
            "longitud": forms.NumberInput(attrs={"step": "any", "readonly": "readonly"}),
        }

    def clean_latitud(self):
        latitud = self.cleaned_data["latitud"]
        if not -90 <= latitud <= 90:
            raise forms.ValidationError("La latitud debe estar entre -90 y 90.")
        return latitud

    def clean_longitud(self):
        longitud = self.cleaned_data["longitud"]
        if not -180 <= longitud <= 180:
            raise forms.ValidationError("La longitud debe estar entre -180 y 180.")
        return longitud


CATEGORIA_CHOICES_CON_TODAS = [("", "Todas las categorías")] + Incidente.CATEGORIA_CHOICES
SEVERIDAD_CHOICES_CON_TODAS = [("", "Todas las severidades")] + Incidente.SEVERIDAD_CHOICES


class IncidenteBusquedaForm(forms.Form):
    titulo = forms.CharField(required=False, label="Buscar por título")
    categoria = forms.ChoiceField(required=False, choices=CATEGORIA_CHOICES_CON_TODAS, label="Categoría")
    severidad = forms.ChoiceField(required=False, choices=SEVERIDAD_CHOICES_CON_TODAS, label="Severidad")
