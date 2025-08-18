from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Paciente, FichaClinica, AtencionMedica, ChequeoFisico, DocumentoAdjunto
from .forms import PacienteForm, AtencionGeneralForm, ChequeoFisicoForm, ProcedimientoForm, AtencionHospitalizacionForm, DocumentoAdjuntoForm

def portal_view(request):
    return render(request, 'portal.html')

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
    }
    return render(request, 'gestion/detalle_paciente.html', contexto)

@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
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
        form = PacienteForm(request.POST, instance=paciente)
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
            atencion.tipo_ficha = 'Hospitalización' if tipo_ficha == 'hospitalizacion' else 'General'
            if request.user.is_authenticated:
                atencion.veterinario = request.user
            atencion.save()
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
    try:
        chequeo = atencion.chequeo
    except ChequeoFisico.DoesNotExist:
        chequeo = None

    if request.method == 'POST':
        atencion_form = AtencionGeneralForm(request.POST, instance=atencion)
        chequeo_form = ChequeoFisicoForm(request.POST, instance=chequeo)

        if atencion_form.is_valid() and chequeo_form.is_valid():
            atencion = atencion_form.save()

            chequeo = chequeo_form.save(commit=False)
            chequeo.atencion_medica = atencion
            chequeo.save()

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