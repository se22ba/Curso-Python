from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from incidentes.models import Incidente
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    fields = ("barrio", "biografia", "avatar")


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "barrio")
    search_fields = ("usuario__username", "barrio")


class UsuarioAdmin(UserAdmin):
    inlines = (PerfilInline,)
    list_display = (
        "username", "email", "is_active", "is_staff",
        "date_joined", "cantidad_entradas_publicadas",
    )
    list_filter = UserAdmin.list_filter + ("date_joined",)

    def cantidad_entradas_publicadas(self, obj):
        return Incidente.objects.filter(autor=obj).count()

    cantidad_entradas_publicadas.short_description = "Entradas publicadas"


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
