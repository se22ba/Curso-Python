import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Incidente, ReporteIncidente, UMBRAL_REPORTES_PARA_OCULTAR
from .forms import IncidenteForm, IncidenteBusquedaForm


def crear_incidente(autor, **overrides):
    creado_en_forzado = overrides.pop("creado_en", None)
    datos = {
        "titulo": "Incidente de prueba",
        "descripcion": "Descripción de prueba con suficiente longitud.",
        "categoria": Incidente.CATEGORIA_ROBO,
        "severidad": Incidente.SEVERIDAD_MEDIA,
        "direccion": "Calle Falsa 123",
        "latitud": "-34.603700",
        "longitud": "-58.381600",
        "fecha_ocurrencia": timezone.now() - timedelta(hours=2),
        "autor": autor,
    }
    datos.update(overrides)
    incidente = Incidente.objects.create(**datos)

    if creado_en_forzado is not None:
        incidente.creado_en = creado_en_forzado
        incidente.save(update_fields=["creado_en"])

    return incidente


class IncidenteModelTest(TestCase):
    def setUp(self):
        self.autor = User.objects.create_user(username="autor", password="Autor123456")

    def test_str_incluye_categoria_y_titulo(self):
        incidente = crear_incidente(self.autor, titulo="Robo en la esquina")
        self.assertEqual(str(incidente), "Robo - Robo en la esquina")

    def test_get_absolute_url(self):
        incidente = crear_incidente(self.autor)
        self.assertEqual(incidente.get_absolute_url(), reverse("incidentes:detalle", kwargs={"pk": incidente.pk}))

    def test_orden_por_fecha_ocurrencia_descendente(self):
        viejo = crear_incidente(self.autor, titulo="Viejo", fecha_ocurrencia=timezone.now() - timedelta(days=5))
        nuevo = crear_incidente(self.autor, titulo="Nuevo", fecha_ocurrencia=timezone.now())
        incidentes = list(Incidente.objects.all())
        self.assertEqual(incidentes[0], nuevo)
        self.assertEqual(incidentes[1], viejo)


class IncidenteFormTest(TestCase):
    def datos_validos(self):
        return {
            "titulo": "Título válido",
            "descripcion": "Descripción con longitud suficiente para pasar validación.",
            "categoria": Incidente.CATEGORIA_HURTO,
            "severidad": Incidente.SEVERIDAD_ALTA,
            "direccion": "Av. Siempre Viva 742",
            "latitud": "-34.6",
            "longitud": "-58.4",
            "fecha_ocurrencia": "2026-06-10T10:30",
        }

    def test_form_valido_con_datos_correctos(self):
        form = IncidenteForm(data=self.datos_validos())
        self.assertTrue(form.is_valid())

    def test_latitud_fuera_de_rango_invalida(self):
        datos = self.datos_validos()
        datos["latitud"] = "120"
        form = IncidenteForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn("latitud", form.errors)

    def test_longitud_fuera_de_rango_invalida(self):
        datos = self.datos_validos()
        datos["longitud"] = "200"
        form = IncidenteForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn("longitud", form.errors)

    def test_busqueda_form_todos_los_campos_opcionales(self):
        form = IncidenteBusquedaForm(data={})
        self.assertTrue(form.is_valid())


class IncidenteListViewTest(TestCase):
    def setUp(self):
        self.autor = User.objects.create_user(username="autor", password="Autor123456")
        self.robo = crear_incidente(self.autor, titulo="Robo en plaza", categoria=Incidente.CATEGORIA_ROBO, severidad=Incidente.SEVERIDAD_ALTA)
        self.vandalismo = crear_incidente(self.autor, titulo="Pintada en pared", categoria=Incidente.CATEGORIA_VANDALISMO, severidad=Incidente.SEVERIDAD_BAJA)

    def test_lista_es_publica(self):
        response = self.client.get(reverse("incidentes:lista"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Robo en plaza")
        self.assertContains(response, "Pintada en pared")

    def test_lista_incluye_datos_geojson_para_el_mapa(self):
        response = self.client.get(reverse("incidentes:lista"))
        self.assertContains(response, "datosIncidentes")
        self.assertContains(response, str(float(self.robo.latitud)))

    def test_busqueda_por_titulo_filtra(self):
        response = self.client.get(reverse("incidentes:lista"), {"titulo": "plaza"})
        self.assertContains(response, "Robo en plaza")
        self.assertNotContains(response, "Pintada en pared")

    def test_busqueda_por_categoria_filtra(self):
        response = self.client.get(reverse("incidentes:lista"), {"categoria": Incidente.CATEGORIA_VANDALISMO})
        self.assertContains(response, "Pintada en pared")
        self.assertNotContains(response, "Robo en plaza")

    def test_busqueda_por_severidad_filtra(self):
        response = self.client.get(reverse("incidentes:lista"), {"severidad": Incidente.SEVERIDAD_ALTA})
        self.assertContains(response, "Robo en plaza")
        self.assertNotContains(response, "Pintada en pared")


class IncidenteDetailViewTest(TestCase):
    def setUp(self):
        self.autor = User.objects.create_user(username="autor", password="Autor123456")
        self.incidente = crear_incidente(self.autor, titulo="Detalle visible")

    def test_detalle_es_publico(self):
        response = self.client.get(reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detalle visible")

    def test_detalle_muestra_acciones_solo_al_autor(self):
        self.client.login(username="autor", password="Autor123456")
        response = self.client.get(reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk}))
        self.assertContains(response, "Editar")

    def test_detalle_no_muestra_acciones_a_otro_usuario(self):
        User.objects.create_user(username="otro", password="OtroSegura123")
        self.client.login(username="otro", password="OtroSegura123")
        response = self.client.get(reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk}))
        self.assertNotContains(response, "Eliminar")


class IncidenteCreateViewTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="reportante", password="Reportante123")

    def datos_validos(self):
        return {
            "titulo": "Nueva entrada del blog",
            "descripcion": "Descripción con longitud suficiente para pasar validación.",
            "categoria": Incidente.CATEGORIA_SOSPECHOSO,
            "severidad": Incidente.SEVERIDAD_MEDIA,
            "direccion": "Calle Nueva 456",
            "latitud": "-34.6",
            "longitud": "-58.4",
            "fecha_ocurrencia": "2026-06-10T10:30",
        }

    def test_crear_requiere_login(self):
        response = self.client.get(reverse("incidentes:crear"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)

    def test_crear_con_login_asigna_autor_automaticamente(self):
        self.client.login(username="reportante", password="Reportante123")
        response = self.client.post(reverse("incidentes:crear"), self.datos_validos())
        self.assertEqual(response.status_code, 302)
        incidente = Incidente.objects.get(titulo="Nueva entrada del blog")
        self.assertEqual(incidente.autor, self.usuario)


class IncidenteUpdateDeleteViewTest(TestCase):
    def setUp(self):
        self.autor = User.objects.create_user(username="autor", password="Autor123456")
        self.otro = User.objects.create_user(username="otro", password="OtroSegura123")
        self.incidente = crear_incidente(self.autor, titulo="Entrada del autor")

    def datos_edicion(self):
        return {
            "titulo": "Entrada editada",
            "descripcion": "Descripción editada con longitud suficiente.",
            "categoria": Incidente.CATEGORIA_OTRO,
            "severidad": Incidente.SEVERIDAD_BAJA,
            "direccion": "Calle Editada 1",
            "latitud": "-34.6",
            "longitud": "-58.4",
            "fecha_ocurrencia": "2026-06-11T09:00",
        }

    def test_autor_puede_editar(self):
        self.client.login(username="autor", password="Autor123456")
        url = reverse("incidentes:editar", kwargs={"pk": self.incidente.pk})
        response = self.client.post(url, self.datos_edicion())
        self.assertEqual(response.status_code, 302)
        self.incidente.refresh_from_db()
        self.assertEqual(self.incidente.titulo, "Entrada editada")

    def test_otro_usuario_no_puede_editar(self):
        self.client.login(username="otro", password="OtroSegura123")
        url = reverse("incidentes:editar", kwargs={"pk": self.incidente.pk})
        response = self.client.post(url, self.datos_edicion())
        self.assertEqual(response.status_code, 403)
        self.incidente.refresh_from_db()
        self.assertEqual(self.incidente.titulo, "Entrada del autor")

    def test_anonimo_redirige_a_login_al_editar(self):
        url = reverse("incidentes:editar", kwargs={"pk": self.incidente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)

    def test_autor_puede_eliminar(self):
        self.client.login(username="autor", password="Autor123456")
        url = reverse("incidentes:eliminar", kwargs={"pk": self.incidente.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Incidente.objects.filter(pk=self.incidente.pk).exists())

    def test_otro_usuario_no_puede_eliminar(self):
        self.client.login(username="otro", password="OtroSegura123")
        url = reverse("incidentes:eliminar", kwargs={"pk": self.incidente.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Incidente.objects.filter(pk=self.incidente.pk).exists())


class CargarDatosEjemploCommandTest(TestCase):
    def test_comando_crea_entradas_y_usuario_demo(self):
        call_command("cargar_datos_ejemplo")
        self.assertEqual(Incidente.objects.count(), 5)
        self.assertTrue(User.objects.filter(username="vecino_demo").exists())

    def test_comando_es_idempotente(self):
        call_command("cargar_datos_ejemplo")
        call_command("cargar_datos_ejemplo")
        self.assertEqual(Incidente.objects.count(), 5)
        self.assertEqual(User.objects.filter(username="vecino_demo").count(), 1)


class IncidenteRateLimitTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="reportante", password="Reportante123")
        self.client.login(username="reportante", password="Reportante123")

    def datos_validos(self, titulo):
        return {
            "titulo": titulo,
            "descripcion": "Descripción con longitud suficiente para pasar validación.",
            "categoria": Incidente.CATEGORIA_OTRO,
            "severidad": Incidente.SEVERIDAD_BAJA,
            "direccion": "Calle Test 1",
            "latitud": "-34.6",
            "longitud": "-58.4",
            "fecha_ocurrencia": "2026-06-19T10:00",
        }

    def test_segunda_publicacion_inmediata_se_rechaza(self):
        self.client.post(reverse("incidentes:crear"), self.datos_validos("Primera"))
        response = self.client.post(reverse("incidentes:crear"), self.datos_validos("Segunda inmediata"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Esperá unos minutos")
        self.assertFalse(Incidente.objects.filter(titulo="Segunda inmediata").exists())

    def test_publicacion_pasado_el_cooldown_se_permite(self):
        crear_incidente(self.usuario, titulo="Primera", creado_en=timezone.now() - timedelta(minutes=10))
        response = self.client.post(reverse("incidentes:crear"), self.datos_validos("Segunda con cooldown pasado"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Incidente.objects.filter(titulo="Segunda con cooldown pasado").exists())

    def test_limite_diario_se_rechaza(self):
        ahora = timezone.now()
        for i in range(5):
            crear_incidente(self.usuario, titulo=f"Entrada {i}", creado_en=ahora - timedelta(hours=i + 1))

        response = self.client.post(reverse("incidentes:crear"), self.datos_validos("Sexta entrada"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "límite de 5 entradas")
        self.assertFalse(Incidente.objects.filter(titulo="Sexta entrada").exists())


class ReporteIncidenteModelTest(TestCase):
    def test_str_incluye_reportante_y_titulo(self):
        autor = User.objects.create_user(username="autor", password="Autor123456")
        reportante = User.objects.create_user(username="reportante", password="Reportante123")
        incidente = crear_incidente(autor, titulo="Entrada reportable")
        reporte = ReporteIncidente.objects.create(incidente=incidente, reportado_por=reportante)
        self.assertEqual(str(reporte), "Reporte de reportante sobre Entrada reportable")


class ReportarIncidenteViewTest(TestCase):
    def setUp(self):
        self.autor = User.objects.create_user(username="autor", password="Autor123456")
        self.incidente = crear_incidente(self.autor, titulo="Entrada bajo reporte")
        self.reportantes = [
            User.objects.create_user(username=f"reportante{i}", password="Reportante123")
            for i in range(UMBRAL_REPORTES_PARA_OCULTAR)
        ]

    def test_requiere_login(self):
        url = reverse("incidentes:reportar", kwargs={"pk": self.incidente.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)

    def test_requiere_post(self):
        self.client.login(username="reportante0", password="Reportante123")
        url = reverse("incidentes:reportar", kwargs={"pk": self.incidente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_autor_no_puede_reportar_su_propia_entrada(self):
        self.client.login(username="autor", password="Autor123456")
        url = reverse("incidentes:reportar", kwargs={"pk": self.incidente.pk})
        self.client.post(url)
        self.assertEqual(self.incidente.cantidad_reportes(), 0)

    def test_reporte_se_registra_correctamente(self):
        self.client.login(username="reportante0", password="Reportante123")
        url = reverse("incidentes:reportar", kwargs={"pk": self.incidente.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.incidente.cantidad_reportes(), 1)

    def test_mismo_usuario_no_puede_reportar_dos_veces(self):
        self.client.login(username="reportante0", password="Reportante123")
        url = reverse("incidentes:reportar", kwargs={"pk": self.incidente.pk})
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(self.incidente.cantidad_reportes(), 1)

    def test_se_oculta_automaticamente_al_alcanzar_el_umbral(self):
        url = reverse("incidentes:reportar", kwargs={"pk": self.incidente.pk})
        for usuario in self.reportantes:
            self.client.login(username=usuario.username, password="Reportante123")
            self.client.post(url)

        self.incidente.refresh_from_db()
        self.assertTrue(self.incidente.oculto_por_reportes)


class IncidenteVisibilidadOcultoTest(TestCase):
    def setUp(self):
        self.autor = User.objects.create_user(username="autor", password="Autor123456")
        self.staff = User.objects.create_user(username="staff", password="StaffSegura123", is_staff=True)
        self.otro = User.objects.create_user(username="otro", password="OtroSegura123")
        self.incidente = crear_incidente(self.autor, titulo="Entrada oculta", oculto_por_reportes=True)

    def test_visitante_anonimo_recibe_404(self):
        url = reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_otro_usuario_logueado_recibe_404(self):
        self.client.login(username="otro", password="OtroSegura123")
        url = reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_autor_puede_ver_su_propia_entrada_oculta(self):
        self.client.login(username="autor", password="Autor123456")
        url = reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_staff_puede_ver_entrada_oculta(self):
        self.client.login(username="staff", password="StaffSegura123")
        url = reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_no_aparece_en_el_listado_publico(self):
        response = self.client.get(reverse("incidentes:lista"))
        self.assertNotContains(response, "Entrada oculta")

    def test_boton_reportar_no_aparece_para_el_autor(self):
        self.incidente.oculto_por_reportes = False
        self.incidente.save()
        self.client.login(username="autor", password="Autor123456")
        url = reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk})
        response = self.client.get(url)
        self.assertNotContains(response, "Reportar esta entrada")

    def test_boton_reportar_aparece_para_otro_usuario_logueado(self):
        self.incidente.oculto_por_reportes = False
        self.incidente.save()
        self.client.login(username="otro", password="OtroSegura123")
        url = reverse("incidentes:detalle", kwargs={"pk": self.incidente.pk})
        response = self.client.get(url)
        self.assertContains(response, "Reportar esta entrada")
