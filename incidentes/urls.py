from django.urls import path
from . import views

app_name = "incidentes"

urlpatterns = [
    path("", views.IncidenteListView.as_view(), name="lista"),
    path("<int:pk>/", views.IncidenteDetailView.as_view(), name="detalle"),
    path("nuevo/", views.IncidenteCreateView.as_view(), name="crear"),
    path("<int:pk>/editar/", views.IncidenteUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.IncidenteDeleteView.as_view(), name="eliminar"),
    path("<int:pk>/reportar/", views.reportar_incidente, name="reportar"),
]
