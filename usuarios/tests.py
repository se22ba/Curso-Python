import os
from unittest import mock

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from incidentes.models import Incidente
from .models import Perfil


class PerfilModelTest(TestCase):
    def test_perfil_se_crea_automaticamente_al_crear_usuario(self):
        usuario = User.objects.create_user(username="nuevo", password="NuevoSegura123")
        self.assertTrue(Perfil.objects.filter(usuario=usuario).exists())

    def test_str_perfil(self):
        usuario = User.objects.create_user(username="ana", password="AnaSegura123")
        self.assertEqual(str(usuario.perfil), "Perfil de ana")

    def test_guardar_usuario_existente_no_duplica_perfil(self):
        usuario = User.objects.create_user(username="ana", password="AnaSegura123")
        usuario.email = "ana@example.com"
        usuario.save()
        self.assertEqual(Perfil.objects.filter(usuario=usuario).count(), 1)


class RegistroViewTest(TestCase):
    def test_get_muestra_formulario(self):
        response = self.client.get(reverse("usuarios:registro"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear cuenta")

    def test_registro_exitoso_crea_usuario_y_perfil(self):
        response = self.client.post(reverse("usuarios:registro"), {
            "username": "nuevo_usuario",
            "password1": "ContraseñaSegura123",
            "password2": "ContraseñaSegura123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("usuarios:login"))
        usuario = User.objects.get(username="nuevo_usuario")
        self.assertTrue(Perfil.objects.filter(usuario=usuario).exists())

    def test_registro_con_passwords_distintas_no_crea_usuario(self):
        response = self.client.post(reverse("usuarios:registro"), {
            "username": "otro_usuario",
            "password1": "ContraseñaSegura123",
            "password2": "OtraDistinta456",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="otro_usuario").exists())

    def test_registro_con_username_duplicado_falla(self):
        User.objects.create_user(username="repetido", password="ContraseñaSegura123")
        response = self.client.post(reverse("usuarios:registro"), {
            "username": "repetido",
            "password1": "OtraSegura789",
            "password2": "OtraSegura789",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="repetido").count(), 1)


class UsuarioLoginViewTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="tester", password="Tester123456")

    def test_get_muestra_formulario(self):
        response = self.client.get(reverse("usuarios:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Iniciar sesión")

    def test_login_exitoso_redirige(self):
        response = self.client.post(reverse("usuarios:login"), {
            "username": "tester",
            "password": "Tester123456",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_con_credenciales_invalidas_no_autentica(self):
        response = self.client.post(reverse("usuarios:login"), {
            "username": "tester",
            "password": "ContraseñaIncorrecta",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario o contraseña incorrectos")

    def test_login_respeta_parametro_next(self):
        url_destino = reverse("incidentes:crear")
        url_login_con_next = f"{reverse('usuarios:login')}?next={url_destino}"
        response = self.client.post(url_login_con_next, {
            "username": "tester",
            "password": "Tester123456",
        })
        self.assertRedirects(response, url_destino)


class UsuarioLogoutViewTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="tester", password="Tester123456")

    def test_logout_requiere_post(self):
        self.client.login(username="tester", password="Tester123456")
        response = self.client.get(reverse("usuarios:logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_post_cierra_sesion(self):
        self.client.login(username="tester", password="Tester123456")
        response = self.client.post(reverse("usuarios:logout"))
        self.assertEqual(response.status_code, 302)

    def test_despues_de_logout_recurso_protegido_redirige(self):
        self.client.login(username="tester", password="Tester123456")
        self.client.post(reverse("usuarios:logout"))
        response = self.client.get(reverse("incidentes:crear"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)


class PerfilDetailViewTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="ana", password="AnaSegura123")

    def test_perfil_es_publico(self):
        response = self.client.get(reverse("usuarios:perfil", kwargs={"username": "ana"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ana")

    def test_perfil_muestra_boton_editar_solo_al_propietario(self):
        self.client.login(username="ana", password="AnaSegura123")
        response = self.client.get(reverse("usuarios:perfil", kwargs={"username": "ana"}))
        self.assertContains(response, "Editar mi perfil")

    def test_perfil_no_muestra_boton_editar_a_visitante(self):
        response = self.client.get(reverse("usuarios:perfil", kwargs={"username": "ana"}))
        self.assertNotContains(response, "Editar mi perfil")

    def test_perfil_muestra_boton_gestionar_usuarios_a_staff(self):
        staff = User.objects.create_user(username="staff_user", password="StaffSegura123", is_staff=True)
        self.client.login(username="staff_user", password="StaffSegura123")
        response = self.client.get(reverse("usuarios:perfil", kwargs={"username": "staff_user"}))
        self.assertContains(response, "Gestionar usuarios")

    def test_perfil_no_muestra_boton_gestionar_usuarios_a_no_staff(self):
        self.client.login(username="ana", password="AnaSegura123")
        response = self.client.get(reverse("usuarios:perfil", kwargs={"username": "ana"}))
        self.assertNotContains(response, "Gestionar usuarios")


class EditarPerfilViewTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="ana", password="AnaSegura123")

    def test_requiere_login(self):
        response = self.client.get(reverse("usuarios:editar_perfil"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)

    def test_get_muestra_formularios_precargados(self):
        self.client.login(username="ana", password="AnaSegura123")
        response = self.client.get(reverse("usuarios:editar_perfil"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar mi perfil")

    def test_post_valido_actualiza_datos_y_perfil(self):
        self.client.login(username="ana", password="AnaSegura123")
        response = self.client.post(reverse("usuarios:editar_perfil"), {
            "first_name": "Ana",
            "last_name": "Gómez",
            "email": "ana@example.com",
            "biografia": "Bio de prueba",
            "barrio": "Belgrano",
        })
        self.assertEqual(response.status_code, 302)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.first_name, "Ana")
        self.assertEqual(self.usuario.perfil.barrio, "Belgrano")

    def test_post_invalido_no_actualiza(self):
        self.client.login(username="ana", password="AnaSegura123")
        response = self.client.post(reverse("usuarios:editar_perfil"), {
            "first_name": "Ana",
            "last_name": "Gómez",
            "email": "no-es-un-email",
            "biografia": "Bio de prueba",
            "barrio": "Belgrano",
        })
        self.assertEqual(response.status_code, 200)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.perfil.barrio, "")


class CrearSuperusuarioInicialCommandTest(TestCase):
    def test_sin_variables_no_crea_usuario(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            call_command("crear_superusuario_inicial")
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 0)

    def test_con_variables_crea_superusuario(self):
        variables = {
            "DJANGO_SUPERUSER_USERNAME": "admin",
            "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "AdminSegura123",
        }
        with mock.patch.dict(os.environ, variables):
            call_command("crear_superusuario_inicial")

        usuario = User.objects.get(username="admin")
        self.assertTrue(usuario.is_superuser)
        self.assertTrue(usuario.check_password("AdminSegura123"))

    def test_comando_es_idempotente(self):
        variables = {
            "DJANGO_SUPERUSER_USERNAME": "admin",
            "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "PrimeraPassword123",
        }
        with mock.patch.dict(os.environ, variables):
            call_command("crear_superusuario_inicial")

        variables["DJANGO_SUPERUSER_PASSWORD"] = "SegundaPassword456"
        with mock.patch.dict(os.environ, variables):
            call_command("crear_superusuario_inicial")

        self.assertEqual(User.objects.filter(username="admin").count(), 1)
        usuario = User.objects.get(username="admin")
        self.assertTrue(usuario.check_password("PrimeraPassword123"))


class UsuarioAdminTest(TestCase):
    def setUp(self):
        self.superusuario = User.objects.create_superuser(
            username="superadmin", email="superadmin@example.com", password="SuperAdmin123"
        )
        self.client.login(username="superadmin", password="SuperAdmin123")

    def test_listado_de_usuarios_muestra_cantidad_de_entradas(self):
        autor = User.objects.create_user(username="autor_demo", password="AutorDemo123")
        Incidente.objects.create(
            titulo="Entrada de prueba",
            descripcion="x" * 20,
            categoria="otro",
            severidad="baja",
            direccion="Calle Test",
            latitud="-34.6",
            longitud="-58.4",
            fecha_ocurrencia="2026-06-19T10:00",
            autor=autor,
        )
        response = self.client.get(reverse("admin:auth_user_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "autor_demo")

    def test_edicion_de_usuario_incluye_inline_de_perfil(self):
        usuario = User.objects.create_user(username="con_perfil", password="ConPerfil123")
        response = self.client.get(reverse("admin:auth_user_change", args=[usuario.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "barrio")
