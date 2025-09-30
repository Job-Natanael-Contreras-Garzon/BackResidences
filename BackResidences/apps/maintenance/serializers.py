from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, Any

from .models import (
    CategoriaMantenimiento, Proveedor, SolicitudMantenimiento, OrdenTrabajo,
    MaterialInventario, MovimientoInventario, MantenimientoPreventivo, Mantenimiento
)
from apps.residences.models import Vivienda
from apps.common_areas.models import AreaComun

User = get_user_model()


# =================== SERIALIZERS BÁSICOS ===================

class UsuarioBasicoSerializer(serializers.ModelSerializer):
    """Serializer básico para información de usuario"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email']
        
    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}".strip()


class CategoriaMantenimientoSerializer(serializers.ModelSerializer):
    """Serializer para categorías de mantenimiento"""
    
    class Meta:
        model = CategoriaMantenimiento
        fields = [
            'id', 'nombre', 'codigo', 'descripcion', 'color', 
            'activo', 'tiempo_respuesta_horas', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProveedorListSerializer(serializers.ModelSerializer):
    """Serializer para listado de proveedores"""
    categoria_principal_info = serializers.SerializerMethodField()
    servicios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre', 'telefono', 'email', 'contacto_principal',
            'categoria_principal_info', 'servicios_count', 'tarifa_hora',
            'calificacion_promedio', 'trabajos_realizados', 'activo',
            'atiende_emergencias', 'tiempo_respuesta_emergencia_horas'
        ]
        
    def get_categoria_principal_info(self, obj) -> Dict[str, Any]:
        return {
            'id': obj.categoria_principal.id,
            'nombre': obj.categoria_principal.nombre,
            'codigo': obj.categoria_principal.codigo
        }
        
    def get_servicios_count(self, obj) -> int:
        return obj.servicios.count()


class ProveedorDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para proveedores"""
    categoria_principal_info = CategoriaMantenimientoSerializer(source='categoria_principal', read_only=True)
    servicios_info = CategoriaMantenimientoSerializer(source='servicios', many=True, read_only=True)
    
    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre', 'telefono', 'email', 'direccion', 'contacto_principal',
            'rut', 'camara_comercio', 'poliza_responsabilidad',
            'categoria_principal_info', 'servicios_info',
            'tarifa_hora', 'tarifa_visita', 'recargo_emergencia_porcentaje',
            'horarios', 'atiende_emergencias', 'tiempo_respuesta_emergencia_horas',
            'activo', 'calificacion_promedio', 'trabajos_realizados',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'calificacion_promedio', 'trabajos_realizados']


# =================== SERIALIZERS PARA SOLICITUDES ===================

class SolicitudMantenimientoListSerializer(serializers.ModelSerializer):
    """Serializer para listado de solicitudes de mantenimiento"""
    categoria_info = serializers.SerializerMethodField()
    solicitante_info = UsuarioBasicoSerializer(source='solicitante', read_only=True)
    ubicacion_info = serializers.SerializerMethodField()
    tecnico_asignado_info = UsuarioBasicoSerializer(source='tecnico_asignado', read_only=True)
    proveedor_asignado_info = serializers.SerializerMethodField()
    tiempo_transcurrido_texto = serializers.SerializerMethodField()
    estado_color = serializers.SerializerMethodField()
    prioridad_color = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'id', 'numero_solicitud', 'titulo', 'categoria_info', 'prioridad', 'estado',
            'solicitante_info', 'ubicacion_info', 'fecha_solicitud', 'fecha_limite',
            'tecnico_asignado_info', 'proveedor_asignado_info', 'costo_estimado',
            'calificacion', 'tiempo_transcurrido_texto', 'dias_abierto',
            'estado_color', 'prioridad_color'
        ]
        
    def get_categoria_info(self, obj) -> Dict[str, Any]:
        return {
            'id': obj.categoria.id,
            'nombre': obj.categoria.nombre,
            'codigo': obj.categoria.codigo,
            'color': obj.categoria.color
        }
        
    def get_ubicacion_info(self, obj) -> Dict[str, Any] | None:
        if obj.ubicacion:
            tipo = "vivienda" if isinstance(obj.ubicacion, Vivienda) else "area_comun"
            return {
                'tipo': tipo,
                'id': obj.ubicacion.pk,
                'nombre': str(obj.ubicacion),
                'ubicacion_especifica': obj.ubicacion_especifica
            }
        return None
        
    def get_proveedor_asignado_info(self, obj) -> Dict[str, Any] | None:
        if obj.proveedor_asignado:
            return {
                'id': obj.proveedor_asignado.id,
                'nombre': obj.proveedor_asignado.nombre,
                'telefono': obj.proveedor_asignado.telefono
            }
        return None
        
    def get_tiempo_transcurrido_texto(self, obj) -> str:
        delta = obj.tiempo_transcurrido
        if delta.days > 0:
            return f"{delta.days} días"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600} horas"
        else:
            return "Menos de 1 hora"
            
    def get_estado_color(self, obj) -> str:
        colores = {
            'pendiente': '#ffc107',      # amarillo
            'asignada': '#17a2b8',       # azul
            'en_proceso': '#007bff',     # azul
            'completada': '#28a745',     # verde
            'cancelada': '#dc3545'       # rojo
        }
        return colores.get(obj.estado, '#6c757d')
        
    def get_prioridad_color(self, obj) -> str:
        colores = {
            'baja': '#28a745',       # verde
            'media': '#ffc107',      # amarillo
            'alta': '#fd7e14',       # naranja
            'urgente': '#dc3545'     # rojo
        }
        return colores.get(obj.prioridad, '#6c757d')


class SolicitudMantenimientoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para solicitudes de mantenimiento"""
    categoria_info = CategoriaMantenimientoSerializer(source='categoria', read_only=True)
    solicitante_info = UsuarioBasicoSerializer(source='solicitante', read_only=True)
    ubicacion_info = serializers.SerializerMethodField()
    tecnico_asignado_info = UsuarioBasicoSerializer(source='tecnico_asignado', read_only=True)
    proveedor_asignado_info = ProveedorListSerializer(source='proveedor_asignado', read_only=True)
    orden_trabajo_info = serializers.SerializerMethodField()
    historial_estados = serializers.SerializerMethodField()
    tiempo_transcurrido_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'id', 'numero_solicitud', 'titulo', 'descripcion', 'subcategoria',
            'categoria_info', 'prioridad', 'estado', 'solicitante_info',
            'ubicacion_info', 'ubicacion_especifica', 'fecha_solicitud',
            'fecha_preferida', 'fecha_limite', 'fecha_asignacion', 'fecha_completada',
            'tecnico_asignado_info', 'proveedor_asignado_info', 'costo_estimado',
            'costo_real', 'contacto_alternativo_nombre', 'contacto_alternativo_telefono',
            'calificacion', 'comentarios_evaluacion', 'orden_trabajo_info',
            'historial_estados', 'tiempo_transcurrido_detalle', 'dias_abierto',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def get_ubicacion_info(self, obj) -> Dict[str, Any] | None:
        if obj.ubicacion:
            if isinstance(obj.ubicacion, Vivienda):
                return {
                    'tipo': 'vivienda',
                    'id': obj.ubicacion.pk,
                    'identificador': obj.ubicacion.identificador,
                    'bloque': obj.ubicacion.bloque,
                    'piso': obj.ubicacion.piso,
                    'propietario': obj.ubicacion.usuario_propietario.get_full_name() if obj.ubicacion.usuario_propietario else None,
                    'inquilino': obj.ubicacion.usuario_inquilino.get_full_name() if obj.ubicacion.usuario_inquilino else None
                }
            elif isinstance(obj.ubicacion, AreaComun):
                return {
                    'tipo': 'area_comun',
                    'id': obj.ubicacion.pk,
                    'nombre': obj.ubicacion.nombre,
                    'descripcion': obj.ubicacion.descripcion,
                    'capacidad': obj.ubicacion.capacidad
                }
        return None
        
    def get_orden_trabajo_info(self, obj) -> Dict[str, Any] | None:
        try:
            orden = obj.orden_trabajo
            return {
                'id': orden.id,
                'numero_orden': orden.numero_orden,
                'estado': orden.estado,
                'fecha_programada': orden.fecha_programada,
                'fecha_inicio': orden.fecha_inicio,
                'fecha_finalizacion': orden.fecha_finalizacion,
                'progreso_porcentaje': orden.progreso_porcentaje,
                'garantia_dias': orden.garantia_dias
            }
        except:
            return None
            
    def get_historial_estados(self, obj) -> list:
        # Placeholder para historial de cambios de estado
        # En una implementación real, esto vendría de un modelo de auditoría
        historial = [
            {
                'estado': 'pendiente',
                'fecha': obj.fecha_solicitud,
                'usuario': obj.solicitante.get_full_name(),
                'comentario': 'Solicitud creada'
            }
        ]
        
        if obj.fecha_asignacion:
            historial.append({
                'estado': 'asignada',
                'fecha': obj.fecha_asignacion,
                'usuario': obj.tecnico_asignado.get_full_name() if obj.tecnico_asignado else 'Sistema',
                'comentario': 'Solicitud asignada'
            })
            
        if obj.fecha_completada:
            historial.append({
                'estado': 'completada',
                'fecha': obj.fecha_completada,
                'usuario': obj.tecnico_asignado.get_full_name() if obj.tecnico_asignado else 'Sistema',
                'comentario': 'Trabajo completado'
            })
            
        return historial
        
    def get_tiempo_transcurrido_detalle(self, obj) -> Dict[str, Any]:
        delta = obj.tiempo_transcurrido
        return {
            'dias': delta.days,
            'horas': delta.seconds // 3600,
            'minutos': (delta.seconds % 3600) // 60,
            'total_horas': delta.total_seconds() / 3600,
            'texto': f"{delta.days} días, {delta.seconds // 3600} horas"
        }


class SolicitudMantenimientoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear solicitudes de mantenimiento"""
    ubicacion_tipo = serializers.ChoiceField(
        choices=[('vivienda', 'Vivienda'), ('area_comun', 'Área Común')],
        write_only=True
    )
    ubicacion_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'titulo', 'descripcion', 'subcategoria', 'categoria', 'prioridad',
            'ubicacion_tipo', 'ubicacion_id', 'ubicacion_especifica',
            'fecha_preferida', 'contacto_alternativo_nombre', 'contacto_alternativo_telefono'
        ]
        
    def validate(self, attrs):  # type: ignore
        """Validaciones personalizadas"""
        # Validar ubicación
        ubicacion_tipo = attrs.get('ubicacion_tipo')
        ubicacion_id = attrs.get('ubicacion_id')
        
        if ubicacion_tipo == 'vivienda':
            try:
                vivienda = Vivienda.objects.get(id=ubicacion_id)
                attrs['ubicacion_object'] = vivienda
                attrs['content_type'] = ContentType.objects.get_for_model(Vivienda)
            except Vivienda.DoesNotExist:
                raise serializers.ValidationError({
                    'ubicacion_id': 'La vivienda especificada no existe'
                })
        elif ubicacion_tipo == 'area_comun':
            try:
                area = AreaComun.objects.get(id=ubicacion_id)
                attrs['ubicacion_object'] = area
                attrs['content_type'] = ContentType.objects.get_for_model(AreaComun)
            except AreaComun.DoesNotExist:
                raise serializers.ValidationError({
                    'ubicacion_id': 'El área común especificada no existe'
                })
        
        # Validar permisos sobre la ubicación
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if not user.is_superuser and ubicacion_tipo == 'vivienda':
                vivienda = attrs['ubicacion_object']
                if not (vivienda.usuario_propietario == user or vivienda.usuario_inquilino == user):
                    raise serializers.ValidationError({
                        'ubicacion_id': 'No tienes permisos para crear solicitudes en esta vivienda'
                    })
        
        return attrs
        
    def create(self, validated_data):
        # Remover campos auxiliares
        ubicacion_tipo = validated_data.pop('ubicacion_tipo')
        ubicacion_id = validated_data.pop('ubicacion_id')
        ubicacion_object = validated_data.pop('ubicacion_object')
        content_type = validated_data.pop('content_type')
        
        # Establecer relación polimórfica
        validated_data['content_type'] = content_type
        validated_data['object_id'] = ubicacion_id
        
        # Obtener usuario del contexto
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['solicitante'] = request.user
        
        solicitud = SolicitudMantenimiento.objects.create(**validated_data)
        return solicitud


class SolicitudMantenimientoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar solicitudes de mantenimiento"""
    
    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'estado', 'tecnico_asignado', 'proveedor_asignado', 'costo_estimado',
            'costo_real', 'fecha_asignacion', 'fecha_completada', 'calificacion',
            'comentarios_evaluacion'
        ]
        
    def validate(self, attrs):  # type: ignore
        """Validaciones para actualización"""
        instance = self.instance
        if not instance:
            return attrs
            
        estado = attrs.get('estado', instance.estado)
        
        # Validar transiciones de estado
        if estado == 'asignada' and not attrs.get('tecnico_asignado') and not instance.tecnico_asignado:
            raise serializers.ValidationError({
                'tecnico_asignado': 'Debe asignar un técnico para cambiar a estado "asignada"'
            })
            
        if estado == 'completada':
            if not attrs.get('costo_real') and not instance.costo_real:
                raise serializers.ValidationError({
                    'costo_real': 'Debe especificar el costo real para completar la solicitud'
                })
            attrs['fecha_completada'] = timezone.now()
        
        if estado == 'asignada' and not instance.fecha_asignacion:
            attrs['fecha_asignacion'] = timezone.now()
            
        return attrs


# =================== SERIALIZERS PARA ÓRDENES DE TRABAJO ===================

class OrdenTrabajoListSerializer(serializers.ModelSerializer):
    """Serializer para listado de órdenes de trabajo"""
    solicitud_info = serializers.SerializerMethodField()
    tecnico_info = UsuarioBasicoSerializer(source='tecnico_asignado', read_only=True)
    proveedor_info = serializers.SerializerMethodField()
    estado_color = serializers.SerializerMethodField()
    tiempo_trabajado_texto = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'numero_orden', 'solicitud_info', 'estado', 'fecha_programada',
            'fecha_inicio', 'fecha_finalizacion', 'tecnico_info', 'proveedor_info',
            'tiempo_estimado_horas', 'tiempo_real_horas', 'progreso_porcentaje',
            'estado_color', 'tiempo_trabajado_texto'
        ]
        
    def get_solicitud_info(self, obj) -> Dict[str, Any]:
        return {
            'id': obj.solicitud.id,
            'numero_solicitud': obj.solicitud.numero_solicitud,
            'titulo': obj.solicitud.titulo,
            'prioridad': obj.solicitud.prioridad
        }
        
    def get_proveedor_info(self, obj) -> Dict[str, Any]:
        return {
            'id': obj.proveedor.id,
            'nombre': obj.proveedor.nombre,
            'telefono': obj.proveedor.telefono
        }
        
    def get_estado_color(self, obj) -> str:
        colores = {
            'pendiente': '#ffc107',
            'en_proceso': '#007bff',
            'completada': '#28a745',
            'cancelada': '#dc3545'
        }
        return colores.get(obj.estado, '#6c757d')
        
    def get_tiempo_trabajado_texto(self, obj) -> str:
        tiempo = obj.tiempo_total_trabajado
        if tiempo > 0:
            horas = int(tiempo)
            minutos = int((tiempo - horas) * 60)
            return f"{horas}h {minutos}m"
        return "No iniciado"


class OrdenTrabajoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para órdenes de trabajo"""
    solicitud_info = SolicitudMantenimientoListSerializer(source='solicitud', read_only=True)
    tecnico_info = UsuarioBasicoSerializer(source='tecnico_asignado', read_only=True)
    proveedor_info = ProveedorDetailSerializer(source='proveedor', read_only=True)
    materiales_usados_info = serializers.SerializerMethodField()
    tiempo_trabajado_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'numero_orden', 'solicitud_info', 'estado', 'fecha_programada',
            'fecha_inicio', 'fecha_finalizacion', 'tiempo_estimado_horas',
            'tiempo_real_horas', 'tecnico_info', 'proveedor_info',
            'descripcion_trabajo', 'observaciones_iniciales', 'recomendaciones',
            'garantia_dias', 'fecha_vencimiento_garantia', 'progreso_porcentaje',
            'materiales_usados_info', 'tiempo_trabajado_detalle',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def get_materiales_usados_info(self, obj) -> list:
        materiales = obj.materiales_usados.all()
        return [
            {
                'id': m.id,
                'material': {
                    'codigo': m.material.codigo,
                    'nombre': m.material.nombre,
                    'unidad_medida': m.material.unidad_medida
                },
                'cantidad': m.cantidad,
                'costo_unitario': m.costo_unitario,
                'valor_total': m.valor_total
            }
            for m in materiales
        ]
        
    def get_tiempo_trabajado_detalle(self, obj) -> Dict[str, Any]:
        tiempo_total = obj.tiempo_total_trabajado
        return {
            'tiempo_total_horas': round(tiempo_total, 2),
            'tiempo_estimado_horas': float(obj.tiempo_estimado_horas),
            'diferencia_horas': round(tiempo_total - float(obj.tiempo_estimado_horas), 2),
            'eficiencia_porcentaje': round((float(obj.tiempo_estimado_horas) / tiempo_total * 100), 2) if tiempo_total > 0 else 0
        }


# =================== SERIALIZERS PARA DASHBOARD ===================

class DashboardMantenimientoSerializer(serializers.Serializer):
    """Serializer para dashboard de mantenimiento"""
    periodo = serializers.CharField()
    solicitudes = serializers.DictField()
    ordenes_trabajo = serializers.DictField()
    proveedores = serializers.DictField()
    inventario = serializers.DictField()
    mantenimiento_preventivo = serializers.DictField()
    costos = serializers.DictField()


class EstadisticasMantenimientoSerializer(serializers.Serializer):
    """Serializer para estadísticas de mantenimiento"""
    periodo = serializers.DictField()
    solicitudes_por_categoria = serializers.ListField()
    tiempo_respuesta_promedio = serializers.CharField()
    satisfaccion_promedio = serializers.FloatField()
    eficiencia_proveedores = serializers.ListField()
    costos_por_mes = serializers.ListField()


# =================== SERIALIZERS PARA INVENTARIO ===================

class MaterialInventarioListSerializer(serializers.ModelSerializer):
    """Serializer para listado de materiales de inventario"""
    categoria_info = serializers.SerializerMethodField()
    proveedor_info = serializers.SerializerMethodField()
    estado_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialInventario
        fields = [
            'id', 'codigo', 'nombre', 'categoria_info', 'stock_actual',
            'stock_minimo', 'stock_maximo', 'unidad_medida', 'costo_unitario',
            'valor_total_stock', 'proveedor_info', 'ubicacion_bodega',
            'alerta_stock_bajo', 'estado_stock', 'activo'
        ]
        
    def get_categoria_info(self, obj) -> Dict[str, Any]:
        return {
            'id': obj.categoria.id,
            'nombre': obj.categoria.nombre,
            'codigo': obj.categoria.codigo
        }
        
    def get_proveedor_info(self, obj) -> Dict[str, Any] | None:
        if obj.proveedor_principal:
            return {
                'id': obj.proveedor_principal.id,
                'nombre': obj.proveedor_principal.nombre,
                'telefono': obj.proveedor_principal.telefono
            }
        return None
        
    def get_estado_stock(self, obj) -> Dict[str, Any]:
        if obj.alerta_stock_bajo:
            estado = 'bajo'
            color = '#dc3545'
        elif obj.stock_actual <= obj.stock_minimo * 1.5:
            estado = 'medio'
            color = '#ffc107'
        else:
            estado = 'bueno'
            color = '#28a745'
            
        return {
            'estado': estado,
            'color': color,
            'porcentaje': (obj.stock_actual / obj.stock_maximo) * 100 if obj.stock_maximo > 0 else 0
        }