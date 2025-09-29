from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.residences.models import Vivienda
from apps.common_areas.models import AreaComun

class Mantenimiento(BaseModel):
    """Mantenimientos realizados en viviendas y áreas comunes"""
    # Relación polimórfica para viviendas o áreas comunes
    ENTIDAD_CHOICES = [
        ('VIVIENDA', 'Vivienda'),
        ('AREA_COMUN', 'Área Común'),
    ]
    
    entidad_tipo = models.CharField(
        max_length=20, 
        choices=ENTIDAD_CHOICES,
        verbose_name="Tipo de entidad"
    )
    entidad_id = models.IntegerField(verbose_name="ID de la entidad")
    
    # Campos relacionados
    reportado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='mantenimientos_reportados',
        verbose_name="Reportado por"
    )
    descripcion = models.TextField(verbose_name="Descripción")
    diagnostico = models.TextField(null=True, blank=True, verbose_name="Diagnóstico")
    
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('preventivo', 'Preventivo'),
            ('correctivo', 'Correctivo'),
            ('urgente', 'Urgente'),
        ],
        verbose_name="Tipo"
    )
    
    prioridad = models.CharField(
        max_length=20,
        choices=[
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
            ('critica', 'Crítica'),
        ],
        verbose_name="Prioridad"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=[
            ('solicitado', 'Solicitado'),
            ('asignado', 'Asignado'),
            ('en_proceso', 'En Proceso'),
            ('completado', 'Completado'),
        ],
        default='solicitado',
        verbose_name="Estado"
    )
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de solicitud")
    fecha_asignacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de asignación")
    
    asignado_a = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='mantenimientos_asignados',
        verbose_name="Asignado a"
    )
    
    fecha_completado = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de completado")
    
    # Costos
    costo_materiales = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Costo de materiales"
    )
    costo_mano_obra = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Costo de mano de obra"
    )
    
    # Información adicional
    proveedor = models.CharField(max_length=200, blank=True, verbose_name="Proveedor")
    garantia_meses = models.IntegerField(null=True, blank=True, verbose_name="Garantía (meses)")
    evidencia_antes = models.URLField(null=True, blank=True, verbose_name="Evidencia antes")
    evidencia_despues = models.URLField(null=True, blank=True, verbose_name="Evidencia después")

    @property
    def costo_total(self):
        """Calcula el costo total"""
        return self.costo_materiales + self.costo_mano_obra

    @property
    def entidad_object(self):
        """Retorna el objeto relacionado según el tipo"""
        if self.entidad_tipo == 'VIVIENDA':
            return Vivienda.objects.filter(id=self.entidad_id).first()
        elif self.entidad_tipo == 'AREA_COMUN':
            return AreaComun.objects.filter(id=self.entidad_id).first()
        return None

    def __str__(self):
        entidad_obj = self.entidad_object
        entidad_str = str(entidad_obj) if entidad_obj else f"{self.entidad_tipo} #{self.entidad_id}"
        return f"Mantenimiento {self.pk} - {entidad_str}"

    class Meta: # type: ignore
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ['-fecha_solicitud']
