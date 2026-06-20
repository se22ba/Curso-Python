from django import forms
from .models import MensajeContacto


class MensajeContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ["nombre", "email", "asunto", "mensaje"]
        widgets = {
            "mensaje": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_mensaje(self):
        mensaje = self.cleaned_data["mensaje"]
        if len(mensaje.strip()) < 10:
            raise forms.ValidationError("El mensaje debe tener al menos 10 caracteres.")
        return mensaje
