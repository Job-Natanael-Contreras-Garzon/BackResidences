from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TipoEventoViewSet, ZonaViewSet, CamaraViewSet,
    VehiculoAutorizadoViewSet, EventoSeguridadViewSet, CredentialAccesoViewSet,
    DashboardSeguridadViewSet, ReporteSeguridadViewSet
)

# Configurar el router
router = DefaultRouter()

# Registrar ViewSets principales
router.register(r'tipos-evento', TipoEventoViewSet, basename='tipoevento')
router.register(r'zonas', ZonaViewSet, basename='zona')
router.register(r'camaras', CamaraViewSet, basename='camara')
router.register(r'vehiculos', VehiculoAutorizadoViewSet, basename='vehiculo')
router.register(r'eventos', EventoSeguridadViewSet, basename='evento')
router.register(r'credenciales', CredentialAccesoViewSet, basename='credencial')

# Registrar ViewSets de dashboard y reportes
router.register(r'dashboard', DashboardSeguridadViewSet, basename='dashboard')
router.register(r'reportes', ReporteSeguridadViewSet, basename='reporte')

# URLs del módulo
urlpatterns = [
    # APIs principales
    path('api/', include(router.urls)),
]

# Información del módulo
app_name = 'security'
