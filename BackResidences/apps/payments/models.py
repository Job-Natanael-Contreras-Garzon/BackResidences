from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.residences.models import Vivienda

# Evitar imports circulares
if TYPE_CHECKING:
    from django.db.models import QuerySet


class ConceptoPago(BaseModel):
    """Conceptos de pago disponibles en el condominio"""
    
    # Relación inversa para type hints
    if TYPE_CHECKING:
        facturas: 'QuerySet[Factura]'
    
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('fijo', 'Fijo'),
            ('variable', 'Variable'),
            ('extraordinario', 'Extraordinario'),
        ],
        default='fijo',
        verbose_name="Tipo"
    )
    valor_base = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Valor base",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    es_obligatorio = models.BooleanField(default=True, verbose_name="Es obligatorio")
    frecuencia = models.CharField(
        max_length=20,
        choices=[
            ('mensual', 'Mensual'),
            ('bimestral', 'Bimestral'),
            ('trimestral', 'Trimestral'),
            ('semestral', 'Semestral'),
            ('anual', 'Anual'),
            ('unica', 'Única vez'),
        ],
        default='mensual',
        verbose_name="Frecuencia"
    )
    aplica_a_todos = models.BooleanField(default=True, verbose_name="Aplica a todas las viviendas")
    fecha_inicio = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de inicio")
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de fin")
    criterios_aplicacion = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name="Criterios de aplicación"
    )
    porcentaje_interes_mora = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('2.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('99.99'))],
        verbose_name="Porcentaje interés mora"
    )

    def __str__(self):
        return self.nombre

    @property
    def total_facturas_generadas(self):
        """Total de facturas generadas para este concepto"""
        return self.facturas.count()
        
    @property
    def total_recaudado(self):
        """Total recaudado para este concepto"""
        return self.facturas.filter(estado='pagada').aggregate(
            total=models.Sum('monto_total')
        )['total'] or Decimal('0.00')

    class Meta:  # type: ignore
        verbose_name = "Concepto de Pago"
        verbose_name_plural = "Conceptos de Pago"
        ordering = ['nombre']


class MetodoPago(BaseModel):
    """Métodos de pago disponibles"""
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    descripcion = models.TextField(verbose_name="Descripción")
    requiere_referencia = models.BooleanField(default=False, verbose_name="Requiere referencia")
    requiere_comprobante = models.BooleanField(default=False, verbose_name="Requiere comprobante")
    configuracion = models.JSONField(default=dict, blank=True, verbose_name="Configuración")
    comision_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('99.99'))],
        verbose_name="Comisión (%)"
    )
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    def __str__(self):
        return self.nombre

    class Meta:  # type: ignore
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['orden', 'nombre']


class Factura(BaseModel):
    """Facturas generadas para las viviendas"""
    numero_factura = models.CharField(max_length=50, unique=True, verbose_name="Número de factura")
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, verbose_name="Vivienda")
    concepto = models.ForeignKey(
        ConceptoPago, 
        on_delete=models.CASCADE, 
        related_name='facturas',
        verbose_name="Concepto"
    )
    periodo = models.CharField(max_length=7, verbose_name="Periodo (YYYY-MM)")  # 2025-10
    fecha_generacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de generación")
    fecha_vencimiento = models.DateTimeField(verbose_name="Fecha de vencimiento")
    monto_original = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Monto original",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    descuentos = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Descuentos"
    )
    intereses = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Intereses por mora"
    )
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto total")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('generada', 'Generada'),
            ('pendiente', 'Pendiente'),
            ('parcialmente_pagada', 'Parcialmente Pagada'),
            ('pagada', 'Pagada'),
            ('vencida', 'Vencida'),
            ('anulada', 'Anulada'),
        ],
        default='generada',
        verbose_name="Estado"
    )
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Saldo pendiente")
    observaciones = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    archivo_pdf = models.URLField(null=True, blank=True, verbose_name="Archivo PDF")
    
    # Auditoría
    generada_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='facturas_generadas',
        verbose_name="Generada por"
    )

    def save(self, *args, **kwargs):
        # Calcular monto total y saldo pendiente
        self.monto_total = self.monto_original + self.intereses - self.descuentos
        if not self.pk:  # Nueva factura
            self.saldo_pendiente = self.monto_total
        super().save(*args, **kwargs)
        
    def calcular_intereses_mora(self):
        """Calcular intereses por mora si la factura está vencida"""
        if self.fecha_vencimiento < timezone.now() and self.saldo_pendiente > 0:
            dias_vencido = (timezone.now() - self.fecha_vencimiento).days
            if dias_vencido > 0:
                interes_diario = self.concepto.porcentaje_interes_mora / Decimal('30')  # Por día
                interes = self.monto_original * (interes_diario / Decimal('100')) * dias_vencido
                self.intereses = interes
                self.save()
                
    @property
    def dias_vencido(self):
        """Número de días vencido"""
        if self.fecha_vencimiento < timezone.now():
            return (timezone.now() - self.fecha_vencimiento).days
        return 0
        
    @property
    def tiene_descuentos(self):
        return self.descuentos > 0
        
    @property
    def tiene_intereses(self):
        return self.intereses > 0

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.vivienda.identificador}"

    class Meta:  # type: ignore
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha_generacion']
        unique_together = ['vivienda', 'concepto', 'periodo']


class Pago(BaseModel):
    """Pagos realizados"""
    numero_pago = models.CharField(max_length=50, unique=True, verbose_name="Número de pago")
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, verbose_name="Vivienda")
    monto_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Monto total",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    metodo_pago = models.ForeignKey(
        MetodoPago, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Método de pago"
    )
    numero_referencia = models.CharField(max_length=100, blank=True, verbose_name="Número de referencia")
    fecha_pago = models.DateTimeField(verbose_name="Fecha de pago")
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha de registro")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmado', 'Confirmado'),
            ('rechazado', 'Rechazado'),
            ('reversado', 'Reversado'),
        ],
        default='pendiente',
        verbose_name="Estado"
    )
    observaciones = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    archivo_comprobante = models.URLField(null=True, blank=True, verbose_name="Archivo comprobante")
    
    # Auditoría y control
    registrado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='pagos_registrados',
        verbose_name="Registrado por"
    )
    confirmado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='pagos_confirmados',
        verbose_name="Confirmado por"
    )
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de confirmación")
    
    # Reverso
    reversado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='pagos_reversados',
        verbose_name="Reversado por"
    )
    fecha_reverso = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de reverso")
    motivo_reverso = models.TextField(null=True, blank=True, verbose_name="Motivo del reverso")

    def __str__(self):
        return f"Pago {self.numero_pago} - {self.vivienda.identificador}"

    class Meta:  # type: ignore
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_registro']


class PagoFactura(BaseModel):
    """Relación entre pagos y facturas (un pago puede cubrir múltiples facturas)"""
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, verbose_name="Pago")
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, verbose_name="Factura")
    monto_aplicado = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Monto aplicado",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    fecha_aplicacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de aplicación")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar saldo de la factura
        self.factura.saldo_pendiente = max(
            Decimal('0.00'), 
            self.factura.saldo_pendiente - self.monto_aplicado
        )
        
        # Actualizar estado de la factura
        if self.factura.saldo_pendiente == 0:
            self.factura.estado = 'pagada'
        elif self.factura.saldo_pendiente < self.factura.monto_total:
            self.factura.estado = 'parcialmente_pagada'
            
        self.factura.save()

    def __str__(self):
        return f"Aplicación {self.pago.numero_pago} -> {self.factura.numero_factura}"

    class Meta:  # type: ignore
        verbose_name = "Pago Factura"
        verbose_name_plural = "Pagos Facturas"
        unique_together = ['pago', 'factura']


class PazYSalvo(BaseModel):
    """Documentos de paz y salvo generados"""
    numero_documento = models.CharField(max_length=50, unique=True, verbose_name="Número de documento")
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, verbose_name="Vivienda")
    fecha_corte = models.DateTimeField(verbose_name="Fecha de corte")
    fecha_generacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de generación")
    fecha_vencimiento = models.DateTimeField(verbose_name="Fecha de vencimiento")
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Saldo pendiente")
    observaciones = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    archivo_pdf = models.URLField(null=True, blank=True, verbose_name="Archivo PDF")
    codigo_verificacion = models.CharField(max_length=50, unique=True, verbose_name="Código de verificación")
    
    # Auditoría
    generado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Generado por"
    )
    
    def save(self, *args, **kwargs):
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = self.fecha_generacion + timedelta(days=30)
        super().save(*args, **kwargs)
    
    @property
    def es_valido(self):
        """Verificar si el paz y salvo aún es válido"""
        return timezone.now() <= self.fecha_vencimiento and self.saldo_pendiente == 0

    def __str__(self):
        return f"Paz y Salvo {self.numero_documento} - {self.vivienda.identificador}"

    class Meta:  # type: ignore
        verbose_name = "Paz y Salvo"
        verbose_name_plural = "Paz y Salvos"
        ordering = ['-fecha_generacion']


# Mantener modelos existentes por compatibilidad
class TipoPago(BaseModel):
    """Tipos de pago disponibles (modelo legacy)"""
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    requiere_comprobante = models.BooleanField(default=False, verbose_name="Requiere comprobante")
    verificacion_automatica = models.BooleanField(default=False, verbose_name="Verificación automática")

    def __str__(self):
        return self.nombre

    class Meta:  # type: ignore
        verbose_name = "Tipo de Pago"
        verbose_name_plural = "Tipos de Pago"


class Deuda(BaseModel):
    """Deudas por vivienda (modelo legacy)"""
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, verbose_name="Vivienda")
    periodo_mes = models.IntegerField(verbose_name="Mes del período")
    periodo_ano = models.IntegerField(verbose_name="Año del período")
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto total")
    fecha_emision = models.DateField(verbose_name="Fecha de emisión")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de vencimiento")
    interes_mora = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name="Interés por mora (%)")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Descuento")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('parcial', 'Pago Parcial'),
            ('pagada', 'Pagada'),
            ('vencida', 'Vencida'),
        ],
        default='pendiente',
        verbose_name="Estado"
    )
    numero_factura = models.CharField(max_length=50, unique=True, verbose_name="Número de factura")
    observaciones = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    def __str__(self):
        return f"Deuda {self.numero_factura} - {self.vivienda.identificador}"

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Deuda"
        verbose_name_plural = "Deudas"
        unique_together = ['vivienda', 'periodo_mes', 'periodo_ano']


class DetalleDeuda(BaseModel):
    """Detalle de conceptos por deuda (modelo legacy)"""
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, related_name='detalles', verbose_name="Deuda")
    concepto = models.CharField(max_length=100, verbose_name="Concepto")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'), verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto")
    detalle = models.TextField(blank=True, verbose_name="Detalle")
    periodo_consumo = models.CharField(max_length=50, null=True, blank=True, verbose_name="Período de consumo")
    base_calculo = models.CharField(max_length=20, null=True, blank=True, verbose_name="Base de cálculo")

    def save(self, *args, **kwargs):
        """Calcular monto automáticamente"""
        self.monto = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.concepto} - {self.deuda.numero_factura}"

    class Meta:  # type: ignore
        verbose_name = "Detalle de Deuda"
        verbose_name_plural = "Detalles de Deuda"