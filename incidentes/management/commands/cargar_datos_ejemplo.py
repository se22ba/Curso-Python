from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from incidentes.models import Incidente


class Command(BaseCommand):
    help = "Carga entradas de ejemplo en el blog de seguridad vecinal"

    def handle(self, *args, **options):
        autor, creado = User.objects.get_or_create(
            username="vecino_demo",
            defaults={"email": "vecino_demo@example.com"},
        )
        if creado:
            autor.set_password("VecinoDemo123")
            autor.save()

        ahora = timezone.now()

        entradas = [
            {
                "titulo": "Robo de bicicleta en Plaza San Martín",
                "descripcion": "Sustrajeron una bicicleta que estaba atada con candado a la reja perimetral de la plaza, durante la tarde.",
                "categoria": Incidente.CATEGORIA_ROBO,
                "severidad": Incidente.SEVERIDAD_ALTA,
                "direccion": "Plaza San Martín, Retiro, CABA",
                "latitud": "-34.594900",
                "longitud": "-58.374100",
                "fecha_ocurrencia": ahora - timedelta(days=1, hours=3),
            },
            {
                "titulo": "Intento de hurto en parada de colectivo",
                "descripcion": "Un grupo de tres personas intentó sustraer pertenencias a pasajeros que esperaban el colectivo. No hubo heridos.",
                "categoria": Incidente.CATEGORIA_HURTO,
                "severidad": Incidente.SEVERIDAD_MEDIA,
                "direccion": "Av. Santa Fe y Av. Pueyrredón, CABA",
                "latitud": "-34.591500",
                "longitud": "-58.410800",
                "fecha_ocurrencia": ahora - timedelta(days=2, hours=8),
            },
            {
                "titulo": "Pintadas en frente de escuela primaria",
                "descripcion": "Aparecieron pintadas con aerosol en la fachada de la escuela durante la madrugada del fin de semana.",
                "categoria": Incidente.CATEGORIA_VANDALISMO,
                "severidad": Incidente.SEVERIDAD_BAJA,
                "direccion": "Av. Corrientes 4500, Almagro, CABA",
                "latitud": "-34.604600",
                "longitud": "-58.430700",
                "fecha_ocurrencia": ahora - timedelta(days=4),
            },
            {
                "titulo": "Persona merodeando vehículos estacionados",
                "descripcion": "Vecinos reportaron a una persona que recorría la cuadra mirando el interior de los autos estacionados, sin llegar a forzar ninguno.",
                "categoria": Incidente.CATEGORIA_SOSPECHOSO,
                "severidad": Incidente.SEVERIDAD_MEDIA,
                "direccion": "Av. Cabildo 2100, Belgrano, CABA",
                "latitud": "-34.561700",
                "longitud": "-58.456400",
                "fecha_ocurrencia": ahora - timedelta(hours=14),
            },
            {
                "titulo": "Corte de luminaria genera punto oscuro",
                "descripcion": "Varias luminarias de la cuadra están fuera de servicio desde hace una semana, generando un tramo sin iluminación nocturna.",
                "categoria": Incidente.CATEGORIA_OTRO,
                "severidad": Incidente.SEVERIDAD_BAJA,
                "direccion": "Av. Rivadavia 8200, Flores, CABA",
                "latitud": "-34.633700",
                "longitud": "-58.469100",
                "fecha_ocurrencia": ahora - timedelta(days=6, hours=5),
            },
        ]

        creadas = 0
        for datos in entradas:
            _, fue_creado = Incidente.objects.get_or_create(
                titulo=datos["titulo"],
                defaults={**datos, "autor": autor},
            )
            if fue_creado:
                creadas += 1

        self.stdout.write(self.style.SUCCESS(f"Entradas creadas: {creadas} (de {len(entradas)} en la lista)"))
        self.stdout.write(self.style.SUCCESS(f"Usuario de demo: vecino_demo / VecinoDemo123"))
