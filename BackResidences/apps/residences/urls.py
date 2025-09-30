from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Vistas de viviendas
    ViviendaListView, ViviendaCreateView, ViviendaDetailView, 
    ViviendaUpdateView, AssignResidentView, ViviendasDisponiblesView,
    
    # Vistas de personas autorizadas
    PersonaAutorizadaListView, PersonaAutorizadaCreateView,
    RenovarAutorizacionView, RevocarAutorizacionView,
    
    # Vistas de mascotas
    MascotaListView, MascotaCreateView, MascotaUpdateView,
    
    # Vistas de dashboard y reportes
    DashboardView,
    
    # Vistas de búsqueda
    SearchResidentesView
)

# URLs para el módulo de residencias
urlpatterns = [
    # =================== ENDPOINTS DE VIVIENDAS ===================
    path('viviendas/', ViviendaListView.as_view(), name='vivienda-list'),
    path('viviendas/crear/', ViviendaCreateView.as_view(), name='vivienda-create'),
    path('viviendas/disponibles/', ViviendasDisponiblesView.as_view(), name='viviendas-disponibles'),
    path('viviendas/<int:pk>/', ViviendaDetailView.as_view(), name='vivienda-detail'),
    path('viviendas/<int:pk>/actualizar/', ViviendaUpdateView.as_view(), name='vivienda-update'),
    path('viviendas/<int:vivienda_id>/asignar-residente/', AssignResidentView.as_view(), name='assign-resident'),
    
    # =================== ENDPOINTS DE PERSONAS AUTORIZADAS ===================
    path('personas-autorizadas/', PersonaAutorizadaListView.as_view(), name='persona-autorizada-list'),
    path('personas-autorizadas/crear/', PersonaAutorizadaCreateView.as_view(), name='persona-autorizada-create'),
    path('personas-autorizadas/<int:persona_id>/renovar/', RenovarAutorizacionView.as_view(), name='renovar-autorizacion'),
    path('personas-autorizadas/<int:persona_id>/revocar/', RevocarAutorizacionView.as_view(), name='revocar-autorizacion'),
    
    # =================== ENDPOINTS DE MASCOTAS ===================
    path('mascotas/', MascotaListView.as_view(), name='mascota-list'),
    path('mascotas/registrar/', MascotaCreateView.as_view(), name='mascota-create'),
    path('mascotas/<int:pk>/actualizar/', MascotaUpdateView.as_view(), name='mascota-update'),
    
    # =================== ENDPOINTS DE DASHBOARD Y REPORTES ===================
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # =================== ENDPOINTS DE BÚSQUEDA ===================
    path('buscar/residentes/', SearchResidentesView.as_view(), name='search-residentes'),
]

# Patrón de URLs para incluir en el proyecto principal
app_name = 'residences'