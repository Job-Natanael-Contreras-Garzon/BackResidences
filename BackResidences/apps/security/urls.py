from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventoSeguridadViewSet)
router.register(r'event-types', views.TipoEventoViewSet)
router.register(r'vehicles', views.VehiculoAutorizadoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]