from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from datetime import date
from .models import Paciente, Tutor, FichaClinica, AtencionMedica, ChequeoFisico, DocumentoAdjunto, Diagnostico, InsumoUtilizado, Cita, Pago, RegistroVacuna
from .forms import PacienteForm, TutorForm, AtencionGeneralForm, ChequeoFisicoForm, ProcedimientoForm, AtencionHospitalizacionForm, DocumentoAdjuntoForm, InsumoUtilizadoForm, AntecedenteExternoForm, CitaForm, PagoForm, RegistroVacunaForm, CustomAuthenticationForm

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
        form = FormClass(request.POST)
        if form.is_valid():
            atencion = form.save(commit=False)

            atencion.ficha_clinica = ficha
            if request.user.is_authenticated:
                atencion.veterinario = request.user

            atencion.save()
            form.save_m2m() 
            
            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        form = FormClass()

    contexto = {
        'form': form,
        'paciente': paciente,
        'titulo': titulo,
        'boton_texto': 'Guardar'
    }
    return render(request, 'gestion/form.html', contexto)

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
    queryset = Cita.objects.filter(estado__in=['Agendada', 'Confirmada']).order_by('fecha_hora')
    titulo = "Calendario de Citas"
    fecha_filtro = request.GET.get('fecha')
    filtro_hoy = request.GET.get('hoy')

    if filtro_hoy:
        hoy = date.today()
        queryset = queryset.filter(fecha_hora__date=hoy)
        titulo = f"Citas para Hoy ({hoy.strftime('%d-%m-%Y')})"
    elif fecha_filtro:
        queryset = queryset.filter(fecha_hora__date=fecha_filtro)
        titulo = f"Citas para el {fecha_filtro}"

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