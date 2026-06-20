import json
from datetime import timedelta
from math import ceil

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Incidente, ReporteIncidente, UMBRAL_REPORTES_PARA_OCULTAR
from .forms import IncidenteForm, IncidenteBusquedaForm

INTERVALO_MINIMO_ENTRE_PUBLICACIONES = timedelta(minutes=5)
MAXIMO_PUBLICACIONES_POR_DIA = 5


class IncidenteListView(ListView):
    model = Incidente
    template_name = "incidentes/lista.html"
    context_object_name = "incidentes"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(oculto_por_reportes=False)
        self.form_busqueda = IncidenteBusquedaForm(self.request.GET or None)

        if self.form_busqueda.is_valid():
            titulo = self.form_busqueda.cleaned_data.get("titulo")
            categoria = self.form_busqueda.cleaned_data.get("categoria")
            severidad = self.form_busqueda.cleaned_data.get("severidad")

            if titulo:
                queryset = queryset.filter(titulo__icontains=titulo)
            if categoria:
                queryset = queryset.filter(categoria=categoria)
            if severidad:
                queryset = queryset.filter(severidad=severidad)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_busqueda"] = self.form_busqueda

        incidentes_geojson = [
            {
                "id": incidente.pk,
                "titulo": incidente.titulo,
                "categoria": incidente.get_categoria_display(),
                "severidad": incidente.severidad,
                "direccion": incidente.direccion,
                "lat": float(incidente.latitud),
                "lng": float(incidente.longitud),
                "url": incidente.get_absolute_url(),
            }
            for incidente in self.get_queryset()
        ]
        context["incidentes_json"] = json.dumps(incidentes_geojson)
        return context


class IncidenteDetailView(DetailView):
    model = Incidente
    template_name = "incidentes/detalle.html"
    context_object_name = "incidente"

    def get_object(self, queryset=None):
        incidente = super().get_object(queryset)
        usuario = self.request.user
        es_autor_o_staff = usuario.is_authenticated and (
            usuario.id == incidente.autor_id or usuario.is_staff
        )
        if incidente.oculto_por_reportes and not es_autor_o_staff:
            raise Http404("Esta entrada no está disponible.")
        return incidente

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        incidente = self.object

        puede_reportar = usuario.is_authenticated and usuario.id != incidente.autor_id
        context["puede_reportar"] = puede_reportar
        context["ya_reportado"] = puede_reportar and ReporteIncidente.objects.filter(
            incidente=incidente, reportado_por=usuario
        ).exists()
        return context


class IncidenteCreateView(LoginRequiredMixin, CreateView):
    model = Incidente
    form_class = IncidenteForm
    template_name = "incidentes/formulario.html"

    def form_valid(self, form):
        ahora = timezone.now()
        ultima_entrada = Incidente.objects.filter(autor=self.request.user).order_by("-creado_en").first()

        if ultima_entrada and ahora - ultima_entrada.creado_en < INTERVALO_MINIMO_ENTRE_PUBLICACIONES:
            restante = INTERVALO_MINIMO_ENTRE_PUBLICACIONES - (ahora - ultima_entrada.creado_en)
            minutos_restantes = max(1, ceil(restante.total_seconds() / 60))
            form.add_error(
                None,
                f"Esperá unos minutos antes de publicar otra entrada (podés volver a intentarlo en {minutos_restantes} min).",
            )
            return self.form_invalid(form)

        publicaciones_ultimas_24h = Incidente.objects.filter(
            autor=self.request.user,
            creado_en__gte=ahora - timedelta(days=1),
        ).count()

        if publicaciones_ultimas_24h >= MAXIMO_PUBLICACIONES_POR_DIA:
            form.add_error(
                None,
                f"Alcanzaste el límite de {MAXIMO_PUBLICACIONES_POR_DIA} entradas por día. Volvé a intentarlo más tarde.",
            )
            return self.form_invalid(form)

        form.instance.autor = self.request.user
        return super().form_valid(form)


class EsAutorMixin(UserPassesTestMixin):
    def test_func(self):
        incidente = self.get_object()
        return incidente.autor_id == self.request.user.id

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("No podés editar o eliminar un incidente reportado por otro usuario.")


class IncidenteUpdateView(LoginRequiredMixin, EsAutorMixin, UpdateView):
    model = Incidente
    form_class = IncidenteForm
    template_name = "incidentes/formulario.html"


class IncidenteDeleteView(LoginRequiredMixin, EsAutorMixin, DeleteView):
    model = Incidente
    template_name = "incidentes/confirmar_borrado.html"
    success_url = reverse_lazy("incidentes:lista")


@login_required
@require_POST
def reportar_incidente(request, pk):
    incidente = get_object_or_404(Incidente, pk=pk)

    if incidente.autor_id == request.user.id:
        messages.error(request, "No podés reportar tu propia entrada.")
        return redirect(incidente.get_absolute_url())

    _, creado = ReporteIncidente.objects.get_or_create(incidente=incidente, reportado_por=request.user)

    if creado:
        if incidente.cantidad_reportes() >= UMBRAL_REPORTES_PARA_OCULTAR:
            incidente.oculto_por_reportes = True
            incidente.save(update_fields=["oculto_por_reportes"])
        messages.success(request, "Gracias, tu reporte fue registrado para revisión.")
    else:
        messages.info(request, "Ya habías reportado esta entrada anteriormente.")

    return redirect(incidente.get_absolute_url())
