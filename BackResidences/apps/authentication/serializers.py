from rest_framework import serializers
from .models import User, Rol, UsuarioRol, Permiso, RolPermiso

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'telefono', 'documento_tipo', 'documento_numero', 'fecha_registro', 'activo']

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'created_at', 'updated_at', 'activo']

class UsuarioRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioRol
        fields = ['id', 'usuario', 'rol', 'fecha_asignacion', 'fecha_vencimiento', 'asignado_por', 'created_at', 'updated_at', 'activo']

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'modulo', 'created_at', 'updated_at', 'activo']

class RolPermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolPermiso
        fields = ['rol', 'permiso', 'asignado_por', 'fecha_asignacion']