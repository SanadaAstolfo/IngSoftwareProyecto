from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from .decorators import group_required
from datetime import date, datetime
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
import pytz
import os
from .models import Paciente, Tutor, Perfil, FichaClinica, AtencionMedica, ChequeoFisico, DocumentoAdjunto, Diagnostico, InsumoUtilizado, Cita, Pago, RegistroVacuna, Mensaje, Receta
from .forms import PacienteForm, TutorForm, AtencionGeneralForm, ChequeoFisicoForm, ProcedimientoForm, AtencionHospitalizacionForm, DocumentoAdjuntoForm, InsumoUtilizadoForm, AntecedenteExternoForm, CitaForm, PagoForm, RegistroVacunaForm, CustomAuthenticationForm, MiPerfilForm, MensajeForm, RecetaForm

def es_personal(user):
    return hasattr(user, 'perfil') and user.perfil.rol in ['ADMIN', 'VET', 'ESP', 'SECRETARIA']

def portal_view(request):
    return render(request, 'portal.html')

class CustomLoginView(auth_views.LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'

@login_required
def lista_pacientes(request):
    queryset = Paciente.objects.all()

    nombre_query = request.GET.get('nombre')
    diagnostico_query = request.GET.get('diagnostico')
    fecha_query = request.GET.get('fecha')

    if nombre_query:
        queryset = queryset.filter(nombre__icontains=nombre_query)

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
    }
    return render(request, 'gestion/detalle_paciente.html', contexto)

@login_required
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
def borrar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)

    if request.method == 'POST':
        paciente.delete()
        return redirect('lista_pacientes')

    return render(request, 'gestion/borrar_paciente.html', {'paciente': paciente})

@login_required
def seleccionar_tipo_atencion(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    return render(request, 'gestion/seleccionar_tipo_atencion.html', {'paciente': paciente})

@login_required
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
def ver_historial_atencion(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    historial = atencion.history.all()
    contexto = {
        'atencion': atencion,
        'historial': historial
    }
    return render(request, 'gestion/historial_atencion.html', contexto)

@login_required
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
def cerrar_atencion(request, paciente_id, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    atencion.esta_cerrada = True
    atencion.save()
    return redirect('detalle_paciente', paciente_id=paciente_id)

@login_required
def lista_tutores(request):
    tutores = Tutor.objects.all().order_by('nombre_completo')
    contexto = {
        'tutores': tutores,
    }
    return render(request, 'gestion/lista_tutores.html', contexto)

@login_required
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
def mis_pacientes(request):
    """Lista de pacientes para el tutor autenticado (Caso de Uso 53).

    Intenta resolver el Tutor asociado al usuario por `Perfil.rut` o por email.
    """
    usuario = request.user
    tutor = None
    try:
        if hasattr(usuario, 'perfil') and usuario.perfil is not None and usuario.perfil.rol == 'TUTOR':
            perfil = usuario.perfil
            tutor = Tutor.objects.filter(rut=perfil.rut).first()
    except Exception:
        tutor = None

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
def detalle_paciente_basico(request, paciente_id):
    """Muestra solo información básica del paciente al tutor propietario.

    No muestra historial clínico ni observaciones sensibles.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    usuario = request.user

    # Resolver tutor del usuario
    tutor_usuario = None
    try:
        if hasattr(usuario, 'perfil') and usuario.perfil is not None and usuario.perfil.rol == 'TUTOR':
            perfil = usuario.perfil
            tutor_usuario = Tutor.objects.filter(rut=perfil.rut).first()
    except Exception:
        tutor_usuario = None

    if tutor_usuario is None:
        tutor_usuario = Tutor.objects.filter(email=usuario.email).first()

    es_personal_usuario = hasattr(usuario, 'perfil') and usuario.perfil.rol in ['ADMIN', 'VET', 'ESP', 'SECRETARIA']

    if not es_personal_usuario:
        if tutor_usuario is None or paciente.tutor != tutor_usuario:
            return HttpResponseForbidden('No tienes permiso para ver los detalles de este paciente.')

    # Registrar el acceso (no crítico)
    try:
        LogEntry.objects.log_action(
            user_id=usuario.id,
            content_type_id=ContentType.objects.get_for_model(paciente).id,
            object_id=paciente.id,
            object_repr=str(paciente),
            action_flag=CHANGE,
            change_message="Acceso básico a la ficha del paciente por tutor."
        )
    except Exception:
        pass

    contexto = {
        'paciente': paciente,
        'edad': getattr(paciente, 'edad', None),
        'titulo': f'Información básica de {paciente.nombre}'
    }
    return render(request, 'gestion/detalle_paciente_basico.html', contexto)

login_required
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
def bloquear_datos_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    tutor.datos_bloqueados = True
    tutor.save()
    return redirect('detalle_tutor', tutor_id=tutor.id)

@login_required
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
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    if request.method == 'POST':
        cita.estado = 'Cancelada'
        cita.save()
        return redirect('calendario_citas')
    
    return render(request, 'gestion/confirmar_cancelacion.html', {'cita': cita})

@login_required
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
def ver_comprobante(request, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id)
    contexto = {
        'pago': pago,
    }
    return render(request, 'gestion/comprobante_pago.html', contexto)

@login_required
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
@user_passes_test(es_personal) # Solo el personal puede acceder a la mensajería
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
@user_passes_test(es_personal)
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
@user_passes_test(es_personal)
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
@group_required('Veterinario', 'Veterinario especialista')
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
    receta = get_object_or_404(Receta, pk=receta_id)
    usuario_actual = request.user
    es_tutor = hasattr(usuario_actual, 'perfil') and usuario_actual.perfil.rol == 'TUTOR'

    if es_tutor:
        if receta.atencion_medica.ficha_clinica.paciente.tutor.user != usuario_actual:
             messages.error(request, "No tienes permiso para ver esta receta.")
             return redirect('portal')

        if receta.impresa:
            messages.error(request, "Esta receta ya ha sido generada/impresa una vez y no puede volver a generarse.")
            return HttpResponseForbidden("Esta receta ya ha sido generada/impresa una vez.")

    firma_url = None

    # try:
    #     # Asumiendo que tienes un campo 'firma' ImageField en el Perfil del User
    #     if receta.atencion_medica.veterinario.perfil.firma:
    #         firma_path = receta.atencion_medica.veterinario.perfil.firma.path
    #         # Convertir path del sistema a URL accesible por Weasyprint
    #         firma_url = request.build_absolute_uri(receta.atencion_medica.veterinario.perfil.firma.url)
    # except (AttributeError, ObjectDoesNotExist):
    #     firma_url = None

    contexto_pdf = {
        'receta': receta,
        'firma_url': firma_url,
    }
    html_string = render_to_string('gestion/pdfs/pdf_receta.html', contexto_pdf)
    html = HTML(string=html_string, base_url=request.build_absolute_uri()) 
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receta_{receta.atencion_medica.ficha_clinica.paciente.nombre}_{receta.id}.pdf"'

    if es_tutor:
        receta.impresa = True
        receta.save()

    return response

@login_required
@group_required('Veterinario', 'Veterinario especialista', 'Secretaria')
def generar_pdf_ficha(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)

    foto_path = None
    paciente = atencion.ficha_clinica.paciente
    if paciente.foto:
        foto_path = paciente.foto.url

    contexto_pdf = {
        'atencion': atencion,
        'foto_path': foto_path
    }

    html_string = render_to_string('gestion/pdfs/pdf_ficha_clinica.html', contexto_pdf)
    html = HTML(string=html_string, base_url=settings.MEDIA_ROOT)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ficha_{atencion.ficha_clinica.paciente.nombre}_{atencion.id}.pdf"'
    return response

@login_required
@group_required('Veterinario', 'Veterinario especialista', 'Secretaria')
def generar_pdf_epicrisis(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)

    firma_url = None
    # try: ... (lógica futura firma) ... except: ...

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