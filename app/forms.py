from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Paciente, AtencionMedica, ChequeoFisico, Procedimiento, DocumentoAdjunto, Diagnostico, InsumoUtilizado, AntecedenteExterno, Cita, Pago, RegistroVacuna, Tutor, Perfil, Mensaje, Receta

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['foto', 'nombre', 'especie', 'raza', 'sexo', 'Estado_Reproductivo', 'fecha_nacimiento', 'tutor', 'alertas']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'alertas': forms.CheckboxSelectMultiple,
        }

class TutorForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['nombre_completo', 'rut', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AtencionGeneralForm(forms.ModelForm):
    #diagnostico_opciones = forms.ModelChoiceField(queryset=Diagnostico.objects.all(), required=False, label="Diagnóstico", widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_diagnostico_select'}))
    #diagnostico_personalizado = forms.CharField(required=False, label="Otro Diagnóstico (especificar)", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'id_diagnostico_personalizado'}))
    class Meta:
        model = AtencionMedica
        exclude = ['diagnostico']
        fields = ['tipo_atencion', 'tipo_visita', 'motivo_consulta', 'anamnesis', 'estado_emocional', 'diagnosticos', 'prediagnosticos', 'tratamiento', 'estado', 'observaciones_sensibles', 'tipo_especialidad']
        widgets = {
            'tipo_atencion': forms.Select(attrs={'class': 'form-select'}),
            'tipo_especialidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Dermatología, Cirugía'}),
            'tipo_visita': forms.Select(attrs={'class': 'form-select'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'anamnesis': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estado_emocional': forms.Select(attrs={'class': 'form-select'}),
            'diagnosticos': forms.CheckboxSelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'prediagnosticos': forms.CheckboxSelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones_sensibles': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

class ChequeoFisicoForm(forms.ModelForm):
    class Meta:
        model = ChequeoFisico
        fields = ['temperatura', 'peso', 'condicion_corporal', 'anotaciones']
        widgets = {
            'temperatura': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'condicion_corporal': forms.TextInput(attrs={'class': 'form-control'}),
            'anotaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class ProcedimientoForm(forms.ModelForm):
    class Meta:
        model = Procedimiento
        fields = ['tipo', 'descripcion', 'tipo_cirugia', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_procedimiento'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'tipo_cirugia': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%d-%m-%YT%H:%M'),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%d-%m-%YT%H:%M'),
        }

class AtencionHospitalizacionForm(AtencionGeneralForm):
    class Meta(AtencionGeneralForm.Meta):
        fields = AtencionGeneralForm.Meta.fields + ['notas_hospitalizacion', 'jaula_numero', 'fecha_egreso']
        widgets = AtencionGeneralForm.Meta.widgets.copy()
        widgets.update({
            'notas_hospitalizacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'jaula_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_egreso': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%d-%m-%YT%H:%M'),
        })

class DocumentoAdjuntoForm(forms.ModelForm):
    class Meta:
        model = DocumentoAdjunto
        fields = ['titulo', 'archivo']

class InsumoUtilizadoForm(forms.ModelForm):
    class Meta:
        model = InsumoUtilizado
        fields = ['insumo', 'cantidad']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

class AntecedenteExternoForm(forms.ModelForm):
    class Meta:
        model = AntecedenteExterno
        fields = ['titulo', 'archivo']

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'veterinario', 'fecha_hora', 'motivo', 'estado', 'es_especialista', 'es_domicilio', 'notas']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'veterinario': forms.Select(attrs={'class': 'form-select'}),
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        help_texts = {
            'es_domicilio': 'Marcar solo si es una visita a domicilio (horario hasta las 19:00 hrs).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['veterinario'].queryset = User.objects.filter(is_staff=True)

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'metodo_pago', 'notas']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.TextInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RegistroVacunaForm(forms.ModelForm):
    class Meta:
        model = RegistroVacuna
        fields = ['vacuna', 'fecha_aplicacion']
        widgets = {
            'vacuna': forms.Select(attrs={'class': 'form-select'}),
            'fecha_aplicacion': forms.DateInput(attrs={'type': 'date'}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "RUT"
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Ingrese su RUT'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Ingrese su contraseña'}
        )

class MiPerfilForm(forms.ModelForm):
    """
    Formulario para que un Tutor edite su propia información.
    """
    # Campos del modelo User (solo lectura o editables)
    first_name = forms.CharField(label="Nombre", max_length=100, required=True)
    last_name = forms.CharField(label="Apellido", max_length=100, required=True)
    email = forms.EmailField(label="Correo Electrónico", required=True)

    # Campos del modelo Tutor
    telefono = forms.CharField(label="Teléfono", max_length=15, required=False)
    direccion = forms.CharField(label="Dirección", widget=forms.Textarea(attrs={'rows': 3}), required=False)

    # Campo del modelo Perfil
    canal_notificacion_preferido = forms.ChoiceField(
        label="Canal de Notificación Preferido",
        choices=Perfil._meta.get_field('canal_notificacion_preferido').choices, # Obtiene las opciones del modelo
        widget=forms.RadioSelect # Muestra como botones de radio
    )

    class Meta:
        # Aunque usamos campos de varios modelos, NO especificamos un 'model' aquí
        # porque los guardaremos manualmente en la vista.
        fields = ['first_name', 'last_name', 'email', 'telefono', 'direccion', 'canal_notificacion_preferido']

    def __init__(self, *args, **kwargs):
        # Recibimos las instancias de user, tutor y perfil para llenar el form
        self.user = kwargs.pop('user_instance', None)
        self.tutor = kwargs.pop('tutor_instance', None)
        self.perfil = kwargs.pop('perfil_instance', None)

        initial = {}
        if self.user:
            initial['first_name'] = self.user.first_name
            initial['last_name'] = self.user.last_name
            initial['email'] = self.user.email
        if self.tutor:
            initial['telefono'] = self.tutor.telefono
            initial['direccion'] = self.tutor.direccion
        if self.perfil:
            initial['canal_notificacion_preferido'] = self.perfil.canal_notificacion_preferido

        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

        # Hacemos que el email no sea editable si ya existe (opcional)
        # if self.user and self.user.email:
        #     self.fields['email'].disabled = True

class MensajeForm(forms.ModelForm):
    destinatario = forms.ModelChoiceField(
        queryset=User.objects.filter(perfil__rol__in=['ADMIN', 'VET', 'ESP', 'SECRETARIA']), # Solo personal
        label="Para",
        empty_label="Selecciona un destinatario"
    )

    class Meta:
        model = Mensaje
        fields = ['destinatario', 'asunto', 'cuerpo']
        widgets = {
            'cuerpo': forms.Textarea(attrs={'rows': 5}),
        }

class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['prescripcion']
        widgets = {
            'prescripcion': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Ingrese aquí la prescripción médica...'}),
        }
        labels = {
            'prescripcion': 'Detalle de la Receta Médica',
        }