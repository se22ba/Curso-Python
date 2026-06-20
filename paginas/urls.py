from django.urls import path
from . import views

app_name = "paginas"

urlpatterns = [
    path("acerca-de/", views.AcercaDeView.as_view(), name="acerca_de"),
    path("contacto/", views.ContactoView.as_view(), name="contacto"),
]
