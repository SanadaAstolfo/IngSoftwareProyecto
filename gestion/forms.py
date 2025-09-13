from django import forms
from django.contrib.auth.models import User
from .models import Paciente, AtencionMedica, ChequeoFisico, Procedimiento, DocumentoAdjunto, Diagnostico, InsumoUtilizado, AntecedenteExterno, Cita, Pago, RegistroVacuna

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['foto', 'nombre', 'especie', 'raza', 'sexo', 'fecha_nacimiento', 'tutor', 'alertas']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'alertas': forms.CheckboxSelectMultiple,
        }

class AtencionGeneralForm(forms.ModelForm):
    #diagnostico_opciones = forms.ModelChoiceField(queryset=Diagnostico.objects.all(), required=False, label="Diagnóstico", widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_diagnostico_select'}))
    #diagnostico_personalizado = forms.CharField(required=False, label="Otro Diagnóstico (especificar)", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'id_diagnostico_personalizado'}))
    class Meta:
        model = AtencionMedica
        exclude = ['diagnostico']
        fields = ['tipo_atencion', 'tipo_visita', 'motivo_consulta', 'anamnesis', 'estado_emocional', 'diagnosticos', 'prediagnosticos', 'tratamiento', 'estado', 'observaciones_sensibles']
        widgets = {
            'tipo_atencion': forms.Select(attrs={'class': 'form-select'}),
            'tipo_visita': forms.Select(attrs={'class': 'form-select'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'anamnesis': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estado_emocional': forms.Select(attrs={'class': 'form-select'}),
            'diagnosticos': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'prediagnosticos': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
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