from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from datetime import date, timedelta
from django.utils import timezone

class Perfil(models.Model):
    ROL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('VET', 'Veterinario'),
        ('ESP', 'Veterinario Especialista'),
        ('SECRETARIA', 'Secretaría'),
        ('TUTOR', 'Tutor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    firma = models.ImageField(
        upload_to='firmas/',
        null=True,
        blank=True,
        verbose_name="Imagen de Firma/Timbre"
        #validators=[validate_image_extension] si defines la función de validación
    )
    canal_notificacion_preferido = models.CharField(
        max_length=10,
        choices=[('EMAIL', 'Correo Electrónico'), ('WHATSAPP', 'WhatsApp'), ('NONE', 'No recibir')],
        default='EMAIL',
        verbose_name="Canal de notificación preferido"
    )

    def __str__(self):
        return f"Perfil de {self.user.username} (RUT: {self.rut})"

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
    datos_bloqueados = models.BooleanField(default=False, verbose_name="Datos Bloqueados (No editar)")

    history = HistoricalRecords()

    def __str__(self):
        return self.nombre_completo

class Paciente(models.Model):
    SEXO_CHOICES = [
        ('Macho', 'Macho'),
        ('Hembra', 'Hembra'),
    ]
    ESTADO_REPRODUCTIVO_CHOICES = [
        ('Entero', 'Entero'),
        ('Castrado', 'Castrado/Esterilizado'),
    ]
    foto = models.ImageField(upload_to='fotos_pacientes/', blank=True, null=True, verbose_name="Fotografía del Paciente")
    nombre = models.CharField(max_length=50)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=50)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    estado_reproductivo = models.CharField(max_length=20, choices=ESTADO_REPRODUCTIVO_CHOICES, default='Entero', verbose_name="Estado Reproductivo")
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

class AtencionMedica(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Completa', 'Completa'),
    ]
    TIPO_ATENCION_CHOICES = [
        ('Clínica', 'Clínica Veterinaria'),
        ('Club', 'Club Entre Patitas')
    ]
    LUGAR_CHOICES = [
        ('Sede Bilbao', 'Sede Bilbao'),
        ('Sede Eliodoro Yáñez', 'Sede Eliodoro Yáñez'),
        ('Domicilio', 'Domicilio'),
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
    lugar_atencion = models.CharField(max_length=30, choices=LUGAR_CHOICES, default='Sede Bilbao', verbose_name="Sede / Lugar")
    tipo_atencion = models.CharField(max_length=10, choices=TIPO_ATENCION_CHOICES)
    tipo_visita = models.CharField(max_length=20, choices=TIPO_VISITA_CHOICES)
    tipo_especialidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo de especialidad", help_text="Ej: Dermatología, Cirugía, Cardiología")
    motivo_consulta = models.TextField(help_text="Debe tener un mínimo de 10 caracteres.")
    anamnesis = models.TextField(verbose_name="Anamnesis (antecedentes previos y actuales)")
    prediagnostico = models.TextField(blank=True, verbose_name="Prediagnóstico", help_text="Ingrese el prediagnóstico aquí.")
    diagnostico = models.TextField(blank=True, verbose_name="Diagnóstico", help_text="Ingrese el diagnóstico final.")
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
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Temperatura (°C)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso (Kg)")
    frecuencia_cardiaca = models.CharField(max_length=50, blank=True, verbose_name="Frecuencia Cardíaca (FC)")
    frecuencia_respiratoria = models.CharField(max_length=50, blank=True, verbose_name="Frecuencia Respiratoria (FR)")
    tllc = models.CharField(max_length=50, blank=True, verbose_name="TLLC")
    mucosas = models.CharField(max_length=100, blank=True, verbose_name="Mucosas")
    condicion_corporal = models.CharField(max_length=50, verbose_name="Condición Corporal")
    anotaciones = models.TextField(blank=True, verbose_name="Hallazgos / Anotaciones")

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
    
class SolicitudDatosPersonales(models.Model):
    TIPO_SOLICITUD_CHOICES = [
        ('Acceso', 'Solicitud de Acceso'),
        ('Modificación', 'Solicitud de Modificación'),
        ('Cancelación', 'Solicitud de Cancelación'),
        ('Bloqueo', 'Solicitud de Bloqueo'),
    ]
    ESTADO_SOLICITUD_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='solicitudes')
    tipo_solicitud = models.CharField(max_length=20, choices=TIPO_SOLICITUD_CHOICES)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_SOLICITUD_CHOICES, default='Pendiente')
    resolucion = models.TextField(blank=True, null=True, help_text="Detalles de la resolución de la solicitud (ej: 'Se enviaron los datos por correo el DD/MM/AAAA').")
    usuario_responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text="Usuario que gestionó la solicitud.")

    def __str__(self):
        return f"Solicitud de {self.tipo_solicitud} para {self.tutor.nombre_completo}"

class AntecedenteExterno(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='antecedentes_externos')
    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='antecedentes_externos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Antecedente '{self.titulo}' para {self.paciente.nombre}"
    
class Cita(models.Model):
    ESTADO_CHOICES = [
        ('Agendada', 'Agendada'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('Completada', 'Completada'),
    ]
    SEDE_CHOICES = [
        ('Sede Bilbao', 'Sede Bilbao'),
        ('Sede Eliodoro Yáñez', 'Sede Eliodoro Yáñez'),
        ('Domicilio', 'Domicilio'),
    ]
    ESPECIALIDAD_CHOICES = [
        ('General', 'Medicina General'),
        ('Cirugía', 'Cirugía'),
        ('Dermatología', 'Dermatología'),
        ('Cardiología', 'Cardiología'),
        ('Oftalmología', 'Oftalmología'),
        ('Traumatología', 'Traumatología'),
        ('Odontología', 'Odontología'),
    ]
    
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE, 
        related_name='citas',
        null=True,
        blank=True
    )
    nombre_paciente_temporal = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Nombre del Paciente (temporal)"
    )
    nombre_tutor_temporal = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Nombre del Tutor (temporal)"
    )
    sede = models.CharField(
        max_length=30, 
        choices=SEDE_CHOICES, 
        default='Sede Bilbao',
        verbose_name="Sede"
    )
    especialidad = models.CharField(
        max_length=30, 
        choices=ESPECIALIDAD_CHOICES, 
        default='General',
        verbose_name="Especialidad"
    )
    es_especialista = models.BooleanField(default=False, verbose_name="¿Es cita con especialista?")
    veterinario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas_asignadas')
    fecha_hora = models.DateTimeField(help_text="Día y hora de la cita")
    es_domicilio = models.BooleanField(default=False, verbose_name="¿Es visita a domicilio?")
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Agendada')
    notas = models.TextField(blank=True, null=True, help_text="Notas adicionales para la cita")

    def __str__(self):
        nombre_display = self.paciente.nombre if self.paciente else self.nombre_paciente_temporal
        return f"Cita para {nombre_display} el {self.fecha_hora.strftime('%d/%m/%Y a las %H:%M')}"
    
class Pago(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, default="No especificado")
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pago de ${self.monto} para la cita {self.cita.id}"
    
class Vacuna(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    especie_objetivo = models.CharField(max_length=50, help_text="Ej: Canino, Felino")
    dosis_necesarias = models.PositiveIntegerField(default=1)
    frecuencia_refuerzo_dias = models.PositiveIntegerField(help_text="Días hasta el próximo refuerzo (ej: 365 para anual)")

    def __str__(self):
        return f"{self.nombre} ({self.especie_objetivo})"

class RegistroVacuna(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historial_vacunas')
    vacuna = models.ForeignKey(Vacuna, on_delete=models.CASCADE)
    fecha_aplicacion = models.DateField()
    proxima_dosis_fecha = models.DateField(blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.proxima_dosis_fecha = self.fecha_aplicacion + timedelta(days=self.vacuna.frecuencia_refuerzo_dias)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vacuna.nombre} aplicada a {self.paciente.nombre} el {self.fecha_aplicacion}"
    
class Mensaje(models.Model):
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    asunto = models.CharField(max_length=200)
    cuerpo = models.TextField()
    fecha_envio = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"De: {self.remitente.username} | Para: {self.destinatario.username} | Asunto: {self.asunto}"

    class Meta:
        ordering = ['-fecha_envio']

class Receta(models.Model):
    atencion_medica = models.ForeignKey(AtencionMedica, on_delete=models.CASCADE, related_name='recetas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    prescripcion = models.TextField(verbose_name="Prescripción")
    # Campo para CU-50 (Restringir reimpresión)
    impresa = models.BooleanField(default=False, verbose_name="¿Impresa/Generada?") 
    # Campo para CU-52 (Firma) - Opcional aquí, podría ir en la generación del PDF
    # firma_veterinario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='recetas_firmadas')

    def __str__(self):
        return f"Receta para Atención ID {self.atencion_medica.id} del {self.fecha_creacion.strftime('%d-%m-%Y')}"

    class Meta:
        ordering = ['-fecha_creacion']