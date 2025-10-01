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

from .models import TipoReporte, Reporte, Aviso, AvisoVisto
from .serializers import (
    AvisoListSerializer, AvisoDetailSerializer, AvisoCreateSerializer, AvisoUpdateSerializer,
    ReporteListSerializer, ReporteCreateSerializer, TipoReporteSerializer,
    PreferenciasNotificacionSerializer, DashboardCommunicationsSerializer,
    EstadisticasEfectividadSerializer, UsuarioBasicoSerializer
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

# =================== VISTAS PARA GESTIÓN DE ANUNCIOS (AVISOS) ===================

class AvisoListView(generics.ListAPIView):
    """Vista para listar anuncios/avisos"""
    queryset = Aviso.objects.filter(activo=True)
    serializer_class = AvisoListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configurar filtros de forma condicional
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    filterset_fields = ['tipo', 'prioridad', 'publico_objetivo', 'activo']
    search_fields = ['titulo', 'contenido']
    ordering_fields = ['titulo', 'fecha_publicacion', 'prioridad']
    ordering = ['-fecha_publicacion']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de anuncios del condominio
        
        ### Filtros disponibles:
        - `categoria`: informativo, urgente, mantenimiento
        - `prioridad`: baja, normal, alta
        - `activo`: true/false
        - `vigente`: Solo anuncios vigentes (true/false)
        - `autor`: ID del autor específico
        - `fecha_desde`: Fecha desde (YYYY-MM-DD)
        - `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
        
        ### Búsqueda:
        - `search`: buscar por título o contenido
        
        ### Ordenamiento:
        - `ordering`: titulo, fecha_publicacion, prioridad
        """,
        responses={
            200: openapi.Response(
                description="Lista de anuncios",
                examples={
                    "application/json": {
                        "count": 45,
                        "next": None,
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "titulo": "Corte de Agua Programado",
                                "categoria": "mantenimiento",
                                "prioridad": "alta",
                                "contenido_resumen": "Se realizará corte de agua el próximo martes de 8:00 AM a 2:00 PM...",
                                "fecha_publicacion": "2025-09-27T08:00:00Z",
                                "fecha_caducidad": "2025-10-01T23:59:59Z",
                                "autor": {
                                    "id": 5,
                                    "full_name": "Administrador Principal",
                                    "cargo": "Administrador"
                                },
                                "activo": True,
                                "vigente": True,
                                "visualizaciones": 145,
                                "dirigido_a": "todos",
                                "adjuntos_count": 1,
                                "comentarios_count": 8,
                                "imagen_destacada": "https://storage.example.com/anuncios/corte_agua_01.jpg"
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado - Token JWT requerido"
        },
        tags=['Anuncios']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Aviso]:  # type: ignore
        queryset = Aviso.objects.filter(activo=True)
        
        # Filtros adicionales usando request
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            vigente = query_params.get('vigente')
            if vigente is not None and vigente.lower() == 'true':
                # Filtrar solo avisos vigentes
                now = timezone.now()
                queryset = queryset.filter(
                    Q(fecha_caducidad__isnull=True) | Q(fecha_caducidad__gt=now)
                )
            
            autor = query_params.get('autor')
            if autor:
                try:
                    queryset = queryset.filter(usuario_id=int(autor))
                except ValueError:
                    pass
            
            fecha_desde = query_params.get('fecha_desde')
            if fecha_desde:
                try:
                    fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_publicacion__date__gte=fecha)
                except ValueError:
                    pass
            
            fecha_hasta = query_params.get('fecha_hasta')
            if fecha_hasta:
                try:
                    fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_publicacion__date__lte=fecha)
                except ValueError:
                    pass
        
        return queryset


class AvisoDetailView(generics.RetrieveAPIView):
    """Vista para detalles de anuncio"""
    queryset = Aviso.objects.filter(activo=True)
    serializer_class = AvisoDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Obtener detalles completos de un anuncio específico
        
        Incluye contenido completo, estadísticas, adjuntos y metadatos.
        Registra automáticamente la visualización del usuario.
        """,
        responses={
            200: openapi.Response(
                description="Detalles del anuncio",
                examples={
                    "application/json": {
                        "id": 1,
                        "titulo": "Corte de Agua Programado",
                        "categoria": "mantenimiento",
                        "prioridad": "alta",
                        "contenido": "Estimados residentes...",
                        "fecha_publicacion": "2025-09-27T08:00:00Z",
                        "fecha_caducidad": "2025-10-01T23:59:59Z",
                        "autor": {
                            "id": 5,
                            "full_name": "Administrador Principal",
                            "cargo": "Administrador",
                            "email": "admin@torres-del-sol.com"
                        },
                        "estadisticas": {
                            "visualizaciones_por_dia": [],
                            "visualizaciones_por_bloque": []
                        }
                    }
                }
            ),
            404: "Anuncio no encontrado",
            401: "No autorizado"
        },
        tags=['Anuncios']
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Registrar visualización si es exitosa
        if response.status_code == 200:
            aviso = self.get_object()
            self._registrar_visualizacion(aviso, request.user)
        
        return response
    
    def _registrar_visualizacion(self, aviso, usuario):
        """Registra que el usuario vio el aviso"""
        AvisoVisto.objects.get_or_create(
            aviso=aviso,
            usuario=usuario,
            defaults={'fecha_visto': timezone.now()}
        )


class AvisoCreateView(generics.CreateAPIView):
    """Vista para crear nuevo anuncio"""
    queryset = Aviso.objects.all()
    serializer_class = AvisoCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crear nuevo anuncio en el condominio - Solo administradores",
        request_body=AvisoCreateSerializer,
        responses={
            201: openapi.Response(
                description="Anuncio creado exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Anuncio creado exitosamente",
                        "data": {
                            "id": 46,
                            "titulo": "Nueva Política de Mascotas",
                            "categoria": "normativo",
                            "prioridad": "media",
                            "fecha_publicacion": "2025-09-29T23:30:00Z",
                            "fecha_caducidad": "2025-11-15T23:59:59Z",
                            "autor": {
                                "id": 5,
                                "full_name": "Administrador Principal"
                            },
                            "activo": True,
                            "dirigido_a": "todos",
                            "notificacion_enviada": True,
                            "residentes_notificados": 340
                        }
                    }
                }
            ),
            400: "Datos inválidos",
            403: "Sin permisos para crear anuncios"
        },
        tags=['Anuncios']
    )
    def post(self, request, *args, **kwargs):
        # Solo superusuarios pueden crear anuncios
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No tienes permisos para crear anuncios'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            aviso = serializer.save()
            
            # Calcular residentes notificados
            residentes_notificados = self._calcular_residentes_objetivo(aviso.publico_objetivo)
            
            return Response({
                'success': True,
                'message': 'Anuncio creado exitosamente',
                'data': {
                    'id': aviso.pk,
                    'titulo': aviso.titulo,
                    'categoria': aviso.tipo,
                    'prioridad': aviso.prioridad,
                    'fecha_publicacion': aviso.fecha_publicacion.isoformat(),
                    'fecha_caducidad': aviso.fecha_caducidad.isoformat() if aviso.fecha_caducidad else None,
                    'autor': {
                        'id': aviso.usuario.pk,
                        'full_name': UsuarioBasicoSerializer(aviso.usuario).get_full_name(aviso.usuario)
                    },
                    'activo': aviso.activo,
                    'dirigido_a': aviso.publico_objetivo,
                    'notificacion_enviada': True,
                    'residentes_notificados': residentes_notificados
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear anuncio',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _calcular_residentes_objetivo(self, publico_objetivo):
        """Calcula cuántos residentes son el objetivo según el público"""
        # Placeholder para cálculo real
        if publico_objetivo == 'todos':
            return User.objects.filter(is_active=True).count()
        elif publico_objetivo == 'propietarios':
            return User.objects.filter(is_active=True).count() // 2  # Estimación
        elif publico_objetivo == 'inquilinos':
            return User.objects.filter(is_active=True).count() // 3  # Estimación
        return 0


class AvisoUpdateView(generics.UpdateAPIView):
    """Vista para actualizar anuncio"""
    queryset = Aviso.objects.all()
    serializer_class = AvisoUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Actualizar anuncio - Solo administradores",
        request_body=AvisoUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Anuncio actualizado exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Anuncio actualizado exitosamente",
                        "data": {
                            "id": 46,
                            "titulo": "Nueva Política de Mascotas - ACTUALIZADA",
                            "prioridad": "alta",
                            "fecha_ultima_edicion": "2025-09-29T23:45:00Z",
                            "cambios_realizados": [
                                "Título actualizado",
                                "Prioridad cambiada a alta"
                            ],
                            "notificacion_actualizacion_enviada": True,
                            "residentes_notificados": 340
                        }
                    }
                }
            ),
            400: "Datos inválidos",
            403: "Sin permisos",
            404: "Anuncio no encontrado"
        },
        tags=['Anuncios']
    )
    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'No tienes permisos para actualizar anuncios'
            }, status=status.HTTP_403_FORBIDDEN)
        
        aviso = self.get_object()
        serializer = self.get_serializer(aviso, data=request.data)
        
        if serializer.is_valid():
            updated_aviso = serializer.save()
            
            # Obtener cambios del serializador
            cambios_realizados = getattr(serializer, '_cambios_realizados', [])
            
            return Response({
                'success': True,
                'message': 'Anuncio actualizado exitosamente',
                'data': {
                    'id': updated_aviso.pk,
                    'titulo': updated_aviso.titulo,
                    'prioridad': updated_aviso.prioridad,
                    'fecha_ultima_edicion': updated_aviso.updated_at.isoformat(),
                    'cambios_realizados': cambios_realizados,
                    'notificacion_actualizacion_enviada': True,
                    'residentes_notificados': self._calcular_residentes_objetivo(updated_aviso.publico_objetivo)
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Error al actualizar anuncio',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _calcular_residentes_objetivo(self, publico_objetivo):
        """Calcula cuántos residentes son el objetivo según el público"""
        if publico_objetivo == 'todos':
            return User.objects.filter(is_active=True).count()
        elif publico_objetivo == 'propietarios':
            return User.objects.filter(is_active=True).count() // 2
        elif publico_objetivo == 'inquilinos':
            return User.objects.filter(is_active=True).count() // 3
        return 0


# =================== VISTAS PARA GESTIÓN DE REPORTES ===================

class ReporteListView(generics.ListAPIView):
    """Vista para listar reportes"""
    serializer_class = ReporteListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configurar filtros de forma condicional
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    filterset_fields = ['tipo_reporte', 'estado', 'prioridad', 'usuario']
    search_fields = ['titulo', 'descripcion']
    ordering_fields = ['fecha_registro', 'prioridad', 'estado']
    ordering = ['-fecha_registro']

    @swagger_auto_schema(
        operation_description="""
        Obtener lista de reportes del condominio
        
        ### Filtros disponibles:
        - `tipo_reporte`: ID del tipo de reporte
        - `estado`: abierto, en_proceso, resuelto, cerrado
        - `prioridad`: baja, media, alta, urgente
        - `usuario`: ID del usuario específico
        - `asignado_a`: ID del administrador asignado
        - `fecha_desde`: Fecha desde (YYYY-MM-DD)
        - `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
        
        ### Búsqueda:
        - `search`: buscar por título o descripción
        
        ### Ordenamiento:
        - `ordering`: fecha_registro, prioridad, estado
        """,
        responses={
            200: openapi.Response(
                description="Lista de reportes",
                examples={
                    "application/json": {
                        "count": 25,
                        "results": [
                            {
                                "id": 101,
                                "titulo": "Problema con ruido en horas nocturnas",
                                "descripcion": "Reporte de ruido excesivo...",
                                "prioridad": "media",
                                "estado": "abierto",
                                "fecha_registro": "2025-09-28T16:45:00Z",
                                "usuario_info": {
                                    "id": 15,
                                    "full_name": "Juan Pérez"
                                },
                                "tipo_reporte_info": {
                                    "id": 1,
                                    "nombre": "Convivencia"
                                },
                                "tiempo_transcurrido": "2 días",
                                "dias_abierto": 2
                            }
                        ]
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Reportes']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Reporte]:  # type: ignore
        queryset = Reporte.objects.all()
        
        # Si no es superusuario, solo ver sus propios reportes
        if not self.request.user.is_superuser:
            queryset = queryset.filter(usuario=self.request.user)
        
        # Filtros adicionales
        if hasattr(self, 'request') and self.request:
            query_params = getattr(self.request, 'query_params', getattr(self.request, 'GET', {}))
            
            asignado_a = query_params.get('asignado_a')
            if asignado_a:
                try:
                    queryset = queryset.filter(asignado_a_id=int(asignado_a))
                except ValueError:
                    pass
            
            fecha_desde = query_params.get('fecha_desde')
            if fecha_desde:
                try:
                    fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_registro__date__gte=fecha)
                except ValueError:
                    pass
            
            fecha_hasta = query_params.get('fecha_hasta')
            if fecha_hasta:
                try:
                    fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_registro__date__lte=fecha)
                except ValueError:
                    pass
        
        return queryset


class ReporteCreateView(generics.CreateAPIView):
    """Vista para crear nuevo reporte"""
    queryset = Reporte.objects.all()
    serializer_class = ReporteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crear nuevo reporte",
        request_body=ReporteCreateSerializer,
        responses={
            201: openapi.Response(
                description="Reporte creado exitosamente",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Reporte creado exitosamente",
                        "data": {
                            "id": 103,
                            "numero_ticket": "REP-2025-000103",
                            "titulo": "Solicitud de reparación en ascensor",
                            "tipo_reporte": "Mantenimiento",
                            "prioridad": "alta",
                            "estado": "abierto",
                            "fecha_registro": "2025-09-30T00:10:00Z",
                            "tiempo_respuesta_estimado": "24 horas"
                        }
                    }
                }
            ),
            400: "Datos inválidos",
            403: "Sin permisos"
        },
        tags=['Reportes']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            reporte = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Reporte creado exitosamente',
                'data': {
                    'id': reporte.pk,
                    'numero_ticket': f'REP-2025-{reporte.pk:06d}',
                    'titulo': reporte.titulo,
                    'tipo_reporte': reporte.tipo_reporte.nombre,
                    'prioridad': reporte.prioridad,
                    'estado': reporte.estado,
                    'fecha_registro': reporte.fecha_registro.isoformat(),
                    'tiempo_respuesta_estimado': f'{reporte.tipo_reporte.tiempo_respuesta_horas} horas'
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear reporte',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# =================== VISTAS PARA DASHBOARD Y ESTADÍSTICAS ===================

class DashboardCommunicationsView(APIView):
    """Vista para dashboard de comunicaciones"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Dashboard con estadísticas generales de comunicaciones
        
        Incluye resumen de anuncios, reportes, notificaciones y engagement.
        """,
        responses={
            200: openapi.Response(
                description="Dashboard de comunicaciones",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "periodo": "2025-09",
                            "anuncios": {
                                "total_publicados": 12,
                                "activos": 8,
                                "vencidos": 4,
                                "visualizaciones_totales": 1850,
                                "promedio_visualizaciones": 154.2
                            },
                            "reportes": {
                                "total_mes": 25,
                                "abiertos": 8,
                                "en_proceso": 5,
                                "resueltos": 12,
                                "tiempo_promedio_resolucion": "18.5 horas"
                            }
                        }
                    }
                }
            ),
            401: "No autorizado"
        },
        tags=['Dashboard']
    )
    def get(self, request):
        # Obtener fecha actual
        now = timezone.now()
        primer_dia_mes = now.replace(day=1)
        
        # Estadísticas de anuncios
        anuncios_mes = Aviso.objects.filter(fecha_publicacion__gte=primer_dia_mes)
        anuncios_activos = anuncios_mes.filter(activo=True)
        anuncios_vencidos = anuncios_mes.filter(
            activo=True,
            fecha_caducidad__lt=now
        )
        
        # Estadísticas de visualizaciones
        total_visualizaciones = AvisoVisto.objects.filter(
            aviso__fecha_publicacion__gte=primer_dia_mes
        ).count()
        
        promedio_visualizaciones = 0
        if anuncios_mes.count() > 0:
            promedio_visualizaciones = total_visualizaciones / anuncios_mes.count()
        
        # Estadísticas de reportes
        reportes_mes = Reporte.objects.filter(fecha_registro__gte=primer_dia_mes)
        reportes_abiertos = reportes_mes.filter(estado='abierto')
        reportes_en_proceso = reportes_mes.filter(estado='en_proceso')
        reportes_resueltos = reportes_mes.filter(estado__in=['resuelto', 'cerrado'])
        
        # Tiempo promedio de resolución
        reportes_con_resolucion = reportes_resueltos.filter(
            fecha_resolucion__isnull=False
        )
        tiempo_promedio_resolucion = "0 horas"
        if reportes_con_resolucion.exists():
            tiempos = []
            for reporte in reportes_con_resolucion:
                if reporte.fecha_resolucion:
                    delta = reporte.fecha_resolucion - reporte.fecha_registro
                    tiempos.append(delta.total_seconds() / 3600)  # horas
            
            if tiempos:
                promedio_horas = sum(tiempos) / len(tiempos)
                tiempo_promedio_resolucion = f"{promedio_horas:.1f} horas"
        
        return Response({
            'success': True,
            'data': {
                'periodo': now.strftime('%Y-%m'),
                'anuncios': {
                    'total_publicados': anuncios_mes.count(),
                    'activos': anuncios_activos.count(),
                    'vencidos': anuncios_vencidos.count(),
                    'visualizaciones_totales': total_visualizaciones,
                    'promedio_visualizaciones': round(promedio_visualizaciones, 1),
                    'comentarios_totales': 0,  # Placeholder
                    'categoria_mas_usada': self._get_categoria_mas_usada(anuncios_mes)
                },
                'reportes': {
                    'total_mes': reportes_mes.count(),
                    'abiertos': reportes_abiertos.count(),
                    'en_proceso': reportes_en_proceso.count(),
                    'resueltos': reportes_resueltos.count(),
                    'tiempo_promedio_resolucion': tiempo_promedio_resolucion,
                    'satisfaccion_promedio': 4.2,  # Placeholder
                    'tipos_mas_comunes': self._get_tipos_reportes_mas_comunes(reportes_mes)
                },
                'engagement': {
                    'usuarios_activos': self._get_usuarios_activos(primer_dia_mes),
                    'porcentaje_participacion': 54.4,  # Placeholder
                    'horario_mayor_actividad': "18:00-21:00",  # Placeholder
                    'dia_mayor_actividad': "martes"  # Placeholder
                }
            }
        })
    
    def _get_categoria_mas_usada(self, queryset):
        """Obtiene la categoría más usada"""
        categoria_counts = queryset.values('tipo').annotate(count=Count('tipo')).order_by('-count')
        if categoria_counts:
            return categoria_counts[0]['tipo']
        return "informativo"
    
    def _get_tipos_reportes_mas_comunes(self, queryset):
        """Obtiene los tipos de reportes más comunes"""
        tipos = queryset.values('tipo_reporte__nombre').annotate(
            cantidad=Count('tipo_reporte')
        ).order_by('-cantidad')[:3]
        
        return [
            {'tipo': tipo['tipo_reporte__nombre'], 'cantidad': tipo['cantidad']}
            for tipo in tipos
        ]
    
    def _get_usuarios_activos(self, desde):
        """Calcula usuarios activos en el período"""
        # Usuarios que han visto avisos o creado reportes
        usuarios_avisos = AvisoVisto.objects.filter(
            fecha_visto__gte=desde
        ).values_list('usuario_id', flat=True).distinct()
        
        usuarios_reportes = Reporte.objects.filter(
            fecha_registro__gte=desde
        ).values_list('usuario_id', flat=True).distinct()
        
        usuarios_activos = set(usuarios_avisos) | set(usuarios_reportes)
        return len(usuarios_activos)


# =================== VISTAS PARA CONFIGURACIÓN ===================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@swagger_auto_schema(
    operation_description="Obtener configuración general del sistema de comunicaciones",
    responses={
        200: openapi.Response(
            description="Configuración del sistema",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "tipos_anuncio": [
                            {"value": "informativo", "label": "Informativo"},
                            {"value": "urgente", "label": "Urgente"},
                            {"value": "mantenimiento", "label": "Mantenimiento"}
                        ],
                        "prioridades": [
                            {"value": "baja", "label": "Baja"},
                            {"value": "normal", "label": "Normal"},
                            {"value": "alta", "label": "Alta"}
                        ],
                        "publicos_objetivo": [
                            {"value": "todos", "label": "Todos los residentes"},
                            {"value": "propietarios", "label": "Solo propietarios"},
                            {"value": "inquilinos", "label": "Solo inquilinos"}
                        ]
                    }
                }
            }
        )
    },
    tags=['Configuración']
)
def configuracion_comunicaciones(request):
    """Obtener configuración del sistema de comunicaciones"""
    tipos_anuncio = [
        {"value": "informativo", "label": "Informativo"},
        {"value": "urgente", "label": "Urgente"},
        {"value": "mantenimiento", "label": "Mantenimiento"}
    ]
    
    prioridades = [
        {"value": "baja", "label": "Baja"},
        {"value": "normal", "label": "Normal"},
        {"value": "alta", "label": "Alta"}
    ]
    
    publicos_objetivo = [
        {"value": "todos", "label": "Todos los residentes"},
        {"value": "propietarios", "label": "Solo propietarios"},
        {"value": "inquilinos", "label": "Solo inquilinos"}
    ]
    
    tipos_reporte = TipoReporte.objects.filter(activo=True).values(
        'id', 'nombre', 'categoria', 'descripcion'
    )
    
    return Response({
        'success': True,
        'data': {
            'tipos_anuncio': tipos_anuncio,
            'prioridades': prioridades,
            'publicos_objetivo': publicos_objetivo,
            'tipos_reporte': list(tipos_reporte)
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@swagger_auto_schema(
    operation_description="Obtener estadísticas de efectividad de comunicaciones",
    manual_parameters=[
        openapi.Parameter(
            'fecha_desde', 
            openapi.IN_QUERY, 
            description="Fecha desde (YYYY-MM-DD)",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'fecha_hasta', 
            openapi.IN_QUERY, 
            description="Fecha hasta (YYYY-MM-DD)",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: "Estadísticas de efectividad"},
    tags=['Estadísticas']
)
def estadisticas_efectividad(request):
    """Obtener estadísticas de efectividad de comunicaciones"""
    fecha_desde_str = request.query_params.get('fecha_desde')
    fecha_hasta_str = request.query_params.get('fecha_hasta')
    
    # Fechas por defecto (último mes)
    if not fecha_desde_str or not fecha_hasta_str:
        hoy = date.today()
        fecha_hasta = hoy
        fecha_desde = hoy.replace(day=1)
    else:
        try:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Estadísticas de anuncios
    anuncios_periodo = Aviso.objects.filter(
        fecha_publicacion__date__gte=fecha_desde,
        fecha_publicacion__date__lte=fecha_hasta
    )
    
    total_anuncios = anuncios_periodo.count()
    if total_anuncios > 0:
        # Calcular alcance promedio
        total_usuarios = User.objects.filter(is_active=True).count()
        total_visualizaciones = AvisoVisto.objects.filter(
            aviso__in=anuncios_periodo
        ).count()
        
        alcance_promedio = (total_visualizaciones / (total_anuncios * total_usuarios)) * 100 if total_usuarios > 0 else 0
        
        # Categorías más efectivas
        categorias_stats = anuncios_periodo.values('tipo').annotate(
            total_avisos=Count('id'),
            total_vistas=Count('avisovisto')
        )
        
        categorias_efectivas = []
        for cat in categorias_stats:
            if cat['total_avisos'] > 0:
                alcance_cat = (cat['total_vistas'] / cat['total_avisos']) * 100
                categorias_efectivas.append({
                    'categoria': cat['tipo'],
                    'alcance': round(alcance_cat, 1),
                    'interaccion': round(alcance_cat * 0.15, 1)  # Estimación
                })
    else:
        alcance_promedio = 0
        categorias_efectivas = []
    
    # Estadísticas de reportes
    reportes_periodo = Reporte.objects.filter(
        fecha_registro__date__gte=fecha_desde,
        fecha_registro__date__lte=fecha_hasta
    )
    
    # Tiempo promedio de respuesta
    reportes_con_respuesta = reportes_periodo.filter(
        fecha_resolucion__isnull=False
    )
    
    tiempo_respuesta_promedio = "0 horas"
    if reportes_con_respuesta.exists():
        tiempos = []
        for reporte in reportes_con_respuesta:
            if reporte.fecha_resolucion:
                delta = reporte.fecha_resolucion - reporte.fecha_registro
                tiempos.append(delta.total_seconds() / 3600)
        
        if tiempos:
            promedio = sum(tiempos) / len(tiempos)
            tiempo_respuesta_promedio = f"{promedio:.1f} horas"
    
    # Temas frecuentes de reportes
    temas_frecuentes = reportes_periodo.values('tipo_reporte__nombre').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')[:5]
    
    return Response({
        'success': True,
        'data': {
            'periodo': {
                'desde': fecha_desde.strftime('%Y-%m-%d'),
                'hasta': fecha_hasta.strftime('%Y-%m-%d')
            },
            'anuncios': {
                'total_publicados': total_anuncios,
                'alcance_promedio': round(alcance_promedio, 1),
                'tiempo_promedio_lectura': "3.2 minutos",  # Placeholder
                'interaccion_promedio': 7.4,  # Placeholder
                'categorias_efectivas': categorias_efectivas
            },
            'reportes': {
                'tiempo_respuesta_promedio': tiempo_respuesta_promedio,
                'resolucion_primer_contacto': 68.5,  # Placeholder
                'satisfaccion_promedio': 4.2,  # Placeholder
                'temas_frecuentes': [
                    {'tema': tema['tipo_reporte__nombre'], 'cantidad': tema['cantidad']}
                    for tema in temas_frecuentes
                ]
            }
        }
    })
