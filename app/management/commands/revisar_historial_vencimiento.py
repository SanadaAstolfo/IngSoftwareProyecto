from django.core.management.base import BaseCommand
from django.db import models
from datetime import date, timedelta
from app.models import Paciente

class Command(BaseCommand):
    help = 'Revisa los historiales de pacientes y notifica sobre aquellos que están próximos a cumplir 5 años de antigüedad.'

    def handle(self, *args, **kwargs):
        hoy = date.today()
        fecha_limite_5_anios = hoy - timedelta(days=365 * 5)
        fecha_alerta = fecha_limite_5_anios + timedelta(days=30)

        self.stdout.write("Buscando pacientes con atenciones médicas próximas a vencer...")

        pacientes_a_revisar = Paciente.objects.annotate(
            ultima_atencion=models.Max('fichaclinica__atenciones__fecha_atencion')
        ).filter(
            ultima_atencion__date__gte=fecha_limite_5_anios,
            ultima_atencion__date__lt=fecha_alerta
        )

        if pacientes_a_revisar.exists():
            self.stdout.write(self.style.WARNING(
                f"Se encontraron {pacientes_a_revisar.count()} pacientes con historiales próximos a cumplir 5 años:"
            ))
            for paciente in pacientes_a_revisar:
                self.stdout.write(
                    f"- Paciente: {paciente.nombre} (ID: {paciente.id}), "
                    f"Última atención: {paciente.ultima_atencion.strftime('%d-%m-%Y')}"
                )

            self.stdout.write("\nEn un sistema de producción, se enviaría una notificación por correo al administrador.")

        else:
            self.stdout.write(self.style.SUCCESS("No hay historiales próximos a vencer."))