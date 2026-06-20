from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from .forms import PerfilForm, DatosUsuarioForm
from .models import Perfil


class RegistroView(CreateView):
    form_class = UserCreationForm
    template_name = "usuarios/registro.html"
    success_url = reverse_lazy("usuarios:login")


class UsuarioLoginView(LoginView):
    template_name = "usuarios/login.html"


class UsuarioLogoutView(LogoutView):
    pass


class PerfilDetailView(DetailView):
    model = Perfil
    template_name = "usuarios/perfil_detalle.html"
    context_object_name = "perfil"
    slug_field = "usuario__username"
    slug_url_kwarg = "username"


@login_required
def editar_perfil(request):
    perfil = request.user.perfil

    if request.method == "POST":
        form_datos = DatosUsuarioForm(request.POST, instance=request.user)
        form_perfil = PerfilForm(request.POST, request.FILES, instance=perfil)

        if form_datos.is_valid() and form_perfil.is_valid():
            form_datos.save()
            form_perfil.save()
            messages.success(request, "Tu perfil se actualizó correctamente.")
            return redirect("usuarios:perfil", username=request.user.username)
    else:
        form_datos = DatosUsuarioForm(instance=request.user)
        form_perfil = PerfilForm(instance=perfil)

    return render(request, "usuarios/editar_perfil.html", {
        "form_datos": form_datos,
        "form_perfil": form_perfil,
    })
