from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg, Max, Min
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, NumberFilter, DateTimeFilter, BooleanFilter
from typing import Dict, Any
from datetime import datetime, timedelta

from .models import (
    TipoEvento, Zona, Camara, VehiculoAutorizado, 
    EventoSeguridad, CredentialAcceso
)
from .serializers import (
    # Serializers básicos
    TipoEventoSerializer, ZonaListSerializer, 
    
    # Serializers para cámaras
    CamaraListSerializer, CamaraDetailSerializer,
    
    # Serializers para vehículos
    VehiculoAutorizadoListSerializer, VehiculoAutorizadoCreateSerializer,
    VehiculoAprobacionSerializer,
    
    # Serializers para eventos
    EventoSeguridadListSerializer, EventoSeguridadDetailSerializer,
    EventoSeguridadCreateSerializer, EventoRevisionSerializer,
    
    # Serializers para credenciales
    CredentialAccesoListSerializer, CredentialAccesoCreateSerializer,
    CredentialEstadoSerializer, UsoCredencialSerializer,
    
    # Serializers para dashboard
    DashboardSeguridadSerializer, ReporteSeguridadSerializer,
    ExportarReporteSerializer
)


# =================== FILTROS ===================

class EventoSeguridadFilter(FilterSet):
    """Filtros para eventos de seguridad"""
    tipo_evento = NumberFilter(field_name='tipo_evento__id')
    zona = NumberFilter(field_name='camara__zona__id')
    severidad = NumberFilter()
    revisado = BooleanFilter()
    fecha_desde = DateTimeFilter(field_name='fecha_hora', lookup_expr='gte')
    fecha_hasta = DateTimeFilter(field_name='fecha_hora', lookup_expr='lte')
    usuario = NumberFilter(field_name='usuario__id')
    
    class Meta:
        model = EventoSeguridad
        fields = ['tipo_evento', 'zona', 'severidad', 'revisado', 'fecha_desde', 'fecha_hasta', 'usuario']


class VehiculoAutorizadoFilter(FilterSet):
    """Filtros para vehículos autorizados"""
    usuario = NumberFilter(field_name='usuario__id')
    tipo_vehiculo = CharFilter()
    aprobado = BooleanFilter(field_name='fecha_aprobacion', lookup_expr='isnull', exclude=True)
    pendiente = BooleanFilter(field_name='fecha_aprobacion', lookup_expr='isnull')
    
    class Meta:
        model = VehiculoAutorizado
        fields = ['usuario', 'tipo_vehiculo', 'aprobado', 'pendiente']


class CredentialAccesoFilter(FilterSet):
    """Filtros para credenciales de acceso"""
    usuario = NumberFilter(field_name='usuario__id')
    tipo = CharFilter()
    estado = CharFilter()
    por_vencer = BooleanFilter(method='filter_por_vencer')
    
    def filter_por_vencer(self, queryset, name, value):
        if value:
            fecha_limite = timezone.now() + timedelta(days=30)
            return queryset.filter(
                fecha_vencimiento__lte=fecha_limite,
                fecha_vencimiento__gt=timezone.now()
            )
        return queryset
    
    class Meta:
        model = CredentialAcceso
        fields = ['usuario', 'tipo', 'estado', 'por_vencer']


# =================== VIEWSETS PRINCIPALES ===================

class TipoEventoViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de evento"""
    queryset = TipoEvento.objects.filter(activo=True)
    serializer_class = TipoEventoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'severidad', 'created_at']
    ordering = ['-created_at']


class ZonaViewSet(viewsets.ModelViewSet):
    """ViewSet para zonas de seguridad"""
    queryset = Zona.objects.filter(activo=True)
    serializer_class = ZonaListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nombre', 'tipo', 'descripcion']
    ordering_fields = ['nombre', 'nivel_seguridad', 'created_at']
    ordering = ['nombre']
    
    @action(detail=True, methods=['get'])
    def camaras(self, request, pk=None):
        """Obtener cámaras de una zona"""
        zona = self.get_object()
        camaras = Camara.objects.filter(zona=zona, activo=True)
        serializer = CamaraListSerializer(camaras, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def eventos(self, request, pk=None):
        """Obtener eventos de una zona"""
        zona = self.get_object()
        eventos = EventoSeguridad.objects.filter(
            camara__zona=zona
        ).order_by('-fecha_hora')[:20]
        serializer = EventoSeguridadListSerializer(eventos, many=True)
        return Response(serializer.data)


class CamaraViewSet(viewsets.ModelViewSet):
    """ViewSet para cámaras"""
    queryset = Camara.objects.filter(activo=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nombre', 'ubicacion', 'modelo']
    ordering_fields = ['nombre', 'fecha_instalacion', 'ultimo_mantenimiento']
    ordering = ['nombre']
    
    def get_serializer_class(self):  # type: ignore
        if self.action == 'retrieve':
            return CamaraDetailSerializer
        return CamaraListSerializer
    
    @action(detail=True, methods=['get'])
    def eventos(self, request, pk=None):
        """Obtener eventos de una cámara"""
        camara = self.get_object()
        eventos = EventoSeguridad.objects.filter(camara=camara).order_by('-fecha_hora')[:50]
        serializer = EventoSeguridadListSerializer(eventos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verificar_conexion(self, request, pk=None):
        """Verificar conexión de la cámara"""
        camara = self.get_object()
        # Placeholder para verificación real de conexión
        return Response({
            'estado': 'online',
            'ultima_verificacion': timezone.now(),
            'latencia': 45  # ms
        })


class VehiculoAutorizadoViewSet(viewsets.ModelViewSet):
    """ViewSet para vehículos autorizados"""
    queryset = VehiculoAutorizado.objects.filter(activo=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VehiculoAutorizadoFilter
    search_fields = ['placa', 'marca', 'modelo', 'usuario__first_name', 'usuario__last_name']
    ordering_fields = ['fecha_registro', 'fecha_aprobacion', 'placa']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):  # type: ignore
        if self.action == 'create':
            return VehiculoAutorizadoCreateSerializer
        return VehiculoAutorizadoListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por usuario si no es admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(usuario=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtener vehículos pendientes de aprobación"""
        vehiculos = self.get_queryset().filter(fecha_aprobacion__isnull=True)
        serializer = self.get_serializer(vehiculos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprobar o rechazar vehículo"""
        vehiculo = self.get_object()
        serializer = VehiculoAprobacionSerializer(data=request.data)
        
        if serializer.is_valid():
            if serializer.validated_data['aprobado']:
                vehiculo.fecha_aprobacion = timezone.now()
                vehiculo.aprobado_por = request.user
            else:
                # Rechazar vehículo (marcar como inactivo)
                vehiculo.activo = False
            
            vehiculo.save()
            
            return Response({
                'message': 'Vehículo aprobado' if serializer.validated_data['aprobado'] else 'Vehículo rechazado',
                'vehiculo': VehiculoAutorizadoListSerializer(vehiculo).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventoSeguridadViewSet(viewsets.ModelViewSet):
    """ViewSet para eventos de seguridad"""
    queryset = EventoSeguridad.objects.select_related(
        'tipo_evento', 'camara', 'usuario', 'vehiculo_autorizado', 'resuelto_por'
    ).all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EventoSeguridadFilter
    search_fields = ['descripcion', 'tipo_evento__nombre', 'usuario__first_name', 'usuario__last_name']
    ordering_fields = ['fecha_hora', 'severidad', 'revisado']
    ordering = ['-fecha_hora']
    
    def get_serializer_class(self):  # type: ignore
        if self.action == 'create':
            return EventoSeguridadCreateSerializer
        elif self.action == 'retrieve':
            return EventoSeguridadDetailSerializer
        return EventoSeguridadListSerializer
    
    @action(detail=False, methods=['get'])
    def no_revisados(self, request):
        """Obtener eventos no revisados"""
        eventos = self.get_queryset().filter(revisado=False)
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def alta_severidad(self, request):
        """Obtener eventos de alta severidad"""
        eventos = self.get_queryset().filter(severidad__gte=3)
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def revisar(self, request, pk=None):
        """Marcar evento como revisado"""
        evento = self.get_object()
        serializer = EventoRevisionSerializer(data=request.data)
        
        if serializer.is_valid():
            evento.revisado = serializer.validated_data['revisado']
            if evento.revisado:
                evento.fecha_resolucion = timezone.now()
                evento.resuelto_por = request.user
                evento.notas_resolucion = serializer.validated_data.get('notas_resolucion', '')
            
            evento.save()
            
            return Response({
                'message': 'Evento actualizado',
                'evento': EventoSeguridadDetailSerializer(evento).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CredentialAccesoViewSet(viewsets.ModelViewSet):
    """ViewSet para credenciales de acceso"""
    queryset = CredentialAcceso.objects.filter(activo=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CredentialAccesoFilter
    search_fields = ['identificador', 'usuario__first_name', 'usuario__last_name']
    ordering_fields = ['fecha_emision', 'fecha_vencimiento', 'ultimo_uso']
    ordering = ['-fecha_emision']
    
    def get_serializer_class(self):  # type: ignore
        if self.action == 'create':
            return CredentialAccesoCreateSerializer
        return CredentialAccesoListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por usuario si no es admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(usuario=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def por_vencer(self, request):
        """Obtener credenciales próximas a vencer"""
        fecha_limite = timezone.now() + timedelta(days=30)
        credenciales = self.get_queryset().filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gt=timezone.now(),
            estado='activo'
        )
        serializer = self.get_serializer(credenciales, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """Obtener credenciales vencidas"""
        credenciales = self.get_queryset().filter(
            fecha_vencimiento__lt=timezone.now(),
            estado='activo'
        )
        serializer = self.get_serializer(credenciales, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de credencial"""
        credencial = self.get_object()
        serializer = CredentialEstadoSerializer(data=request.data)
        
        if serializer.is_valid():
            credencial.estado = serializer.validated_data['estado']
            credencial.save()
            
            return Response({
                'message': f'Credencial {credencial.estado}',
                'credencial': CredentialAccesoListSerializer(credencial).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def registrar_uso(self, request, pk=None):
        """Registrar uso de credencial"""
        credencial = self.get_object()
        serializer = UsoCredencialSerializer(data=request.data)
        
        if serializer.is_valid():
            if serializer.validated_data['exitoso']:
                credencial.ultimo_uso = timezone.now()
                credencial.save()
            
            # Aquí se podría crear un registro de uso en otra tabla
            
            return Response({
                'message': 'Uso registrado',
                'exitoso': serializer.validated_data['exitoso']
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =================== DASHBOARD Y REPORTES ===================

class DashboardSeguridadViewSet(viewsets.ViewSet):
    """ViewSet para dashboard de seguridad"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Resumen general de seguridad"""
        hoy = timezone.now().date()
        esta_semana = hoy - timedelta(days=7)
        
        # Eventos hoy
        eventos_hoy = EventoSeguridad.objects.filter(fecha_hora__date=hoy).count()
        eventos_semana = EventoSeguridad.objects.filter(fecha_hora__date__gte=esta_semana).count()
        eventos_no_revisados = EventoSeguridad.objects.filter(revisado=False).count()
        eventos_alta_severidad = EventoSeguridad.objects.filter(
            severidad__gte=3, 
            fecha_hora__date=hoy
        ).count()
        
        # Vehículos
        vehiculos_pendientes = VehiculoAutorizado.objects.filter(
            fecha_aprobacion__isnull=True,
            activo=True
        ).count()
        
        # Credenciales
        credenciales_por_vencer = CredentialAcceso.objects.filter(
            fecha_vencimiento__lte=timezone.now() + timedelta(days=30),
            fecha_vencimiento__gt=timezone.now(),
            activo=True
        ).count()
        
        # Cámaras
        camaras_total = Camara.objects.filter(activo=True).count()
        
        data = {
            'resumen': {
                'eventos_hoy': eventos_hoy,
                'eventos_semana': eventos_semana,
                'eventos_no_revisados': eventos_no_revisados,
                'eventos_alta_severidad': eventos_alta_severidad,
                'vehiculos_pendientes': vehiculos_pendientes,
                'credenciales_por_vencer': credenciales_por_vencer,
                'camaras_activas': camaras_total
            },
            'eventos_por_severidad': self._eventos_por_severidad(),
            'eventos_por_zona': self._eventos_por_zona(),
            'tendencias': self._calcular_tendencias()
        }
        
        serializer = DashboardSeguridadSerializer(data)
        return Response(serializer.data)
    
    def _eventos_por_severidad(self) -> Dict[str, int]:
        """Calcular eventos por severidad"""
        hoy = timezone.now().date()
        return dict(
            EventoSeguridad.objects.filter(fecha_hora__date=hoy)
            .values('severidad')
            .annotate(count=Count('id'))
            .values_list('severidad', 'count')
        )
    
    def _eventos_por_zona(self) -> list:
        """Calcular eventos por zona"""
        hoy = timezone.now().date()
        return list(
            EventoSeguridad.objects.filter(fecha_hora__date=hoy)
            .values('camara__zona__nombre')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
    
    def _calcular_tendencias(self) -> Dict[str, Any]:
        """Calcular tendencias de eventos"""
        hoy = timezone.now().date()
        hace_7_dias = hoy - timedelta(days=7)
        hace_14_dias = hoy - timedelta(days=14)
        
        eventos_semana_actual = EventoSeguridad.objects.filter(
            fecha_hora__date__gte=hace_7_dias
        ).count()
        
        eventos_semana_anterior = EventoSeguridad.objects.filter(
            fecha_hora__date__gte=hace_14_dias,
            fecha_hora__date__lt=hace_7_dias
        ).count()
        
        if eventos_semana_anterior > 0:
            cambio_porcentual = ((eventos_semana_actual - eventos_semana_anterior) / eventos_semana_anterior) * 100
        else:
            cambio_porcentual = 100 if eventos_semana_actual > 0 else 0
        
        return {
            'eventos_semana_actual': eventos_semana_actual,
            'eventos_semana_anterior': eventos_semana_anterior,
            'cambio_porcentual': round(cambio_porcentual, 2),
            'tendencia': 'subida' if cambio_porcentual > 0 else 'bajada' if cambio_porcentual < 0 else 'estable'
        }


class ReporteSeguridadViewSet(viewsets.ViewSet):
    """ViewSet para reportes de seguridad"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def eventos(self, request):
        """Reporte de eventos de seguridad"""
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        queryset = EventoSeguridad.objects.all()
        
        if fecha_desde:
            queryset = queryset.filter(fecha_hora__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_hora__date__lte=fecha_hasta)
        
        # Resumen
        total_eventos = queryset.count()
        eventos_revisados = queryset.filter(revisado=True).count()
        severidad_promedio = queryset.aggregate(Avg('severidad'))['severidad__avg'] or 0
        
        # Por tipo
        por_tipo = list(
            queryset.values('tipo_evento__nombre')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Por zona
        por_zona = list(
            queryset.values('camara__zona__nombre')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        data = {
            'periodo': {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta
            },
            'resumen': {
                'total_eventos': total_eventos,
                'eventos_revisados': eventos_revisados,
                'eventos_pendientes': total_eventos - eventos_revisados,
                'severidad_promedio': round(severidad_promedio, 2)
            },
            'por_tipo': por_tipo,
            'por_zona': por_zona
        }
        
        serializer = ReporteSeguridadSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def exportar(self, request):
        """Exportar reporte"""
        serializer = ExportarReporteSerializer(data=request.data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data or {}
            tipo_reporte = validated_data.get('tipo_reporte', 'eventos')  # type: ignore
            formato = validated_data.get('formato', 'json')  # type: ignore
            
            # Placeholder para exportación
            return Response({
                'message': 'Reporte generado exitosamente',
                'archivo': f"reporte_{tipo_reporte}.{formato}",
                'url_descarga': f"/api/security/reportes/descargar/123/"
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)