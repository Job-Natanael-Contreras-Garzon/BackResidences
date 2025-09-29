from django.db import models
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.residences.models import Vivienda

class TipoReporte(BaseModel):
    """Tipos de reportes disponibles"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('tecnico', 'Técnico'),
            ('administrativo', 'Administrativo'),
            ('convivencia', 'Convivencia'),
        ],
        verbose_name="Categoría"
    )
    prioridad_default = models.CharField(
        max_length=20,
        choices=[
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente'),
        ],
        default='media',
        verbose_name="Prioridad por defecto"
    )
    tiempo_respuesta_horas = models.IntegerField(default=24, verbose_name="Tiempo de respuesta (horas)")

    def __str__(self):
        return self.nombre

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Tipo de Reporte"
        verbose_name_plural = "Tipos de Reportes"

class Reporte(BaseModel):
    """Reportes del sistema"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    vivienda = models.ForeignKey(Vivienda, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vivienda")
    tipo_reporte = models.ForeignKey(TipoReporte, on_delete=models.CASCADE, verbose_name="Tipo de reporte")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    prioridad = models.CharField(
        max_length=20,
        choices=[
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente'),
        ],
        default='media',
        verbose_name="Prioridad"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('abierto', 'Abierto'),
            ('en_proceso', 'En Proceso'),
            ('resuelto', 'Resuelto'),
            ('cerrado', 'Cerrado'),
        ],
        default='abierto',
        verbose_name="Estado"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    fecha_asignacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de asignación")
    fecha_resolucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de resolución")
    asignado_a = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reportes_asignados',
        verbose_name="Asignado a"
    )
    evidencia_foto = models.URLField(null=True, blank=True, verbose_name="Evidencia fotográfica")

    def __str__(self):
        return f"Reporte {self.pk} - {self.titulo}"

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ['-fecha_registro']

class Aviso(BaseModel):
    """Avisos generales del condominio"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Publicado por")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    contenido = models.TextField(verbose_name="Contenido")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('informativo', 'Informativo'),
            ('urgente', 'Urgente'),
            ('mantenimiento', 'Mantenimiento'),
        ],
        default='informativo',
        verbose_name="Tipo"
    )
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de publicación")
    fecha_caducidad = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de caducidad")
    prioridad = models.CharField(
        max_length=20,
        choices=[
            ('baja', 'Baja'),
            ('normal', 'Normal'),
            ('alta', 'Alta'),
        ],
        default='normal',
        verbose_name="Prioridad"
    )
    publico_objetivo = models.CharField(
        max_length=30,
        choices=[
            ('todos', 'Todos'),
            ('propietarios', 'Propietarios'),
            ('inquilinos', 'Inquilinos'),
        ],
        default='todos',
        verbose_name="Público objetivo"
    )
    adjunto_url = models.URLField(null=True, blank=True, verbose_name="Adjunto")

    def __str__(self):
        return self.titulo

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
        ordering = ['-fecha_publicacion']

class AvisoVisto(models.Model):
    """Control de avisos vistos por usuario"""
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_visto = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['aviso', 'usuario']
        verbose_name = "Aviso Visto"
        verbose_name_plural = "Avisos Vistos"

    def __str__(self):
        return f"{self.usuario.username} vió {self.aviso.titulo}"
