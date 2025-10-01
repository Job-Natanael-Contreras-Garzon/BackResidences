from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # =================== RUTAS PARA CATEGORÍAS ===================
    
    # Categorías de mantenimiento
    path('categorias/', views.CategoriaMantenimientoListView.as_view(), name='categorias-list'),
    
    # =================== RUTAS PARA PROVEEDORES ===================
    
    # Gestión de proveedores
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedores-list'),
    path('proveedores/<int:pk>/', views.ProveedorDetailView.as_view(), name='proveedores-detail'),
    
    # =================== RUTAS PARA SOLICITUDES DE MANTENIMIENTO ===================
    
    # Gestión de solicitudes
    path('solicitudes/', views.SolicitudMantenimientoListView.as_view(), name='solicitudes-list'),
    path('solicitudes/crear/', views.SolicitudMantenimientoCreateView.as_view(), name='solicitudes-create'),
    path('solicitudes/<int:pk>/', views.SolicitudMantenimientoDetailView.as_view(), name='solicitudes-detail'),
    path('solicitudes/<int:pk>/actualizar/', views.SolicitudMantenimientoUpdateView.as_view(), name='solicitudes-update'),
    
    # =================== RUTAS PARA ÓRDENES DE TRABAJO ===================
    
    # Gestión de órdenes de trabajo
    path('ordenes-trabajo/', views.OrdenTrabajoListView.as_view(), name='ordenes-trabajo-list'),
    path('ordenes-trabajo/<int:pk>/', views.OrdenTrabajoDetailView.as_view(), name='ordenes-trabajo-detail'),
    
    # =================== RUTAS PARA DASHBOARD Y ESTADÍSTICAS ===================
    
    # Dashboard principal
    path('dashboard/', views.DashboardMantenimientoView.as_view(), name='dashboard'),
    
    # =================== RUTAS PARA CONFIGURACIÓN ===================
    
    # Configuración del sistema
    path('configuracion/', views.configuracion_mantenimiento, name='configuracion'),
]