from django.contrib import admin
from .models import MensajeContacto


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ("asunto", "nombre", "email", "creado_en", "leido")
    list_filter = ("leido",)
    search_fields = ("nombre", "email", "asunto", "mensaje")
    readonly_fields = ("nombre", "email", "asunto", "mensaje", "creado_en")
