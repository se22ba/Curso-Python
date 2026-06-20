from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import MensajeContactoForm


class AcercaDeView(TemplateView):
    template_name = "paginas/acerca_de.html"


class ContactoView(CreateView):
    form_class = MensajeContactoForm
    template_name = "paginas/contacto.html"
    success_url = reverse_lazy("paginas:contacto")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, "Tu mensaje fue enviado correctamente. Te responderemos a la brevedad.")
        return respuesta
