from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Vista para redireccionar la raíz a la documentación
def redirect_to_docs(request):
    return redirect('/docs/')

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="BackResidences API",
        default_version='v1',
        description="""
        API para el sistema de gestión de residencias BackResidences
        
        ## Características principales:
        - 🔐 Autenticación JWT
        - 👥 Gestión de usuarios y roles
        - 🏠 Gestión de residencias y viviendas
        - �‍👩‍👧‍👦 Control de personas autorizadas
        - 🐕 Registro de mascotas
        - �💰 Sistema de pagos
        - 🔒 Control de acceso
        - 🏊 Gestión de áreas comunes
        - 📊 Dashboard y reportes
        
        ## Autenticación:
        Esta API utiliza JWT (JSON Web Tokens) para la autenticación.
        
        1. Registrarse en `/api/v1/auth/register/`
        2. Hacer login en `/api/v1/auth/login/` para obtener tokens
        3. Usar el token de acceso en el header: `Authorization: Bearer <token>`
        
        ## Módulos disponibles:
        
        ### 🔐 Autenticación (`/api/v1/auth/`)
        - Registro y login de usuarios
        - Gestión de perfiles
        - Control de roles y permisos
        - Actividad de usuarios
        
        ### 🏠 Residencias (`/api/v1/residences/`)
        - Gestión de viviendas y apartamentos
        - Asignación de propietarios e inquilinos
        - Control de personas autorizadas
        - Registro de mascotas
        - Dashboard con estadísticas
        - Búsqueda de residentes
        
        ### 🏊 Áreas Comunes (`/api/v1/common-areas/`)
        - Gestión de áreas comunes del condominio
        - Sistema de reservas con validación de conflictos
        - Consulta de disponibilidad en tiempo real
        - Dashboard con estadísticas de uso
        - Control de horarios y tarifas
        - Gestión de pagos y depósitos
        
        ### 📞 Comunicaciones (`/api/v1/communications/`)
        - Sistema de anuncios y notificaciones
        - Gestión de reportes y solicitudes
        - Dashboard con estadísticas de efectividad
        - Control de visualizaciones y engagement
        - Configuración de tipos de reportes
        - Seguimiento de tiempos de respuesta
        
        ### 🔧 Mantenimiento (`/api/v1/maintenance/`)
        - Gestión completa de solicitudes de mantenimiento
        - Sistema de órdenes de trabajo y asignación
        - Control de proveedores y servicios
        - Inventario de materiales y herramientas
        - Mantenimiento preventivo programado
        - Dashboard con estadísticas y KPIs
        
        ### 📋 Endpoints principales:
        - `/api/v1/auth/` - Autenticación y gestión de usuarios
        - `/api/v1/residences/` - Gestión completa de residencias
        - `/api/v1/common-areas/` - Sistema completo de áreas comunes
        - `/api/v1/communications/` - Sistema completo de comunicaciones
        - `/api/v1/maintenance/` - Sistema completo de mantenimiento
        - `/docs/` - Esta documentación
        - `/admin/` - Panel de administración Django
        """,
        terms_of_service="https://www.backresidences.com/terms/",
        contact=openapi.Contact(email="admin@backresidences.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # =================== PÁGINA PRINCIPAL ===================
    path('', redirect_to_docs, name='home'),
    
    # =================== ADMINISTRACIÓN ===================
    path('admin/', admin.site.urls),
    
    # =================== API DOCUMENTATION ===================
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    
    # =================== API ENDPOINTS ===================
    path('api/v1/auth/', include(('apps.authentication.urls', 'auth'), namespace='api_auth')),
    path('api/v1/residences/', include(('apps.residences.urls', 'residences'), namespace='api_residences')),
    path('api/v1/common-areas/', include(('apps.common_areas.urls', 'common_areas'), namespace='api_common_areas')),
    path('api/v1/communications/', include(('apps.communications.urls', 'communications'), namespace='api_communications')),
    path('api/v1/maintenance/', include(('apps.maintenance.urls', 'maintenance'), namespace='api_maintenance')),
    
    # Mantener la ruta original para compatibilidad
    path('auth/', include('apps.authentication.urls')),
    
    # path('api/v1/security/', include('apps.security.urls')),
    # path('api/v1/payments/', include('apps.payments.urls'));
]