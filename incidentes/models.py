from django.conf import settings
from django.db import models
from django.urls import reverse


class Incidente(models.Model):
    CATEGORIA_ROBO = "robo"
    CATEGORIA_HURTO = "hurto"
    CATEGORIA_VANDALISMO = "vandalismo"
    CATEGORIA_SOSPECHOSO = "sospechoso"
    CATEGORIA_OTRO = "otro"

    CATEGORIA_CHOICES = [
        (CATEGORIA_ROBO, "Robo"),
        (CATEGORIA_HURTO, "Hurto"),
        (CATEGORIA_VANDALISMO, "Vandalismo"),
        (CATEGORIA_SOSPECHOSO, "Actividad sospechosa"),
        (CATEGORIA_OTRO, "Otro"),
    ]

    SEVERIDAD_BAJA = "baja"
    SEVERIDAD_MEDIA = "media"
    SEVERIDAD_ALTA = "alta"

    SEVERIDAD_CHOICES = [
        (SEVERIDAD_BAJA, "Baja"),
        (SEVERIDAD_MEDIA, "Media"),
        (SEVERIDAD_ALTA, "Alta"),
    ]

    titulo = models.CharField(max_length=140)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    severidad = models.CharField(max_length=10, choices=SEVERIDAD_CHOICES, default=SEVERIDAD_MEDIA)
    direccion = models.CharField(max_length=200)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    fecha_ocurrencia = models.DateTimeField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="incidentes")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_ocurrencia"]
        verbose_name = "Entrada del blog"
        verbose_name_plural = "Entradas del blog"

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.titulo}"

    def get_absolute_url(self):
        return reverse("incidentes:detalle", kwargs={"pk": self.pk})
