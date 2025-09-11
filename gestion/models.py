from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from datetime import date

class AlertaClinica(models.Model):
    CATEGORIA_CHOICES = [
        ('Alergia', 'Alergia'),
        ('Condición Crónica', 'Condición Crónica'),
        ('Comportamiento', 'Comportamiento'),
        ('Manejo Específico', 'Manejo Específico'),
    ]
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripcion de la alerta y qué implica.")
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, default='Manejo Específico')
    NIVEL_SEVERIDAD_CHOICES = [
        ('Alta', 'Alta (Roja)'),
        ('Media', 'Media (Naranja)'),
        ('Baja', 'Baja (Azul)'),
    ]
    severidad = models.CharField(max_length=10, choices=NIVEL_SEVERIDAD_CHOICES, default='Baja')

    def __str__(self):
        return self.nombre

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
    microchip_tatuaje = models.CharField(max_length=50, blank=True, null=True)
    alertas = models.ManyToManyField(AlertaClinica, blank=True, verbose_name="Alertas Clinicas")
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='pacientes')

    @property
    def edad(self):
        hoy = date.today()
        if self.fecha_nacimiento:
            edad_calculada = hoy.year - self.fecha_nacimiento.year
            if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
                edad_calculada -= 1
            return edad_calculada
        return None

    def __str__(self):
        return f"{self.nombre} ({self.especie})"

class FichaClinica(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, primary_key=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ficha de {self.paciente.nombre}"

class Diagnostico(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class AtencionMedica(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Completa', 'Completa'),
    ]
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
    #diagnostico = models.TextField()
    diagnosticos = models.ManyToManyField(Diagnostico, related_name='atenciones', blank=True, verbose_name="Diagnósticos")
    prediagnosticos = models.ManyToManyField(Diagnostico, related_name='atenciones_prediagnostico', blank=True, verbose_name="Prediagnósticos (Opcional)")
    tratamiento = models.TextField()
    estado_emocional = models.CharField(max_length=20, choices=ESTADO_EMOCIONAL_CHOICES, blank=True, null=True, verbose_name="Comportamiento del Paciente")

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente', verbose_name="Estado de la Ficha")
    esta_cerrada = models.BooleanField(default=False)

    notas_hospitalizacion = models.TextField(blank=True, null=True, help_text="Notas específicas de la hospitalización")
    jaula_numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número de Jaula")
    fecha_egreso = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Egreso")

    observaciones_sensibles = models.TextField(blank=True, null=True, verbose_name="Observaciones Médicas Sensibles (Solo personal)", help_text="Estas notas no serán visibles para el tutor.")

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
    
class Insumo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo por unidad del insumo")
    
    def __str__(self):
        return f"{self.nombre} (${self.costo})"
    
class InsumoUtilizado(models.Model):
    atencion_medica = models.ForeignKey(AtencionMedica, on_delete=models.CASCADE, related_name='insumos_utilizados')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.costo_total = self.insumo.costo * self.cantidad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.insumo.nombre} en atencion {self.atencion_medica.id}"