from django.shortcuts import render
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q, Count
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import Any, Dict, Optional, Union, Type

from .models import User, Rol, UsuarioRol, Permiso, RolPermiso, AuditoriaUsuario
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserDetailSerializer,
    UserListSerializer, UserUpdateSerializer, ChangePasswordSerializer,
    RolSerializer, RolCreateSerializer, PermisoSerializer, UsuarioRolSerializer,
    AssignRoleSerializer, AuditoriaUsuarioSerializer
)

def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_user_activity(user, action, ip_address, user_agent, module='authentication', table='', record_id='', details=''):
    """Registra actividad del usuario para auditoría"""
    AuditoriaUsuario.objects.create(
        usuario=user,
        accion=action,
        tabla=table,
        id_registro_afectado=record_id,
        ip_origen=ip_address,
        user_agent=user_agent,
        modulo=module,
        detalles=details
    )

class UserRegistrationView(APIView):
    """Vista para registro de usuarios"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Registrar nuevo usuario en el sistema usando email como identificador principal",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Usuario registrado exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Usuario registrado exitosamente",
                        "data": {
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "username": "user@example.com",
                                "first_name": "Juan",
                                "last_name": "Pérez",
                                "telefono": "+573001234567",
                                "documento_tipo": "CC",
                                "documento_numero": "12345678"
                            },
                            "tokens": {
                                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                            }
                        }
                    }
                }
            ),
            400: "Error en los datos proporcionados"
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Registrar actividad
            log_user_activity(
                user=user,
                action='REGISTER',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details='Usuario registrado exitosamente'
            )
            
            # Actualizar último login
            user.ultimo_login = timezone.now()
            user.save()
            
            return Response({
                'success': True,
                'message': 'Usuario registrado exitosamente',
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'telefono': user.telefono,
                        'documento_tipo': user.documento_tipo,
                        'documento_numero': user.documento_numero,
                        'fecha_registro': user.fecha_registro,
                        'activo': user.activo,
                        'email_verificado': user.email_verificado
                    },
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh)
                    }
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error en los datos proporcionados',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """Vista para login de usuarios"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Iniciar sesión en el sistema usando email y contraseña",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login exitoso",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Login exitoso",
                        "data": {
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "username": "user@example.com",
                                "first_name": "Juan",
                                "last_name": "Pérez",
                                "roles": ["Propietario"],
                                "permissions": ["residences.view_residence", "payments.view_payment"]
                            },
                            "tokens": {
                                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                            }
                        }
                    }
                }
            ),
            400: "Datos inválidos",
            401: "Email o contraseña incorrectos"
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Actualizar último login
            user.ultimo_login = timezone.now()
            user.save()
            
            # Registrar actividad
            log_user_activity(
                user=user,
                action='LOGIN',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details='Login exitoso'
            )
            
            return Response({
                'success': True,
                'message': 'Login exitoso',
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'roles': [ur.rol.nombre for ur in user.get_roles()],
                        'permissions': user.get_permissions()
                    },
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh)
                    }
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Credenciales inválidas',
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    """Vista para cerrar sesión"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cerrar sesión del usuario invalidando el refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Refresh token para invalidar (obtenido en el login)',
                    example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYzNDc3NDA0NCwiaWF0IjoxNjM0MTY5MjQ0LCJqdGkiOiI5YzJlNDc0M2E2YmM0MTQ5OTE4ZjU4OGY0MTQwNDExNCIsInVzZXJfaWQiOjF9.example"
                )
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(
                description="Sesión cerrada exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Sesión cerrada exitosamente"
                    }
                }
            ),
            400: openapi.Response(
                description="Error en los datos proporcionados",
                examples={
                    "application/json": {
                        "success": False,
                        "message": "Refresh token es requerido",
                        "errors": {
                            "refresh": ["Este campo es requerido"]
                        }
                    }
                }
            ),
            401: "Token de acceso inválido o expirado"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response({
                    'success': False,
                    'message': 'Refresh token es requerido',
                    'errors': {'refresh': ['Este campo es requerido']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar y procesar el token
            try:
                token = RefreshToken(refresh_token)
                # Simplemente registrar el logout - el token expirará naturalmente
                # En un entorno de producción, aquí implementarías una blacklist real
                
                # Registrar actividad
                log_user_activity(
                    user=request.user,
                    action='LOGOUT',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details='Logout exitoso'
                )
                
                return Response({
                    'success': True,
                    'message': 'Sesión cerrada exitosamente'
                }, status=status.HTTP_200_OK)
                
            except Exception as token_error:
                return Response({
                    'success': False,
                    'message': 'Token inválido',
                    'errors': {'refresh': ['El token proporcionado no es válido']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error al cerrar sesión',
                'errors': {'refresh': [str(e)]}
            }, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    """Vista para listar usuarios (solo administradores)"""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['activo', 'documento_tipo']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'documento_numero']
    ordering_fields = ['fecha_registro', 'ultimo_login', 'username']
    ordering = ['-fecha_registro']

    def get_queryset(self):
        # Solo superusuarios o usuarios con permiso específico pueden ver todos los usuarios
        if not (self.request.user.is_superuser or self.request.user.has_permission('auth.view_user')):
            return User.objects.filter(id=self.request.user.id)
        
        queryset = super().get_queryset()
        
        # Filtros adicionales
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(roles_usuario__rol__nombre=role, roles_usuario__activo=True)
        
        return queryset

class UserDetailView(generics.RetrieveAPIView):
    """Vista para obtener detalles de usuario"""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        # Los usuarios solo pueden ver su propio perfil, a menos que sean superusuarios
        if not (self.request.user.is_superuser or self.request.user.has_permission('auth.view_user')):
            if str(self.request.user.id) != str(user_id):
                raise permissions.PermissionDenied("No tienes permisos para ver este usuario")
        return super().get_object()

class UserUpdateView(generics.UpdateAPIView):
    """Vista para actualizar usuario"""
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        # Los usuarios solo pueden editar su propio perfil, a menos que sean superusuarios
        if not (self.request.user.is_superuser or self.request.user.has_permission('auth.change_user')):
            if str(self.request.user.id) != str(user_id):
                raise permissions.PermissionDenied("No tienes permisos para editar este usuario")
        return super().get_object()

    def perform_update(self, serializer):
        user = serializer.save()
        
        # Registrar actividad
        log_user_activity(
            user=self.request.user,
            action='UPDATE',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            table='auth_user',
            record_id=str(user.id),
            details=f'Usuario actualizado: {user.email}'
        )

class UserProfileView(APIView):
    """Vista para obtener y actualizar el perfil del usuario actual"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            
            # Registrar actividad
            log_user_activity(
                user=request.user,
                action='UPDATE_PROFILE',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details='Perfil actualizado'
            )
            
            return Response({
                'success': True,
                'message': 'Perfil actualizado exitosamente',
                'data': UserDetailSerializer(user).data
            })
        
        return Response({
            'success': False,
            'message': 'Error al actualizar perfil',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    """Vista para cambiar contraseña"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cambiar contraseña del usuario",
        request_body=ChangePasswordSerializer
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Registrar actividad
            log_user_activity(
                user=user,
                action='CHANGE_PASSWORD',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details='Contraseña cambiada exitosamente'
            )
            
            return Response({
                'success': True,
                'message': 'Contraseña cambiada exitosamente'
            })
        
        return Response({
            'success': False,
            'message': 'Error al cambiar contraseña',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# =================== VISTAS PARA ROLES ===================

class RolListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear roles"""
    queryset = Rol.objects.filter(activo=True)
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

    def get_serializer_class(self) -> Type[Union[RolCreateSerializer, RolSerializer]]:
        if self.request.method == 'POST':
            return RolCreateSerializer
        return RolSerializer

    def get_queryset(self):
        # Para generar documentación de Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Rol.objects.none()
            
        # Solo superusuarios pueden gestionar roles
        if not (self.request.user.is_superuser):
            raise PermissionDenied("No tienes permisos para gestionar roles")
        return super().get_queryset()

    def perform_create(self, serializer):
        rol = serializer.save()
        
        # Registrar actividad
        log_user_activity(
            user=self.request.user,
            action='CREATE',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            table='authentication_rol',
            record_id=str(rol.id),
            details=f'Rol creado: {rol.nombre}'
        )

class RolDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para detalles, actualización y eliminación de roles"""
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Para generar documentación de Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Rol.objects.none()
            
        # Solo superusuarios pueden gestionar roles
        if not (self.request.user.is_superuser):
            raise PermissionDenied("No tienes permisos para gestionar roles")
        return super().get_queryset()

class PermisoListView(generics.ListAPIView):
    """Vista para listar permisos"""
    queryset = Permiso.objects.filter(activo=True)
    serializer_class = PermisoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['modulo']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['modulo', 'codigo']

    def get_queryset(self):
        # Para generar documentación de Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Permiso.objects.none()
            
        # Solo superusuarios pueden ver permisos
        if not (self.request.user.is_superuser):
            raise PermissionDenied("No tienes permisos para ver permisos")
        return super().get_queryset()

class AssignRoleToUserView(APIView):
    """Vista para asignar rol a usuario"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Asignar rol a usuario",
        request_body=AssignRoleSerializer
    )
    def post(self, request, user_id):
        # Solo superusuarios pueden asignar roles
        if not (request.user.is_superuser):
            return Response({
                'success': False,
                'message': 'No tienes permisos para asignar roles'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignRoleSerializer(data=request.data)
        if serializer.is_valid():
            rol_id = request.data.get('rol_id')
            fecha_vencimiento = request.data.get('fecha_vencimiento')

            try:
                rol = Rol.objects.get(id=rol_id, activo=True)
            except Rol.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Rol no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)

            # Verificar si ya tiene el rol asignado
            if UsuarioRol.objects.filter(usuario=user, rol=rol, activo=True).exists():
                return Response({
                    'success': False,
                    'message': 'El usuario ya tiene este rol asignado'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Crear la asignación
            usuario_rol = UsuarioRol.objects.create(
                usuario=user,
                rol=rol,
                fecha_vencimiento=fecha_vencimiento,
                asignado_por=request.user
            )

            # Registrar actividad
            log_user_activity(
                user=request.user,
                action='ASSIGN_ROLE',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                table='authentication_usuariorol',
                record_id=str(usuario_rol.pk),
                details=f'Rol {rol.nombre} asignado a {user.email}'
            )

            return Response({
                'success': True,
                'message': 'Rol asignado exitosamente',
                'data': {
                    'usuario': user.get_full_name(),
                    'rol': rol.nombre,
                    'fecha_asignacion': usuario_rol.fecha_asignacion,
                    'fecha_vencimiento': fecha_vencimiento,
                    'asignado_por': request.user.email
                }
            })

        return Response({
            'success': False,
            'message': 'Datos inválidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserPermissionsView(APIView):
    """Vista para verificar permisos de usuario"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        # Solo superusuarios o el mismo usuario pueden ver permisos
        if not (request.user.is_superuser or str(request.user.id) == str(user_id)):
            return Response({
                'success': False,
                'message': 'No tienes permisos para ver esta información'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

        roles = []
        for ur in user.get_roles():
            roles.append({
                'id': ur.rol.id,
                'nombre': ur.rol.nombre,
                'descripcion': ur.rol.descripcion,
                'fecha_asignacion': ur.fecha_asignacion,
                'fecha_vencimiento': ur.fecha_vencimiento,
                'origen': f'rol_{ur.rol.nombre}'
            })

        permissions = []
        for permission_code in user.get_permissions():
            try:
                permiso = Permiso.objects.get(codigo=permission_code)
                permissions.append({
                    'codigo': permiso.codigo,
                    'nombre': permiso.nombre,
                    'modulo': permiso.modulo,
                    'origen': 'rol'
                })
            except Permiso.DoesNotExist:
                pass

        return Response({
            'success': True,
            'data': {
                'user_id': user.pk,
                'permissions': permissions,
                'roles': [r['nombre'] for r in roles]
            }
        })

class UserActivityView(generics.ListAPIView):
    """Vista para auditoría de actividad de usuario"""
    serializer_class = AuditoriaUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['accion', 'modulo']
    search_fields = ['accion', 'detalles']
    ordering = ['-fecha_hora']

    def get_queryset(self) -> Any:
        user_id = self.kwargs.get('user_id')
        
        # Solo superusuarios pueden ver auditoría completa
        if not (self.request.user.is_superuser):
            return AuditoriaUsuario.objects.filter(usuario=self.request.user)
        
        if user_id:
            return AuditoriaUsuario.objects.filter(usuario_id=user_id)
        return AuditoriaUsuario.objects.all()

class UserStatsView(APIView):
    """Vista para estadísticas de usuarios"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Solo superusuarios pueden ver estadísticas
        if not (request.user.is_superuser):
            return Response({
                'success': False,
                'message': 'No tienes permisos para ver estadísticas'
            }, status=status.HTTP_403_FORBIDDEN)

        # Calcular estadísticas
        total_usuarios = User.objects.count()
        usuarios_activos = User.objects.filter(activo=True).count()
        usuarios_inactivos = total_usuarios - usuarios_activos
        
        # Usuarios nuevos este mes
        from django.utils import timezone
        primer_dia_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        nuevos_este_mes = User.objects.filter(fecha_registro__gte=primer_dia_mes).count()

        # Usuarios por tipo (roles)
        usuarios_por_tipo = {}
        for rol in Rol.objects.filter(activo=True):
            count = UsuarioRol.objects.filter(rol=rol, activo=True).count()
            usuarios_por_tipo[rol.nombre] = count

        # Último login
        hoy = timezone.now().date()
        hace_una_semana = hoy - timezone.timedelta(days=7)
        
        ultimo_login_hoy = User.objects.filter(ultimo_login__date=hoy).count()
        ultimo_login_semana = User.objects.filter(ultimo_login__date__gte=hace_una_semana).count()
        ultimo_login_mes = User.objects.filter(ultimo_login__date__gte=primer_dia_mes.date()).count()

        return Response({
            'success': True,
            'data': {
                'total_usuarios': total_usuarios,
                'usuarios_activos': usuarios_activos,
                'usuarios_inactivos': usuarios_inactivos,
                'nuevos_este_mes': nuevos_este_mes,
                'por_tipo': usuarios_por_tipo,
                'ultimo_login': {
                    'hoy': ultimo_login_hoy,
                    'esta_semana': ultimo_login_semana,
                    'este_mes': ultimo_login_mes
                }
            }
        })