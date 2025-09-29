from rest_framework import serializers
from .models import Pago, Deuda, DetalleDeuda

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

class DeudaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deuda
        fields = '__all__'

class DetalleDeudaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleDeuda
        fields = '__all__'