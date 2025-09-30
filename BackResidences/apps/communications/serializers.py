from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
from typing import Any, Dict

from .models import TipoReporte, Reporte, Aviso, AvisoVisto
from apps.residences.models import Vivienda

User = get_user_model()


# =================== SERIALIZADORES PARA AVISOS (ANUNCIOS) ===================

class UsuarioBasicoSerializer(serializers.ModelSerializer):
    """Serializador básico para información de usuario"""
    full_name = serializers.SerializerMethodField()
    cargo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'cargo', 'email']
        
    def get_full_name(self, obj):
        if hasattr(obj, 'get_full_name'):
            return obj.get_full_name()
        return f"{getattr(obj, 'first_name', '')} {getattr(obj, 'last_name', '')}".strip() or str(obj.username)
    
    def get_cargo(self, obj):
        # Aquí podrías obtener el cargo desde roles o perfil
        if obj.is_superuser:
            return "Administrador Principal"
        return "Residente"


class AvisoListSerializer(serializers.ModelSerializer):
    """Serializador para listado de avisos (anuncios)"""
    autor = UsuarioBasicoSerializer(source='usuario', read_only=True)
    contenido_resumen = serializers.SerializerMethodField()
    vigente = serializers.SerializerMethodField()
    visualizaciones = serializers.SerializerMethodField()
    comentarios_count = serializers.SerializerMethodField()
    adjuntos_count = serializers.SerializerMethodField()
    imagen_destacada = serializers.SerializerMethodField()
    dirigido_a = serializers.CharField(source='publico_objetivo', read_only=True)
    categoria = serializers.CharField(source='tipo', read_only=True)
    
    class Meta:
        model = Aviso
        fields = [
            'id', 'titulo', 'categoria', 'prioridad', 'contenido_resumen',
            'fecha_publicacion', 'fecha_caducidad', 'autor', 'activo', 'vigente',
            'visualizaciones', 'dirigido_a', 'adjuntos_count', 'comentarios_count',
            'imagen_destacada'
        ]
    
    def get_contenido_resumen(self, obj):
        """Resumen del contenido limitado a 150 caracteres"""
        if len(obj.contenido) > 150:
            return obj.contenido[:147] + "..."
        return obj.contenido
    
    def get_vigente(self, obj):
        """Verifica si el aviso está vigente"""
        if not obj.fecha_caducidad:
            return True
        return obj.fecha_caducidad > timezone.now()
    
    def get_visualizaciones(self, obj):
        """Cuenta las visualizaciones del aviso"""
        return AvisoVisto.objects.filter(aviso=obj).count()
    
    def get_comentarios_count(self, obj):
        """Placeholder para comentarios - se puede implementar más tarde"""
        return 0
    
    def get_adjuntos_count(self, obj):
        """Cuenta adjuntos (por ahora solo URL)"""
        return 1 if obj.adjunto_url else 0
    
    def get_imagen_destacada(self, obj):
        """Imagen destacada del aviso"""
        return obj.adjunto_url if obj.adjunto_url and any(ext in obj.adjunto_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']) else None


class AvisoDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado para avisos"""
    autor = UsuarioBasicoSerializer(source='usuario', read_only=True)
    vigente = serializers.SerializerMethodField()
    visualizaciones = serializers.SerializerMethodField()
    fecha_ultima_edicion = serializers.DateTimeField(source='updated_at', read_only=True)
    etiquetas = serializers.SerializerMethodField()
    adjuntos = serializers.SerializerMethodField()
    imagenes = serializers.SerializerMethodField()
    estadisticas = serializers.SerializerMethodField()
    dirigido_a = serializers.CharField(source='publico_objetivo', read_only=True)
    categoria = serializers.CharField(source='tipo', read_only=True)
    
    class Meta:
        model = Aviso
        fields = [
            'id', 'titulo', 'categoria', 'prioridad', 'contenido',
            'fecha_publicacion', 'fecha_caducidad', 'autor', 'activo', 'vigente',
            'dirigido_a', 'visualizaciones', 'fecha_ultima_edicion', 'etiquetas',
            'adjuntos', 'imagenes', 'estadisticas'
        ]
    
    def get_vigente(self, obj):
        if not obj.fecha_caducidad:
            return True
        return obj.fecha_caducidad > timezone.now()
    
    def get_visualizaciones(self, obj):
        return AvisoVisto.objects.filter(aviso=obj).count()
    
    def get_etiquetas(self, obj):
        """Genera etiquetas basadas en el tipo y contenido"""
        etiquetas = [obj.tipo.lower()]
        
        # Agregar etiquetas según palabras clave en el contenido
        contenido_lower = obj.contenido.lower()
        if 'agua' in contenido_lower:
            etiquetas.append('agua')
        if 'mantenimiento' in contenido_lower:
            etiquetas.append('mantenimiento')
        if 'pago' in contenido_lower or 'cuota' in contenido_lower:
            etiquetas.append('pagos')
        if 'ascensor' in contenido_lower:
            etiquetas.append('ascensor')
        if 'reunion' in contenido_lower:
            etiquetas.append('reunion')
        
        return list(set(etiquetas))  # Eliminar duplicados
    
    def get_adjuntos(self, obj):
        """Lista de adjuntos del aviso"""
        if not obj.adjunto_url:
            return []
        
        import os
        filename = os.path.basename(obj.adjunto_url)
        
        return [{
            'id': 1,
            'nombre': filename,
            'tipo': 'application/pdf' if filename.endswith('.pdf') else 'image/jpeg',
            'tamaño': '245KB',  # Placeholder
            'url': obj.adjunto_url
        }]
    
    def get_imagenes(self, obj):
        """Lista de imágenes del aviso"""
        if not obj.adjunto_url:
            return []
        
        if any(ext in obj.adjunto_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            return [obj.adjunto_url]
        
        return []
    
    def get_estadisticas(self, obj):
        """Estadísticas de visualización del aviso"""
        # Obtener visualizaciones por día (últimos 7 días)
        visualizaciones_por_dia = []
        for i in range(7):
            fecha = timezone.now().date() - timedelta(days=i)
            count = AvisoVisto.objects.filter(
                aviso=obj,
                fecha_visto__date=fecha
            ).count()
            visualizaciones_por_dia.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'visualizaciones': count
            })
        
        # Placeholder para visualizaciones por bloque
        visualizaciones_por_bloque = [
            {'bloque': 'TORRE-A', 'visualizaciones': 55},
            {'bloque': 'TORRE-B', 'visualizaciones': 50},
            {'bloque': 'TORRE-C', 'visualizaciones': 40}
        ]
        
        return {
            'visualizaciones_por_dia': visualizaciones_por_dia,
            'visualizaciones_por_bloque': visualizaciones_por_bloque
        }


class AvisoCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear avisos"""
    etiquetas = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )
    adjuntos = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    enviar_notificacion = serializers.BooleanField(default=True, write_only=True)  # type: ignore
    programar_publicacion = serializers.BooleanField(default=False, write_only=True)  # type: ignore
    dirigido_a = serializers.CharField(source='publico_objetivo')
    categoria = serializers.CharField(source='tipo')
    
    class Meta:
        model = Aviso
        fields = [
            'titulo', 'categoria', 'prioridad', 'contenido', 'dirigido_a',
            'fecha_caducidad', 'etiquetas', 'adjuntos', 'enviar_notificacion',
            'programar_publicacion'
        ]
    
    def validate_categoria(self, value):
        """Validar que la categoría sea válida"""
        valid_choices = ['informativo', 'urgente', 'mantenimiento']
        if value not in valid_choices:
            raise serializers.ValidationError(f"Categoría debe ser una de: {valid_choices}")
        return value
    
    def validate_dirigido_a(self, value):
        """Validar público objetivo"""
        valid_choices = ['todos', 'propietarios', 'inquilinos']
        if value not in valid_choices:
            raise serializers.ValidationError(f"Dirigido a debe ser uno de: {valid_choices}")
        return value
    
    def create(self, validated_data):
        # Remover campos que no van al modelo
        etiquetas = validated_data.pop('etiquetas', [])
        adjuntos = validated_data.pop('adjuntos', [])
        enviar_notificacion = validated_data.pop('enviar_notificacion', True)
        programar_publicacion = validated_data.pop('programar_publicacion', False)
        
        # Obtener usuario del contexto
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        
        # Procesar adjuntos (primer adjunto como URL)
        if adjuntos:
            validated_data['adjunto_url'] = adjuntos[0]  # Tomar el primer adjunto
        
        aviso = super().create(validated_data)
        
        # Aquí se podría implementar la lógica de envío de notificaciones
        if enviar_notificacion:
            self._enviar_notificaciones(aviso)
        
        return aviso
    
    def _enviar_notificaciones(self, aviso):
        """Enviar notificaciones del nuevo aviso"""
        # Placeholder para lógica de notificaciones
        # Se implementaría aquí el envío de notificaciones push, email, etc.
        pass


class AvisoUpdateSerializer(serializers.ModelSerializer):
    """Serializador para actualizar avisos"""
    enviar_notificacion_actualizacion = serializers.BooleanField(default=False, write_only=True)  # type: ignore
    dirigido_a = serializers.CharField(source='publico_objetivo')
    categoria = serializers.CharField(source='tipo')
    
    class Meta:
        model = Aviso
        fields = [
            'titulo', 'categoria', 'prioridad', 'contenido', 'dirigido_a',
            'fecha_caducidad', 'enviar_notificacion_actualizacion'
        ]
    
    def update(self, instance, validated_data):
        enviar_notificacion = validated_data.pop('enviar_notificacion_actualizacion', False)
        
        # Guardar valores anteriores para detectar cambios
        valores_anteriores = {
            'titulo': instance.titulo,
            'contenido': instance.contenido,
            'prioridad': instance.prioridad
        }
        
        aviso = super().update(instance, validated_data)
        
        # Detectar cambios realizados
        cambios = []
        if valores_anteriores['titulo'] != aviso.titulo:
            cambios.append('Título actualizado')
        if valores_anteriores['contenido'] != aviso.contenido:
            cambios.append('Contenido modificado')
        if valores_anteriores['prioridad'] != aviso.prioridad:
            cambios.append(f'Prioridad cambiada a {aviso.prioridad}')
        
        # Guardar cambios en el contexto para la respuesta
        self._cambios_realizados = cambios
        
        if enviar_notificacion:
            self._enviar_notificacion_actualizacion(aviso, cambios)
        
        return aviso
    
    def _enviar_notificacion_actualizacion(self, aviso, cambios):
        """Enviar notificación de actualización"""
        # Placeholder para lógica de notificaciones de actualización
        pass


# =================== SERIALIZADORES PARA REPORTES ===================

class TipoReporteSerializer(serializers.ModelSerializer):
    """Serializador para tipos de reporte"""
    
    class Meta:
        model = TipoReporte
        fields = [
            'id', 'nombre', 'descripcion', 'categoria',
            'prioridad_default', 'tiempo_respuesta_horas', 'activo'
        ]


class ReporteListSerializer(serializers.ModelSerializer):
    """Serializador para listado de reportes"""
    usuario_info = UsuarioBasicoSerializer(source='usuario', read_only=True)
    tipo_reporte_info = TipoReporteSerializer(source='tipo_reporte', read_only=True)
    vivienda_info = serializers.SerializerMethodField()
    tiempo_transcurrido = serializers.SerializerMethodField()
    dias_abierto = serializers.SerializerMethodField()
    
    class Meta:
        model = Reporte
        fields = [
            'id', 'titulo', 'descripcion', 'prioridad', 'estado',
            'fecha_registro', 'fecha_asignacion', 'fecha_resolucion',
            'usuario_info', 'tipo_reporte_info', 'vivienda_info',
            'tiempo_transcurrido', 'dias_abierto', 'evidencia_foto'
        ]
    
    def get_vivienda_info(self, obj):
        """Información básica de la vivienda"""
        if not obj.vivienda:
            return None
        
        return {
            'id': obj.vivienda.id,
            'identificador': obj.vivienda.identificador,
            'bloque': getattr(obj.vivienda, 'bloque', ''),
            'piso': getattr(obj.vivienda, 'piso', '')
        }
    
    def get_tiempo_transcurrido(self, obj):
        """Tiempo transcurrido desde la creación"""
        now = timezone.now()
        delta = now - obj.fecha_registro
        
        if delta.days > 0:
            return f"{delta.days} días"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} horas"
        else:
            minutes = delta.seconds // 60
            return f"{minutes} minutos"
    
    def get_dias_abierto(self, obj):
        """Días que lleva abierto el reporte"""
        if obj.estado in ['resuelto', 'cerrado'] and obj.fecha_resolucion:
            delta = obj.fecha_resolucion - obj.fecha_registro
        else:
            delta = timezone.now() - obj.fecha_registro
        
        return delta.days


class ReporteCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear reportes"""
    adjuntos = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    etiquetas = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
        write_only=True
    )
    
    class Meta:
        model = Reporte
        fields = [
            'tipo_reporte', 'vivienda', 'titulo', 'descripcion',
            'prioridad', 'adjuntos', 'etiquetas'
        ]
    
    def validate(self, attrs):  # type: ignore
        """Validaciones personalizadas"""
        # Verificar que el usuario tenga acceso a la vivienda
        request = self.context.get('request')
        if request and hasattr(request, 'user') and attrs.get('vivienda'):
            vivienda = attrs['vivienda']
            user = request.user
            
            # Solo admins o residentes de la vivienda pueden crear reportes
            if not user.is_superuser:
                if not (vivienda.usuario_propietario == user or vivienda.usuario_inquilino == user):
                    raise serializers.ValidationError(
                        "No tiene permisos para crear reportes de esta vivienda"
                    )
        
        return attrs
    
    def create(self, validated_data):
        # Remover campos extras
        adjuntos = validated_data.pop('adjuntos', [])
        etiquetas = validated_data.pop('etiquetas', [])
        
        # Obtener usuario del contexto
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        
        # Si no se especifica prioridad, usar la del tipo de reporte
        if 'prioridad' not in validated_data:
            validated_data['prioridad'] = validated_data['tipo_reporte'].prioridad_default
        
        # Procesar adjuntos (tomar el primero como evidencia)
        if adjuntos:
            validated_data['evidencia_foto'] = adjuntos[0]
        
        reporte = super().create(validated_data)
        
        # Auto-asignar según el tipo de reporte
        self._auto_asignar_reporte(reporte)
        
        return reporte
    
    def _auto_asignar_reporte(self, reporte):
        """Auto-asignar reporte según tipo y disponibilidad"""
        # Placeholder para lógica de auto-asignación
        # Se podría implementar lógica para asignar automáticamente
        # según el tipo de reporte y disponibilidad de administradores
        pass


# =================== SERIALIZADORES PARA CONFIGURACIÓN ===================

class PreferenciasNotificacionSerializer(serializers.Serializer):
    """Serializador para preferencias de notificación"""
    usuario_id = serializers.IntegerField(read_only=True)
    canales_preferidos = serializers.ListField(
        child=serializers.ChoiceField(choices=['app', 'email', 'sms']),
        default=['app', 'email']
    )
    frecuencia_resumen = serializers.ChoiceField(
        choices=['diario', 'semanal', 'mensual'],
        default='diario'
    )
    horario_no_molestar = serializers.DictField(
        child=serializers.TimeField(),
        required=False
    )
    tipos_notificacion = serializers.DictField(required=False)
    
    def validate_horario_no_molestar(self, value):
        """Validar horario no molestar"""
        if value and ('inicio' not in value or 'fin' not in value):
            raise serializers.ValidationError(
                "Horario no molestar debe incluir 'inicio' y 'fin'"
            )
        return value


# =================== SERIALIZADORES PARA DASHBOARD ===================

class DashboardCommunicationsSerializer(serializers.Serializer):
    """Serializador para dashboard de comunicaciones"""
    periodo = serializers.CharField()
    anuncios = serializers.DictField()
    notificaciones = serializers.DictField()
    conversaciones = serializers.DictField()
    engagement = serializers.DictField()


class EstadisticasEfectividadSerializer(serializers.Serializer):
    """Serializador para estadísticas de efectividad"""
    periodo = serializers.DictField()
    anuncios = serializers.DictField()
    notificaciones = serializers.DictField()
    mensajeria = serializers.DictField()