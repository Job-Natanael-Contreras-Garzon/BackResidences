from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel
from apps.authentication.models import User

class AreaComun(BaseModel):
    """Áreas comunes del condominio"""
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    capacidad = models.IntegerField(verbose_name="Capacidad (personas)")
    capacidad_vehiculos = models.IntegerField(null=True, blank=True, verbose_name="Capacidad de vehículos")
    precio_hora = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por hora")
    precio_dia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio por día")
    servicios_incluidos = models.JSONField(default=list, blank=True, verbose_name="Servicios incluidos")
    normas_uso = models.TextField(blank=True, verbose_name="Normas de uso")
    deposito_garantia = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Depósito de garantía")
    foto_url = models.URLField(null=True, blank=True, verbose_name="Foto")
    tipo_reserva = models.CharField(
        max_length=20,
        choices=[
            ('por_horas', 'Por horas'),
            ('por_dias', 'Por días'),
            ('eventos', 'Eventos'),
        ],
        verbose_name="Tipo de reserva"
    )

    def __str__(self):
        return self.nombre

    class Meta: # type: ignore
        verbose_name = "Área Común"
        verbose_name_plural = "Áreas Comunes"

class HorarioArea(BaseModel):
    """Horarios disponibles por área común"""
    area_comun = models.ForeignKey(AreaComun, on_delete=models.CASCADE, verbose_name="Área común")
    dia_semana = models.IntegerField(
        choices=[
            (1, 'Lunes'),
            (2, 'Martes'),
            (3, 'Miércoles'),
            (4, 'Jueves'),
            (5, 'Viernes'),
            (6, 'Sábado'),
            (7, 'Domingo'),
        ],
        verbose_name="Día de la semana"
    )
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")

    class Meta: # type: ignore
        unique_together = ['area_comun', 'dia_semana', 'hora_inicio', 'hora_fin']
        verbose_name = "Horario de Área"
        verbose_name_plural = "Horarios de Áreas"

    def __str__(self):
        return f"{self.area_comun.nombre} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}" # pyright: ignore[reportAttributeAccessIssue]

class Reserva(BaseModel):
    """Reservas de áreas comunes"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    area_comun = models.ForeignKey(AreaComun, on_delete=models.CASCADE, verbose_name="Área común")
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de fin")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto total")
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Monto pagado")
    metodo_pago = models.CharField(max_length=30, null=True, blank=True, verbose_name="Método de pago")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada'),
            ('completada', 'Completada'),
        ],
        default='pendiente',
        verbose_name="Estado"
    )
    motivo_evento = models.CharField(max_length=200, blank=True, verbose_name="Motivo del evento")
    numero_personas = models.IntegerField(null=True, blank=True, verbose_name="Número de personas")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    cancelada_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reservas_canceladas',
        verbose_name="Cancelada por"
    )
    fecha_cancelacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de cancelación")

    def __str__(self):
        return f'Reserva {self.pk} - {self.area_comun.nombre} - {self.usuario.username}'

    class Meta: # type: ignore
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_creacion']