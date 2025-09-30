from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # =================== RUTAS PARA ANUNCIOS/AVISOS ===================
    
    # Gestión de anuncios
    path('anuncios/', views.AvisoListView.as_view(), name='anuncios-list'),
    path('anuncios/crear/', views.AvisoCreateView.as_view(), name='anuncios-create'),
    path('anuncios/<int:pk>/', views.AvisoDetailView.as_view(), name='anuncios-detail'),
    path('anuncios/<int:pk>/editar/', views.AvisoUpdateView.as_view(), name='anuncios-update'),
    
    # =================== RUTAS PARA REPORTES ===================
    
    # Gestión de reportes
    path('reportes/', views.ReporteListView.as_view(), name='reportes-list'),
    path('reportes/crear/', views.ReporteCreateView.as_view(), name='reportes-create'),
    
    # =================== RUTAS PARA DASHBOARD Y ESTADÍSTICAS ===================
    
    # Dashboard principal
    path('dashboard/', views.DashboardCommunicationsView.as_view(), name='dashboard'),
    
    # Estadísticas y reportes
    path('estadisticas/efectividad/', views.estadisticas_efectividad, name='estadisticas-efectividad'),
    
    # =================== RUTAS PARA CONFIGURACIÓN ===================
    
    # Configuración del sistema
    path('configuracion/', views.configuracion_comunicaciones, name='configuracion'),
]