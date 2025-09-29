from django.db import models
from apps.core.models import BaseModel
from apps.authentication.models import User

class TipoEvento(BaseModel):
    """Tipos de eventos de seguridad"""
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    severidad = models.IntegerField(
        default=1,
        choices=[
            (1, 'Baja'),
            (2, 'Media'),
            (3, 'Alta'),
            (4, 'Crítica'),
        ],
        verbose_name="Severidad"
    )

    def __str__(self):
        return self.nombre

    class Meta: # type: ignore
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Eventos"

class Zona(BaseModel):
    """Zonas del condominio"""
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('entrada', 'Entrada'),
            ('parqueadero', 'Parqueadero'),
            ('lobby', 'Lobby'),
            ('piscina', 'Piscina'),
            ('gimnasio', 'Gimnasio'),
            ('salon', 'Salón Social'),
        ],
        verbose_name="Tipo"
    )
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    nivel_seguridad = models.CharField(
        max_length=20,
        choices=[
            ('bajo', 'Bajo'),
            ('medio', 'Medio'),
            ('alto', 'Alto'),
        ],
        default='medio',
        verbose_name="Nivel de seguridad"
    )

    def __str__(self):
        return self.nombre

    class Meta: # type: ignore
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"

class Camara(BaseModel):
    """Cámaras del sistema de seguridad"""
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, verbose_name="Zona")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    ubicacion = models.CharField(max_length=200, verbose_name="Ubicación")
    direccion_ip = models.GenericIPAddressField(verbose_name="Dirección IP")
    puerto = models.IntegerField(default=80, verbose_name="Puerto")
    usuario_camara = models.CharField(max_length=50, blank=True, verbose_name="Usuario")
    password_camara = models.CharField(max_length=100, blank=True, verbose_name="Contraseña")
    url_stream = models.URLField(verbose_name="URL de streaming")
    modelo = models.CharField(max_length=100, blank=True, verbose_name="Modelo")
    resolucion = models.CharField(max_length=20, blank=True, verbose_name="Resolución")
    vision_nocturna = models.BooleanField(default=False, verbose_name="Visión nocturna")
    angulo_vision = models.IntegerField(null=True, blank=True, verbose_name="Ángulo de visión")
    fecha_instalacion = models.DateField(null=True, blank=True, verbose_name="Fecha de instalación")
    ultimo_mantenimiento = models.DateField(null=True, blank=True, verbose_name="Último mantenimiento")

    def __str__(self):
        return f"{self.nombre} - {self.zona.nombre}"

    class Meta: # type: ignore
        verbose_name = "Cámara"
        verbose_name_plural = "Cámaras"

class VehiculoAutorizado(BaseModel):
    """Vehículos autorizados"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    placa = models.CharField(max_length=15, unique=True, verbose_name="Placa")
    marca = models.CharField(max_length=50, verbose_name="Marca")
    modelo = models.CharField(max_length=50, verbose_name="Modelo")
    anio = models.IntegerField(verbose_name="Año")
    color = models.CharField(max_length=30, verbose_name="Color")
    tipo_vehiculo = models.CharField(
        max_length=20,
        choices=[
            ('auto', 'Automóvil'),
            ('moto', 'Motocicleta'),
            ('bicicleta', 'Bicicleta'),
        ],
        verbose_name="Tipo de vehículo"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    aprobado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='vehiculos_aprobados',
        verbose_name="Aprobado por"
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de aprobación")

    def __str__(self):
        return f"{self.placa} - {self.usuario.get_full_name()}"

    class Meta: # type: ignore
        verbose_name = "Vehículo Autorizado"
        verbose_name_plural = "Vehículos Autorizados"

class EventoSeguridad(BaseModel):
    """Eventos de seguridad"""
    camara = models.ForeignKey(Camara, on_delete=models.SET_NULL, null=True, verbose_name="Cámara")
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.CASCADE, verbose_name="Tipo de evento")
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Usuario"
    )
    vehiculo_autorizado = models.ForeignKey(
        VehiculoAutorizado, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Vehículo"
    )
    fecha_hora = models.DateTimeField(verbose_name="Fecha y hora")
    descripcion = models.TextField(verbose_name="Descripción")
    evidencia_url = models.URLField(null=True, blank=True, verbose_name="URL de evidencia")
    severidad = models.IntegerField(default=1, verbose_name="Severidad")
    revisado = models.BooleanField(default=False, verbose_name="Revisado")
    resuelto_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='eventos_resueltos',
        verbose_name="Resuelto por"
    )
    fecha_resolucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de resolución")
    notas_resolucion = models.TextField(null=True, blank=True, verbose_name="Notas de resolución")

    def __str__(self):
        return f"Evento {self.pk} - {self.tipo_evento.nombre}"

    class Meta: # type: ignore
        verbose_name = "Evento de Seguridad"
        verbose_name_plural = "Eventos de Seguridad"
        ordering = ['-fecha_hora']

class CredentialAcceso(BaseModel):
    """Credenciales de acceso"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    vehiculo_autorizado = models.ForeignKey(
        VehiculoAutorizado, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Vehículo"
    )
    identificador = models.CharField(max_length=100, verbose_name="Identificador")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('tarjeta', 'Tarjeta'),
            ('pin', 'PIN'),
            ('biometrico', 'Biométrico'),
            ('app', 'Aplicación'),
        ],
        verbose_name="Tipo"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('bloqueado', 'Bloqueado'),
            ('vencido', 'Vencido'),
        ],
        default='activo',
        verbose_name="Estado"
    )
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de emisión")
    fecha_vencimiento = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de vencimiento")
    ultimo_uso = models.DateTimeField(null=True, blank=True, verbose_name="Último uso")

    def __str__(self):
        return f"{self.identificador} - {self.usuario.username}"

    class Meta: # type: ignore
        verbose_name = "Credencial de Acceso"
        verbose_name_plural = "Credenciales de Acceso"