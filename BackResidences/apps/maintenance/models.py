from decimal import Decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.residences.models import Vivienda
from apps.common_areas.models import AreaComun


class CategoriaMantenimiento(BaseModel):
    """Categorías de mantenimiento disponibles"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    color = models.CharField(max_length=7, default="#007bff", verbose_name="Color hex")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    tiempo_respuesta_horas = models.IntegerField(default=24, verbose_name="Tiempo respuesta (horas)")
    
    def __str__(self):
        return self.nombre
    
    class Meta: # type: ignore
        verbose_name = "Categoría de Mantenimiento"
        verbose_name_plural = "Categorías de Mantenimiento"
        ordering = ['nombre']


class Proveedor(BaseModel):
    """Proveedores de servicios de mantenimiento"""
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    categoria_principal = models.ForeignKey(
        CategoriaMantenimiento, 
        on_delete=models.CASCADE,
        verbose_name="Categoría principal"
    )
    servicios = models.ManyToManyField(
        CategoriaMantenimiento, 
        related_name='proveedores_servicios',
        verbose_name="Servicios que ofrece"
    )
    
    # Información de contacto
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    direccion = models.TextField(verbose_name="Dirección")
    contacto_principal = models.CharField(max_length=100, verbose_name="Contacto principal")
    
    # Documentación
    rut = models.CharField(max_length=20, unique=True, verbose_name="RUT/NIT")
    camara_comercio = models.CharField(max_length=50, blank=True, verbose_name="Cámara de comercio")
    poliza_responsabilidad = models.CharField(max_length=100, blank=True, verbose_name="Póliza responsabilidad")
    
    # Tarifas
    tarifa_hora = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Tarifa por hora"
    )
    tarifa_visita = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Tarifa visita diagnóstico"
    )
    recargo_emergencia_porcentaje = models.IntegerField(
        default=50, 
        verbose_name="Recargo emergencia (%)"
    )
    
    # Disponibilidad
    horarios = models.CharField(max_length=200, verbose_name="Horarios de atención")
    atiende_emergencias = models.BooleanField(default=False, verbose_name="Atiende emergencias")
    tiempo_respuesta_emergencia_horas = models.IntegerField(
        default=24, 
        verbose_name="Tiempo respuesta emergencia (horas)"
    )
    
    # Estado y calificación
    activo = models.BooleanField(default=True, verbose_name="Activo")
    calificacion_promedio = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Calificación promedio"
    )
    trabajos_realizados = models.IntegerField(default=0, verbose_name="Trabajos realizados")
    
    def __str__(self):
        return self.nombre
    
    class Meta: # type: ignore
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']


class SolicitudMantenimiento(BaseModel):
    """Solicitudes de mantenimiento de residentes"""
    # Identificación única
    numero_solicitud = models.CharField(max_length=20, unique=True, verbose_name="Número solicitud")
    
    # Categorización
    categoria = models.ForeignKey(
        CategoriaMantenimiento, 
        on_delete=models.CASCADE,
        verbose_name="Categoría"
    )
    subcategoria = models.CharField(max_length=100, blank=True, verbose_name="Subcategoría")
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    prioridad = models.CharField(
        max_length=20, 
        choices=PRIORIDAD_CHOICES, 
        default='media',
        verbose_name="Prioridad"
    )
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('asignada', 'Asignada'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado"
    )
    
    # Descripción del problema
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción detallada")
    
    # Ubicación (polimórfica)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    ubicacion = GenericForeignKey('content_type', 'object_id')
    ubicacion_especifica = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Ubicación específica"
    )
    
    # Solicitante
    solicitante = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='solicitudes_mantenimiento',
        verbose_name="Solicitante"
    )
    
    # Fechas importantes
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha solicitud")
    fecha_preferida = models.DateTimeField(null=True, blank=True, verbose_name="Fecha preferida")
    fecha_limite = models.DateTimeField(null=True, blank=True, verbose_name="Fecha límite")
    fecha_asignacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha asignación")
    fecha_completada = models.DateTimeField(null=True, blank=True, verbose_name="Fecha completada")
    
    # Asignación
    tecnico_asignado = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='mantenimientos_asignados',
        verbose_name="Técnico asignado"
    )
    proveedor_asignado = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Proveedor asignado"
    )
    
    # Costos
    costo_estimado = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Costo estimado"
    )
    costo_real = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Costo real"
    )
    
    # Contacto alternativo
    contacto_alternativo_nombre = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Contacto alternativo"
    )
    contacto_alternativo_telefono = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Teléfono alternativo"
    )
    
    # Evaluación final
    calificacion = models.IntegerField(
        null=True, 
        blank=True, 
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name="Calificación (1-5)"
    )
    comentarios_evaluacion = models.TextField(
        blank=True, 
        verbose_name="Comentarios evaluación"
    )
    
    def save(self, *args, **kwargs):
        if not self.numero_solicitud:
            # Generar número de solicitud único
            last_solicitud = SolicitudMantenimiento.objects.order_by('id').last()
            if last_solicitud:
                last_number = int(last_solicitud.numero_solicitud.split('-')[-1])
                self.numero_solicitud = f"SOL-2025-{(last_number + 1):06d}"
            else:
                self.numero_solicitud = "SOL-2025-000001"
        
        # Establecer fecha límite basada en prioridad
        if not self.fecha_limite and self.categoria:
            horas = self.categoria.tiempo_respuesta_horas
            if self.prioridad == 'urgente':
                horas = min(horas, 4)
            elif self.prioridad == 'alta':
                horas = min(horas, 12)
            
            self.fecha_limite = self.fecha_solicitud + timedelta(hours=horas)
        
        super().save(*args, **kwargs)
    
    @property
    def tiempo_transcurrido(self):
        """Tiempo transcurrido desde la solicitud"""
        if self.fecha_completada:
            return self.fecha_completada - self.fecha_solicitud
        return timezone.now() - self.fecha_solicitud
    
    @property
    def dias_abierto(self):
        """Días que lleva abierta la solicitud"""
        return self.tiempo_transcurrido.days
    
    def __str__(self):
        return f"{self.numero_solicitud} - {self.titulo}"
    
    class Meta: # type: ignore
        verbose_name = "Solicitud de Mantenimiento"
        verbose_name_plural = "Solicitudes de Mantenimiento"
        ordering = ['-fecha_solicitud']


class OrdenTrabajo(BaseModel):
    """Órdenes de trabajo para ejecución de mantenimientos"""
    numero_orden = models.CharField(max_length=20, unique=True, verbose_name="Número orden")
    solicitud = models.OneToOneField(
        SolicitudMantenimiento, 
        on_delete=models.CASCADE,
        related_name='orden_trabajo',
        verbose_name="Solicitud"
    )
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado"
    )
    
    # Programación
    fecha_programada = models.DateTimeField(verbose_name="Fecha programada")
    fecha_inicio = models.DateTimeField(null=True, blank=True, verbose_name="Fecha inicio")
    fecha_finalizacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha finalización")
    
    # Tiempo estimado
    tiempo_estimado_horas = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Tiempo estimado (horas)"
    )
    tiempo_real_horas = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Tiempo real (horas)"
    )
    
    # Asignación
    tecnico_asignado = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='ordenes_trabajo_tecnico',
        verbose_name="Técnico asignado"
    )
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.CASCADE,
        verbose_name="Proveedor"
    )
    
    # Trabajo realizado
    descripcion_trabajo = models.TextField(
        blank=True, 
        verbose_name="Descripción trabajo realizado"
    )
    observaciones_iniciales = models.TextField(
        blank=True, 
        verbose_name="Observaciones iniciales"
    )
    recomendaciones = models.TextField(
        blank=True, 
        verbose_name="Recomendaciones"
    )
    
    # Garantía
    garantia_dias = models.IntegerField(default=30, verbose_name="Garantía (días)")
    fecha_vencimiento_garantia = models.DateField(null=True, blank=True, verbose_name="Vencimiento garantía")
    
    # Progreso
    progreso_porcentaje = models.IntegerField(default=0, verbose_name="Progreso (%)")
    
    def save(self, *args, **kwargs):
        if not self.numero_orden:
            # Generar número de orden único
            last_orden = OrdenTrabajo.objects.order_by('id').last()
            if last_orden:
                last_number = int(last_orden.numero_orden.split('-')[-1])
                self.numero_orden = f"OT-2025-{(last_number + 1):06d}"
            else:
                self.numero_orden = "OT-2025-000001"
        
        # Calcular fecha vencimiento garantía
        if self.fecha_finalizacion and self.garantia_dias:
            self.fecha_vencimiento_garantia = (
                self.fecha_finalizacion.date() + timedelta(days=self.garantia_dias)
            )
        
        super().save(*args, **kwargs)
    
    @property
    def tiempo_total_trabajado(self):
        """Tiempo total trabajado en la orden"""
        if self.fecha_inicio and self.fecha_finalizacion:
            delta = self.fecha_finalizacion - self.fecha_inicio
            return delta.total_seconds() / 3600  # horas
        elif self.fecha_inicio:
            delta = timezone.now() - self.fecha_inicio
            return delta.total_seconds() / 3600  # horas
        return 0
    
    def __str__(self):
        return f"{self.numero_orden} - {self.solicitud.titulo}"
    
    class Meta: # type: ignore
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ['-fecha_programada']


class MaterialInventario(BaseModel):
    """Inventario de materiales para mantenimiento"""
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    categoria = models.ForeignKey(
        CategoriaMantenimiento, 
        on_delete=models.CASCADE,
        verbose_name="Categoría"
    )
    
    # Stock
    stock_actual = models.IntegerField(default=0, verbose_name="Stock actual")
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock mínimo")
    stock_maximo = models.IntegerField(default=100, verbose_name="Stock máximo")
    
    UNIDAD_CHOICES = [
        ('unidad', 'Unidad'),
        ('metro', 'Metro'),
        ('kilogramo', 'Kilogramo'),
        ('litro', 'Litro'),
        ('caja', 'Caja'),
        ('rollo', 'Rollo'),
    ]
    unidad_medida = models.CharField(
        max_length=20, 
        choices=UNIDAD_CHOICES, 
        default='unidad',
        verbose_name="Unidad de medida"
    )
    
    # Costos
    costo_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Costo unitario"
    )
    
    # Proveedor
    proveedor_principal = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Proveedor principal"
    )
    
    # Ubicación en bodega
    ubicacion_bodega = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Ubicación en bodega"
    )
    
    # Estado
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    @property
    def valor_total_stock(self):
        """Valor total del stock actual"""
        return self.stock_actual * self.costo_unitario
    
    @property
    def alerta_stock_bajo(self):
        """Indica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta: # type: ignore
        verbose_name = "Material de Inventario"
        verbose_name_plural = "Materiales de Inventario"
        ordering = ['codigo']


class MovimientoInventario(BaseModel):
    """Movimientos de entrada y salida de inventario"""
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    material = models.ForeignKey(
        MaterialInventario, 
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name="Material"
    )
    
    cantidad = models.IntegerField(verbose_name="Cantidad")
    costo_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Costo unitario"
    )
    
    # Referencias
    orden_trabajo = models.ForeignKey(
        OrdenTrabajo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='materiales_usados',
        verbose_name="Orden de trabajo"
    )
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Proveedor"
    )
    
    # Información adicional
    lote = models.CharField(max_length=100, blank=True, verbose_name="Lote")
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name="Fecha vencimiento")
    numero_factura = models.CharField(max_length=100, blank=True, verbose_name="Número factura")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    # Usuario responsable
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuario responsable"
    )
    
    @property
    def valor_total(self):
        """Valor total del movimiento"""
        if self.costo_unitario:
            return self.cantidad * self.costo_unitario
        return self.cantidad * self.material.costo_unitario
    
    def save(self, *args, **kwargs):
        # Actualizar stock del material
        if self.pk is None:  # Nuevo movimiento
            if self.tipo == 'entrada':
                self.material.stock_actual += self.cantidad
            elif self.tipo == 'salida':
                self.material.stock_actual -= self.cantidad
            elif self.tipo == 'ajuste':
                # El ajuste reemplaza el stock actual
                self.material.stock_actual = self.cantidad
            
            self.material.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tipo} - {self.material.nombre} ({self.cantidad})"
    
    class Meta: # type: ignore
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-created_at']


class MantenimientoPreventivo(BaseModel):
    """Programación de mantenimientos preventivos"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    
    # Equipo o área
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    equipo_area = GenericForeignKey('content_type', 'object_id')
    
    # Programación
    FRECUENCIA_CHOICES = [
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    frecuencia = models.CharField(
        max_length=20, 
        choices=FRECUENCIA_CHOICES,
        verbose_name="Frecuencia"
    )
    
    fecha_inicio = models.DateField(verbose_name="Fecha inicio")
    ultima_ejecucion = models.DateField(null=True, blank=True, verbose_name="Última ejecución")
    proxima_ejecucion = models.DateField(verbose_name="Próxima ejecución")
    
    # Proveedor responsable
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.CASCADE,
        verbose_name="Proveedor responsable"
    )
    
    # Costos
    costo_estimado = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Costo estimado"
    )
    
    # Estado
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    # Recordatorios
    dias_recordatorio = models.CharField(
        max_length=50, 
        default="30,7,1", 
        verbose_name="Días de recordatorio (separados por coma)"
    )
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código único
            last_preventivo = MantenimientoPreventivo.objects.order_by('id').last()
            if last_preventivo:
                last_number = int(last_preventivo.codigo.split('-')[-1])
                self.codigo = f"PREV-2025-{(last_number + 1):03d}"
            else:
                self.codigo = "PREV-2025-001"
        
        super().save(*args, **kwargs)
    
    @property
    def dias_hasta_vencimiento(self):
        """Días hasta la próxima ejecución"""
        if self.proxima_ejecucion:
            delta = self.proxima_ejecucion - timezone.now().date()
            return delta.days
        return 0
    
    @property
    def requiere_recordatorio(self):
        """Verifica si requiere envío de recordatorio"""
        dias_recordatorio = [int(d.strip()) for d in self.dias_recordatorio.split(',') if d.strip().isdigit()]
        return self.dias_hasta_vencimiento in dias_recordatorio
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta: # type: ignore
        verbose_name = "Mantenimiento Preventivo"
        verbose_name_plural = "Mantenimientos Preventivos"
        ordering = ['proxima_ejecucion']


# Mantener el modelo original para compatibilidad (deprecated)
class Mantenimiento(BaseModel):
    """DEPRECATED: Usar SolicitudMantenimiento en su lugar"""
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
        related_name='mantenimientos_asignados_legacy',
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
        verbose_name = "Mantenimiento (Legacy)"
        verbose_name_plural = "Mantenimientos (Legacy)"
        ordering = ['-fecha_solicitud']
