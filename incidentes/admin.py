from django.contrib import admin
from .models import Incidente


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "severidad", "direccion", "autor", "fecha_ocurrencia")
    list_filter = ("categoria", "severidad")
    search_fields = ("titulo", "descripcion", "direccion")
    date_hierarchy = "fecha_ocurrencia"
    fieldsets = (
        ("Información del incidente", {
            "fields": ("titulo", "descripcion", "categoria", "severidad"),
        }),
        ("Ubicación", {
            "fields": ("direccion", "latitud", "longitud"),
        }),
        ("Metadatos", {
            "fields": ("autor", "fecha_ocurrencia", "creado_en", "actualizado_en"),
        }),
    )
    readonly_fields = ("creado_en", "actualizado_en")
