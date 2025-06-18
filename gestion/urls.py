from django.urls import path
from . import views

urlpatterns = [
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/<int:paciente_id>/editar/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/<int:paciente_id>/borrar/', views.borrar_paciente, name='borrar_paciente'),
    path('pacientes/<int:paciente_id>/atencion/seleccionar-tipo/', views.seleccionar_tipo_atencion, name='seleccionar_tipo_atencion'),
    path('pacientes/<int:paciente_id>/atencion/nueva/<str:tipo_ficha>/', views.crear_atencion, name='crear_atencion'),
    path('pacientes/<int:paciente_id>/atencion/<int:atencion_id>/editar/', views.editar_atencion, name='editar_atencion'),
    path('pacientes/<int:paciente_id>/atencion/<int:atencion_id>/borrar/', views.borrar_atencion, name='borrar_atencion'),
    path('atencion/<int:atencion_id>/procedimiento/nuevo/', views.crear_procedimiento, name='crear_procedimiento'),
    path('atencion/<int:atencion_id>/historial/', views.ver_historial_atencion, name='ver_historial_atencion'),
]