from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, date, time
from decimal import Decimal
from .models import AreaComun, HorarioArea, Reserva

User = get_user_model()

# =================== SERIALIZERS BÁSICOS ===================

class HorarioAreaSerializer(serializers.ModelSerializer):
    """Serializer para horarios de áreas comunes"""
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)
    
    class Meta:
        model = HorarioArea
        fields = [
            'id', 'dia_semana', 'dia_semana_display', 
            'hora_inicio', 'hora_fin', 'activo'
        ]

# =================== SERIALIZERS PARA ÁREAS COMUNES ===================

class AreaComunListSerializer(serializers.ModelSerializer):
    """Serializer para lista de áreas comunes"""
    disponible_hoy = serializers.SerializerMethodField()
    proxima_disponibilidad = serializers.SerializerMethodField()
    reservas_activas = serializers.SerializerMethodField()
    total_reservas_mes = serializers.SerializerMethodField()
    equipamiento = serializers.SerializerMethodField()
    imagen_principal = serializers.SerializerMethodField()
    
    class Meta:
        model = AreaComun
        fields = [
            'id', 'nombre', 'descripcion', 'tipo_reserva',
            'capacidad', 'precio_hora', 'deposito_garantia',
            'disponible_hoy', 'proxima_disponibilidad',
            'reservas_activas', 'total_reservas_mes',
            'equipamiento', 'imagen_principal', 'activo'
        ]
    
    def get_disponible_hoy(self, obj):
        """Verificar si el área está disponible hoy"""
        hoy = date.today()
        dia_semana = hoy.isoweekday()  # 1=Lunes, 7=Domingo
        
        # Verificar si hay horarios configurados para hoy
        horarios_hoy = HorarioArea.objects.filter(
            area_comun=obj,
            dia_semana=dia_semana,
            activo=True
        ).exists()
        
        if not horarios_hoy:
            return False
            
        # Verificar si hay conflictos con reservas
        reservas_hoy = Reserva.objects.filter(
            area_comun=obj,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
            estado__in=['confirmada', 'en_uso']
        ).exists()
        
        return not reservas_hoy
    
    def get_proxima_disponibilidad(self, obj):
        """Obtener próxima fecha/hora disponible"""
        # Implementación simplificada - devuelve mañana a las 8:00
        mañana = date.today() + timezone.timedelta(days=1)
        return datetime.combine(mañana, time(8, 0)).isoformat() + 'Z'
    
    def get_reservas_activas(self, obj):
        """Contar reservas activas (confirmadas o en uso)"""
        return Reserva.objects.filter(
            area_comun=obj,
            estado__in=['confirmada', 'en_uso']
        ).count()
    
    def get_total_reservas_mes(self, obj):
        """Contar reservas del mes actual"""
        hoy = date.today()
        return Reserva.objects.filter(
            area_comun=obj,
            fecha_inicio__year=hoy.year,
            fecha_inicio__month=hoy.month
        ).count()
    
    def get_equipamiento(self, obj):
        """Obtener lista de equipamiento"""
        return obj.servicios_incluidos if obj.servicios_incluidos else []
    
    def get_imagen_principal(self, obj):
        """Obtener imagen principal del área"""
        return obj.foto_url if obj.foto_url else None

class AreaComunDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para área común"""
    horarios = HorarioAreaSerializer(source='horarioarea_set', many=True, read_only=True)
    equipamiento = serializers.SerializerMethodField()
    normas_uso_lista = serializers.SerializerMethodField()
    imagenes = serializers.SerializerMethodField()
    contacto_administracion = serializers.SerializerMethodField()
    estadisticas = serializers.SerializerMethodField()
    
    class Meta:
        model = AreaComun
        fields = [
            'id', 'nombre', 'descripcion', 'tipo_reserva',
            'capacidad', 'precio_hora', 'precio_dia',
            'deposito_garantia', 'horarios', 'equipamiento',
            'normas_uso_lista', 'imagenes', 'contacto_administracion',
            'estadisticas', 'fecha_creacion', 'activo'
        ]
    
    def get_equipamiento(self, obj):
        """Lista detallada de equipamiento"""
        return obj.servicios_incluidos if obj.servicios_incluidos else []
    
    def get_normas_uso_lista(self, obj):
        """Convertir normas de uso en lista"""
        if obj.normas_uso:
            return obj.normas_uso.split('\n')
        return []
    
    def get_imagenes(self, obj):
        """Lista de imágenes del área"""
        imagenes = []
        if obj.foto_url:
            imagenes.append(obj.foto_url)
        return imagenes
    
    def get_contacto_administracion(self, obj):
        """Información de contacto de administración"""
        return {
            "responsable": "Administración",
            "telefono": "+573000000000",
            "extension": "100"
        }
    
    def get_estadisticas(self, obj):
        """Estadísticas del área"""
        hoy = date.today()
        mes_actual = Reserva.objects.filter(
            area_comun=obj,
            fecha_inicio__year=hoy.year,
            fecha_inicio__month=hoy.month
        ).count()
        
        mes_anterior_mes = hoy.month - 1 if hoy.month > 1 else 12
        mes_anterior_año = hoy.year if hoy.month > 1 else hoy.year - 1
        
        mes_anterior = Reserva.objects.filter(
            area_comun=obj,
            fecha_inicio__year=mes_anterior_año,
            fecha_inicio__month=mes_anterior_mes
        ).count()
        
        return {
            "reservas_mes_actual": mes_actual,
            "reservas_mes_anterior": mes_anterior,
            "promedio_duracion": 4.5,  # Placeholder
            "ocupacion_porcentaje": 65.0  # Placeholder
        }

class AreaComunCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear áreas comunes"""
    
    class Meta:
        model = AreaComun
        fields = [
            'nombre', 'descripcion', 'tipo_reserva',
            'capacidad', 'capacidad_vehiculos', 'precio_hora',
            'precio_dia', 'servicios_incluidos', 'normas_uso',
            'deposito_garantia', 'foto_url'
        ]
    
    def validate_nombre(self, value):
        """Validar que el nombre no esté duplicado"""
        if AreaComun.objects.filter(nombre=value, activo=True).exists():
            raise serializers.ValidationError("Ya existe un área común con este nombre")
        return value
    
    def validate_capacidad(self, value):
        """Validar capacidad mínima"""
        if value < 1:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0")
        return value
    
    def validate_precio_hora(self, value):
        """Validar precio por hora"""
        if value < 0:
            raise serializers.ValidationError("El precio por hora no puede ser negativo")
        return value

class AreaComunUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar áreas comunes"""
    
    class Meta:
        model = AreaComun
        fields = [
            'descripcion', 'capacidad', 'capacidad_vehiculos',
            'precio_hora', 'precio_dia', 'servicios_incluidos',
            'normas_uso', 'deposito_garantia', 'foto_url', 'activo'
        ]

# =================== SERIALIZERS PARA RESERVAS ===================

class ReservaListSerializer(serializers.ModelSerializer):
    """Serializer para lista de reservas"""
    area = serializers.SerializerMethodField()
    usuario_info = serializers.SerializerMethodField()
    duracion_horas = serializers.SerializerMethodField()
    estado_pago = serializers.SerializerMethodField()
    dias_restantes = serializers.SerializerMethodField()
    puede_cancelar = serializers.SerializerMethodField()
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'area', 'usuario_info', 'fecha_inicio', 'fecha_fin',
            'hora_inicio', 'hora_fin', 'duracion_horas', 'motivo_evento',
            'numero_personas', 'estado', 'monto_total', 'estado_pago',
            'fecha_creacion', 'dias_restantes', 'puede_cancelar'
        ]
    
    def get_area(self, obj):
        """Información del área"""
        return {
            "id": obj.area_comun.id,
            "nombre": obj.area_comun.nombre,
            "tipo": obj.area_comun.tipo_reserva
        }
    
    def get_usuario_info(self, obj):
        """Información del usuario"""
        # Obtener vivienda del usuario si existe
        vivienda = "N/A"
        try:
            # Verificar si el usuario es propietario
            from apps.residences.models import Vivienda
            vivienda_prop = Vivienda.objects.filter(usuario_propietario=obj.usuario, activo=True).first()
            if vivienda_prop:
                vivienda = vivienda_prop.identificador
            else:
                # Verificar si es inquilino
                vivienda_inq = Vivienda.objects.filter(usuario_inquilino=obj.usuario, activo=True).first()
                if vivienda_inq:
                    vivienda = vivienda_inq.identificador
        except:
            pass
        
        return {
            "id": obj.usuario.id,
            "full_name": obj.usuario.get_full_name(),
            "vivienda": vivienda
        }
    
    def get_duracion_horas(self, obj):
        """Calcular duración en horas"""
        inicio = datetime.combine(obj.fecha_inicio, obj.hora_inicio)
        fin = datetime.combine(obj.fecha_fin, obj.hora_fin)
        duracion = fin - inicio
        return round(duracion.total_seconds() / 3600, 1)
    
    def get_estado_pago(self, obj):
        """Estado del pago"""
        if obj.monto_total == 0:
            return "no_aplica"
        elif obj.monto_pagado >= obj.monto_total:
            return "pagado"
        elif obj.monto_pagado > 0:
            return "parcial"
        else:
            return "pendiente"
    
    def get_dias_restantes(self, obj):
        """Días restantes para la reserva"""
        if obj.fecha_inicio <= date.today():
            return 0
        return (obj.fecha_inicio - date.today()).days
    
    def get_puede_cancelar(self, obj):
        """Verificar si se puede cancelar"""
        if obj.estado in ['cancelada', 'completada']:
            return False
        return obj.fecha_inicio > date.today()

class ReservaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reservas"""
    contacto_emergencia = serializers.JSONField(required=False)
    servicios_adicionales = serializers.ListField(
        child=serializers.CharField(), 
        required=False,
        default=list
    )
    
    class Meta:
        model = Reserva
        fields = [
            'area_comun', 'fecha_inicio', 'fecha_fin',
            'hora_inicio', 'hora_fin', 'motivo_evento',
            'numero_personas', 'contacto_emergencia',
            'servicios_adicionales'
        ]
    
    def validate(self, attrs):
        """Validaciones complejas"""
        area_comun = attrs['area_comun']
        fecha_inicio = attrs['fecha_inicio']
        fecha_fin = attrs['fecha_fin']
        hora_inicio = attrs['hora_inicio']
        hora_fin = attrs['hora_fin']
        numero_personas = attrs.get('numero_personas', 0)
        
        # Validar que las fechas sean futuras
        if fecha_inicio < date.today():
            raise serializers.ValidationError("La fecha de inicio no puede ser en el pasado")
        
        # Validar que fecha fin >= fecha inicio
        if fecha_fin < fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser mayor o igual a la fecha de inicio")
        
        # Validar que hora fin > hora inicio (mismo día)
        if fecha_inicio == fecha_fin and hora_fin <= hora_inicio:
            raise serializers.ValidationError("La hora de fin debe ser mayor a la hora de inicio")
        
        # Validar capacidad
        if numero_personas and numero_personas > area_comun.capacidad:
            raise serializers.ValidationError(f"El número de personas excede la capacidad máxima ({area_comun.capacidad})")
        
        # Validar disponibilidad (verificar conflictos)
        conflictos = Reserva.objects.filter(
            area_comun=area_comun,
            estado__in=['confirmada', 'en_uso'],
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio
        )
        
        # Filtrar por horarios que se solapan
        for reserva in conflictos:
            if self._horarios_se_solapan(
                hora_inicio, hora_fin,
                reserva.hora_inicio, reserva.hora_fin,
                fecha_inicio, fecha_fin,
                reserva.fecha_inicio, reserva.fecha_fin
            ):
                raise serializers.ValidationError("Ya existe una reserva confirmada en ese horario")
        
        return attrs
    
    def _horarios_se_solapan(self, h1_inicio, h1_fin, h2_inicio, h2_fin, f1_inicio, f1_fin, f2_inicio, f2_fin):
        """Verificar si dos horarios se solapan"""
        # Si las fechas no se solapan, no hay conflicto
        if f1_fin < f2_inicio or f2_fin < f1_inicio:
            return False
        
        # Si hay solapamiento de fechas, verificar horarios
        if f1_inicio == f2_inicio and f1_fin == f2_fin:
            # Mismo día, verificar horarios
            return not (h1_fin <= h2_inicio or h2_fin <= h1_inicio)
        
        # Para casos de múltiples días, considerar solapamiento
        return True
    
    def create(self, validated_data):
        """Crear reserva calculando el monto"""
        # Extraer datos adicionales
        contacto_emergencia = validated_data.pop('contacto_emergencia', {})
        servicios_adicionales = validated_data.pop('servicios_adicionales', [])
        
        # Asignar usuario del contexto
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        
        # Calcular monto total
        area_comun = validated_data['area_comun']
        duracion = self._calcular_duracion(
            validated_data['fecha_inicio'],
            validated_data['fecha_fin'],
            validated_data['hora_inicio'],
            validated_data['hora_fin']
        )
        
        if area_comun.tipo_reserva == 'por_horas':
            monto_base = area_comun.precio_hora * Decimal(str(duracion))
        else:
            dias = (validated_data['fecha_fin'] - validated_data['fecha_inicio']).days + 1
            monto_base = area_comun.precio_dia * Decimal(str(dias)) if area_comun.precio_dia else area_comun.precio_hora * Decimal(str(duracion))
        
        validated_data['monto_total'] = monto_base
        
        # Crear reserva
        reserva = super().create(validated_data)
        
        # Aquí podrías guardar información adicional en campos JSON o tablas relacionadas
        # Por ahora simplificamos
        
        return reserva
    
    def _calcular_duracion(self, fecha_inicio, fecha_fin, hora_inicio, hora_fin):
        """Calcular duración en horas"""
        inicio = datetime.combine(fecha_inicio, hora_inicio)
        fin = datetime.combine(fecha_fin, hora_fin)
        duracion = fin - inicio
        return duracion.total_seconds() / 3600

# =================== SERIALIZERS PARA REPORTES ===================

class DisponibilidadSerializer(serializers.Serializer):
    """Serializer para consultar disponibilidad"""
    fecha = serializers.DateField()
    dia_semana = serializers.CharField()
    disponible = serializers.BooleanField()
    horarios_libres = serializers.ListField(child=serializers.DictField())
    reservas_existentes = serializers.ListField(child=serializers.DictField())

class DashboardAreasSerializer(serializers.Serializer):
    """Serializer para dashboard de áreas comunes"""
    periodo = serializers.CharField()
    resumen_general = serializers.DictField()
    areas_mas_usadas = serializers.ListField(child=serializers.DictField())
    ocupacion_por_dia = serializers.ListField(child=serializers.DictField())
    horarios_pico = serializers.ListField(child=serializers.DictField())

# Mantener compatibilidad con nombres antiguos
AreaComunSerializer = AreaComunListSerializer
ReservaSerializer = ReservaListSerializer