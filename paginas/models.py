from django.db import models


class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self):
        return f"{self.asunto} ({self.nombre})"
