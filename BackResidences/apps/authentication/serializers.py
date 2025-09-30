from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Rol, UsuarioRol, Permiso, RolPermiso, AuditoriaUsuario

# =================== SERIALIZERS DE AUTENTICACIÓN ===================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'confirm_password',
            'first_name', 'last_name', 'telefono', 
            'documento_tipo', 'documento_numero'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer para login de usuarios"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Email o contraseña incorrectos')
            if not user.activo:
                raise serializers.ValidationError('Usuario inactivo')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Email y contraseña son requeridos')
        
        return attrs

# =================== SERIALIZERS DE USUARIOS ===================

class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para lista de usuarios"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    roles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'telefono', 'documento_tipo', 'documento_numero', 'fecha_registro',
            'ultimo_login', 'activo', 'email_verificado', 'roles_count'
        ]
    
    def get_roles_count(self, obj):
        return UsuarioRol.objects.filter(usuario=obj, activo=True).count()

class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para usuarios"""
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'telefono', 'documento_tipo', 'documento_numero', 'fecha_registro',
            'ultimo_login', 'activo', 'email_verificado', 'roles', 'permissions'
        ]

    def get_roles(self, obj):
        roles_usuario = obj.get_roles()
        return [
            {
                'id': ur.rol.id,
                'nombre': ur.rol.nombre,
                'descripcion': ur.rol.descripcion,
                'fecha_asignacion': ur.fecha_asignacion,
                'fecha_vencimiento': ur.fecha_vencimiento
            }
            for ur in roles_usuario
        ]

    def get_permissions(self, obj):
        return obj.get_permissions()

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar información de usuario"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'telefono', 
            'documento_tipo', 'documento_numero'
        ]
    
    def validate_documento_numero(self, value):
        user = self.instance
        if user and User.objects.filter(documento_numero=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Ya existe un usuario con este número de documento")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden")
        return attrs

# =================== SERIALIZERS DE PERMISOS ===================

class PermisoSerializer(serializers.ModelSerializer):
    """Serializer para permisos"""
    class Meta:
        model = Permiso
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'modulo', 'activo']

# =================== SERIALIZERS DE ROLES ===================

class RolSerializer(serializers.ModelSerializer):
    """Serializer para roles"""
    permisos = PermisoSerializer(many=True, read_only=True)
    usuarios_count = serializers.SerializerMethodField()
    permisos_count = serializers.SerializerMethodField()

    class Meta:
        model = Rol
        fields = [
            'id', 'nombre', 'descripcion', 'created_at', 'activo',
            'permisos', 'usuarios_count', 'permisos_count'
        ]

    def get_usuarios_count(self, obj):
        return UsuarioRol.objects.filter(rol=obj, activo=True).count()

    def get_permisos_count(self, obj):
        return RolPermiso.objects.filter(rol=obj).count()

class RolCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear roles"""
    permisos = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="Lista de códigos de permisos a asignar al rol"
    )
    
    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion', 'permisos']
    
    def create(self, validated_data):
        permisos_codes = validated_data.pop('permisos', [])
        rol = Rol.objects.create(**validated_data)
        
        # Asignar permisos al rol
        for codigo in permisos_codes:
            try:
                permiso = Permiso.objects.get(codigo=codigo, activo=True)
                RolPermiso.objects.create(rol=rol, permiso=permiso)
            except Permiso.DoesNotExist:
                pass  # Ignorar permisos que no existen
        
        return rol

# =================== SERIALIZERS DE RELACIONES ===================

class UsuarioRolSerializer(serializers.ModelSerializer):
    """Serializer para relación usuario-rol"""
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    asignado_por_email = serializers.CharField(source='asignado_por.email', read_only=True)

    class Meta:
        model = UsuarioRol
        fields = [
            'id', 'usuario', 'rol', 'fecha_asignacion', 'fecha_vencimiento',
            'asignado_por', 'activo', 'rol_nombre', 'usuario_email', 'asignado_por_email'
        ]

class AssignRoleSerializer(serializers.Serializer):
    """Serializer para asignar rol a usuario"""
    rol_id = serializers.IntegerField()
    fecha_vencimiento = serializers.DateTimeField(required=False, allow_null=True)

    def validate_rol_id(self, value):
        try:
            Rol.objects.get(id=value, activo=True)
        except Rol.DoesNotExist:
            raise serializers.ValidationError('El rol especificado no existe o está inactivo')
        return value

# =================== SERIALIZERS DE AUDITORÍA ===================

class AuditoriaUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para auditoría de usuarios"""
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)

    class Meta:
        model = AuditoriaUsuario
        fields = [
            'id', 'usuario_email', 'usuario_nombre', 'accion', 'tabla',
            'id_registro_afectado', 'ip_origen', 'user_agent', 'modulo',
            'detalles', 'fecha_hora'
        ]