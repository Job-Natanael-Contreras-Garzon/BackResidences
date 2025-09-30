from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, QuerySet, F
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
from typing import Any
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Importación condicional de django_filters
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None

from .models import (
    CategoriaMantenimiento, Proveedor, SolicitudMantenimiento, OrdenTrabajo,
    MaterialInventario, MovimientoInventario, MantenimientoPreventivo
)
from .serializers import (
    CategoriaMantenimientoSerializer, ProveedorListSerializer, ProveedorDetailSerializer,
    SolicitudMantenimientoListSerializer, SolicitudMantenimientoDetailSerializer,
    SolicitudMantenimientoCreateSerializer, SolicitudMantenimientoUpdateSerializer,
    OrdenTrabajoListSerializer, OrdenTrabajoDetailSerializer,
    MaterialInventarioListSerializer, DashboardMantenimientoSerializer,
    EstadisticasMantenimientoSerializer
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


# =================== VISTAS PARA CATEGORÍAS DE MANTENIMIENTO ===================

class CategoriaMantenimientoListView(generics.ListAPIView):
    """Vista para listar categorías de mantenimiento"""
    queryset = CategoriaMantenimiento.objects.filter(activo=True)
    serializer_class = CategoriaMantenimientoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Obtener lista de categorías de mantenimiento disponibles",
        responses={
            200: openapi.Response(
                description="Lista de categorías",
                examples={
                    "application/json": {
                        "count": 8,
                        "results": [
                            {
                                "id": 1,
                                "nombre": "Plomería",
                                "codigo": "PLO",
                                "descripcion": "Reparaciones de tuberías, grifos y sanitarios",
                                "color": "#007bff",
                                "activo": True,
                                "tiempo_respuesta_horas": 24,
                                "created_at": "2025-09-30T10:00:00Z",
                                "updated_at": "2025-09-30T10:00:00Z"
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Mantenimiento - Categorías']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# =================== VISTAS PARA PROVEEDORES ===================

class ProveedorListView(generics.ListAPIView):
    """Vista para listar proveedores"""
    queryset = Proveedor.objects.filter(activo=True)
    serializer_class = ProveedorListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configurar filtros de forma condicional
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    filterset_fields = ['categoria_principal', 'atiende_emergencias', 'activo']
    search_fields = ['nombre', 'contacto_principal', 'servicios__nombre']
    ordering_fields = ['nombre', 'calificacion_promedio', 'trabajos_realizados', 'tarifa_hora']
    ordering = ['nombre']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de proveedores de mantenimiento
        
        ### Filtros disponibles:
        - `categoria_principal`: ID de la categoría principal
        - `atiende_emergencias`: true/false
        - `activo`: true/false
        - `servicios`: ID del servicio específico
        - `calificacion_minima`: Calificación mínima (1-5)
        
        ### Búsqueda:
        - `search`: buscar por nombre, contacto o servicios
        
        ### Ordenamiento:
        - `ordering`: nombre, calificacion_promedio, trabajos_realizados, tarifa_hora
        """,
        responses={
            200: openapi.Response(
                description="Lista de proveedores",
                examples={
                    "application/json": {
                        "count": 15,
                        "results": [
                            {
                                "id": 1,
                                "nombre": "PlomeroExpress SAS",
                                "telefono": "+57 300 123 4567",
                                "email": "contacto@plomeroexpress.com",
                                "contacto_principal": "Carlos Méndez",
                                "categoria_principal_info": {
                                    "id": 1,
                                    "nombre": "Plomería",
                                    "codigo": "PLO"
                                },
                                "servicios_count": 3,
                                "tarifa_hora": "45000.00",
                                "calificacion_promedio": "4.50",
                                "trabajos_realizados": 127,
                                "activo": True,
                                "atiende_emergencias": True,
                                "tiempo_respuesta_emergencia_horas": 4
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Mantenimiento - Proveedores']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Proveedor]:  # type: ignore
        queryset = Proveedor.objects.filter(activo=True)
        
        # Filtros adicionales
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            servicios = query_params.get('servicios')
            if servicios:
                try:
                    queryset = queryset.filter(servicios__id=int(servicios))
                except ValueError:
                    pass
            
            calificacion_minima = query_params.get('calificacion_minima')
            if calificacion_minima:
                try:
                    queryset = queryset.filter(calificacion_promedio__gte=float(calificacion_minima))
                except ValueError:
                    pass
        
        return queryset


class ProveedorDetailView(generics.RetrieveAPIView):
    """Vista para detalles de proveedor"""
    queryset = Proveedor.objects.filter(activo=True)
    serializer_class = ProveedorDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Obtener detalles completos de un proveedor específico",
        responses={
            200: openapi.Response(
                description="Detalles del proveedor",
                examples={
                    "application/json": {
                        "id": 1,
                        "nombre": "PlomeroExpress SAS",
                        "telefono": "+57 300 123 4567",
                        "email": "contacto@plomeroexpress.com",
                        "direccion": "Calle 123 #45-67, Bogotá",
                        "contacto_principal": "Carlos Méndez",
                        "rut": "900123456-7",
                        "camara_comercio": "CC-BOG-001234",
                        "poliza_responsabilidad": "POL-2025-567890",
                        "categoria_principal_info": {
                            "id": 1,
                            "nombre": "Plomería",
                            "codigo": "PLO"
                        },
                        "servicios_info": [],
                        "tarifa_hora": "45000.00",
                        "tarifa_visita": "25000.00",
                        "recargo_emergencia_porcentaje": 50,
                        "horarios": "Lunes a Viernes 8:00-18:00, Sábados 8:00-12:00",
                        "atiende_emergencias": True,
                        "tiempo_respuesta_emergencia_horas": 4,
                        "activo": True,
                        "calificacion_promedio": "4.50",
                        "trabajos_realizados": 127
                    }
                }
            ),
            404: "Proveedor no encontrado",
            401: "No autorizado"
        },
        tags=['Mantenimiento - Proveedores']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# =================== VISTAS PARA SOLICITUDES DE MANTENIMIENTO ===================

class SolicitudMantenimientoListView(generics.ListAPIView):
    """Vista para listar solicitudes de mantenimiento"""
    serializer_class = SolicitudMantenimientoListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configurar filtros de forma condicional
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    filterset_fields = ['categoria', 'prioridad', 'estado', 'solicitante', 'tecnico_asignado']
    search_fields = ['numero_solicitud', 'titulo', 'descripcion']
    ordering_fields = ['fecha_solicitud', 'prioridad', 'estado', 'fecha_limite']
    ordering = ['-fecha_solicitud']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de solicitudes de mantenimiento
        
        ### Filtros disponibles:
        - `categoria`: ID de la categoría
        - `prioridad`: baja, media, alta, urgente
        - `estado`: pendiente, asignada, en_proceso, completada, cancelada
        - `solicitante`: ID del solicitante
        - `tecnico_asignado`: ID del técnico asignado
        - `fecha_desde`: Fecha desde (YYYY-MM-DD)
        - `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
        - `vencidas`: Solo solicitudes vencidas (true/false)
        
        ### Búsqueda:
        - `search`: buscar por número, título o descripción
        
        ### Ordenamiento:
        - `ordering`: fecha_solicitud, prioridad, estado, fecha_limite
        """,
        responses={
            200: openapi.Response(
                description="Lista de solicitudes",
                examples={
                    "application/json": {
                        "count": 45,
                        "results": [
                            {
                                "id": 1,
                                "numero_solicitud": "SOL-2025-000001",
                                "titulo": "Goteo en grifo de cocina",
                                "categoria_info": {
                                    "id": 1,
                                    "nombre": "Plomería",
                                    "codigo": "PLO",
                                    "color": "#007bff"
                                },
                                "prioridad": "media",
                                "estado": "asignada",
                                "solicitante_info": {
                                    "id": 15,
                                    "full_name": "María González"
                                },
                                "ubicacion_info": {
                                    "tipo": "vivienda",
                                    "id": 101,
                                    "nombre": "Apartamento 501-A"
                                },
                                "fecha_solicitud": "2025-09-28T10:30:00Z",
                                "fecha_limite": "2025-09-29T10:30:00Z",
                                "tecnico_asignado_info": {
                                    "id": 8,
                                    "full_name": "Carlos Técnico"
                                },
                                "costo_estimado": "75000.00",
                                "tiempo_transcurrido_texto": "2 días",
                                "dias_abierto": 2,
                                "estado_color": "#17a2b8",
                                "prioridad_color": "#ffc107"
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Mantenimiento - Solicitudes']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[SolicitudMantenimiento]:  # type: ignore
        queryset = SolicitudMantenimiento.objects.all()
        
        # Si no es superusuario, filtrar por permisos
        if not self.request.user.is_superuser:
            # Mostrar solo solicitudes del usuario o que le están asignadas
            queryset = queryset.filter(
                Q(solicitante=self.request.user) | 
                Q(tecnico_asignado=self.request.user)
            )
        
        # Filtros adicionales
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            fecha_desde = query_params.get('fecha_desde')
            if fecha_desde:
                try:
                    fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_solicitud__date__gte=fecha)
                except ValueError:
                    pass
            
            fecha_hasta = query_params.get('fecha_hasta')
            if fecha_hasta:
                try:
                    fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_solicitud__date__lte=fecha)
                except ValueError:
                    pass
            
            vencidas = query_params.get('vencidas')
            if vencidas and vencidas.lower() == 'true':
                now = timezone.now()
                queryset = queryset.filter(
                    fecha_limite__lt=now,
                    estado__in=['pendiente', 'asignada', 'en_proceso']
                )
        
        return queryset


class SolicitudMantenimientoDetailView(generics.RetrieveAPIView):
    """Vista para detalles de solicitud de mantenimiento"""
    queryset = SolicitudMantenimiento.objects.all()
    serializer_class = SolicitudMantenimientoDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Obtener detalles completos de una solicitud de mantenimiento",
        responses={
            200: openapi.Response(
                description="Detalles de la solicitud",
                examples={
                    "application/json": {
                        "id": 1,
                        "numero_solicitud": "SOL-2025-000001",
                        "titulo": "Goteo en grifo de cocina",
                        "descripcion": "El grifo de la cocina presenta un goteo constante...",
                        "categoria_info": {
                            "id": 1,
                            "nombre": "Plomería"
                        },
                        "prioridad": "media",
                        "estado": "asignada",
                        "ubicacion_info": {
                            "tipo": "vivienda",
                            "id": 101,
                            "identificador": "501-A",
                            "bloque": "Torre A",
                            "piso": 5
                        },
                        "orden_trabajo_info": {
                            "id": 1,
                            "numero_orden": "OT-2025-000001",
                            "estado": "pendiente",
                            "fecha_programada": "2025-09-30T14:00:00Z",
                            "progreso_porcentaje": 0
                        },
                        "historial_estados": [],
                        "tiempo_transcurrido_detalle": {
                            "dias": 2,
                            "horas": 6,
                            "total_horas": 54.5
                        }
                    }
                }
            ),
            404: "Solicitud no encontrada",
            401: "No autorizado"
        },
        tags=['Mantenimiento - Solicitudes']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[SolicitudMantenimiento]:  # type: ignore
        queryset = SolicitudMantenimiento.objects.all()
        
        # Aplicar filtros de permisos si no es superusuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(solicitante=self.request.user) | 
                Q(tecnico_asignado=self.request.user)
            )
        
        return queryset


class SolicitudMantenimientoCreateView(generics.CreateAPIView):
    """Vista para crear nueva solicitud de mantenimiento"""
    queryset = SolicitudMantenimiento.objects.all()
    serializer_class = SolicitudMantenimientoCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crear nueva solicitud de mantenimiento",
        request_body=SolicitudMantenimientoCreateSerializer,
        responses={
            201: openapi.Response(
                description="Solicitud creada exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Solicitud de mantenimiento creada exitosamente",
                        "data": {
                            "id": 46,
                            "numero_solicitud": "SOL-2025-000046",
                            "titulo": "Reparación aire acondicionado",
                            "categoria": "Climatización",
                            "prioridad": "alta",
                            "estado": "pendiente",
                            "fecha_solicitud": "2025-09-30T15:20:00Z",
                            "fecha_limite": "2025-10-01T15:20:00Z",
                            "tiempo_respuesta_estimado": "24 horas",
                            "costo_estimado": "0.00"
                        }
                    }
                }
            ),
            400: "Datos inválidos",
            403: "Sin permisos"
        },
        tags=['Mantenimiento - Solicitudes']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            solicitud = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Solicitud de mantenimiento creada exitosamente',
                'data': {
                    'id': solicitud.pk,
                    'numero_solicitud': solicitud.numero_solicitud,
                    'titulo': solicitud.titulo,
                    'categoria': solicitud.categoria.nombre,
                    'prioridad': solicitud.prioridad,
                    'estado': solicitud.estado,
                    'fecha_solicitud': solicitud.fecha_solicitud.isoformat(),
                    'fecha_limite': solicitud.fecha_limite.isoformat() if solicitud.fecha_limite else None,
                    'tiempo_respuesta_estimado': f'{solicitud.categoria.tiempo_respuesta_horas} horas',
                    'costo_estimado': str(solicitud.costo_estimado)
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear solicitud de mantenimiento',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SolicitudMantenimientoUpdateView(generics.UpdateAPIView):
    """Vista para actualizar solicitud de mantenimiento"""
    queryset = SolicitudMantenimiento.objects.all()
    serializer_class = SolicitudMantenimientoUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Actualizar solicitud de mantenimiento - Solo administradores",
        request_body=SolicitudMantenimientoUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Solicitud actualizada exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Solicitud actualizada exitosamente",
                        "data": {
                            "id": 46,
                            "numero_solicitud": "SOL-2025-000046",
                            "estado": "asignada",
                            "tecnico_asignado": "Carlos Técnico",
                            "fecha_asignacion": "2025-09-30T16:00:00Z",
                            "cambios_realizados": [
                                "Estado cambiado a asignada",
                                "Técnico asignado"
                            ]
                        }
                    }
                }
            ),
            400: "Datos inválidos",
            403: "Sin permisos",
            404: "Solicitud no encontrada"
        },
        tags=['Mantenimiento - Solicitudes']
    )
    def put(self, request, *args, **kwargs):
        # Solo superusuarios pueden actualizar solicitudes
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No tienes permisos para actualizar solicitudes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        solicitud = self.get_object()
        estado_anterior = solicitud.estado
        
        serializer = self.get_serializer(solicitud, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_solicitud = serializer.save()
            
            # Detectar cambios
            cambios_realizados = []
            if updated_solicitud.estado != estado_anterior:
                cambios_realizados.append(f"Estado cambiado de {estado_anterior} a {updated_solicitud.estado}")
            if 'tecnico_asignado' in request.data:
                cambios_realizados.append("Técnico asignado")
            if 'costo_estimado' in request.data:
                cambios_realizados.append("Costo estimado actualizado")
            
            return Response({
                'success': True,
                'message': 'Solicitud actualizada exitosamente',
                'data': {
                    'id': updated_solicitud.pk,
                    'numero_solicitud': updated_solicitud.numero_solicitud,
                    'estado': updated_solicitud.estado,
                    'tecnico_asignado': updated_solicitud.tecnico_asignado.get_full_name() if updated_solicitud.tecnico_asignado else None,
                    'fecha_asignacion': updated_solicitud.fecha_asignacion.isoformat() if updated_solicitud.fecha_asignacion else None,
                    'cambios_realizados': cambios_realizados
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Error al actualizar solicitud',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# =================== VISTAS PARA ÓRDENES DE TRABAJO ===================

class OrdenTrabajoListView(generics.ListAPIView):
    """Vista para listar órdenes de trabajo"""
    serializer_class = OrdenTrabajoListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configurar filtros de forma condicional
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    filterset_fields = ['estado', 'tecnico_asignado', 'proveedor']
    search_fields = ['numero_orden', 'solicitud__titulo', 'descripcion_trabajo']
    ordering_fields = ['fecha_programada', 'fecha_inicio', 'progreso_porcentaje']
    ordering = ['-fecha_programada']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de órdenes de trabajo
        
        ### Filtros disponibles:
        - `estado`: pendiente, en_proceso, completada, cancelada
        - `tecnico_asignado`: ID del técnico
        - `proveedor`: ID del proveedor
        - `fecha_desde`: Fecha desde (YYYY-MM-DD)
        - `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
        
        ### Búsqueda:
        - `search`: buscar por número de orden, título de solicitud o descripción
        
        ### Ordenamiento:
        - `ordering`: fecha_programada, fecha_inicio, progreso_porcentaje
        """,
        responses={
            200: openapi.Response(
                description="Lista de órdenes de trabajo",
                examples={
                    "application/json": {
                        "count": 20,
                        "results": [
                            {
                                "id": 1,
                                "numero_orden": "OT-2025-000001",
                                "solicitud_info": {
                                    "id": 1,
                                    "numero_solicitud": "SOL-2025-000001",
                                    "titulo": "Goteo en grifo de cocina",
                                    "prioridad": "media"
                                },
                                "estado": "en_proceso",
                                "fecha_programada": "2025-09-30T14:00:00Z",
                                "fecha_inicio": "2025-09-30T14:15:00Z",
                                "tecnico_info": {
                                    "id": 8,
                                    "full_name": "Carlos Técnico"
                                },
                                "proveedor_info": {
                                    "id": 1,
                                    "nombre": "PlomeroExpress SAS",
                                    "telefono": "+57 300 123 4567"
                                },
                                "tiempo_estimado_horas": "2.00",
                                "progreso_porcentaje": 45,
                                "estado_color": "#007bff",
                                "tiempo_trabajado_texto": "1h 30m"
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Mantenimiento - Órdenes de Trabajo']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[OrdenTrabajo]:  # type: ignore
        queryset = OrdenTrabajo.objects.all()
        
        # Filtrar por permisos si no es superusuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(tecnico_asignado=self.request.user) |
                Q(solicitud__solicitante=self.request.user)
            )
        
        # Filtros adicionales
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            fecha_desde = query_params.get('fecha_desde')
            if fecha_desde:
                try:
                    fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_programada__date__gte=fecha)
                except ValueError:
                    pass
            
            fecha_hasta = query_params.get('fecha_hasta')
            if fecha_hasta:
                try:
                    fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_programada__date__lte=fecha)
                except ValueError:
                    pass
        
        return queryset


class OrdenTrabajoDetailView(generics.RetrieveAPIView):
    """Vista para detalles de orden de trabajo"""
    queryset = OrdenTrabajo.objects.all()
    serializer_class = OrdenTrabajoDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Obtener detalles completos de una orden de trabajo",
        responses={
            200: openapi.Response(
                description="Detalles de la orden de trabajo",
                examples={
                    "application/json": {
                        "id": 1,
                        "numero_orden": "OT-2025-000001",
                        "solicitud_info": {
                            "id": 1,
                            "numero_solicitud": "SOL-2025-000001",
                            "titulo": "Goteo en grifo de cocina"
                        },
                        "estado": "en_proceso",
                        "fecha_programada": "2025-09-30T14:00:00Z",
                        "fecha_inicio": "2025-09-30T14:15:00Z",
                        "tecnico_info": {
                            "id": 8,
                            "full_name": "Carlos Técnico"
                        },
                        "descripcion_trabajo": "Reparación de empaque de grifo...",
                        "garantia_dias": 30,
                        "progreso_porcentaje": 45,
                        "materiales_usados_info": [],
                        "tiempo_trabajado_detalle": {
                            "tiempo_total_horas": 1.5,
                            "tiempo_estimado_horas": 2.0,
                            "eficiencia_porcentaje": 133.33
                        }
                    }
                }
            ),
            404: "Orden de trabajo no encontrada",
            401: "No autorizado"
        },
        tags=['Mantenimiento - Órdenes de Trabajo']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[OrdenTrabajo]:  # type: ignore
        queryset = OrdenTrabajo.objects.all()
        
        # Aplicar filtros de permisos si no es superusuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(tecnico_asignado=self.request.user) |
                Q(solicitud__solicitante=self.request.user)
            )
        
        return queryset


# =================== VISTAS PARA DASHBOARD Y ESTADÍSTICAS ===================

class DashboardMantenimientoView(APIView):
    """Vista para dashboard de mantenimiento"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Dashboard con estadísticas generales de mantenimiento
        
        Incluye resumen de solicitudes, órdenes de trabajo, proveedores y costos.
        """,
        responses={
            200: openapi.Response(
                description="Dashboard de mantenimiento",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "periodo": "2025-09",
                            "solicitudes": {
                                "total_mes": 45,
                                "pendientes": 8,
                                "asignadas": 12,
                                "en_proceso": 15,
                                "completadas": 10,
                                "tiempo_respuesta_promedio": "18.5 horas",
                                "satisfaccion_promedio": 4.3
                            },
                            "ordenes_trabajo": {
                                "programadas_hoy": 6,
                                "en_proceso": 15,
                                "completadas_mes": 38,
                                "eficiencia_promedio": 92.5
                            },
                            "proveedores": {
                                "activos": 12,
                                "mejor_calificado": "PlomeroExpress SAS",
                                "mas_trabajos": "ElectricoRápido LTDA"
                            },
                            "costos": {
                                "total_mes": "2450000.00",
                                "promedio_por_solicitud": "54444.44",
                                "categoria_mayor_gasto": "Plomería"
                            }
                        }
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Mantenimiento - Dashboard']
    )
    def get(self, request):
        # Obtener fecha actual
        now = timezone.now()
        primer_dia_mes = now.replace(day=1)
        
        # Estadísticas de solicitudes
        solicitudes_mes = SolicitudMantenimiento.objects.filter(fecha_solicitud__gte=primer_dia_mes)
        solicitudes_pendientes = solicitudes_mes.filter(estado='pendiente')
        solicitudes_asignadas = solicitudes_mes.filter(estado='asignada')
        solicitudes_en_proceso = solicitudes_mes.filter(estado='en_proceso')
        solicitudes_completadas = solicitudes_mes.filter(estado='completada')
        
        # Tiempo promedio de respuesta
        solicitudes_con_asignacion = solicitudes_mes.filter(fecha_asignacion__isnull=False)
        tiempo_respuesta_promedio = "0 horas"
        if solicitudes_con_asignacion.exists():
            tiempos = []
            for solicitud in solicitudes_con_asignacion:
                if solicitud.fecha_asignacion:
                    delta = solicitud.fecha_asignacion - solicitud.fecha_solicitud
                    tiempos.append(delta.total_seconds() / 3600)
            
            if tiempos:
                promedio_horas = sum(tiempos) / len(tiempos)
                tiempo_respuesta_promedio = f"{promedio_horas:.1f} horas"
        
        # Satisfacción promedio
        solicitudes_calificadas = solicitudes_completadas.filter(calificacion__isnull=False)
        satisfaccion_promedio = 0
        if solicitudes_calificadas.exists():
            satisfaccion_promedio = solicitudes_calificadas.aggregate(
                promedio=Avg('calificacion')
            )['promedio'] or 0
        
        # Estadísticas de órdenes de trabajo
        ordenes_hoy = OrdenTrabajo.objects.filter(fecha_programada__date=now.date())
        ordenes_en_proceso = OrdenTrabajo.objects.filter(estado='en_proceso')
        ordenes_completadas_mes = OrdenTrabajo.objects.filter(
            fecha_finalizacion__gte=primer_dia_mes,
            estado='completada'
        )
        
        # Eficiencia promedio (tiempo real vs estimado)
        eficiencia_promedio = 0
        ordenes_con_tiempo = ordenes_completadas_mes.filter(
            tiempo_real_horas__isnull=False,
            tiempo_estimado_horas__gt=0
        )
        if ordenes_con_tiempo.exists():
            eficiencias = []
            for orden in ordenes_con_tiempo:
                if orden.tiempo_real_horas and orden.tiempo_estimado_horas:
                    eficiencia = (float(orden.tiempo_estimado_horas) / float(orden.tiempo_real_horas)) * 100
                    eficiencias.append(min(eficiencia, 200))  # Cap at 200%
            
            if eficiencias:
                eficiencia_promedio = sum(eficiencias) / len(eficiencias)
        
        # Estadísticas de proveedores
        proveedores_activos = Proveedor.objects.filter(activo=True)
        mejor_calificado = proveedores_activos.order_by('-calificacion_promedio').first()
        mas_trabajos = proveedores_activos.order_by('-trabajos_realizados').first()
        
        # Estadísticas de costos
        costos_mes = solicitudes_completadas.aggregate(
            total=Sum('costo_real')
        )['total'] or 0
        
        promedio_por_solicitud = 0
        if solicitudes_completadas.count() > 0:
            promedio_por_solicitud = costos_mes / solicitudes_completadas.count()
        
        # Categoría con mayor gasto
        categoria_mayor_gasto = solicitudes_completadas.values('categoria__nombre').annotate(
            total_gasto=Sum('costo_real')
        ).order_by('-total_gasto').first()
        
        return Response({
            'success': True,
            'data': {
                'periodo': now.strftime('%Y-%m'),
                'solicitudes': {
                    'total_mes': solicitudes_mes.count(),
                    'pendientes': solicitudes_pendientes.count(),
                    'asignadas': solicitudes_asignadas.count(),
                    'en_proceso': solicitudes_en_proceso.count(),
                    'completadas': solicitudes_completadas.count(),
                    'tiempo_respuesta_promedio': tiempo_respuesta_promedio,
                    'satisfaccion_promedio': round(satisfaccion_promedio, 1),
                    'vencidas': solicitudes_mes.filter(
                        fecha_limite__lt=now,
                        estado__in=['pendiente', 'asignada', 'en_proceso']
                    ).count()
                },
                'ordenes_trabajo': {
                    'programadas_hoy': ordenes_hoy.count(),
                    'en_proceso': ordenes_en_proceso.count(),
                    'completadas_mes': ordenes_completadas_mes.count(),
                    'eficiencia_promedio': round(eficiencia_promedio, 1)
                },
                'proveedores': {
                    'activos': proveedores_activos.count(),
                    'mejor_calificado': mejor_calificado.nombre if mejor_calificado else None,
                    'mas_trabajos': mas_trabajos.nombre if mas_trabajos else None
                },
                'inventario': {
                    'materiales_stock_bajo': MaterialInventario.objects.filter(
                        stock_actual__lte=F('stock_minimo'),
                        activo=True
                    ).count()
                },
                'costos': {
                    'total_mes': str(costos_mes),
                    'promedio_por_solicitud': str(round(promedio_por_solicitud, 2)),
                    'categoria_mayor_gasto': categoria_mayor_gasto['categoria__nombre'] if categoria_mayor_gasto else None
                }
            }
        })


# =================== VISTAS PARA CONFIGURACIÓN ===================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@swagger_auto_schema(
    operation_description="Obtener configuración general del sistema de mantenimiento",
    responses={
        200: openapi.Response(
            description="Configuración del sistema",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "prioridades": [
                            {"value": "baja", "label": "Baja", "color": "#28a745"},
                            {"value": "media", "label": "Media", "color": "#ffc107"},
                            {"value": "alta", "label": "Alta", "color": "#fd7e14"},
                            {"value": "urgente", "label": "Urgente", "color": "#dc3545"}
                        ],
                        "estados_solicitud": [
                            {"value": "pendiente", "label": "Pendiente", "color": "#ffc107"},
                            {"value": "asignada", "label": "Asignada", "color": "#17a2b8"},
                            {"value": "en_proceso", "label": "En Proceso", "color": "#007bff"},
                            {"value": "completada", "label": "Completada", "color": "#28a745"},
                            {"value": "cancelada", "label": "Cancelada", "color": "#dc3545"}
                        ],
                        "categorias": []
                    }
                }
            }
        )
    },
    tags=['Mantenimiento - Configuración']
)
def configuracion_mantenimiento(request):
    """Obtener configuración del sistema de mantenimiento"""
    prioridades = [
        {"value": "baja", "label": "Baja", "color": "#28a745"},
        {"value": "media", "label": "Media", "color": "#ffc107"},
        {"value": "alta", "label": "Alta", "color": "#fd7e14"},
        {"value": "urgente", "label": "Urgente", "color": "#dc3545"}
    ]
    
    estados_solicitud = [
        {"value": "pendiente", "label": "Pendiente", "color": "#ffc107"},
        {"value": "asignada", "label": "Asignada", "color": "#17a2b8"},
        {"value": "en_proceso", "label": "En Proceso", "color": "#007bff"},
        {"value": "completada", "label": "Completada", "color": "#28a745"},
        {"value": "cancelada", "label": "Cancelada", "color": "#dc3545"}
    ]
    
    estados_orden = [
        {"value": "pendiente", "label": "Pendiente", "color": "#ffc107"},
        {"value": "en_proceso", "label": "En Proceso", "color": "#007bff"},
        {"value": "completada", "label": "Completada", "color": "#28a745"},
        {"value": "cancelada", "label": "Cancelada", "color": "#dc3545"}
    ]
    
    categorias = CategoriaMantenimiento.objects.filter(activo=True).values(
        'id', 'nombre', 'codigo', 'descripcion', 'color', 'tiempo_respuesta_horas'
    )
    
    return Response({
        'success': True,
        'data': {
            'prioridades': prioridades,
            'estados_solicitud': estados_solicitud,
            'estados_orden': estados_orden,
            'categorias': list(categorias),
            'tiempos_respuesta_default': {
                'baja': 72,      # 3 días
                'media': 24,     # 1 día
                'alta': 12,      # 12 horas
                'urgente': 4     # 4 horas
            }
        }
    })
