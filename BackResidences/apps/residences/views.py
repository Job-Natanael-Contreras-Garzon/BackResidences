from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Importación condicional de django_filters
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None

from .models import Vivienda, PersonaAutorizada, Mascota
from .serializers import (
    ViviendaListSerializer, ViviendaDetailSerializer, ViviendaCreateSerializer,
    ViviendaUpdateSerializer, AssignResidentSerializer,
    PersonaAutorizadaSerializer, PersonaAutorizadaCreateSerializer,
    MascotaSerializer, MascotaCreateSerializer,
    DashboardSerializer, ViviendaReportSerializer
)

User = get_user_model()

def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# =================== VISTAS PARA GESTIÓN DE VIVIENDAS ===================

class ViviendaListView(generics.ListAPIView):
    """Vista para listar viviendas"""
    queryset = Vivienda.objects.all()
    serializer_class = ViviendaListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configurar filtros de forma condicional
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    filterset_fields = ['tipo', 'bloque', 'piso', 'activo']
    search_fields = ['identificador', 'bloque']
    ordering_fields = ['identificador', 'fecha_registro', 'cuota_administracion']
    ordering = ['identificador']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de viviendas del condominio
        
        ### Filtros disponibles:
        - `tipo`: apartamento, casa, penthouse, local
        - `bloque`: nombre del bloque o torre
        - `piso`: número de piso
        - `activo`: true/false
        - `tiene_propietario`: true/false - viviendas con/sin propietario
        - `tiene_inquilino`: true/false - viviendas con/sin inquilino
        
        ### Búsqueda:
        - `search`: buscar por identificador o bloque
        
        ### Ordenamiento:
        - `ordering`: identificador, fecha_registro, cuota_administracion
        """,
        responses={
            200: openapi.Response(
                description="Lista de viviendas",
                examples={
                    "application/json": {
                        "count": 150,
                        "next": "http://api.example.org/viviendas/?page=2",
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "identificador": "TORRE-A-101",
                                "bloque": "TORRE-A",
                                "tipo": "apartamento",
                                "piso": 1,
                                "habitaciones": 3,
                                "banos": 2,
                                "metros_cuadrados": "85.50",
                                "cuota_administracion": "250000.00",
                                "tiene_propietario": True,
                                "tiene_inquilino": False,
                                "activo": True
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado - Token JWT requerido"
        },
        tags=['Viviendas']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        from django.db.models import QuerySet
        from typing import Any
        queryset: Any = Vivienda.objects.all()
        
        # Filtros adicionales usando request
        if hasattr(self, 'request') and self.request:
            # Usar getattr para evitar errores de tipado
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            tiene_propietario = query_params.get('tiene_propietario')
            if tiene_propietario is not None:
                if tiene_propietario.lower() == 'true':
                    queryset = queryset.filter(usuario_propietario__isnull=False)
                else:
                    queryset = queryset.filter(usuario_propietario__isnull=True)
            
            tiene_inquilino = query_params.get('tiene_inquilino')
            if tiene_inquilino is not None:
                if tiene_inquilino.lower() == 'true':
                    queryset = queryset.filter(usuario_inquilino__isnull=False)
                else:
                    queryset = queryset.filter(usuario_inquilino__isnull=True)
        
        return queryset

class ViviendaCreateView(generics.CreateAPIView):
    """Vista para crear nueva vivienda"""
    queryset = Vivienda.objects.all()
    serializer_class = ViviendaCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crear nueva vivienda en el condominio",
        request_body=ViviendaCreateSerializer,
        responses={
            201: openapi.Response(
                description="Vivienda creada exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Vivienda creada exitosamente",
                        "data": {
                            "id": 121,
                            "identificador": "TORRE-B-205",
                            "bloque": "TORRE-B",
                            "tipo": "apartamento",
                            "metros_cuadrados": "92.75",
                            "cuota_administracion": "275000.00"
                        }
                    }
                }
            ),
            400: "Datos inválidos",
            403: "Sin permisos para crear viviendas"
        }
    )
    def post(self, request, *args, **kwargs):
        # Solo superusuarios o usuarios con permiso específico
        if not (request.user.is_superuser):
            return Response({
                'success': False,
                'message': 'No tienes permisos para crear viviendas'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            vivienda = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Vivienda creada exitosamente',
                'data': ViviendaDetailSerializer(vivienda).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear vivienda',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ViviendaDetailView(generics.RetrieveAPIView):
    """Vista para detalles de vivienda"""
    queryset = Vivienda.objects.all()
    serializer_class = ViviendaDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Obtener detalles completos de una vivienda específica
        
        Incluye información del propietario, inquilino, personas autorizadas y mascotas.
        """,
        responses={
            200: openapi.Response(
                description="Detalles de la vivienda",
                examples={
                    "application/json": {
                        "id": 1,
                        "identificador": "TORRE-A-101",
                        "bloque": "TORRE-A",
                        "tipo": "apartamento",
                        "piso": 1,
                        "habitaciones": 3,
                        "banos": 2,
                        "metros_cuadrados": "85.50",
                        "cuota_administracion": "250000.00",
                        "propietario": {
                            "id": 5,
                            "full_name": "Juan Pérez",
                            "email": "juan.perez@email.com"
                        },
                        "inquilino": None,
                        "personas_autorizadas": [
                            {
                                "id": 1,
                                "nombre": "María Pérez",
                                "parentesco": "esposa",
                                "vigente": True
                            }
                        ],
                        "mascotas": [
                            {
                                "id": 1,
                                "nombre": "Max",
                                "especie": "perro",
                                "raza": "Golden Retriever"
                            }
                        ]
                    }
                }
            ),
            404: "Vivienda no encontrada",
            401: "No autorizado"
        },
        tags=['Viviendas']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ViviendaUpdateView(generics.UpdateAPIView):
    """Vista para actualizar vivienda"""
    queryset = Vivienda.objects.all()
    serializer_class = ViviendaUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        vivienda = super().get_object()
        # Verificar permisos: solo superusuarios o propietarios pueden actualizar
        if not (self.request.user.is_superuser or 
                vivienda.usuario_propietario == self.request.user):
            raise PermissionDenied("No tienes permisos para actualizar esta vivienda")
        return vivienda

class AssignResidentView(APIView):
    """Vista para asignar propietario/inquilino a vivienda"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Asignar propietario o inquilino a una vivienda",
        request_body=AssignResidentSerializer
    )
    def patch(self, request, vivienda_id):
        try:
            vivienda = Vivienda.objects.get(id=vivienda_id)
        except Vivienda.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Vivienda no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        # Solo superusuarios pueden asignar residentes
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No tienes permisos para asignar residentes'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = AssignResidentSerializer(data=request.data)
        if serializer.is_valid():
            # Acceder a los campos directamente desde el serializer
            tipo_residente = request.data.get('tipo_residente')
            usuario_id = request.data.get('usuario')
            
            if not tipo_residente or not usuario_id:
                return Response({
                    'success': False,
                    'message': 'Tipo de residente y usuario son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                usuario = User.objects.get(id=usuario_id, activo=True)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)

            # Asignar según tipo usando setattr para evitar errores de tipado
            if tipo_residente == 'propietario':
                setattr(vivienda, 'usuario_propietario', usuario)
            else:  # inquilino
                setattr(vivienda, 'usuario_inquilino', usuario)
            
            vivienda.save()

            return Response({
                'success': True,
                'message': f'{str(tipo_residente).title()} asignado exitosamente',
                'data': {
                    'vivienda': vivienda.identificador,
                    'tipo_residente': tipo_residente,
                    'usuario': {
                        'id': usuario.pk,
                        'full_name': usuario.get_full_name()
                    },
                    'fecha_asignacion': timezone.now()
                }
            })

        return Response({
            'success': False,
            'message': 'Datos inválidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# =================== VISTAS PARA PERSONAS AUTORIZADAS ===================

class PersonaAutorizadaListView(generics.ListAPIView):
    """Vista para listar personas autorizadas"""
    queryset = PersonaAutorizada.objects.filter(activo=True)
    serializer_class = PersonaAutorizadaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vivienda', 'parentesco', 'activo']
    search_fields = ['nombre', 'apellido', 'cedula']
    ordering = ['nombre', 'apellido']

    def get_queryset(self):
        from django.db.models import QuerySet
        from typing import Any
        queryset: Any = PersonaAutorizada.objects.filter(activo=True)
        
        # Filtro por vigencia
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            vigente = query_params.get('vigente')
            if vigente == 'true':
                now = timezone.now()
                queryset = queryset.filter(
                    fecha_inicio__lte=now
                ).filter(
                    Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=now)
                )
        
        return queryset

class PersonaAutorizadaCreateView(generics.CreateAPIView):
    """Vista para crear persona autorizada"""
    queryset = PersonaAutorizada.objects.all()
    serializer_class = PersonaAutorizadaCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Registrar nueva persona autorizada para una vivienda",
        request_body=PersonaAutorizadaCreateSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            persona = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Persona autorizada registrada exitosamente',
                'data': PersonaAutorizadaSerializer(persona).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al registrar persona autorizada',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RenovarAutorizacionView(APIView):
    """Vista para renovar autorización de persona"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Renovar autorización de una persona",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nueva_fecha_fin': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description='Nueva fecha de vencimiento'
                ),
                'motivo': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Motivo de la renovación'
                )
            },
            required=['nueva_fecha_fin']
        )
    )
    def patch(self, request, persona_id):
        try:
            persona = PersonaAutorizada.objects.get(id=persona_id, activo=True)
        except PersonaAutorizada.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Persona autorizada no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verificar permisos
        if not (request.user.is_superuser or 
                persona.vivienda.usuario_propietario == request.user or
                persona.vivienda.usuario_inquilino == request.user):
            return Response({
                'success': False,
                'message': 'No tienes permisos para renovar esta autorización'
            }, status=status.HTTP_403_FORBIDDEN)

        nueva_fecha_fin = request.data.get('nueva_fecha_fin')
        if not nueva_fecha_fin:
            return Response({
                'success': False,
                'message': 'Nueva fecha de fin es requerida'
            }, status=status.HTTP_400_BAD_REQUEST)

        fecha_fin_anterior = persona.fecha_fin
        persona.fecha_fin = nueva_fecha_fin
        persona.save()

        return Response({
            'success': True,
            'message': 'Autorización renovada exitosamente',
            'data': {
                'id': persona.pk,
                'nombre': f"{persona.nombre} {persona.apellido}",
                'fecha_fin_anterior': fecha_fin_anterior,
                'fecha_fin_nueva': nueva_fecha_fin,
                'renovado_por': {
                    'id': request.user.pk,
                    'full_name': request.user.get_full_name()
                },
                'fecha_renovacion': timezone.now()
            }
        })

class RevocarAutorizacionView(APIView):
    """Vista para revocar autorización de persona"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Revocar autorización de una persona",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'motivo': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Motivo de la revocación'
                ),
                'fecha_revocacion': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description='Fecha de revocación'
                )
            },
            required=['motivo']
        )
    )
    def patch(self, request, persona_id):
        try:
            persona = PersonaAutorizada.objects.get(id=persona_id, activo=True)
        except PersonaAutorizada.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Persona autorizada no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verificar permisos
        if not (request.user.is_superuser or 
                persona.vivienda.usuario_propietario == request.user or
                persona.vivienda.usuario_inquilino == request.user):
            return Response({
                'success': False,
                'message': 'No tienes permisos para revocar esta autorización'
            }, status=status.HTTP_403_FORBIDDEN)

        motivo = request.data.get('motivo')
        if not motivo:
            return Response({
                'success': False,
                'message': 'Motivo es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        persona.activo = False
        persona.fecha_fin = timezone.now()
        persona.save()

        return Response({
            'success': True,
            'message': 'Autorización revocada exitosamente',
            'data': {
                'id': persona.pk,
                'nombre': f"{persona.nombre} {persona.apellido}",
                'activa': False,
                'fecha_revocacion': persona.fecha_fin,
                'motivo': motivo
            }
        })

# =================== VISTAS PARA MASCOTAS ===================

class MascotaListView(generics.ListAPIView):
    """Vista para listar mascotas"""
    queryset = Mascota.objects.filter(activo=True)
    serializer_class = MascotaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vivienda', 'especie', 'activo', 'vacunas_al_dia']
    search_fields = ['nombre', 'raza']
    ordering = ['nombre']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de mascotas registradas en el condominio
        
        ### Filtros disponibles:
        - `vivienda`: ID de la vivienda
        - `especie`: perro, gato, ave, pez, etc.
        - `activo`: true/false
        - `vacunas_al_dia`: true/false
        
        ### Búsqueda:
        - `search`: buscar por nombre o raza
        
        ### Ordenamiento:
        - `ordering`: nombre, fecha_registro, especie
        """,
        responses={
            200: openapi.Response(
                description="Lista de mascotas",
                examples={
                    "application/json": {
                        "count": 75,
                        "next": None,
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "nombre": "Max",
                                "especie": "perro",
                                "raza": "Golden Retriever",
                                "edad": 3,
                                "color": "dorado",
                                "peso": "25.5",
                                "vacunas_al_dia": True,
                                "observaciones": "Muy amigable",
                                "vivienda": {
                                    "id": 1,
                                    "identificador": "TORRE-A-101"
                                }
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Mascotas']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class MascotaCreateView(generics.CreateAPIView):
    """Vista para registrar nueva mascota"""
    queryset = Mascota.objects.all()
    serializer_class = MascotaCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Registrar nueva mascota en una vivienda",
        request_body=MascotaCreateSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            mascota = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Mascota registrada exitosamente',
                'data': MascotaSerializer(mascota).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al registrar mascota',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class MascotaUpdateView(generics.UpdateAPIView):
    """Vista para actualizar información de mascota"""
    queryset = Mascota.objects.all()
    serializer_class = MascotaCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        mascota = super().get_object()
        # Verificar permisos
        if not (self.request.user.is_superuser or 
                mascota.vivienda.usuario_propietario == self.request.user or
                mascota.vivienda.usuario_inquilino == self.request.user):
            raise PermissionDenied("No tienes permisos para actualizar esta mascota")
        return mascota

# =================== VISTAS PARA REPORTES Y DASHBOARD ===================

class DashboardView(APIView):
    """Vista para dashboard de residencias"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Obtener estadísticas completas del dashboard de residencias
        
        **Requiere permisos de administrador**
        
        ### Estadísticas incluidas:
        - **Viviendas**: Total, ocupadas, disponibles, con inquilinos
        - **Residentes**: Propietarios, inquilinos, personas autorizadas
        - **Mascotas**: Total por especie, estado de vacunas
        - **Distribución**: Por tipo de vivienda y ocupación por bloque
        """,
        responses={
            200: openapi.Response(
                description="Estadísticas del dashboard",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "viviendas": {
                                "total": 150,
                                "ocupadas": 120,
                                "disponibles": 30,
                                "con_inquilinos": 45,
                                "solo_propietarios": 75
                            },
                            "residentes": {
                                "total_propietarios": 120,
                                "total_inquilinos": 45,
                                "personas_autorizadas": 85,
                                "credenciales_activas": 85
                            },
                            "mascotas": {
                                "total": 75,
                                "perros": 45,
                                "gatos": 25,
                                "otras": 5,
                                "vacunas_al_dia": 65
                            },
                            "distribucion_por_tipo": {
                                "apartamento": 120,
                                "penthouse": 20,
                                "local": 10
                            },
                            "ocupacion_por_bloque": [
                                {
                                    "bloque": "TORRE-A",
                                    "total": 50,
                                    "ocupadas": 40,
                                    "porcentaje": 80.0
                                }
                            ]
                        }
                    }
                }
            ),
            403: "Sin permisos - Solo administradores",
            401: "No autorizado"
        },
        tags=['Dashboard']
    )
    def get(self, request):
        # Solo usuarios con permisos pueden ver el dashboard completo
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No tienes permisos para ver el dashboard'
            }, status=status.HTTP_403_FORBIDDEN)

        # Estadísticas de viviendas
        total_viviendas = Vivienda.objects.filter(activo=True).count()
        ocupadas = Vivienda.objects.filter(activo=True, usuario_propietario__isnull=False).count()
        disponibles = total_viviendas - ocupadas
        con_inquilinos = Vivienda.objects.filter(activo=True, usuario_inquilino__isnull=False).count()
        solo_propietarios = ocupadas - con_inquilinos

        # Estadísticas de residentes - usando filtros directos
        total_propietarios = Vivienda.objects.filter(activo=True, usuario_propietario__isnull=False).values('usuario_propietario').distinct().count()
        total_inquilinos = Vivienda.objects.filter(activo=True, usuario_inquilino__isnull=False).values('usuario_inquilino').distinct().count()
        personas_autorizadas = PersonaAutorizada.objects.filter(activo=True).count()

        # Estadísticas de mascotas
        total_mascotas = Mascota.objects.filter(activo=True).count()
        mascotas_por_especie = Mascota.objects.filter(activo=True).values('especie').annotate(count=Count('id'))
        perros = next((item['count'] for item in mascotas_por_especie if item['especie'].lower() == 'perro'), 0)
        gatos = next((item['count'] for item in mascotas_por_especie if item['especie'].lower() == 'gato'), 0)
        otras = total_mascotas - perros - gatos
        vacunas_al_dia = Mascota.objects.filter(activo=True, vacunas_al_dia=True).count()

        # Distribución por tipo
        tipos = Vivienda.objects.filter(activo=True).values('tipo').annotate(count=Count('id'))
        distribucion_tipo = {item['tipo']: item['count'] for item in tipos}

        # Ocupación por bloque
        bloques = Vivienda.objects.filter(activo=True).values('bloque').annotate(
            total=Count('id'),
            ocupadas=Count('usuario_propietario')
        ).order_by('bloque')
        
        ocupacion_bloque = []
        for bloque in bloques:
            porcentaje = (bloque['ocupadas'] / bloque['total'] * 100) if bloque['total'] > 0 else 0
            ocupacion_bloque.append({
                'bloque': bloque['bloque'],
                'total': bloque['total'],
                'ocupadas': bloque['ocupadas'],
                'porcentaje': round(porcentaje, 1)
            })

        data = {
            'viviendas': {
                'total': total_viviendas,
                'ocupadas': ocupadas,
                'disponibles': disponibles,
                'con_inquilinos': con_inquilinos,
                'solo_propietarios': solo_propietarios
            },
            'residentes': {
                'total_propietarios': total_propietarios,
                'total_inquilinos': total_inquilinos,
                'personas_autorizadas': personas_autorizadas,
                'credenciales_activas': personas_autorizadas  # Placeholder
            },
            'mascotas': {
                'total': total_mascotas,
                'perros': perros,
                'gatos': gatos,
                'otras': otras,
                'vacunas_al_dia': vacunas_al_dia
            },
            'distribucion_por_tipo': distribucion_tipo,
            'ocupacion_por_bloque': ocupacion_bloque
        }

        return Response({
            'success': True,
            'data': data
        })

# =================== VISTAS DE BÚSQUEDA Y FILTROS ===================

class SearchResidentesView(APIView):
    """Vista para buscar residentes"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Buscar residentes en el condominio
        
        ### Parámetros de búsqueda:
        - `q` (requerido): Término de búsqueda (mínimo 3 caracteres)
        - `tipo` (opcional): Filtrar por tipo de residente
          - `propietario`: Solo propietarios
          - `inquilino`: Solo inquilinos  
          - `autorizado`: Solo personas autorizadas
        
        ### Campos de búsqueda:
        - **Propietarios/Inquilinos**: Nombre, apellido, email
        - **Personas autorizadas**: Nombre, apellido, cédula
        """,
        manual_parameters=[
            openapi.Parameter(
                'q', 
                openapi.IN_QUERY, 
                description="Término de búsqueda (mínimo 3 caracteres)",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'tipo', 
                openapi.IN_QUERY, 
                description="Tipo de residente a buscar",
                type=openapi.TYPE_STRING,
                enum=['propietario', 'inquilino', 'autorizado']
            ),
        ],
        responses={
            200: openapi.Response(
                description="Resultados de búsqueda",
                examples={
                    "application/json": {
                        "success": True,
                        "data": [
                            {
                                "tipo": "propietario",
                                "usuario": {
                                    "id": 5,
                                    "full_name": "Juan Pérez",
                                    "email": "juan.perez@email.com"
                                },
                                "vivienda": {
                                    "id": 1,
                                    "identificador": "TORRE-A-101"
                                },
                                "fecha_relacion": "2024-01-15T10:30:00Z"
                            },
                            {
                                "tipo": "autorizado",
                                "persona": {
                                    "id": 3,
                                    "nombre": "María Pérez",
                                    "cedula": "12345678",
                                    "parentesco": "esposa"
                                },
                                "vivienda": {
                                    "id": 1,
                                    "identificador": "TORRE-A-101"
                                },
                                "autorizado_por": "Juan Pérez",
                                "vigente": True
                            }
                        ]
                    }
                }
            ),
            400: "Término de búsqueda muy corto",
            401: "No autorizado"
        },
        tags=['Búsqueda']
    )

    def get(self, request):
        query_params = getattr(request, 'query_params', getattr(request, 'GET', {}))
        query = query_params.get('q', '')
        tipo = query_params.get('tipo', '')
        
        if len(query) < 3:
            return Response({
                'success': False,
                'message': 'El término de búsqueda debe tener al menos 3 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)

        resultados = []

        # Buscar propietarios usando filtros directos
        if not tipo or tipo == 'propietario':
            try:
                viviendas_con_prop = Vivienda.objects.filter(
                    usuario_propietario__isnull=False,
                    activo=True
                ).filter(
                    Q(usuario_propietario__first_name__icontains=query) |
                    Q(usuario_propietario__last_name__icontains=query) |
                    Q(usuario_propietario__email__icontains=query)
                ).select_related('usuario_propietario')

                for vivienda in viviendas_con_prop:
                    prop = vivienda.usuario_propietario
                    if prop:
                        resultados.append({
                            'tipo': 'propietario',
                            'usuario': {
                                'id': prop.pk,
                                'full_name': prop.get_full_name(),
                                'email': prop.email,
                            },
                            'vivienda': {
                                'id': vivienda.pk,
                                'identificador': vivienda.identificador
                            },
                            'fecha_relacion': vivienda.fecha_registro
                        })
            except Exception:
                pass  # En caso de error, continúa con otros tipos

        # Buscar inquilinos
        if not tipo or tipo == 'inquilino':
            try:
                viviendas_con_inq = Vivienda.objects.filter(
                    usuario_inquilino__isnull=False,
                    activo=True
                ).filter(
                    Q(usuario_inquilino__first_name__icontains=query) |
                    Q(usuario_inquilino__last_name__icontains=query) |
                    Q(usuario_inquilino__email__icontains=query)
                ).select_related('usuario_inquilino')

                for vivienda in viviendas_con_inq:
                    inq = vivienda.usuario_inquilino
                    if inq:
                        resultados.append({
                            'tipo': 'inquilino',
                            'usuario': {
                                'id': inq.pk,
                                'full_name': inq.get_full_name(),
                                'email': inq.email,
                            },
                            'vivienda': {
                                'id': vivienda.pk,
                                'identificador': vivienda.identificador
                            },
                            'fecha_relacion': vivienda.fecha_registro
                        })
            except Exception:
                pass

        # Buscar personas autorizadas
        if not tipo or tipo == 'autorizado':
            try:
                autorizados = PersonaAutorizada.objects.filter(
                    Q(nombre__icontains=query) | 
                    Q(apellido__icontains=query) | 
                    Q(cedula__icontains=query),
                    activo=True
                ).select_related('vivienda', 'autorizado_por')

                for auth in autorizados:
                    now = timezone.now()
                    vigente = (auth.fecha_inicio <= now and 
                              (auth.fecha_fin is None or auth.fecha_fin >= now))
                    
                    resultados.append({
                        'tipo': 'autorizado',
                        'persona': {
                            'id': auth.pk,
                            'nombre': f"{auth.nombre} {auth.apellido}",
                            'cedula': auth.cedula,
                            'parentesco': auth.parentesco
                        },
                        'vivienda': {
                            'id': auth.vivienda.pk,
                            'identificador': auth.vivienda.identificador
                        },
                        'autorizado_por': auth.autorizado_por.get_full_name(),
                        'vigente': vigente
                    })
            except Exception:
                pass

        return Response({
            'success': True,
            'data': resultados
        })

class ViviendasDisponiblesView(generics.ListAPIView):
    """Vista para listar viviendas disponibles"""
    serializer_class = ViviendaListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'bloque']

    def get_queryset(self):
        from django.db.models import QuerySet
        from typing import Any
        # Viviendas sin propietario
        queryset: Any = Vivienda.objects.filter(
            activo=True,
            usuario_propietario__isnull=True
        )
        
        # Filtros adicionales
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            min_habitaciones = query_params.get('min_habitaciones')
            if min_habitaciones:
                try:
                    queryset = queryset.filter(habitaciones__gte=int(min_habitaciones))
                except (ValueError, TypeError):
                    pass
            
            max_cuota = query_params.get('max_cuota')
            if max_cuota:
                try:
                    queryset = queryset.filter(cuota_administracion__lte=float(max_cuota))
                except (ValueError, TypeError):
                    pass
        
        return queryset