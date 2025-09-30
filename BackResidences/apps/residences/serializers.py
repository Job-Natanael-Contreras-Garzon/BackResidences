from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, date
from .models import Vivienda, PersonaAutorizada, Mascota

User = get_user_model()

# =================== SERIALIZERS PARA USUARIOS ===================

class ResidenteBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para información de residentes"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'telefono', 'documento_numero']

# =================== SERIALIZERS PARA VIVIENDAS ===================

class ViviendaListSerializer(serializers.ModelSerializer):
    """Serializer para lista de viviendas"""
    usuario_propietario = ResidenteBasicSerializer(read_only=True)
    usuario_inquilino = ResidenteBasicSerializer(read_only=True)
    personas_autorizadas_count = serializers.SerializerMethodField()
    mascotas_count = serializers.SerializerMethodField()
    estado_financiero = serializers.SerializerMethodField()
    
    class Meta:
        model = Vivienda
        fields = [
            'id', 'identificador', 'bloque', 'piso', 'tipo', 
            'metros_cuadrados', 'habitaciones', 'banos', 
            'cuota_administracion', 'fecha_registro', 'activo',
            'usuario_propietario', 'usuario_inquilino',
            'personas_autorizadas_count', 'mascotas_count', 'estado_financiero'
        ]
    
    def get_personas_autorizadas_count(self, obj):
        return obj.personaautorizada_set.filter(activo=True).count()
    
    def get_mascotas_count(self, obj):
        return obj.mascota_set.filter(activo=True).count()
    
    def get_estado_financiero(self, obj):
        # Placeholder para información financiera
        return {
            'deudas_pendientes': 0,  # Implementar cuando esté el módulo de pagos
            'monto_pendiente': '0.00',
            'ultimo_pago': None
        }

class ViviendaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para vivienda"""
    usuario_propietario = ResidenteBasicSerializer(read_only=True)
    usuario_inquilino = ResidenteBasicSerializer(read_only=True)
    personas_autorizadas = serializers.SerializerMethodField()
    mascotas = serializers.SerializerMethodField()
    vehiculos = serializers.SerializerMethodField()  # Para futuro módulo
    
    class Meta:
        model = Vivienda
        fields = [
            'id', 'identificador', 'bloque', 'piso', 'tipo',
            'metros_cuadrados', 'habitaciones', 'banos',
            'cuota_administracion', 'fecha_registro', 'activo',
            'usuario_propietario', 'usuario_inquilino',
            'personas_autorizadas', 'mascotas', 'vehiculos'
        ]
    
    def get_personas_autorizadas(self, obj):
        personas = obj.personaautorizada_set.filter(activo=True)
        return PersonaAutorizadaSerializer(personas, many=True).data
    
    def get_mascotas(self, obj):
        mascotas = obj.mascota_set.filter(activo=True)
        return MascotaSerializer(mascotas, many=True).data
    
    def get_vehiculos(self, obj):
        # Placeholder para futuros vehículos
        return []

class ViviendaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear viviendas"""
    
    class Meta:
        model = Vivienda
        fields = [
            'identificador', 'bloque', 'piso', 'tipo',
            'metros_cuadrados', 'habitaciones', 'banos',
            'cuota_administracion', 'usuario_propietario'
        ]
    
    def validate_identificador(self, value):
        if Vivienda.objects.filter(identificador=value).exists():
            raise serializers.ValidationError("Ya existe una vivienda con este identificador")
        return value
    
    def validate_usuario_propietario(self, value):
        if value:
            # Verificar que el usuario no sea ya propietario de otra vivienda activa
            if Vivienda.objects.filter(usuario_propietario=value, activo=True).exists():
                raise serializers.ValidationError("Este usuario ya es propietario de otra vivienda")
        return value

class ViviendaUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar viviendas"""
    
    class Meta:
        model = Vivienda
        fields = [
            'cuota_administracion', 'usuario_inquilino',
            'habitaciones', 'banos', 'activo'
        ]

class AssignResidentSerializer(serializers.Serializer):
    """Serializer para asignar propietario/inquilino"""
    tipo_residente = serializers.ChoiceField(choices=['propietario', 'inquilino'])
    usuario = serializers.IntegerField()
    fecha_inicio = serializers.DateTimeField(required=False)
    fecha_fin = serializers.DateTimeField(required=False)
    
    def validate_usuario(self, value):
        try:
            User.objects.get(id=value, activo=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado o inactivo")
        return value
    
    def validate(self, attrs):
        if attrs['tipo_residente'] == 'inquilino':
            if not attrs.get('fecha_inicio'):
                raise serializers.ValidationError("Fecha de inicio es requerida para inquilinos")
        return attrs

# =================== SERIALIZERS PARA PERSONAS AUTORIZADAS ===================

class PersonaAutorizadaSerializer(serializers.ModelSerializer):
    """Serializer para personas autorizadas"""
    vivienda_info = serializers.SerializerMethodField()
    autorizado_por_info = serializers.SerializerMethodField()
    vigente = serializers.SerializerMethodField()
    credenciales_activas = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonaAutorizada
        fields = [
            'id', 'vivienda', 'vivienda_info', 'autorizado_por', 'autorizado_por_info',
            'cedula', 'nombre', 'apellido', 'telefono', 'parentesco',
            'fecha_inicio', 'fecha_fin', 'fecha_registro', 'activo',
            'vigente', 'credenciales_activas'
        ]
    
    def get_vivienda_info(self, obj):
        return {
            'id': obj.vivienda.id,
            'identificador': obj.vivienda.identificador
        }
    
    def get_autorizado_por_info(self, obj):
        return {
            'id': obj.autorizado_por.id,
            'full_name': obj.autorizado_por.get_full_name()
        }
    
    def get_vigente(self, obj):
        if not obj.activo:
            return False
        now = timezone.now()
        if obj.fecha_fin and obj.fecha_fin < now:
            return False
        return obj.fecha_inicio <= now
    
    def get_credenciales_activas(self, obj):
        # Placeholder para credenciales de acceso
        return 0

class PersonaAutorizadaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear personas autorizadas"""
    
    class Meta:
        model = PersonaAutorizada
        fields = [
            'vivienda', 'cedula', 'nombre', 'apellido', 'telefono',
            'parentesco', 'fecha_inicio', 'fecha_fin'
        ]
    
    def validate_cedula(self, value):
        if PersonaAutorizada.objects.filter(cedula=value, activo=True).exists():
            raise serializers.ValidationError("Ya existe una persona autorizada con esta cédula")
        return value
    
    def validate(self, attrs):
        vivienda = attrs['vivienda']
        # Verificar que el usuario actual tenga permisos sobre esta vivienda
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if not (user.is_superuser or 
                   vivienda.usuario_propietario == user or 
                   vivienda.usuario_inquilino == user):
                raise serializers.ValidationError("No tienes permisos para autorizar personas en esta vivienda")
        
        # Validar fechas
        if attrs.get('fecha_fin') and attrs['fecha_inicio'] >= attrs['fecha_fin']:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
        
        return attrs
    
    def create(self, validated_data):
        # Asignar automáticamente quien autoriza
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['autorizado_por'] = request.user
        return super().create(validated_data)

# =================== SERIALIZERS PARA MASCOTAS ===================

class MascotaSerializer(serializers.ModelSerializer):
    """Serializer para mascotas"""
    vivienda_info = serializers.SerializerMethodField()
    edad_meses = serializers.SerializerMethodField()
    
    class Meta:
        model = Mascota
        fields = [
            'id', 'vivienda', 'vivienda_info', 'nombre', 'especie', 'raza',
            'peso', 'color', 'fecha_nacimiento', 'vacunas_al_dia',
            'foto_url', 'fecha_registro', 'activo', 'edad_meses'
        ]
    
    def get_vivienda_info(self, obj):
        return {
            'id': obj.vivienda.id,
            'identificador': obj.vivienda.identificador,
            'propietario': obj.vivienda.usuario_propietario.get_full_name() if obj.vivienda.usuario_propietario else None
        }
    
    def get_edad_meses(self, obj):
        if obj.fecha_nacimiento:
            today = date.today()
            return (today.year - obj.fecha_nacimiento.year) * 12 + (today.month - obj.fecha_nacimiento.month)
        return None

class MascotaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear mascotas"""
    
    class Meta:
        model = Mascota
        fields = [
            'vivienda', 'nombre', 'especie', 'raza', 'peso',
            'color', 'fecha_nacimiento', 'vacunas_al_dia', 'foto_url'
        ]
    
    def validate(self, attrs):
        vivienda = attrs['vivienda']
        # Verificar permisos sobre la vivienda
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if not (user.is_superuser or 
                   vivienda.usuario_propietario == user or 
                   vivienda.usuario_inquilino == user):
                raise serializers.ValidationError("No tienes permisos para registrar mascotas en esta vivienda")
        
        # Validar fecha de nacimiento
        if attrs.get('fecha_nacimiento') and attrs['fecha_nacimiento'] > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura")
        
        return attrs

# =================== SERIALIZERS PARA REPORTES ===================

class DashboardSerializer(serializers.Serializer):
    """Serializer para dashboard de residencias"""
    viviendas = serializers.DictField()
    residentes = serializers.DictField()
    mascotas = serializers.DictField()
    distribucion_por_tipo = serializers.DictField()
    ocupacion_por_bloque = serializers.ListField()

class ViviendaReportSerializer(serializers.ModelSerializer):
    """Serializer para reportes de viviendas"""
    propietario = serializers.CharField(source='usuario_propietario.get_full_name', allow_null=True)
    inquilino = serializers.CharField(source='usuario_inquilino.get_full_name', allow_null=True)
    estado_financiero = serializers.CharField(default='al_dia')  # Placeholder
    personas_autorizadas = serializers.SerializerMethodField()
    mascotas = serializers.SerializerMethodField()
    
    class Meta:
        model = Vivienda
        fields = [
            'identificador', 'propietario', 'inquilino', 'metros_cuadrados',
            'cuota_administracion', 'estado_financiero', 'personas_autorizadas', 'mascotas'
        ]
    
    def get_personas_autorizadas(self, obj):
        return obj.personaautorizada_set.filter(activo=True).count()
    
    def get_mascotas(self, obj):
        return obj.mascota_set.filter(activo=True).count()