from django.core.management.base import BaseCommand
from datetime import date, timedelta
from app.models import AtencionMedica

class Command(BaseCommand):
    help = 'Busca y elimina los registros de atención médica con más de 5 años de antigüedad.'

    def handle(self, *args, **kwargs):
        fecha_limite = date.today() - timedelta(days=365 * 5)
        
        self.stdout.write(f"Buscando registros anteriores a {fecha_limite.strftime('%Y-%m-%d')}...")

        atenciones_antiguas = AtencionMedica.objects.filter(fecha_atencion__date__lt=fecha_limite)

        cantidad_a_borrar = atenciones_antiguas.count()

        if cantidad_a_borrar > 0:
            self.stdout.write(self.style.WARNING(f"Se encontraron {cantidad_a_borrar} registros para eliminar."))
            
            atenciones_antiguas.delete()
            
            self.stdout.write(self.style.SUCCESS(f"Se eliminaron exitosamente {cantidad_a_borrar} registros antiguos."))
        else:
            self.stdout.write(self.style.SUCCESS("No se encontraron registros para eliminar. La base de datos está actualizada."))
