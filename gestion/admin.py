from django.contrib import admin
from .models import Tutor, Paciente, FichaClinica, AtencionMedica, ChequeoFisico, Procedimiento, Diagnostico, Insumo, InsumoUtilizado, AlertaClinica, SolicitudDatosPersonales, AntecedenteExterno, Cita, Pago, Vacuna, RegistroVacuna

admin.site.register(Tutor)
admin.site.register(Paciente)
admin.site.register(FichaClinica)
admin.site.register(AtencionMedica)
admin.site.register(ChequeoFisico)
admin.site.register(Procedimiento)
admin.site.register(Diagnostico)
admin.site.register(Insumo)
admin.site.register(InsumoUtilizado)
admin.site.register(AlertaClinica)
admin.site.register(SolicitudDatosPersonales)
admin.site.register(AntecedenteExterno)
admin.site.register(Cita)
admin.site.register(Pago)
admin.site.register(Vacuna)
admin.site.register(RegistroVacuna)