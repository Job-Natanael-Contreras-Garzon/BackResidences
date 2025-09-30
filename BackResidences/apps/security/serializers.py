from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
from typing import Dict, Any

from .models import (
    TipoEvento, Zona, Camara, VehiculoAutorizado, 
    EventoSeguridad, CredentialAcceso
)

User = get_user_model()


# =================== SERIALIZERS BÁSICOS ===================

class UsuarioBasicoSerializer(serializers.ModelSerializer):
    """Serializer básico para información de usuario"""
    full_name = serializers.SerializerMethodField()
    vivienda = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'documento_numero', 'vivienda']
        
    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}".strip()
        
    def get_vivienda(self, obj) -> str | None:
        # Obtener vivienda del usuario (propietario o inquilino)
        from apps.residences.models import Vivienda
        vivienda = Vivienda.objects.filter(
            models.Q(usuario_propietario=obj) | models.Q(usuario_inquilino=obj)
        ).first()
        return vivienda.identificador if vivienda else None


class TipoEventoSerializer(serializers.ModelSerializer):
    """Serializer para tipos de evento"""
    eventos_count = serializers.SerializerMethodField()
    severidad_texto = serializers.SerializerMethodField()
    
    class Meta:
        model = TipoEvento
        fields = [
            'id', 'nombre', 'descripcion', 'severidad', 'severidad_texto',
            'eventos_count', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def get_eventos_count(self, obj) -> int:
        return obj.eventoseguridad_set.count()
        
    def get_severidad_texto(self, obj) -> str:
        severidades = {1: 'Baja', 2: 'Media', 3: 'Alta', 4: 'Crítica'}
        return severidades.get(obj.severidad, 'Desconocida')


class ZonaListSerializer(serializers.ModelSerializer):
    """Serializer para listado de zonas"""
    camaras_count = serializers.SerializerMethodField()
    eventos_hoy = serializers.SerializerMethodField()
    
    class Meta:
        model = Zona
        fields = [
            'id', 'nombre', 'tipo', 'descripcion', 'nivel_seguridad',
            'camaras_count', 'eventos_hoy', 'activo'
        ]
        
    def get_camaras_count(self, obj) -> int:
        return obj.camara_set.filter(activo=True).count()
        
    def get_eventos_hoy(self, obj) -> int:
        hoy = timezone.now().date()
        return EventoSeguridad.objects.filter(
            camara__zona=obj,
            fecha_hora__date=hoy
        ).count()


class CamaraListSerializer(serializers.ModelSerializer):
    """Serializer para listado de cámaras"""
    zona_info = serializers.SerializerMethodField()
    estado_conexion = serializers.SerializerMethodField()
    
    class Meta:
        model = Camara
        fields = [
            'id', 'nombre', 'ubicacion', 'zona_info', 'direccion_ip', 'puerto',
            'url_stream', 'modelo', 'resolucion', 'vision_nocturna', 
            'angulo_vision', 'fecha_instalacion', 'ultimo_mantenimiento',
            'estado_conexion', 'activo'
        ]
        
    def get_zona_info(self, obj) -> Dict[str, Any]:
        return {
            'id': obj.zona.pk,
            'nombre': obj.zona.nombre,
            'tipo': obj.zona.tipo
        }
        
    def get_estado_conexion(self, obj) -> str:
        # Placeholder para estado de conexión real
        return "online"  # En implementación real, verificar conectividad


class CamaraDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para cámaras"""
    zona_info = ZonaListSerializer(source='zona', read_only=True)
    eventos_recientes = serializers.SerializerMethodField()
    
    class Meta:
        model = Camara
        fields = [
            'id', 'nombre', 'ubicacion', 'zona_info', 'direccion_ip', 'puerto',
            'usuario_camara', 'url_stream', 'modelo', 'resolucion', 
            'vision_nocturna', 'angulo_vision', 'fecha_instalacion', 
            'ultimo_mantenimiento', 'eventos_recientes', 'activo',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def get_eventos_recientes(self, obj) -> list:
        eventos = EventoSeguridad.objects.filter(camara=obj).order_by('-fecha_hora')[:5]
        return [
            {
                'id': evento.pk,
                'tipo_evento': evento.tipo_evento.nombre,
                'fecha_hora': evento.fecha_hora,
                'severidad': evento.severidad,
                'revisado': evento.revisado
            }
            for evento in eventos
        ]


# =================== SERIALIZERS PARA VEHÍCULOS ===================

class VehiculoAutorizadoListSerializer(serializers.ModelSerializer):
    """Serializer para listado de vehículos autorizados"""
    usuario_info = UsuarioBasicoSerializer(source='usuario', read_only=True)
    aprobado_por_info = serializers.SerializerMethodField()
    dias_pendiente = serializers.SerializerMethodField()
    estado_aprobacion = serializers.SerializerMethodField()
    
    class Meta:
        model = VehiculoAutorizado
        fields = [
            'id', 'usuario_info', 'placa', 'marca', 'modelo', 'anio', 'color',
            'tipo_vehiculo', 'fecha_registro', 'aprobado_por_info', 
            'fecha_aprobacion', 'dias_pendiente', 'estado_aprobacion', 'activo'
        ]
        
    def get_aprobado_por_info(self, obj) -> Dict[str, Any] | None:
        if obj.aprobado_por:
            return {
                'id': obj.aprobado_por.pk,
                'full_name': f"{obj.aprobado_por.first_name} {obj.aprobado_por.last_name}".strip()
            }
        return None
        
    def get_dias_pendiente(self, obj) -> int:
        if not obj.fecha_aprobacion:
            delta = timezone.now() - obj.fecha_registro
            return delta.days
        return 0
        
    def get_estado_aprobacion(self, obj) -> str:
        if obj.fecha_aprobacion:
            return "aprobado"
        else:
            return "pendiente"


class VehiculoAutorizadoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear vehículo autorizado"""
    
    class Meta:
        model = VehiculoAutorizado
        fields = [
            'usuario', 'placa', 'marca', 'modelo', 'anio', 'color', 'tipo_vehiculo'
        ]
        
    def validate_placa(self, value):
        """Validar que la placa no esté duplicada"""
        if VehiculoAutorizado.objects.filter(placa=value.upper(), activo=True).exists():
            raise serializers.ValidationError("Ya existe un vehículo registrado con esta placa")
        return value.upper()
        
    def validate_anio(self, value):
        """Validar año del vehículo"""
        current_year = timezone.now().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError(f"El año debe estar entre 1900 y {current_year + 1}")
        return value
        
    def create(self, validated_data):
        # El vehículo se crea sin aprobación automática
        vehiculo = VehiculoAutorizado.objects.create(**validated_data)
        return vehiculo


class VehiculoAprobacionSerializer(serializers.Serializer):
    """Serializer para aprobar/rechazar vehículo"""
    aprobado = serializers.BooleanField()
    notas = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, attrs):  # type: ignore
        if not attrs.get('aprobado') and not attrs.get('notas'):
            raise serializers.ValidationError({
                'notas': 'Las notas son requeridas cuando se rechaza un vehículo'
            })
        return attrs


# =================== SERIALIZERS PARA EVENTOS DE SEGURIDAD ===================

class EventoSeguridadListSerializer(serializers.ModelSerializer):
    """Serializer para listado de eventos de seguridad"""
    tipo_evento_info = TipoEventoSerializer(source='tipo_evento', read_only=True)
    camara_info = serializers.SerializerMethodField()
    usuario_info = UsuarioBasicoSerializer(source='usuario', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    resuelto_por_info = UsuarioBasicoSerializer(source='resuelto_por', read_only=True)
    severidad_color = serializers.SerializerMethodField()
    tiempo_transcurrido = serializers.SerializerMethodField()
    
    class Meta:
        model = EventoSeguridad
        fields = [
            'id', 'tipo_evento_info', 'camara_info', 'usuario_info', 'vehiculo_info',
            'fecha_hora', 'descripcion', 'evidencia_url', 'severidad', 'revisado',
            'resuelto_por_info', 'fecha_resolucion', 'severidad_color', 
            'tiempo_transcurrido'
        ]
        
    def get_camara_info(self, obj) -> Dict[str, Any] | None:
        if obj.camara:
            return {
                'id': obj.camara.pk,
                'nombre': obj.camara.nombre,
                'zona': obj.camara.zona.nombre,
                'ubicacion': obj.camara.ubicacion
            }
        return None
        
    def get_vehiculo_info(self, obj) -> Dict[str, Any] | None:
        if obj.vehiculo_autorizado:
            return {
                'id': obj.vehiculo_autorizado.pk,
                'placa': obj.vehiculo_autorizado.placa,
                'marca': obj.vehiculo_autorizado.marca,
                'modelo': obj.vehiculo_autorizado.modelo
            }
        return None
        
    def get_severidad_color(self, obj) -> str:
        colores = {
            1: '#28a745',  # verde - baja
            2: '#ffc107',  # amarillo - media
            3: '#fd7e14',  # naranja - alta
            4: '#dc3545'   # rojo - crítica
        }
        return colores.get(obj.severidad, '#6c757d')
        
    def get_tiempo_transcurrido(self, obj) -> str:
        if obj.fecha_resolucion:
            delta = obj.fecha_resolucion - obj.fecha_hora
        else:
            delta = timezone.now() - obj.fecha_hora
            
        if delta.days > 0:
            return f"{delta.days} días"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600} horas"
        else:
            return "Menos de 1 hora"


class EventoSeguridadDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para eventos de seguridad"""
    tipo_evento_info = TipoEventoSerializer(source='tipo_evento', read_only=True)
    camara_info = CamaraListSerializer(source='camara', read_only=True)
    usuario_info = UsuarioBasicoSerializer(source='usuario', read_only=True)
    vehiculo_info = VehiculoAutorizadoListSerializer(source='vehiculo_autorizado', read_only=True)
    resuelto_por_info = UsuarioBasicoSerializer(source='resuelto_por', read_only=True)
    
    class Meta:
        model = EventoSeguridad
        fields = [
            'id', 'tipo_evento_info', 'camara_info', 'usuario_info', 'vehiculo_info',
            'fecha_hora', 'descripcion', 'evidencia_url', 'severidad', 'revisado',
            'resuelto_por_info', 'fecha_resolucion', 'notas_resolucion',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EventoSeguridadCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear evento de seguridad"""
    
    class Meta:
        model = EventoSeguridad
        fields = [
            'tipo_evento', 'camara', 'usuario', 'vehiculo_autorizado',
            'fecha_hora', 'descripcion', 'evidencia_url', 'severidad'
        ]
        
    def validate_fecha_hora(self, value):
        """Validar que la fecha no sea futura"""
        if value > timezone.now():
            raise serializers.ValidationError("La fecha del evento no puede ser futura")
        return value
        
    def create(self, validated_data):
        # El evento se crea como no revisado
        evento = EventoSeguridad.objects.create(**validated_data)
        return evento


class EventoRevisionSerializer(serializers.Serializer):
    """Serializer para revisar evento de seguridad"""
    revisado = serializers.BooleanField()
    notas_resolucion = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate(self, attrs):  # type: ignore
        if attrs.get('revisado') and not attrs.get('notas_resolucion'):
            raise serializers.ValidationError({
                'notas_resolucion': 'Las notas de resolución son requeridas al marcar como revisado'
            })
        return attrs


# =================== SERIALIZERS PARA CREDENCIALES ===================

class CredentialAccesoListSerializer(serializers.ModelSerializer):
    """Serializer para listado de credenciales de acceso"""
    usuario_info = UsuarioBasicoSerializer(source='usuario', read_only=True)
    vehiculo_info = serializers.SerializerMethodField()
    dias_para_vencer = serializers.SerializerMethodField()
    estado_color = serializers.SerializerMethodField()
    
    class Meta:
        model = CredentialAcceso
        fields = [
            'id', 'usuario_info', 'vehiculo_info', 'identificador', 'tipo', 'estado',
            'fecha_emision', 'fecha_vencimiento', 'ultimo_uso', 'dias_para_vencer',
            'estado_color'
        ]
        
    def get_vehiculo_info(self, obj) -> Dict[str, Any] | None:
        if obj.vehiculo_autorizado:
            return {
                'id': obj.vehiculo_autorizado.pk,
                'placa': obj.vehiculo_autorizado.placa
            }
        return None
        
    def get_dias_para_vencer(self, obj) -> int | None:
        if obj.fecha_vencimiento:
            delta = obj.fecha_vencimiento.date() - timezone.now().date()
            return delta.days
        return None
        
    def get_estado_color(self, obj) -> str:
        colores = {
            'activo': '#28a745',      # verde
            'bloqueado': '#dc3545',   # rojo
            'vencido': '#6c757d'      # gris
        }
        return colores.get(obj.estado, '#6c757d')


class CredentialAccesoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear credencial de acceso"""
    
    class Meta:
        model = CredentialAcceso
        fields = [
            'usuario', 'vehiculo_autorizado', 'identificador', 'tipo', 'fecha_vencimiento'
        ]
        
    def validate_identificador(self, value):
        """Validar que el identificador sea único"""
        if CredentialAcceso.objects.filter(identificador=value, activo=True).exists():
            raise serializers.ValidationError("Ya existe una credencial con este identificador")
        return value
        
    def validate_fecha_vencimiento(self, value):
        """Validar fecha de vencimiento"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("La fecha de vencimiento debe ser futura")
        return value
        
    def create(self, validated_data):
        # La credencial se crea activa por defecto
        credencial = CredentialAcceso.objects.create(**validated_data)
        return credencial


class CredentialEstadoSerializer(serializers.Serializer):
    """Serializer para cambiar estado de credencial"""
    estado = serializers.ChoiceField(choices=['activo', 'bloqueado', 'vencido'])
    motivo = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    def validate(self, attrs):  # type: ignore
        if attrs.get('estado') == 'bloqueado' and not attrs.get('motivo'):
            raise serializers.ValidationError({
                'motivo': 'El motivo es requerido al bloquear una credencial'
            })
        return attrs


class UsoCredencialSerializer(serializers.Serializer):
    """Serializer para registrar uso de credencial"""
    zona = serializers.IntegerField()
    tipo_acceso = serializers.ChoiceField(choices=['entrada', 'salida'])
    exitoso = serializers.BooleanField()
    
    def validate_zona(self, value):
        """Validar que la zona exista"""
        if not Zona.objects.filter(id=value, activo=True).exists():
            raise serializers.ValidationError("La zona especificada no existe")
        return value


# =================== SERIALIZERS PARA DASHBOARD ===================

class DashboardSeguridadSerializer(serializers.Serializer):
    """Serializer para dashboard de seguridad"""
    resumen = serializers.DictField()
    eventos_por_severidad = serializers.DictField()
    eventos_por_zona = serializers.ListField()
    tendencias = serializers.DictField()


class ReporteSeguridadSerializer(serializers.Serializer):
    """Serializer para reportes de seguridad"""
    periodo = serializers.DictField()
    resumen = serializers.DictField()
    por_tipo = serializers.ListField()
    por_zona = serializers.ListField()


class ExportarReporteSerializer(serializers.Serializer):
    """Serializer para exportar reportes"""
    tipo_reporte = serializers.ChoiceField(choices=['eventos', 'vehiculos', 'accesos'])
    formato = serializers.ChoiceField(choices=['json', 'pdf', 'excel'])
    filtros = serializers.DictField()
    incluir_graficos = serializers.BooleanField(required=False)