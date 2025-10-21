from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil, Tutor, Paciente, FichaClinica, AtencionMedica, ChequeoFisico, Procedimiento, Diagnostico, Insumo, InsumoUtilizado, AlertaClinica, SolicitudDatosPersonales, AntecedenteExterno, Cita, Pago, Vacuna, RegistroVacuna, Mensaje, Receta

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfiles de Usuario'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
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
admin.site.register(Mensaje)
admin.site.register(Receta)