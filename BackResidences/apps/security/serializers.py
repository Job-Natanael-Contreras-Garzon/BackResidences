from rest_framework import serializers
from .models import TipoEvento, EventoSeguridad, VehiculoAutorizado, CredentialAcceso, Camara, Zona

class TipoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEvento
        fields = '__all__'

class EventoSeguridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoSeguridad
        fields = '__all__'

class VehiculoAutorizadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculoAutorizado
        fields = '__all__'

class CredentialAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialAcceso
        fields = '__all__'

class CamaraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camara
        fields = '__all__'

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = '__all__'