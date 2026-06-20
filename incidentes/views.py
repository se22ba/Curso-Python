import json

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Incidente
from .forms import IncidenteForm, IncidenteBusquedaForm


class IncidenteListView(ListView):
    model = Incidente
    template_name = "incidentes/lista.html"
    context_object_name = "incidentes"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
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


class IncidenteCreateView(LoginRequiredMixin, CreateView):
    model = Incidente
    form_class = IncidenteForm
    template_name = "incidentes/formulario.html"

    def form_valid(self, form):
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
