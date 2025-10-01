from django.urls import path
from . import views

urlpatterns = [
    # Define your security-related URL patterns here
    path('eventos/', views.EventoListView.as_view(), name='evento-list'),
    path('eventos/<int:pk>/', views.EventoDetailView.as_view(), name='evento-detail'),
    path('vehiculos-autorizados/', views.VehiculoAutorizadoListView.as_view(), name='vehiculo-autorizado-list'),
    path('vehiculos-autorizados/<int:pk>/', views.VehiculoAutorizadoDetailView.as_view(), name='vehiculo-autorizado-detail'),
    path('credenciales-acceso/', views.CredentialAccesoListView.as_view(), name='credential-acceso-list'),
    path('credenciales-acceso/<int:pk>/', views.CredentialAccesoDetailView.as_view(), name='credential-acceso-detail'),
]