from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.residences.models import Vivienda

class TipoPago(BaseModel):
    """Tipos de pago disponibles"""
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    requiere_comprobante = models.BooleanField(default=False, verbose_name="Requiere comprobante")
    verificacion_automatica = models.BooleanField(default=False, verbose_name="Verificación automática")

    def __str__(self):
        return self.nombre

    class Meta: # type: ignore
        verbose_name = "Tipo de Pago"
        verbose_name_plural = "Tipos de Pago"

class Deuda(BaseModel):
    """Deudas por vivienda"""
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

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Deuda"
        verbose_name_plural = "Deudas"
        unique_together = ['vivienda', 'periodo_mes', 'periodo_ano']

class DetalleDeuda(BaseModel):
    """Detalle de conceptos por deuda"""
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

    class Meta: # type: ignore
        verbose_name = "Detalle de Deuda"
        verbose_name_plural = "Detalles de Deuda"

class Pago(BaseModel):
    """Pagos realizados"""
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, verbose_name="Deuda")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario que registra")
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE, verbose_name="Tipo de pago")
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto pagado")
    fecha_pago = models.DateField(verbose_name="Fecha de pago")
    numero_referencia = models.CharField(max_length=100, blank=True, verbose_name="Número de referencia")
    comprobante_url = models.URLField(null=True, blank=True, verbose_name="Comprobante")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('verificado', 'Verificado'),
            ('rechazado', 'Rechazado'),
        ],
        default='pendiente',
        verbose_name="Estado"
    )
    verificado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='pagos_verificados',
        verbose_name="Verificado por"
    )
    fecha_verificacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de verificación")
    observaciones = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    def __str__(self):
        return f"Pago {self.pk} - {self.deuda.numero_factura}"

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"