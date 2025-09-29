"""
Comando para inicializar datos básicos del sistema de autenticación
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.authentication.models import Rol, Permiso, RolPermiso

User = get_user_model()

class Command(BaseCommand):
    help = 'Inicializa datos básicos de roles y permisos del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando creación de datos básicos...')
        
        # Crear permisos básicos
        permisos_data = [
            # Autenticación
            {'codigo': 'auth.view_user', 'nombre': 'Ver usuarios', 'descripcion': 'Puede ver la lista de usuarios', 'modulo': 'authentication'},
            {'codigo': 'auth.add_user', 'nombre': 'Crear usuarios', 'descripcion': 'Puede crear nuevos usuarios', 'modulo': 'authentication'},
            {'codigo': 'auth.change_user', 'nombre': 'Editar usuarios', 'descripcion': 'Puede editar información de usuarios', 'modulo': 'authentication'},
            {'codigo': 'auth.delete_user', 'nombre': 'Eliminar usuarios', 'descripcion': 'Puede eliminar usuarios', 'modulo': 'authentication'},
            {'codigo': 'auth.assign_role', 'nombre': 'Asignar roles', 'descripcion': 'Puede asignar roles a usuarios', 'modulo': 'authentication'},
            
            # Residencias
            {'codigo': 'residences.view_residence', 'nombre': 'Ver residencias', 'descripcion': 'Puede ver información de residencias', 'modulo': 'residences'},
            {'codigo': 'residences.add_residence', 'nombre': 'Crear residencias', 'descripcion': 'Puede crear nuevas residencias', 'modulo': 'residences'},
            {'codigo': 'residences.change_residence', 'nombre': 'Editar residencias', 'descripcion': 'Puede editar información de residencias', 'modulo': 'residences'},
            {'codigo': 'residences.delete_residence', 'nombre': 'Eliminar residencias', 'descripcion': 'Puede eliminar residencias', 'modulo': 'residences'},
            
            # Seguridad
            {'codigo': 'security.view_access', 'nombre': 'Ver accesos', 'descripcion': 'Puede ver registros de acceso', 'modulo': 'security'},
            {'codigo': 'security.manage_access', 'nombre': 'Gestionar accesos', 'descripcion': 'Puede gestionar el control de acceso', 'modulo': 'security'},
            
            # Pagos
            {'codigo': 'payments.view_payment', 'nombre': 'Ver pagos', 'descripcion': 'Puede ver información de pagos', 'modulo': 'payments'},
            {'codigo': 'payments.add_payment', 'nombre': 'Registrar pagos', 'descripcion': 'Puede registrar nuevos pagos', 'modulo': 'payments'},
            {'codigo': 'payments.change_payment', 'nombre': 'Editar pagos', 'descripcion': 'Puede editar información de pagos', 'modulo': 'payments'},
            
            # Áreas comunes
            {'codigo': 'common_areas.view_area', 'nombre': 'Ver áreas comunes', 'descripcion': 'Puede ver información de áreas comunes', 'modulo': 'common_areas'},
            {'codigo': 'common_areas.book_area', 'nombre': 'Reservar áreas', 'descripcion': 'Puede hacer reservas de áreas comunes', 'modulo': 'common_areas'},
            {'codigo': 'common_areas.manage_bookings', 'nombre': 'Gestionar reservas', 'descripcion': 'Puede gestionar todas las reservas', 'modulo': 'common_areas'},
        ]
        
        for permiso_data in permisos_data:
            permiso, created = Permiso.objects.get_or_create(
                codigo=permiso_data['codigo'],
                defaults={
                    'nombre': permiso_data['nombre'],
                    'descripcion': permiso_data['descripcion'],
                    'modulo': permiso_data['modulo']
                }
            )
            if created:
                self.stdout.write(f'✓ Permiso creado: {permiso.codigo}')
            else:
                self.stdout.write(f'- Permiso ya existe: {permiso.codigo}')
        
        # Crear roles básicos
        roles_data = [
            {
                'nombre': 'Administrador',
                'descripcion': 'Administrador del sistema con todos los permisos',
                'permisos': [p['codigo'] for p in permisos_data]  # Todos los permisos
            },
            {
                'nombre': 'Conserje',
                'descripcion': 'Conserje con permisos de seguridad y áreas comunes',
                'permisos': [
                    'security.view_access',
                    'security.manage_access',
                    'common_areas.view_area',
                    'common_areas.manage_bookings',
                    'residences.view_residence'
                ]
            },
            {
                'nombre': 'Propietario',
                'descripcion': 'Propietario con permisos básicos',
                'permisos': [
                    'residences.view_residence',
                    'payments.view_payment',
                    'common_areas.view_area',
                    'common_areas.book_area'
                ]
            },
            {
                'nombre': 'Inquilino',
                'descripcion': 'Inquilino con permisos limitados',
                'permisos': [
                    'common_areas.view_area',
                    'common_areas.book_area'
                ]
            }
        ]
        
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={
                    'descripcion': rol_data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'✓ Rol creado: {rol.nombre}')
                
                # Asignar permisos al rol
                for codigo_permiso in rol_data['permisos']:
                    try:
                        permiso = Permiso.objects.get(codigo=codigo_permiso)
                        RolPermiso.objects.get_or_create(
                            rol=rol,
                            permiso=permiso
                        )
                    except Permiso.DoesNotExist:
                        self.stdout.write(f'⚠ Permiso no encontrado: {codigo_permiso}')
                        
                self.stdout.write(f'  → {len(rol_data["permisos"])} permisos asignados')
            else:
                self.stdout.write(f'- Rol ya existe: {rol.nombre}')
        
        # Crear superusuario si no existe
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('\n¿Desea crear un superusuario? (s/n): ', ending='')
            respuesta = input().lower()
            
            if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                email = input('Email del superusuario: ')
                password = input('Contraseña: ')
                
                superuser = User.objects.create_user(
                    email=email,
                    password=password,
                    username=email.split('@')[0],
                    first_name='Super',
                    last_name='Usuario',
                    is_staff=True,
                    is_superuser=True,
                    activo=True,
                    email_verificado=True
                )
                
                self.stdout.write(f'✓ Superusuario creado: {superuser.email}')
        else:
            self.stdout.write('- Ya existe un superusuario en el sistema')
        
        self.stdout.write('\n🎉 Inicialización completada exitosamente!')
        self.stdout.write(f'📊 Total permisos: {Permiso.objects.count()}')
        self.stdout.write(f'👥 Total roles: {Rol.objects.count()}')
        self.stdout.write(f'👤 Total usuarios: {User.objects.count()}')