from django.urls import path, include
from . import views
from django.conf import settings

urlpatterns = [
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('pacientes/<int:paciente_id>/editar/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/<int:paciente_id>/registrar-vacuna/', views.registrar_vacuna, name='registrar_vacuna'),
    path('pacientes/<int:paciente_id>/cargar-antecedente/', views.cargar_antecedente, name='cargar_antecedente'),
    path('pacientes/<int:paciente_id>/borrar/', views.borrar_paciente, name='borrar_paciente'),
    path('pacientes/<int:paciente_id>/atencion/seleccionar-tipo/', views.seleccionar_tipo_atencion, name='seleccionar_tipo_atencion'),
    path('pacientes/<int:paciente_id>/atencion/nueva/<str:tipo_ficha>/', views.crear_atencion, name='crear_atencion'),
    path('pacientes/<int:paciente_id>/atencion/<int:atencion_id>/editar/', views.editar_atencion, name='editar_atencion'),
    path('pacientes/<int:paciente_id>/atencion/<int:atencion_id>/cerrar/', views.cerrar_atencion, name='cerrar_atencion'),
    path('pacientes/<int:paciente_id>/atencion/<int:atencion_id>/borrar/', views.borrar_atencion, name='borrar_atencion'),
    path('tutores/', views.lista_tutores, name='lista_tutores'),
    path('tutores/nuevo/', views.crear_tutor, name='crear_tutor'),
    path('tutores/mis-pacientes/', views.mis_pacientes, name='mis_pacientes'),
    path('tutores/<int:tutor_id>/', views.detalle_tutor, name='detalle_tutor'),
    path('tutores/<int:tutor_id>/registrar-pago/', views.registrar_pago_tutor, name='registrar_pago_tutor'),
    path('tutores/<int:tutor_id>/bloquear/', views.bloquear_datos_tutor, name='bloquear_datos_tutor'),
    path('atencion/<int:atencion_id>/procedimiento/nuevo/', views.crear_procedimiento, name='crear_procedimiento'),
    path('atencion/<int:atencion_id>/insumo/nuevo/', views.agregar_insumo, name='agregar_insumo'),
    path('atencion/<int:atencion_id>/receta/nuevo/', views.agregar_receta, name='agregar_receta'),
    path('atencion/<int:atencion_id>/adjuntar/', views.adjuntar_documento, name='adjuntar_documento'),
    path('atencion/<int:atencion_id>/historial/', views.ver_historial_atencion, name='ver_historial_atencion'),
    path('atencion/<int:atencion_id>/ficha-pdf/', views.generar_pdf_ficha, name='generar_pdf_ficha'),
    path('atencion/<int:atencion_id>/epicrisis-pdf/', views.generar_pdf_epicrisis, name='generar_pdf_epicrisis'),
    path('citas/', views.calendario_citas, name='calendario_citas'),
    path('citas/nueva/', views.crear_cita, name='crear_cita'),
    path('citas/<int:cita_id>/editar/', views.editar_cita, name='editar_cita'),
    path('citas/<int:cita_id>/cancelar/', views.cancelar_cita, name='cancelar_cita'),
    path('citas/<int:cita_id>/registrar-abono/', views.registrar_abono, name='registrar_abono'),
    path('pagos/<int:pago_id>/comprobante/', views.ver_comprobante, name='ver_comprobante'),
    path('mi-perfil/editar/', views.editar_mi_perfil, name='editar_mi_perfil'),
    path('mensajes/', views.bandeja_entrada, name='bandeja_entrada'),
    path('mensajes/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path('mensajes/<int:mensaje_id>/', views.ver_mensaje, name='ver_mensaje'),
    path('receta/<int:receta_id>/pdf/', views.generar_pdf_receta, name='generar_pdf_receta'),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls"))
        ]