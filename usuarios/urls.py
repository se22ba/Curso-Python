from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("registro/", views.RegistroView.as_view(), name="registro"),
    path("login/", views.UsuarioLoginView.as_view(), name="login"),
    path("logout/", views.UsuarioLogoutView.as_view(), name="logout"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("perfil/<str:username>/", views.PerfilDetailView.as_view(), name="perfil"),
]
