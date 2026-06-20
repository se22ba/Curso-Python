from django.test import TestCase
from django.urls import reverse

from .models import MensajeContacto
from .forms import MensajeContactoForm


class MensajeContactoModelTest(TestCase):
    def test_str_incluye_asunto_y_nombre(self):
        mensaje = MensajeContacto.objects.create(
            nombre="Juan",
            email="juan@example.com",
            asunto="Consulta",
            mensaje="Mensaje de prueba con longitud suficiente.",
        )
        self.assertEqual(str(mensaje), "Consulta (Juan)")

    def test_leido_por_defecto_false(self):
        mensaje = MensajeContacto.objects.create(
            nombre="Juan",
            email="juan@example.com",
            asunto="Consulta",
            mensaje="Mensaje de prueba con longitud suficiente.",
        )
        self.assertFalse(mensaje.leido)


class MensajeContactoFormTest(TestCase):
    def datos_validos(self):
        return {
            "nombre": "Juan",
            "email": "juan@example.com",
            "asunto": "Consulta",
            "mensaje": "Mensaje de prueba con longitud suficiente.",
        }

    def test_form_valido_con_datos_correctos(self):
        form = MensajeContactoForm(data=self.datos_validos())
        self.assertTrue(form.is_valid())

    def test_form_invalido_con_email_malformado(self):
        datos = self.datos_validos()
        datos["email"] = "no-es-un-email"
        form = MensajeContactoForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_invalido_con_mensaje_muy_corto(self):
        datos = self.datos_validos()
        datos["mensaje"] = "corto"
        form = MensajeContactoForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn("mensaje", form.errors)

    def test_form_invalido_con_mensaje_solo_espacios(self):
        datos = self.datos_validos()
        datos["mensaje"] = "             "
        form = MensajeContactoForm(data=datos)
        self.assertFalse(form.is_valid())


class AcercaDeViewTest(TestCase):
    def test_pagina_es_publica_y_responde_200(self):
        response = self.client.get(reverse("paginas:acerca_de"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "blog")


class ContactoViewTest(TestCase):
    def test_get_muestra_formulario(self):
        response = self.client.get(reverse("paginas:contacto"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enviar mensaje")

    def test_post_valido_persiste_mensaje_y_redirige(self):
        response = self.client.post(reverse("paginas:contacto"), {
            "nombre": "Juan",
            "email": "juan@example.com",
            "asunto": "Consulta",
            "mensaje": "Mensaje de prueba con longitud suficiente.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MensajeContacto.objects.filter(asunto="Consulta").exists())

    def test_post_invalido_no_persiste(self):
        response = self.client.post(reverse("paginas:contacto"), {
            "nombre": "Juan",
            "email": "no-es-un-email",
            "asunto": "Consulta",
            "mensaje": "corto",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(MensajeContacto.objects.exists())

    def test_no_requiere_login(self):
        response = self.client.get(reverse("paginas:contacto"))
        self.assertEqual(response.status_code, 200)
