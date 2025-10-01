from django.shortcuts import render
from rest_framework import viewsets
from .models import EventoSeguridad, TipoEvento, VehiculoAutorizado
from apps.authentication.models import User as Usuario
from .serializers import EventoSeguridadSerializer, TipoEventoSerializer, VehiculoAutorizadoSerializer

class EventoSeguridadViewSet(viewsets.ModelViewSet):
    queryset = EventoSeguridad.objects.all()
    serializer_class = EventoSeguridadSerializer

class TipoEventoViewSet(viewsets.ModelViewSet):
    queryset = TipoEvento.objects.all()
    serializer_class = TipoEventoSerializer

class VehiculoAutorizadoViewSet(viewsets.ModelViewSet):
    queryset = VehiculoAutorizado.objects.all()
    serializer_class = VehiculoAutorizadoSerializer