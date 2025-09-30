from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, QuerySet
from datetime import datetime, date, time, timedelta
from typing import Any
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

from .models import AreaComun, HorarioArea, Reserva
from .serializers import (
    AreaComunListSerializer, AreaComunDetailSerializer, AreaComunCreateSerializer,
    AreaComunUpdateSerializer, ReservaListSerializer, ReservaCreateSerializer,
    DisponibilidadSerializer, DashboardAreasSerializer, HorarioAreaSerializer
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

# =================== VISTAS PARA GESTIÓN DE ÁREAS COMUNES ===================

class AreaComunListView(generics.ListAPIView):
    """Vista para listar áreas comunes"""
    queryset = AreaComun.objects.filter(activo=True)
    serializer_class = AreaComunListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configurar filtros de forma condicional
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    filterset_fields = ['tipo_reserva', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'precio_hora', 'capacidad', 'fecha_creacion']
    ordering = ['nombre']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de áreas comunes del condominio
        
        ### Filtros disponibles:
        - `tipo_reserva`: por_horas, por_dias, eventos
        - `activo`: true/false
        - `requiere_pago`: Areas que requieren pago (true/false)
        - `disponible`: Solo áreas disponibles para reserva (true/false)
        
        ### Búsqueda:
        - `search`: buscar por nombre o descripción
        
        ### Ordenamiento:
        - `ordering`: nombre, precio_hora, capacidad, fecha_creacion
        """,
        responses={
            200: openapi.Response(
                description="Lista de áreas comunes",
                examples={
                    "application/json": {
                        "count": 12,
                        "next": None,
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "nombre": "Salón Social",
                                "descripcion": "Salón principal para eventos y reuniones",
                                "tipo_reserva": "eventos",
                                "capacidad": 80,
                                "precio_hora": "37500.00",
                                "deposito_garantia": "150000.00",
                                "disponible_hoy": True,
                                "proxima_disponibilidad": "2025-09-30T08:00:00Z",
                                "reservas_activas": 2,
                                "total_reservas_mes": 15,
                                "equipamiento": [
                                    "Sistema de sonido",
                                    "Proyector",
                                    "Aire acondicionado"
                                ],
                                "imagen_principal": "https://storage.example.com/areas/salon_social_1.jpg",
                                "activo": True
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado - Token JWT requerido"
        },
        tags=['Áreas Comunes']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[AreaComun]:  # type: ignore
        queryset = AreaComun.objects.filter(activo=True)
        
        # Filtros adicionales usando request
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            requiere_pago = query_params.get('requiere_pago')
            if requiere_pago is not None:
                if requiere_pago.lower() == 'true':
                    queryset = queryset.filter(precio_hora__gt=0)
                else:
                    queryset = queryset.filter(precio_hora=0)
            
            disponible = query_params.get('disponible')
            if disponible is not None and disponible.lower() == 'true':
                # Filtrar áreas que no tengan reservas activas hoy
                hoy = date.today()
                areas_ocupadas = Reserva.objects.filter(
                    fecha_inicio__lte=hoy,
                    fecha_fin__gte=hoy,
                    estado__in=['confirmada', 'en_uso']
                ).values_list('area_comun_id', flat=True)
                queryset = queryset.exclude(id__in=areas_ocupadas)
        
        return queryset

class AreaComunDetailView(generics.RetrieveAPIView):
    """Vista para detalles de área común"""
    queryset = AreaComun.objects.filter(activo=True)
    serializer_class = AreaComunDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Obtener detalles completos de un área común específica
        
        Incluye información de horarios, equipamiento, normas de uso, estadísticas y contacto.
        """,
        responses={
            200: openapi.Response(
                description="Detalles del área común",
                examples={
                    "application/json": {
                        "id": 1,
                        "nombre": "Salón Social",
                        "descripcion": "Salón principal para eventos y reuniones sociales del condominio",
                        "tipo_reserva": "eventos",
                        "capacidad": 80,
                        "precio_hora": "37500.00",
                        "precio_dia": "300000.00",
                        "deposito_garantia": "150000.00",
                        "horarios": [
                            {
                                "id": 1,
                                "dia_semana": 1,
                                "dia_semana_display": "Lunes",
                                "hora_inicio": "08:00:00",
                                "hora_fin": "22:00:00",
                                "activo": True
                            }
                        ],
                        "equipamiento": [
                            "Sistema de sonido profesional",
                            "Proyector Full HD",
                            "Aire acondicionado"
                        ],
                        "normas_uso_lista": [
                            "Prohibido fumar en el interior",
                            "Música máximo hasta las 22:00"
                        ],
                        "imagenes": [
                            "https://storage.example.com/areas/salon_social_1.jpg"
                        ],
                        "contacto_administracion": {
                            "responsable": "Administración",
                            "telefono": "+573000000000",
                            "extension": "100"
                        },
                        "estadisticas": {
                            "reservas_mes_actual": 15,
                            "reservas_mes_anterior": 12,
                            "promedio_duracion": 4.5,
                            "ocupacion_porcentaje": 65.0
                        }
                    }
                }
            ),
            404: "Área común no encontrada",
            401: "No autorizado"
        },
        tags=['Áreas Comunes']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AreaComunCreateView(generics.CreateAPIView):
    """Vista para crear nueva área común"""
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crear nueva área común en el condominio - Solo administradores",
        request_body=AreaComunCreateSerializer,
        responses={
            201: openapi.Response(
                description="Área común creada exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Área común creada exitosamente",
                        "data": {
                            "id": 13,
                            "nombre": "Gimnasio",
                            "descripcion": "Gimnasio equipado para uso de residentes",
                            "tipo_reserva": "por_horas",
                            "capacidad": 20,
                            "precio_hora": "25000.00",
                            "activo": True,
                            "fecha_creacion": "2025-09-29T22:00:00Z"
                        }
                    }
                }
            ),
            400: "Datos inválidos",
            403: "Sin permisos para crear áreas comunes"
        },
        tags=['Áreas Comunes']
    )
    def post(self, request, *args, **kwargs):
        # Solo superusuarios pueden crear áreas comunes
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No tienes permisos para crear áreas comunes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            area = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Área común creada exitosamente',
                'data': AreaComunDetailSerializer(area).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear área común',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class AreaComunUpdateView(generics.UpdateAPIView):
    """Vista para actualizar área común"""
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Actualizar área común - Solo administradores",
        request_body=AreaComunUpdateSerializer,
        tags=['Áreas Comunes']
    )
    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No tienes permisos para actualizar áreas comunes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().put(request, *args, **kwargs)

class ConsultarDisponibilidadView(APIView):
    """Vista para consultar disponibilidad de área común"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Consultar disponibilidad de un área común en un rango de fechas
        """,
        manual_parameters=[
            openapi.Parameter(
                'fecha_inicio', 
                openapi.IN_QUERY, 
                description="Fecha inicio consulta (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'fecha_fin', 
                openapi.IN_QUERY, 
                description="Fecha fin consulta (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'duracion_horas', 
                openapi.IN_QUERY, 
                description="Duración deseada en horas",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: openapi.Response(
                description="Disponibilidad del área",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "area": {
                                "id": 1,
                                "nombre": "Salón Social"
                            },
                            "periodo_consulta": {
                                "fecha_inicio": "2025-09-30",
                                "fecha_fin": "2025-10-06"
                            },
                            "disponibilidad_por_dia": [
                                {
                                    "fecha": "2025-09-30",
                                    "dia_semana": "lunes",
                                    "disponible": True,
                                    "horarios_libres": [
                                        {
                                            "inicio": "08:00:00",
                                            "fin": "14:00:00"
                                        }
                                    ],
                                    "reservas_existentes": []
                                }
                            ]
                        }
                    }
                }
            ),
            400: "Parámetros inválidos",
            404: "Área común no encontrada"
        },
        tags=['Áreas Comunes']
    )
    def get(self, request, area_id):
        try:
            area = AreaComun.objects.get(id=area_id, activo=True)
        except AreaComun.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Área común no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        # Obtener parámetros
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')
        
        if not fecha_inicio_str or not fecha_fin_str:
            return Response({
                'success': False,
                'message': 'Debe especificar fecha_inicio y fecha_fin'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generar disponibilidad por día
        disponibilidad_por_dia = []
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            dia_semana = fecha_actual.isoweekday()
            
            # Obtener horarios configurados para este día
            horarios_area = HorarioArea.objects.filter(
                area_comun=area,
                dia_semana=dia_semana,
                activo=True
            )
            
            # Obtener reservas existentes para este día
            reservas_dia = Reserva.objects.filter(
                area_comun=area,
                fecha_inicio__lte=fecha_actual,
                fecha_fin__gte=fecha_actual,
                estado__in=['confirmada', 'en_uso']
            )
            
            # Calcular horarios libres y ocupados
            horarios_libres = []
            reservas_existentes = []
            
            for horario in horarios_area:
                horarios_libres.append({
                    "inicio": horario.hora_inicio.strftime('%H:%M:%S'),
                    "fin": horario.hora_fin.strftime('%H:%M:%S')
                })
            
            for reserva in reservas_dia:
                reservas_existentes.append({
                    "inicio": reserva.hora_inicio.strftime('%H:%M:%S'),
                    "fin": reserva.hora_fin.strftime('%H:%M:%S'),
                    "evento": reserva.motivo_evento or "Reserva privada"
                })
            
            disponibilidad_por_dia.append({
                "fecha": fecha_actual.strftime('%Y-%m-%d'),
                "dia_semana": fecha_actual.strftime('%A').lower(),
                "disponible": len(horarios_libres) > 0 and len(reservas_existentes) == 0,
                "horarios_libres": horarios_libres,
                "reservas_existentes": reservas_existentes
            })
            
            fecha_actual += timedelta(days=1)

        return Response({
            'success': True,
            'data': {
                "area": {
                    "id": area.pk,  # Usar pk en lugar de id
                    "nombre": area.nombre
                },
                "periodo_consulta": {
                    "fecha_inicio": fecha_inicio_str,
                    "fecha_fin": fecha_fin_str
                },
                "disponibilidad_por_dia": disponibilidad_por_dia
            }
        })

# =================== VISTAS PARA GESTIÓN DE RESERVAS ===================

class ReservaListView(generics.ListAPIView):
    """Vista para listar reservas"""
    serializer_class = ReservaListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configurar filtros de forma condicional
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    filterset_fields = ['area_comun', 'estado', 'usuario']
    search_fields = ['motivo_evento', 'area_comun__nombre']
    ordering_fields = ['fecha_inicio', 'fecha_creacion', 'monto_total']
    ordering = ['-fecha_creacion']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de reservas de áreas comunes
        
        ### Filtros disponibles:
        - `area_comun`: ID de área específica
        - `usuario`: ID de usuario específico
        - `estado`: Estado de reserva (pendiente, confirmada, cancelada, completada)
        - `fecha_desde`: Fecha desde (YYYY-MM-DD)
        - `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
        - `proximas`: Solo reservas próximas (true/false)
        
        ### Búsqueda:
        - `search`: buscar por motivo del evento o nombre del área
        
        ### Ordenamiento:
        - `ordering`: fecha_inicio, fecha_creacion, monto_total
        """,
        responses={
            200: openapi.Response(
                description="Lista de reservas",
                examples={
                    "application/json": {
                        "count": 45,
                        "next": "http://api.backresidences.com/api/common-areas/reservas/?page=2",
                        "previous": None,
                        "results": [
                            {
                                "id": 101,
                                "area": {
                                    "id": 1,
                                    "nombre": "Salón Social",
                                    "tipo": "eventos"
                                },
                                "usuario_info": {
                                    "id": 15,
                                    "full_name": "Juan Pérez",
                                    "vivienda": "TORRE-A-101"
                                },
                                "fecha_inicio": "2025-10-05",
                                "fecha_fin": "2025-10-05",
                                "hora_inicio": "14:00:00",
                                "hora_fin": "18:00:00",
                                "duracion_horas": 4.0,
                                "motivo_evento": "Cumpleaños infantil",
                                "numero_personas": 25,
                                "estado": "confirmada",
                                "monto_total": "150000.00",
                                "estado_pago": "pagado",
                                "fecha_creacion": "2025-09-25T10:30:00Z",
                                "dias_restantes": 6,
                                "puede_cancelar": True
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Reservas']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Reserva]:  # type: ignore
        queryset = Reserva.objects.all()
        
        # Si no es superusuario, solo ver sus propias reservas
        if not self.request.user.is_superuser:
            queryset = queryset.filter(usuario=self.request.user)
        
        # Filtros adicionales usando request
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            fecha_desde = query_params.get('fecha_desde')
            if fecha_desde:
                try:
                    fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_inicio__gte=fecha)
                except ValueError:
                    pass
            
            fecha_hasta = query_params.get('fecha_hasta')
            if fecha_hasta:
                try:
                    fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_fin__lte=fecha)
                except ValueError:
                    pass
            
            proximas = query_params.get('proximas')
            if proximas and proximas.lower() == 'true':
                queryset = queryset.filter(fecha_inicio__gte=date.today())
        
        return queryset

class ReservaCreateView(generics.CreateAPIView):
    """Vista para crear nueva reserva"""
    queryset = Reserva.objects.all()
    serializer_class = ReservaCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crear nueva reserva de área común",
        request_body=ReservaCreateSerializer,
        responses={
            201: openapi.Response(
                description="Reserva creada exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Reserva creada exitosamente",
                        "data": {
                            "id": 103,
                            "numero_reserva": "RES-2025-000103",
                            "area": {
                                "id": 1,
                                "nombre": "Salón Social"
                            },
                            "fecha_inicio": "2025-10-12",
                            "fecha_fin": "2025-10-12",
                            "hora_inicio": "15:00:00",
                            "hora_fin": "20:00:00",
                            "duracion_horas": 5.0,
                            "motivo_evento": "Fiesta de graduación",
                            "numero_personas": 45,
                            "estado": "pendiente",
                            "monto_total": "187500.00",
                            "estado_pago": "pendiente"
                        }
                    }
                }
            ),
            400: "Datos inválidos o conflicto de horarios",
            403: "Sin permisos"
        },
        tags=['Reservas']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            reserva = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Reserva creada exitosamente',
                'data': {
                    'id': reserva.id,
                    'numero_reserva': f'RES-2025-{reserva.id:06d}',
                    'area': {
                        'id': reserva.area_comun.id,
                        'nombre': reserva.area_comun.nombre
                    },
                    'fecha_inicio': reserva.fecha_inicio,
                    'fecha_fin': reserva.fecha_fin,
                    'hora_inicio': reserva.hora_inicio,
                    'hora_fin': reserva.hora_fin,
                    'duracion_horas': ReservaListSerializer(reserva).get_duracion_horas(reserva),
                    'motivo_evento': reserva.motivo_evento,
                    'numero_personas': reserva.numero_personas,
                    'estado': reserva.estado,
                    'monto_total': str(reserva.monto_total),
                    'estado_pago': 'pendiente' if reserva.monto_total > 0 else 'no_aplica'
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear reserva',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Continúa views.py - Parte 2

class ReservaDetailView(generics.RetrieveAPIView):
    """Vista para detalles de reserva"""
    serializer_class = ReservaListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Reserva]:  # type: ignore
        if self.request.user.is_superuser:
            return Reserva.objects.all()
        return Reserva.objects.filter(usuario=self.request.user)

    @swagger_auto_schema(
        operation_description="Obtener detalles de una reserva específica",
        responses={
            200: "Detalles de la reserva",
            404: "Reserva no encontrada",
            403: "Sin permisos para ver esta reserva"
        },
        tags=['Reservas']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CancelarReservaView(APIView):
    """Vista para cancelar reserva"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cancelar reserva de área común",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'motivo_cancelacion': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Motivo de la cancelación'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Reserva cancelada exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Reserva cancelada exitosamente",
                        "data": {
                            "id": 103,
                            "estado": "cancelada",
                            "fecha_cancelacion": "2025-09-29T22:30:00Z",
                            "motivo_cancelacion": "Cambio de fecha del evento"
                        }
                    }
                }
            ),
            400: "No se puede cancelar la reserva",
            404: "Reserva no encontrada"
        },
        tags=['Reservas']
    )
    def post(self, request, reserva_id):
        try:
            reserva = Reserva.objects.get(id=reserva_id)
        except Reserva.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Reserva no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verificar permisos
        if not request.user.is_superuser and reserva.usuario != request.user:
            return Response({
                'success': False,
                'message': 'No tienes permisos para cancelar esta reserva'
            }, status=status.HTTP_403_FORBIDDEN)

        # Verificar si se puede cancelar
        if reserva.estado not in ['pendiente', 'confirmada']:
            return Response({
                'success': False,
                'message': f'No se puede cancelar una reserva en estado {reserva.estado}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar tiempo mínimo de cancelación (48 horas antes)
        horas_hasta_evento = (
            datetime.combine(reserva.fecha_inicio, reserva.hora_inicio) - 
            timezone.now()
        ).total_seconds() / 3600

        if horas_hasta_evento < 48 and not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No se puede cancelar con menos de 48 horas de anticipación'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cancelar reserva
        motivo = request.data.get('motivo_cancelacion', 'Sin motivo especificado')
        reserva.estado = 'cancelada'
        reserva.motivo_cancelacion = motivo
        reserva.fecha_cancelacion = timezone.now()
        reserva.save()

        # Formatear fecha de cancelación de manera completamente segura
        fecha_cancelacion_str = None
        fecha_cancelacion = getattr(reserva, 'fecha_cancelacion', None)
        if fecha_cancelacion and hasattr(fecha_cancelacion, 'isoformat'):
            fecha_cancelacion_str = fecha_cancelacion.isoformat()

        return Response({
            'success': True,
            'message': 'Reserva cancelada exitosamente',
            'data': {
                'id': reserva.pk,  # Usar pk en lugar de id
                'estado': reserva.estado,
                'fecha_cancelacion': fecha_cancelacion_str,
                'motivo_cancelacion': motivo
            }
        })

# =================== VISTAS PARA DASHBOARD Y ESTADÍSTICAS ===================

class DashboardAreasView(APIView):
    """Vista para dashboard de áreas comunes"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Dashboard con estadísticas generales de áreas comunes
        
        Incluye resumen de áreas, reservas activas, próximas reservas y estadísticas generales.
        """,
        responses={
            200: openapi.Response(
                description="Dashboard de áreas comunes",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "resumen": {
                                "total_areas": 12,
                                "areas_disponibles": 8,
                                "areas_ocupadas": 2,
                                "areas_mantenimiento": 2
                            },
                            "mis_reservas": {
                                "activas": 1,
                                "proximas": 3,
                                "pendientes_pago": 0
                            },
                            "estadisticas_mes": {
                                "total_reservas": 156,
                                "ingresos_generados": "4650000.00",
                                "area_mas_popular": "Salón Social",
                                "promedio_ocupacion": 67.5
                            },
                            "proximas_reservas": [
                                {
                                    "id": 104,
                                    "area": "Salón Social",
                                    "fecha": "2025-10-05",
                                    "hora": "14:00",
                                    "usuario": "Juan Pérez",
                                    "evento": "Cumpleaños infantil"
                                }
                            ],
                            "areas_populares": [
                                {
                                    "area": "Salón Social",
                                    "reservas_mes": 28,
                                    "ocupacion_porcentaje": 85.2
                                }
                            ]
                        }
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Dashboard']
    )
    def get(self, request):
        # Resumen general de áreas
        total_areas = AreaComun.objects.filter(activo=True).count()
        
        # Calcular áreas ocupadas hoy
        hoy = date.today()
        areas_ocupadas_hoy = Reserva.objects.filter(
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
            estado__in=['confirmada', 'en_uso']
        ).values_list('area_comun_id', flat=True).distinct().count()

        # Mis reservas (si no es admin)
        if request.user.is_superuser:
            reservas_usuario = Reserva.objects.all()
        else:
            reservas_usuario = Reserva.objects.filter(usuario=request.user)

        mis_reservas_activas = reservas_usuario.filter(
            fecha_inicio__gte=hoy,
            estado__in=['confirmada', 'en_uso']
        ).count()

        mis_reservas_proximas = reservas_usuario.filter(
            fecha_inicio__gt=hoy,
            estado='confirmada'
        ).count()

        # Estadísticas del mes actual
        primer_dia_mes = date.today().replace(day=1)
        total_reservas_mes = Reserva.objects.filter(
            fecha_creacion__gte=primer_dia_mes,
            estado__in=['confirmada', 'completada']
        ).count()

        ingresos_mes = Reserva.objects.filter(
            fecha_creacion__gte=primer_dia_mes,
            estado__in=['confirmada', 'completada']
        ).aggregate(total=Sum('monto_total'))['total'] or 0

        # Área más popular del mes
        area_popular = Reserva.objects.filter(
            fecha_creacion__gte=primer_dia_mes
        ).values('area_comun__nombre').annotate(
            total=Count('id')
        ).order_by('-total').first()

        # Próximas reservas (las siguientes 5)
        proximas_reservas = Reserva.objects.filter(
            fecha_inicio__gte=hoy,
            estado='confirmada'
        ).select_related('area_comun', 'usuario').order_by('fecha_inicio', 'hora_inicio')[:5]

        proximas_data = []
        for reserva in proximas_reservas:
            usuario_name = getattr(reserva.usuario, 'get_full_name', lambda: 'Usuario')() or str(reserva.usuario)
            proximas_data.append({
                'id': reserva.pk,  # Usar pk en lugar de id
                'area': reserva.area_comun.nombre,
                'fecha': reserva.fecha_inicio.strftime('%Y-%m-%d'),
                'hora': reserva.hora_inicio.strftime('%H:%M'),
                'usuario': usuario_name,
                'evento': reserva.motivo_evento or 'Sin especificar'
            })

        # Áreas más populares
        areas_populares = Reserva.objects.filter(
            fecha_creacion__gte=primer_dia_mes
        ).values('area_comun__nombre').annotate(
            reservas_mes=Count('id')
        ).order_by('-reservas_mes')[:5]

        return Response({
            'success': True,
            'data': {
                'resumen': {
                    'total_areas': total_areas,
                    'areas_disponibles': total_areas - areas_ocupadas_hoy,
                    'areas_ocupadas': areas_ocupadas_hoy,
                    'areas_mantenimiento': 0  # Podríamos agregar este campo al modelo
                },
                'mis_reservas': {
                    'activas': mis_reservas_activas,
                    'proximas': mis_reservas_proximas,
                    'pendientes_pago': 0  # Se puede calcular si agregamos estado de pago
                },
                'estadisticas_mes': {
                    'total_reservas': total_reservas_mes,
                    'ingresos_generados': str(ingresos_mes),
                    'area_mas_popular': area_popular['area_comun__nombre'] if area_popular else 'N/A',
                    'promedio_ocupacion': 67.5  # Cálculo más complejo requerido
                },
                'proximas_reservas': proximas_data,
                'areas_populares': list(areas_populares)
            }
        })

# =================== VISTAS PARA GESTIÓN DE HORARIOS ===================

class HorarioAreaListView(generics.ListCreateAPIView):
    """Vista para listar y crear horarios de área"""
    serializer_class = HorarioAreaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[HorarioArea]:  # type: ignore
        area_id = self.kwargs.get('area_id')
        return HorarioArea.objects.filter(area_comun_id=area_id, activo=True)

    @swagger_auto_schema(
        operation_description="Obtener horarios de funcionamiento de un área común",
        responses={
            200: "Lista de horarios del área",
            404: "Área común no encontrada"
        },
        tags=['Horarios']
    )
    def get(self, request, *args, **kwargs):
        try:
            area = AreaComun.objects.get(id=self.kwargs['area_id'], activo=True)
        except AreaComun.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Área común no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Crear nuevo horario para área común - Solo administradores",
        request_body=HorarioAreaSerializer,
        tags=['Horarios']
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No tienes permisos para crear horarios'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validar que el área existe
        try:
            area = AreaComun.objects.get(id=self.kwargs['area_id'], activo=True)
        except AreaComun.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Área común no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(area_comun=area)
            return Response({
                'success': True,
                'message': 'Horario creado exitosamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear horario',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# =================== VISTAS DE UTILIDAD ===================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@swagger_auto_schema(
    operation_description="Obtener configuración general del sistema de áreas comunes",
    responses={
        200: openapi.Response(
            description="Configuración del sistema",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "tipos_reserva": [
                            {"value": "por_horas", "label": "Por horas"},
                            {"value": "por_dias", "label": "Por días"},
                            {"value": "eventos", "label": "Eventos"}
                        ],
                        "estados_reserva": [
                            {"value": "pendiente", "label": "Pendiente"},
                            {"value": "confirmada", "label": "Confirmada"},
                            {"value": "cancelada", "label": "Cancelada"},
                            {"value": "completada", "label": "Completada"}
                        ],
                        "configuracion": {
                            "horas_minimas_cancelacion": 48,
                            "horas_maximas_reserva": 168,
                            "deposito_garantia_requerido": True,
                            "requiere_aprobacion_admin": False
                        }
                    }
                }
            }
        )
    },
    tags=['Configuración']
)
def configuracion_sistema(request):
    """Obtener configuración del sistema"""
    tipos_reserva = [
        {"value": "por_horas", "label": "Por horas"},
        {"value": "por_dias", "label": "Por días"},
        {"value": "eventos", "label": "Eventos"}
    ]
    
    estados_reserva = [
        {"value": "pendiente", "label": "Pendiente"},
        {"value": "confirmada", "label": "Confirmada"},
        {"value": "cancelada", "label": "Cancelada"},
        {"value": "completada", "label": "Completada"},
        {"value": "en_uso", "label": "En uso"}
    ]
    
    configuracion = {
        "horas_minimas_cancelacion": 48,
        "horas_maximas_reserva": 168,  # 7 días
        "deposito_garantia_requerido": True,
        "requiere_aprobacion_admin": False
    }
    
    return Response({
        'success': True,
        'data': {
            'tipos_reserva': tipos_reserva,
            'estados_reserva': estados_reserva,
            'configuracion': configuracion
        }
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@swagger_auto_schema(
    operation_description="Obtener estadísticas de uso de áreas comunes",
    manual_parameters=[
        openapi.Parameter(
            'periodo', 
            openapi.IN_QUERY, 
            description="Periodo: mes, trimestre, año",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: "Estadísticas de uso"},
    tags=['Estadísticas']
)
def estadisticas_uso(request):
    """Obtener estadísticas de uso"""
    periodo = request.query_params.get('periodo', 'mes')
    
    # Calcular fecha de inicio según período
    hoy = date.today()
    if periodo == 'año':
        fecha_inicio = hoy.replace(month=1, day=1)
    elif periodo == 'trimestre':
        # Calcular inicio del trimestre actual
        trimestre = (hoy.month - 1) // 3 + 1
        mes_inicio = (trimestre - 1) * 3 + 1
        fecha_inicio = hoy.replace(month=mes_inicio, day=1)
    else:  # mes por defecto
        fecha_inicio = hoy.replace(day=1)
    
    # Estadísticas de reservas
    reservas_periodo = Reserva.objects.filter(
        fecha_creacion__gte=fecha_inicio,
        estado__in=['confirmada', 'completada']
    )
    
    total_reservas = reservas_periodo.count()
    ingresos_total = reservas_periodo.aggregate(total=Sum('monto_total'))['total'] or 0
    promedio_personas = reservas_periodo.aggregate(avg=Avg('numero_personas'))['avg'] or 0
    
    # Áreas más utilizadas
    areas_populares = reservas_periodo.values(
        'area_comun__nombre'
    ).annotate(
        total_reservas=Count('id'),
        ingresos=Sum('monto_total')
    ).order_by('-total_reservas')[:5]
    
    # Días de la semana más populares
    reservas_por_dia = {}
    for reserva in reservas_periodo:
        dia = reserva.fecha_inicio.strftime('%A')
        reservas_por_dia[dia] = reservas_por_dia.get(dia, 0) + 1
    
    return Response({
        'success': True,
        'data': {
            'periodo': periodo,
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'resumen': {
                'total_reservas': total_reservas,
                'ingresos_total': str(ingresos_total),
                'promedio_personas_por_evento': round(promedio_personas, 1)
            },
            'areas_populares': list(areas_populares),
            'reservas_por_dia_semana': reservas_por_dia
        }
    })