from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

class Tutor(models.Model):
    nombre_completo = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre_completo

class Paciente(models.Model):
    nombre = models.CharField(max_length=50)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=50)
    sexo = models.CharField(max_length=10)
    fecha_nacimiento = models.DateField()
    microchip_tatuaje = models.CharField(max_length=50, blank=True, null=True) # 
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='pacientes')

    def __str__(self):
        return f"{self.nombre} ({self.especie})"

class FichaClinica(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, primary_key=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ficha de {self.paciente.nombre}"

class AtencionMedica(models.Model):
    TIPO_ATENCION_CHOICES = [
        ('Clínica', 'Clínica Veterinaria'),
        ('Club', 'Club Entre Patitas')
    ]
    TIPO_VISITA_CHOICES = [
        ('Consulta', 'Consulta Básica'),
        ('Urgencia', 'Urgencia'),
        ('Domicilio', 'Visita a Domicilio'),
    ]
    ESTADO_EMOCIONAL_CHOICES = [
        ('Tranquilo', 'Tranquilo'),
        ('Nervioso', 'Nervioso'),
        ('Agresivo', 'Agresivo'),
    ]
    ficha_clinica = models.ForeignKey(FichaClinica, on_delete=models.CASCADE, related_name='atenciones')
    fecha_atencion = models.DateTimeField(auto_now_add=True)
    veterinario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tipo_atencion = models.CharField(max_length=10, choices=TIPO_ATENCION_CHOICES)
    tipo_visita = models.CharField(max_length=20, choices=TIPO_VISITA_CHOICES)
    motivo_consulta = models.TextField(help_text="Debe tener un mínimo de 10 caracteres.")
    anamnesis = models.TextField(verbose_name="Anamnesis (antecedentes previos y actuales)")
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    estado_emocional = models.CharField(max_length=20, choices=ESTADO_EMOCIONAL_CHOICES, blank=True, null=True, verbose_name="Comportamiento del Paciente")

    esta_cerrada = models.BooleanField(default=False)

    notas_hospitalizacion = models.TextField(blank=True, null=True, help_text="Notas específicas de la hospitalización")
    jaula_numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número de Jaula")

    history = HistoricalRecords()

    def __str__(self):
        return f"Atención para {self.ficha_clinica.paciente.nombre} el {self.fecha_atencion.strftime('%d-%m-%Y')}"

class ChequeoFisico(models.Model):
    atencion_medica = models.OneToOneField(AtencionMedica, on_delete=models.CASCADE, related_name='chequeo')
    temperatura = models.DecimalField(max_digits=4, decimal_places=2)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    condicion_corporal = models.CharField(max_length=100)
    anotaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Chequeo Físico del {self.atencion_medica.fecha_atencion.strftime('%d-%m-%Y')}"

class Procedimiento(models.Model):
    TIPO_PROCEDIMIENTO_CHOICES = [
        ('Cirugía', 'Cirugía'),
        ('Examen', 'Examen'),
        ('Hospitalización', 'Hospitalización')
    ]
    TIPO_CIRUGIA_CHOICES = [
        ('Urgencia', 'Urgencia'),
        ('Programada', 'Programada'),
    ]
    atencion_medica = models.ForeignKey(AtencionMedica, on_delete=models.CASCADE, related_name='procedimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_PROCEDIMIENTO_CHOICES)
    tipo_cirugia = models.CharField(max_length=20, choices=TIPO_CIRUGIA_CHOICES, blank=True, null=True, verbose_name="Tipo de Cirugía")
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} para {self.atencion_medica.ficha_clinica.paciente.nombre}"
    
class DocumentoAdjunto(models.Model):
    atencion_medica = models.ForeignKey(AtencionMedica, on_delete=models.CASCADE, related_name='documentos')
    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='documentos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.atencion_medica.ficha_clinica.paciente.nombre}"