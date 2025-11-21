from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
# WeasyPrint se importa dinámicamente donde se necesita
from datetime import date, datetime
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
import pytz
import os
from .models import Paciente, Tutor, Perfil, FichaClinica, AtencionMedica, ChequeoFisico, DocumentoAdjunto, InsumoUtilizado, Cita, Pago, RegistroVacuna, Mensaje, Receta, SolicitudDatosPersonales
from .forms import PacienteForm, TutorForm, AtencionGeneralForm, ChequeoFisicoForm, ProcedimientoForm, AtencionHospitalizacionForm, DocumentoAdjuntoForm, InsumoUtilizadoForm, AntecedenteExternoForm, CitaForm, PagoForm, RegistroVacunaForm, CustomAuthenticationForm, MiPerfilForm, MensajeForm, RecetaForm, SolicitudDatosPersonalesForm
from .decorators import group_required

def es_personal(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=['Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria']).exists() or user.is_superuser

def es_tutor(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='Tutor').exists()

def portal_view(request):
    return render(request, 'portal.html')

class CustomLoginView(auth_views.LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'

class TutorLoginView(auth_views.LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login_tutor.html'
    
    def get_success_url(self):
        return '/tutores/mis-pacientes/'

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def lista_pacientes(request):
    queryset = Paciente.objects.all()

    nombre_query = request.GET.get('nombre')
    diagnostico_query = request.GET.get('diagnostico')
    fecha_query = request.GET.get('fecha')

    if nombre_query:
        # Búsqueda mejorada: incluye nombre del paciente, nombre del tutor y RUT del tutor
        queryset = queryset.filter(
            Q(nombre__icontains=nombre_query) |
            Q(tutor__nombre_completo__icontains=nombre_query) |
            Q(tutor__rut__icontains=nombre_query)
        )

    if diagnostico_query:
        queryset = queryset.filter(atenciones__diagnostico__icontains=diagnostico_query)

    if fecha_query:
        queryset = queryset.filter(atenciones__fecha_atencion__date=fecha_query)

    pacientes_filtrados = queryset.distinct().order_by('nombre')

    contexto = {
        'pacientes': pacientes_filtrados,
    }
    return render(request, 'gestion/lista_pacientes.html', contexto)

@login_required
def detalle_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    usuario_actual = request.user
    es_personal_usuario = es_personal(usuario_actual)
    es_propietario_tutor = False
    if es_tutor(usuario_actual):
        try:
            tutor_del_usuario = Tutor.objects.get(user=usuario_actual)
            if paciente.tutor == tutor_del_usuario:
                es_propietario_tutor = True
        except Tutor.DoesNotExist:
             messages.warning(request, "Tu perfil de tutor no está completamente configurado.")
             pass

    if not es_personal_usuario and not es_propietario_tutor:
        messages.error(request, "No tienes permiso para ver la ficha de este paciente.")
        return redirect('mis_pacientes' if es_tutor(usuario_actual) else 'portal')

    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(paciente).id,
        object_id=paciente.id,
        object_repr=str(paciente),
        action_flag=CHANGE,
        change_message="Acceso a la ficha del paciente."
    )
    try:
        ficha = FichaClinica.objects.get(paciente=paciente)
        atenciones = AtencionMedica.objects.filter(ficha_clinica=ficha).order_by('-fecha_atencion')
    except FichaClinica.DoesNotExist:
        ficha = None
        atenciones = []

    contexto = {
        'paciente': paciente,
        'ficha': ficha,
        'atenciones': atenciones,
        'today': date.today(),
        'es_personal_usuario': es_personal_usuario,
        'es_propietario_tutor': es_propietario_tutor
    }
    return render(request, 'gestion/detalle_paciente.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()

    contexto = {
        'form': form,
        'titulo': 'Registrar Nuevo Paciente',
        'boton_texto': 'Guardar Paciente'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, request.FILES, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)

    contexto = {
        'form': form,
        'titulo': f'Editar a {paciente.nombre}',
        'boton_texto': 'Actualizar Paciente',
        'object': paciente
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def borrar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)

    if request.method == 'POST':
        paciente.delete()
        return redirect('lista_pacientes')

    return render(request, 'gestion/borrar_paciente.html', {'paciente': paciente})

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def seleccionar_tipo_atencion(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    return render(request, 'gestion/seleccionar_tipo_atencion.html', {'paciente': paciente})

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def crear_atencion(request, paciente_id, tipo_ficha):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    ficha, created = FichaClinica.objects.get_or_create(paciente=paciente)

    if tipo_ficha == 'hospitalizacion':
        FormClass = AtencionHospitalizacionForm
        titulo = f'Nueva Hospitalización para {paciente.nombre}'
    else:
        FormClass = AtencionGeneralForm
        titulo = f'Nueva Consulta General para {paciente.nombre}'

    if request.method == 'POST':
        atencion_form = FormClass(request.POST)
        chequeo_form = ChequeoFisicoForm(request.POST)

        if atencion_form.is_valid() and chequeo_form.is_valid():
            atencion = atencion_form.save(commit=False)
            atencion.ficha_clinica = ficha
            if request.user.is_authenticated:
                atencion.veterinario = request.user
            atencion.save()
            atencion_form.save_m2m()

            chequeo = chequeo_form.save(commit=False)
            chequeo.atencion_medica = atencion
            chequeo.save()
            
            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        atencion_form = FormClass()
        chequeo_form = ChequeoFisicoForm()

    contexto = {
        'atencion_form': atencion_form,
        'chequeo_form': chequeo_form,
        'paciente': paciente,
        'titulo': titulo,
    }
    return render(request, 'gestion/atencion_form.html', contexto)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def editar_atencion(request, paciente_id, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    paciente = get_object_or_404(Paciente, pk=paciente_id)

    if atencion.esta_cerrada:
        return redirect('detalle_paciente', paciente_id=paciente_id)

    try:
        chequeo = atencion.chequeo
    except ChequeoFisico.DoesNotExist:
        chequeo = None

    if request.method == 'POST':
        atencion_form = AtencionGeneralForm(request.POST, instance=atencion)
        chequeo_form = ChequeoFisicoForm(request.POST, instance=chequeo)

        if atencion_form.is_valid() and chequeo_form.is_valid():
            atencion_form.save()

            chequeo_guardado = chequeo_form.save(commit=False)
            chequeo_guardado.atencion_medica = atencion
            chequeo_guardado.save()

            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        atencion_form = AtencionGeneralForm(instance=atencion)
        chequeo_form = ChequeoFisicoForm(instance=chequeo)

    contexto = {
        'atencion_form': atencion_form,
        'chequeo_form': chequeo_form,
        'paciente': paciente,
        'titulo': f'Editando Atención del {atencion.fecha_atencion.strftime("%d-%m-%Y")}',
    }
    return render(request, 'gestion/atencion_form.html', contexto)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def borrar_atencion(request, paciente_id, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)

    if request.method == 'POST':
        atencion.delete()
        return redirect('detalle_paciente', paciente_id=paciente_id)

    contexto = {
        'atencion': atencion,
        'paciente_id': paciente_id
    }
    return render(request, 'gestion/borrar_atencion.html', contexto)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def crear_procedimiento(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)

    if request.method == 'POST':
        form = ProcedimientoForm(request.POST)
        if form.is_valid():
            procedimiento = form.save(commit=False)
            procedimiento.atencion_medica = atencion
            procedimiento.save()
            return redirect('detalle_paciente', paciente_id=atencion.ficha_clinica.paciente.id)
    else:
        form = ProcedimientoForm()

    contexto = {
        'form': form,
        'atencion': atencion,
        'titulo': 'Añadir Nuevo Procedimiento',
        'boton_texto': 'Guardar Procedimiento'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def ver_historial_atencion(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    historial = atencion.history.all()
    contexto = {
        'atencion': atencion,
        'historial': historial
    }
    return render(request, 'gestion/historial_atencion.html', contexto)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def adjuntar_documento(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    if request.method == 'POST':
        form = DocumentoAdjuntoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.atencion_medica = atencion
            documento.save()
            return redirect('detalle_paciente', paciente_id=atencion.ficha_clinica.paciente.id)
    else:
        form = DocumentoAdjuntoForm()
    contexto = {
        'form': form,
        'atencion': atencion,
        'titulo': 'Adjuntar Documento a la Atención',
        'boton_texto': 'Subir Documento'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def cerrar_atencion(request, paciente_id, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    atencion.esta_cerrada = True
    atencion.save()
    return redirect('detalle_paciente', paciente_id=paciente_id)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def lista_tutores(request):
    tutores = Tutor.objects.all().order_by('nombre_completo')
    contexto = {
        'tutores': tutores,
    }
    return render(request, 'gestion/lista_tutores.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def detalle_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(tutor).id,
        object_id=tutor.id,
        object_repr=str(tutor),
        action_flag=CHANGE,
        change_message="Acceso a los datos del tutor."
    )
    pacientes = tutor.pacientes.all()
    contexto = {
        'tutor': tutor,
        'pacientes': pacientes,
    }
    return render(request, 'gestion/detalle_tutor.html', contexto)

@login_required
@group_required('Tutor')
def mis_pacientes(request):
    usuario = request.user
    tutor = None
    
    # Primero intentar por RUT del perfil
    try:
        if hasattr(usuario, 'perfil') and usuario.perfil is not None:
            perfil = usuario.perfil
            tutor = Tutor.objects.filter(rut=perfil.rut).first()
    except Exception:
        tutor = None

    # Si no se encontró, intentar por email
    if tutor is None:
        tutor = Tutor.objects.filter(email=usuario.email).first()

    if tutor is None:
        contexto = {'mensaje': 'No hay un Tutor asociado a tu cuenta. Contacta al administrador.'}
        return render(request, 'gestion/mis_pacientes.html', contexto)

    pacientes = tutor.pacientes.all().order_by('nombre')
    contexto = {
        'tutor': tutor,
        'pacientes': pacientes,
    }
    return render(request, 'gestion/mis_pacientes.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def crear_tutor(request):
    if request.method == 'POST':
        form = TutorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_tutores')
    else:
        form = TutorForm()

    contexto = {
        'form': form,
        'titulo': 'Registrar Nuevo Tutor',
        'boton_texto': 'Guardar Tutor'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def agregar_insumo(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    if request.method == 'POST':
        form = InsumoUtilizadoForm(request.POST)
        if form.is_valid():
            insumo_utilizado = form.save(commit=False)
            insumo_utilizado.atencion_medica = atencion
            insumo_utilizado.save()
            return redirect('detalle_paciente', paciente_id=atencion.ficha_clinica.paciente.id)
    else:
        form = InsumoUtilizadoForm()
    
    contexto = {
        'form': form,
        'atencion': atencion,
        'titulo': 'Agregar Insumo Utilizado',
        'boton_texto': 'Agregar Insumo'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def bloquear_datos_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, id=tutor_id)
    tutor.datos_bloqueados = True
    tutor.save()
    return redirect('detalle_tutor', tutor_id=tutor.id)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def cargar_antecedente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    if request.method == 'POST':
        form = AntecedenteExternoForm(request.POST, request.FILES)
        if form.is_valid():
            antecedente = form.save(commit=False)
            antecedente.paciente = paciente
            antecedente.save()
            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        form = AntecedenteExternoForm()

    contexto = {
        'form': form,
        'paciente': paciente,
        'titulo': f'Cargar Antecedente Externo para {paciente.nombre}',
        'boton_texto': 'Cargar Antecedente'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def calendario_citas(request):
    titulo = "Calendario de Citas"
    fecha_filtro = request.GET.get('fecha')
    filtro_hoy = request.GET.get('hoy')

    if filtro_hoy:
        santiago_tz = pytz.timezone('America/Santiago')
        hoy_santiago = timezone.now().astimezone(santiago_tz).date()

        queryset = Cita.objects.filter(fecha_hora__date=hoy_santiago).order_by('fecha_hora')
        titulo = f"Citas para Hoy ({hoy_santiago.strftime('%d-%m-%Y')})"
    
    elif fecha_filtro:
        try:
            fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            queryset = Cita.objects.filter(fecha_hora__date=fecha_obj, estado__in=['Agendada', 'Confirmada']).order_by('fecha_hora')
            titulo = f"Citas para el {fecha_obj.strftime('%d-%m-%Y')}"
        except ValueError:
            queryset = Cita.objects.none()
    else:
        queryset = Cita.objects.filter(estado__in=['Agendada', 'Confirmada']).order_by('fecha_hora')

    contexto = {
        'citas': queryset,
        'titulo': titulo,
    }
    return render(request, 'gestion/calendario.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def crear_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calendario_citas')
    else:
        form = CitaForm()
    
    contexto = {
        'form': form,
        'titulo': 'Agendar Nueva Cita',
        'boton_texto': 'Agendar Cita'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            return redirect('calendario_citas')
    else:
        form = CitaForm(instance=cita)

    contexto = {
        'form': form,
        'titulo': f'Editar Cita para {cita.paciente.nombre}',
        'boton_texto': 'Actualizar Cita'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    if request.method == 'POST':
        cita.estado = 'Cancelada'
        cita.save()
        return redirect('calendario_citas')
    
    return render(request, 'gestion/confirmar_cancelacion.html', {'cita': cita})

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def registrar_abono(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.tutor = cita.paciente.tutor
            pago.cita = cita
            pago.save()
            return redirect('calendario_citas')
    else:
        form = PagoForm()

    contexto = {
        'form': form,
        'cita': cita,
        'titulo': f'Registrar Abono para Cita de {cita.paciente.nombre}',
        'boton_texto': 'Registrar Abono'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def registrar_vacuna(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    if request.method == 'POST':
        form = RegistroVacunaForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.paciente = paciente
            registro.save()
            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        form = RegistroVacunaForm()

    contexto = {
        'form': form,
        'paciente': paciente,
        'titulo': f'Registrar Vacuna para {paciente.nombre}',
        'boton_texto': 'Registrar Vacuna'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def registrar_pago_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.tutor = tutor
            pago.save()
            return redirect('detalle_tutor', tutor_id=tutor.id)
    else:
        form = PagoForm()

    contexto = {
        'form': form,
        'tutor': tutor,
        'titulo': f'Registrar Pago para {tutor.nombre_completo}',
        'boton_texto': 'Registrar Pago'
    }
    return render(request, 'gestion/form.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria', 'Tutor')
def ver_comprobante(request, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id)
    
    # Verificar permisos: El personal puede ver todos, los tutores solo los suyos
    if es_tutor(request.user):
        try:
            tutor_usuario = Tutor.objects.get(email=request.user.email)
            if pago.tutor != tutor_usuario:
                messages.error(request, "No tienes permiso para ver este comprobante.")
                return redirect('mis_pacientes')
        except Tutor.DoesNotExist:
            messages.error(request, "No se encontró tu perfil de tutor.")
            return redirect('portal')
    
    contexto = {
        'pago': pago,
    }
    return render(request, 'gestion/comprobante_pago.html', contexto)

@login_required
@group_required('Tutor')
def editar_mi_perfil(request):
    """
    Vista para que un Tutor edite su propia información de perfil.
    """
    user = request.user
    titulo = "Editar Mi Perfil"

    # Intentamos obtener el Perfil y el Tutor asociados al usuario logueado
    try:
        perfil = user.perfil
        # Asumiendo que hay una relación OneToOne o ForeignKey desde Tutor a User
        tutor = Tutor.objects.get(user=user) 
    except (ObjectDoesNotExist, AttributeError):
        messages.error(request, "No se encontró tu perfil de tutor. Contacta al administrador.")
        return redirect('portal') # O a donde corresponda si falla

    if request.method == 'POST':
        form = MiPerfilForm(request.POST, user_instance=user, tutor_instance=tutor, perfil_instance=perfil)
        if form.is_valid():
            # Actualizar datos del User
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            # Actualizar datos del Tutor
            tutor.telefono = form.cleaned_data['telefono']
            tutor.direccion = form.cleaned_data['direccion']
            tutor.save()

            # Actualizar datos del Perfil
            perfil.canal_notificacion_preferido = form.cleaned_data['canal_notificacion_preferido']
            perfil.save()

            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('editar_mi_perfil') # Redirige a la misma página para ver los cambios
    else:
        form = MiPerfilForm(user_instance=user, tutor_instance=tutor, perfil_instance=perfil)

    contexto = {
        'form': form,
        'titulo': titulo
    }
    # Usaremos la plantilla genérica form.html por ahora, pero podemos crear una específica
    return render(request, 'gestion/form_editar_perfil.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def bandeja_entrada(request):
    mensajes_recibidos = Mensaje.objects.filter(destinatario=request.user)
    mensajes_enviados = Mensaje.objects.filter(remitente=request.user)

    contexto = {
        'mensajes_recibidos': mensajes_recibidos,
        'mensajes_enviados': mensajes_enviados,
        'titulo': "Bandeja de Mensajes"
    }
    return render(request, 'gestion/bandeja_entrada.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def ver_mensaje(request, mensaje_id):
    mensaje = get_object_or_404(Mensaje, id=mensaje_id, destinatario=request.user) # Solo puede ver si es destinatario

    # Marcar como leído si no lo estaba
    if not mensaje.leido:
        mensaje.leido = True
        mensaje.save()

    contexto = {
        'mensaje': mensaje,
        'titulo': f"Mensaje: {mensaje.asunto}"
    }
    return render(request, 'gestion/mensaje_detalle.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def enviar_mensaje(request):
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.remitente = request.user
            mensaje.save()
            messages.success(request, 'Mensaje enviado correctamente.')
            return redirect('bandeja_entrada')
    else:
        form = MensajeForm()

    contexto = {
        'form': form,
        'titulo': "Enviar Nuevo Mensaje"
    }
    # Reutilizamos la plantilla genérica, adaptándola si es necesario
    return render(request, 'gestion/form_enviar_mensaje.html', contexto)

@login_required
@group_required('Veterinario', 'Veterinario Especialista')
def agregar_receta(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    paciente = atencion.ficha_clinica.paciente
    try:
        receta_instance = Receta.objects.get(atencion_medica=atencion)
        titulo = f"Editar Receta para Atención de {paciente.nombre}"
    except Receta.DoesNotExist:
        receta_instance = None
        titulo = f"Agregar Receta para Atención de {paciente.nombre}"

    if request.method == 'POST':
        form = RecetaForm(request.POST, instance=receta_instance)
        if form.is_valid():
            receta = form.save(commit=False)
            receta.atencion_medica = atencion
            if not form.cleaned_data.get('prescripcion'):
                if receta_instance:
                    receta_instance.delete()
                    messages.info(request, 'Receta eliminada ya que el campo estaba vacío.')
                else:
                     messages.warning(request, 'No se guardó la receta porque el campo estaba vacío.')
            else:
                receta.save()
                messages.success(request, f'Receta {"actualizada" if receta_instance else "agregada"} correctamente.')

            return redirect('detalle_paciente', paciente_id=paciente.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RecetaForm(instance=receta_instance)

    contexto = {
        'form': form,
        'atencion': atencion,
        'paciente': paciente,
        'titulo': titulo
    }
    return render(request, 'gestion/receta_form.html', contexto)

def generar_pdf_receta(request, receta_id):
    from weasyprint import HTML
    
    receta = get_object_or_404(Receta, pk=receta_id)
    usuario_actual = request.user
    es_personal_usuario = es_personal(usuario_actual)
    es_propietario_tutor_receta = False

    if es_tutor(usuario_actual):
        try:
            tutor_del_usuario = Tutor.objects.get(user=usuario_actual)
            if receta.atencion_medica.ficha_clinica.paciente.tutor == tutor_del_usuario:
                es_propietario_tutor_receta = True
        except Tutor.DoesNotExist: pass

    if not es_personal_usuario and not es_propietario_tutor_receta:
        messages.error(request, "No tienes permiso para ver esta receta.")
        return redirect('mis_pacientes' if es_tutor(usuario_actual) else 'portal')

    if es_propietario_tutor_receta and receta.impresa:
        messages.error(request, "Esta receta ya ha sido generada/impresa una vez.")
        return HttpResponseForbidden("Receta ya generada.")

    firma_url = None
    veterinario = receta.atencion_medica.veterinario
    if veterinario:
        try:
            perfil_vet = veterinario.perfil
            if perfil_vet and perfil_vet.firma:
                firma_url = request.build_absolute_uri(perfil_vet.firma.url)
        except ObjectDoesNotExist: pass
        except AttributeError: messages.warning(request, "Error perfil vet. firma.")

    contexto_pdf = {
        'receta': receta,
        'firma_url': firma_url,
    }
    html_string = render_to_string('gestion/pdfs/pdf_receta.html', contexto_pdf)
    html = HTML(string=html_string, base_url=request.build_absolute_uri()) 
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receta_{receta.atencion_medica.ficha_clinica.paciente.nombre}_{receta.id}.pdf"'

    if es_propietario_tutor_receta:
        receta.impresa = True
        receta.save()

    return response

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def generar_pdf_ficha(request, atencion_id):
    from weasyprint import HTML
    
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    foto_url = None
    paciente = atencion.ficha_clinica.paciente
    if paciente.foto:
        foto_url = request.build_absolute_uri(paciente.foto.url)

    contexto_pdf = {
        'atencion': atencion,
        'foto_url': foto_url
    }
    
    html_string = render_to_string('gestion/pdfs/pdf_ficha_clinica.html', contexto_pdf)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ficha_{atencion.ficha_clinica.paciente.nombre}_{atencion.id}.pdf"'
    return response

@login_required
def generar_pdf_epicrisis(request, atencion_id):
    from weasyprint import HTML
    
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    usuario_actual = request.user
    es_personal_usuario = es_personal(usuario_actual)
    es_propietario_tutor_epicrisis = False

    if es_tutor(usuario_actual):
        try:
            tutor_del_usuario = Tutor.objects.get(user=usuario_actual)
            if atencion.ficha_clinica.paciente.tutor == tutor_del_usuario:
                es_propietario_tutor_epicrisis = True
        except Tutor.DoesNotExist: pass

    if not es_personal_usuario and not es_propietario_tutor_epicrisis:
        messages.error(request, "No tienes permiso para ver esta epicrisis.")
        return redirect('mis_pacientes' if es_tutor(usuario_actual) else 'portal')

    firma_url = None
    veterinario = atencion.veterinario
    if veterinario:
        try:
            perfil_vet = veterinario.perfil
            if perfil_vet and perfil_vet.firma:
                firma_url = request.build_absolute_uri(perfil_vet.firma.url)
        except ObjectDoesNotExist: pass
        except AttributeError: messages.warning(request, "Error perfil vet. firma.")

    contexto_pdf = {
        'atencion': atencion,
        'firma_url': firma_url
    }

    html_string = render_to_string('gestion/pdfs/pdf_epicrisis.html', contexto_pdf)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="epicrisis_{atencion.ficha_clinica.paciente.nombre}_{atencion.id}.pdf"'
    return response

# Vista para gestión de datos personales (CU 30)
@login_required
@group_required('Tutor')
def solicitar_gestion_datos(request):
    try:
        tutor = Tutor.objects.get(email=request.user.email)
    except Tutor.DoesNotExist:
        messages.error(request, "No se encontró un perfil de tutor asociado a tu cuenta.")
        return redirect('portal')
    
    if request.method == 'POST':
        form = SolicitudDatosPersonalesForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.tutor = tutor
            solicitud.save()
            messages.success(request, f"Tu solicitud de {solicitud.get_tipo_solicitud_display()} ha sido enviada. Será procesada por el personal.")
            return redirect('mis_solicitudes_datos')
    else:
        form = SolicitudDatosPersonalesForm()
    
    contexto = {
        'form': form,
        'titulo': 'Solicitar Gestión de Datos Personales'
    }
    return render(request, 'gestion/solicitar_gestion_datos.html', contexto)

@login_required
@group_required('Tutor')
def mis_solicitudes_datos(request):
    try:
        tutor = Tutor.objects.get(email=request.user.email)
    except Tutor.DoesNotExist:
        messages.error(request, "No se encontró un perfil de tutor asociado a tu cuenta.")
        return redirect('portal')
    
    solicitudes = SolicitudDatosPersonales.objects.filter(tutor=tutor).order_by('-fecha_solicitud')
    
    contexto = {
        'solicitudes': solicitudes,
        'titulo': 'Mis Solicitudes de Gestión de Datos'
    }
    return render(request, 'gestion/mis_solicitudes_datos.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def lista_solicitudes_datos(request):
    solicitudes = SolicitudDatosPersonales.objects.all().order_by('-fecha_solicitud')
    
    # Filtrar por estado si se solicita
    estado_filtro = request.GET.get('estado')
    if estado_filtro:
        solicitudes = solicitudes.filter(estado=estado_filtro)
    
    contexto = {
        'solicitudes': solicitudes,
        'titulo': 'Solicitudes de Gestión de Datos Personales'
    }
    return render(request, 'gestion/lista_solicitudes_datos.html', contexto)

@login_required
@group_required('Administrador', 'Veterinario', 'Veterinario Especialista', 'Secretaria')
def gestionar_solicitud_datos(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudDatosPersonales, pk=solicitud_id)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        resolucion = request.POST.get('resolucion', '')
        
        if accion == 'aprobar':
            solicitud.estado = 'Aprobada'
            solicitud.resolucion = resolucion
            solicitud.usuario_responsable = request.user
            solicitud.save()
            messages.success(request, "Solicitud aprobada exitosamente.")
        elif accion == 'rechazar':
            solicitud.estado = 'Rechazada'
            solicitud.resolucion = resolucion
            solicitud.usuario_responsable = request.user
            solicitud.save()
            messages.success(request, "Solicitud rechazada.")
        
        return redirect('lista_solicitudes_datos')
    
    contexto = {
        'solicitud': solicitud,
        'titulo': f'Gestionar Solicitud #{solicitud.id}'
    }
    return render(request, 'gestion/gestionar_solicitud_datos.html', contexto)