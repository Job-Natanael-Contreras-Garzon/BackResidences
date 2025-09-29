from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import BaseModel

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

    # USERNAME_FIELD = 'email'  # Si quieres usar email como login
    REQUIRED_FIELDS = ['email', 'documento_numero']

    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

class Rol(BaseModel):
    """Roles del sistema"""
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

class UsuarioRol(BaseModel):
    """Relación usuario-rol"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, verbose_name="Rol")
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de asignación")
    fecha_vencimiento = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de vencimiento")
    asignado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='roles_asignados', verbose_name="Asignado por")

    class Meta: # type: ignore
        unique_together = ['usuario', 'rol']
        verbose_name = "Usuario-Rol"
        verbose_name_plural = "Usuario-Roles"

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre}"

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