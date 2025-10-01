"""
URLs para el módulo de pagos
Configuración completa de rutas según API specification
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConceptoPagoViewSet,
    MetodoPagoViewSet,
    FacturaViewSet,
    PagoViewSet,
    PazYSalvoViewSet,
    ReportesFinancierosViewSet,
    StripeViewSet,
    # Legacy
    TipoPagoViewSet,
    DeudaViewSet,
    DetalleDeudaViewSet
)

# Router principal
router = DefaultRouter()

# Endpoints principales
router.register(r'conceptos', ConceptoPagoViewSet, basename='conceptos')
router.register(r'metodos-pago', MetodoPagoViewSet, basename='metodos-pago')
router.register(r'facturas', FacturaViewSet, basename='facturas')
router.register(r'pagos', PagoViewSet, basename='pagos')
router.register(r'paz-y-salvo', PazYSalvoViewSet, basename='paz-y-salvo')

# Reportes
router.register(r'reportes', ReportesFinancierosViewSet, basename='reportes')

# Integración Stripe
router.register(r'stripe', StripeViewSet, basename='stripe')

# Legacy endpoints (compatibilidad)
router.register(r'legacy/tipos-pago', TipoPagoViewSet, basename='legacy-tipos-pago')
router.register(r'legacy/deudas', DeudaViewSet, basename='legacy-deudas')
router.register(r'legacy/detalle-deudas', DetalleDeudaViewSet, basename='legacy-detalle-deudas')

# URLs del módulo
urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints específicos adicionales
urlpatterns += [
    # Generar paz y salvo para vivienda específica
    path('paz-y-salvo/<int:vivienda_id>/', 
         PazYSalvoViewSet.as_view({'post': 'generar_paz_y_salvo'}), 
         name='generar-paz-y-salvo'),
    
    # Estado de cuenta por vivienda
    path('reportes/estado-cuenta/<int:vivienda_id>/', 
         ReportesFinancierosViewSet.as_view({'get': 'estado_cuenta'}), 
         name='estado-cuenta-vivienda'),
]