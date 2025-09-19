from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone, formats
from datetime import timedelta
from app.models import Cita

class Command(BaseCommand):
    help = 'Busca citas agendadas para mañana y envía recordatorios por correo a los tutores.'

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()
        maniana = hoy + timedelta(days=1)
        
        self.stdout.write(f"Buscando citas para mañana ({maniana.strftime('%d-%m-%Y')})...")

        citas_de_maniana = Cita.objects.filter(
            fecha_hora__date=maniana,
            estado__in=['Agendada', 'Confirmada']
        )

        if not citas_de_maniana.exists():
            self.stdout.write(self.style.SUCCESS("No hay citas agendadas para mañana."))
            return

        self.stdout.write(self.style.WARNING(f"Se encontraron {citas_de_maniana.count()} citas. Enviando correos..."))

        for cita in citas_de_maniana:
            paciente = cita.paciente
            tutor = paciente.tutor
            asunto = f"Recordatorio de Cita para {paciente.nombre}"
            fecha_formateada = formats.date_format(cita.fecha_hora, r"d \d\e F \d\e Y \a \l\a\s H:i \h\r\s.")

            mensaje = (
                f"Hola {tutor.nombre_completo},\n\n"
                f"Te recordamos que tienes una cita agendada para tu mascota {paciente.nombre} mañana, {fecha_formateada}\n\n"
                f"Motivo de la cita: {cita.motivo}\n\n"
                f"Si necesitas reagendar o cancelar, por favor contáctanos.\n\n"
                f"Saludos cordiales,\n"
                f"El equipo de la Clínica Entre Patitas"
            )
            
            try:
                send_mail(
                    asunto,
                    mensaje,
                    None,
                    [tutor.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"Correo enviado a {tutor.email} para la cita de {paciente.nombre}."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al enviar correo a {tutor.email}: {e}"))