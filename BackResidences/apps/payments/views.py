from django.shortcuts import render
from rest_framework import viewsets
from .models import Pago, Deuda
from .serializers import PagoSerializer, DeudaSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class DeudaViewSet(viewsets.ModelViewSet):
    queryset = Deuda.objects.all()
    serializer_class = DeudaSerializer