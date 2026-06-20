from django.contrib import admin
from .models import Incidente, ReporteIncidente


class ReporteIncidenteInline(admin.TabularInline):
    model = ReporteIncidente
    extra = 0
    readonly_fields = ("reportado_por", "motivo", "creado_en")
    can_delete = True


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "severidad", "direccion", "autor", "fecha_ocurrencia", "oculto_por_reportes")
    list_filter = ("categoria", "severidad", "oculto_por_reportes")
    search_fields = ("titulo", "descripcion", "direccion")
    date_hierarchy = "fecha_ocurrencia"
    inlines = (ReporteIncidenteInline,)
    fieldsets = (
        ("Información del incidente", {
            "fields": ("titulo", "descripcion", "categoria", "severidad"),
        }),
        ("Ubicación", {
            "fields": ("direccion", "latitud", "longitud"),
        }),
        ("Moderación", {
            "fields": ("oculto_por_reportes",),
        }),
        ("Metadatos", {
            "fields": ("autor", "fecha_ocurrencia", "creado_en", "actualizado_en"),
        }),
    )
    readonly_fields = ("creado_en", "actualizado_en")
