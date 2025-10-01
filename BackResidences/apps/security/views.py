from django.shortcuts import render
from rest_framework import viewsets
from .models import EventoSeguridad, TipoEvento, VehiculoAutorizado, Usuario
from .serializers import EventoSeguridadSerializer, TipoEventoSerializer, VehiculoAutorizadoSerializer, UsuarioSerializer

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
    queryset = VehiculoAutorizado.objects.all()
    serializer_class = VehiculoAutorizadoSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer