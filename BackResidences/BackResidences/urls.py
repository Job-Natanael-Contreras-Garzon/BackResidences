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
        - 🏠 Gestión de residencias
        - 💰 Sistema de pagos
        - 🔒 Control de acceso
        - 🏊 Gestión de áreas comunes
        
        ## Autenticación:
        Esta API utiliza JWT (JSON Web Tokens) para la autenticación.
        
        1. Registrarse en `/api/v1/auth/register/`
        2. Hacer login en `/api/v1/auth/login/` para obtener tokens
        3. Usar el token de acceso en el header: `Authorization: Bearer <token>`
        
        ## Endpoints principales:
        - `/api/v1/auth/` - Autenticación y gestión de usuarios
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
    
    # Mantener la ruta original para compatibilidad
    path('auth/', include('apps.authentication.urls')),
    
    # path('api/v1/security/', include('apps.security.urls')),
    # path('api/v1/residences/', include('apps.residences.urls')),
    # path('api/v1/payments/', include('apps.payments.urls')),
    # path('api/v1/common-areas/', include('apps.common_areas.urls')),
]