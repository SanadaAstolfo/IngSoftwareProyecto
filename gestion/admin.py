from django.contrib import admin
from .models import Tutor, Paciente, FichaClinica, AtencionMedica, ChequeoFisico, Procedimiento

admin.site.register(Tutor)
admin.site.register(Paciente)
admin.site.register(FichaClinica)
admin.site.register(AtencionMedica)
admin.site.register(ChequeoFisico)
admin.site.register(Procedimiento)