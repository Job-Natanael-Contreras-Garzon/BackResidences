from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets (si los usáramos en el futuro)
router = DefaultRouter()

# URLs específicas para áreas comunes
urlpatterns = [
    # =================== GESTIÓN DE ÁREAS COMUNES ===================
    
    # Listar todas las áreas comunes
    path('areas/', views.AreaComunListView.as_view(), name='areas-list'),
    
    # Detalles de área común específica
    path('areas/<int:pk>/', views.AreaComunDetailView.as_view(), name='area-detail'),
    
    # Crear nueva área común (solo administradores)
    path('areas/crear/', views.AreaComunCreateView.as_view(), name='area-create'),
    
    # Actualizar área común (solo administradores)
    path('areas/<int:pk>/actualizar/', views.AreaComunUpdateView.as_view(), name='area-update'),
    
    # Consultar disponibilidad de área común
    path('areas/<int:area_id>/disponibilidad/', views.ConsultarDisponibilidadView.as_view(), name='area-disponibilidad'),
    
    # =================== GESTIÓN DE RESERVAS ===================
    
    # Listar reservas (propias o todas si es admin)
    path('reservas/', views.ReservaListView.as_view(), name='reservas-list'),
    
    # Crear nueva reserva
    path('reservas/crear/', views.ReservaCreateView.as_view(), name='reserva-create'),
    
    # Detalles de reserva específica
    path('reservas/<int:pk>/', views.ReservaDetailView.as_view(), name='reserva-detail'),
    
    # Cancelar reserva
    path('reservas/<int:reserva_id>/cancelar/', views.CancelarReservaView.as_view(), name='reserva-cancelar'),
    
    # =================== GESTIÓN DE HORARIOS ===================
    
    # Horarios de un área específica
    path('areas/<int:area_id>/horarios/', views.HorarioAreaListView.as_view(), name='area-horarios'),
    
    # =================== DASHBOARD Y ESTADÍSTICAS ===================
    
    # Dashboard principal
    path('dashboard/', views.DashboardAreasView.as_view(), name='dashboard'),
    
    # Configuración del sistema
    path('configuracion/', views.configuracion_sistema, name='configuracion'),
    
    # Estadísticas de uso
    path('estadisticas/', views.estadisticas_uso, name='estadisticas'),
    
    # =================== RUTAS DEL ROUTER ===================
    
    # Incluir rutas del router (para futuros ViewSets)
    path('', include(router.urls)),
]

# Agregar nombres de app para namespace
app_name = 'common_areas'