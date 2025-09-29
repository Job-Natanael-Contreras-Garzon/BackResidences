from django.contrib import admin
from .models import User, Rol, UsuarioRol, Permiso, RolPermiso

admin.site.register(User)
admin.site.register(Rol)
admin.site.register(UsuarioRol)
admin.site.register(Permiso)
admin.site.register(RolPermiso)