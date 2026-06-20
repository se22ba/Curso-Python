from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    biografia = models.TextField(max_length=500, blank=True)
    barrio = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to="avatares/", blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_automaticamente(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
