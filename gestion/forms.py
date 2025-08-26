from django import forms
from .models import Paciente, AtencionMedica, ChequeoFisico, Procedimiento, DocumentoAdjunto, Diagnostico

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'especie', 'raza', 'sexo', 'fecha_nacimiento', 'tutor']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class AtencionGeneralForm(forms.ModelForm):
    diagnostico_predefinido = forms.ModelChoiceField(
        queryset=Diagnostico.objects.all(),
        required=False,
        label="Diagnóstico",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_diagnostico_predefinido'})
    )
    diagnostico_personalizado = forms.CharField(
        required=False,
        label="Otro Diagnóstico (especificar)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'id_diagnostico_personalizado'})
    )
    class Meta:
        model = AtencionMedica
        exclude = ['diagnostico']
        fields = ['tipo_atencion', 'tipo_visita', 'motivo_consulta', 'anamnesis', 'estado_emocional', 'tratamiento']
        widgets = {
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'anamnesis': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo_atencion': forms.Select(attrs={'class': 'form-select'}),
            'tipo_visita': forms.Select(attrs={'class': 'form-select'}),
            'estado_emocional': forms.Select(attrs={'class': 'form-select'}),
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
        fields = AtencionGeneralForm.Meta.fields + ['notas_hospitalizacion', 'jaula_numero']
        widgets = AtencionGeneralForm.Meta.widgets.copy()
        widgets.update({
            'notas_hospitalizacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'jaula_numero': forms.TextInput(attrs={'class': 'form-control'}),
        })

class DocumentoAdjuntoForm(forms.ModelForm):
    class Meta:
        model = DocumentoAdjunto
        fields = ['titulo', 'archivo']