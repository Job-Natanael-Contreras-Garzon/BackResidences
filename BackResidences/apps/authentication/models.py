from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from apps.core.models import BaseModel

class Rol(BaseModel):
    """Roles del sistema"""
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

class Permiso(BaseModel):
    """Permisos del sistema"""
    codigo = models.CharField(max_length=100, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    modulo = models.CharField(max_length=50, verbose_name="Módulo")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta: # type: ignore
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"

class User(AbstractUser):
    """Usuario extendido del sistema"""
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    documento_tipo = models.CharField(
        max_length=10, 
        choices=[
            ('CC', 'Cédula de Ciudadanía'),
            ('CE', 'Cédula de Extranjería'),
            ('PAS', 'Pasaporte'),
        ],
        verbose_name="Tipo de documento"
    )
    documento_numero = models.CharField(max_length=20, unique=True, verbose_name="Número de documento")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    ultimo_login = models.DateTimeField(null=True, blank=True, verbose_name="Último acceso")
    email_verificado = models.BooleanField(default=False, verbose_name="Email verificado")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'documento_numero']

    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"

    def get_roles(self):
        """Obtiene los roles activos del usuario"""
        from django.utils import timezone
        return self.roles_usuario.filter(
            activo=True
        ).filter(
            models.Q(fecha_vencimiento__isnull=True) | models.Q(fecha_vencimiento__gt=timezone.now())
        ).select_related('rol')

    def has_role(self, role_name):
        """Verifica si el usuario tiene un rol específico"""
        return self.get_roles().filter(rol__nombre=role_name).exists()

    def get_permissions(self):
        """Obtiene todos los permisos del usuario a través de sus roles"""
        roles = self.get_roles()
        permissions = set()
        for usuario_rol in roles:
            rol_permisos = RolPermiso.objects.filter(rol=usuario_rol.rol).select_related('permiso')
            for rol_permiso in rol_permisos:
                permissions.add(rol_permiso.permiso.codigo)
        return list(permissions)

    def has_permission(self, permission_code):
        """Verifica si el usuario tiene un permiso específico"""
        if self.is_superuser:
            return True
        return permission_code in self.get_permissions()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

class UsuarioRol(BaseModel):
    """Relación usuario-rol"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name='roles_usuario')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, verbose_name="Rol")
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de asignación")
    fecha_vencimiento = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de vencimiento")
    asignado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='roles_asignados', verbose_name="Asignado por")

    class Meta: # type: ignore
        unique_together = ['usuario', 'rol']
        verbose_name = "Usuario-Rol"
        verbose_name_plural = "Usuario-Roles"

    def __str__(self):
        return f"{self.usuario.email} - {self.rol.nombre}"

    @property
    def is_expired(self):
        """Verifica si el rol ha expirado"""
        if self.fecha_vencimiento:
            return timezone.now() > self.fecha_vencimiento
        return False

class Permiso(BaseModel):
    """Permisos del sistema"""
    codigo = models.CharField(max_length=100, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    modulo = models.CharField(max_length=50, verbose_name="Módulo")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta: # type: ignore
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"

class RolPermiso(models.Model):
    """Relación rol-permiso"""
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
    asignado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['rol', 'permiso']
        verbose_name = "Rol-Permiso"
        verbose_name_plural = "Rol-Permisos"

class AuditoriaUsuario(BaseModel):
    """Auditoría de actividades de usuarios"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    accion = models.CharField(max_length=50, verbose_name="Acción")
    tabla = models.CharField(max_length=100, blank=True, verbose_name="Tabla afectada")
    id_registro_afectado = models.CharField(max_length=50, blank=True, verbose_name="ID del registro")
    ip_origen = models.GenericIPAddressField(verbose_name="IP de origen")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    modulo = models.CharField(max_length=50, verbose_name="Módulo")
    detalles = models.TextField(blank=True, verbose_name="Detalles")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")

    def __str__(self):
        return f"{self.usuario.email} - {self.accion} - {self.fecha_hora}"

    class Meta: # type: ignore
        verbose_name = "Auditoría de Usuario"
        verbose_name_plural = "Auditoría de Usuarios"
        ordering = ['-fecha_hora']