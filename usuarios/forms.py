from django import forms
from django.contrib.auth.models import User
from .models import Perfil


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["biografia", "barrio", "avatar"]
        widgets = {
            "biografia": forms.Textarea(attrs={"rows": 4}),
        }


class DatosUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
