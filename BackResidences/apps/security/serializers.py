from rest_framework import serializers
from .models import TIPO_EVENTO, EVENTO_SEGURIDAD, VEHICULO_AUTORIZADO, CREDENTIAL_ACCESO, USUARIO, ROL, USUARIO_ROL, REPORTE, PERSONA_AUTORIZADA, BITACORA, VIVIENDA, MASCOTA, AVISO, RESERVA, AREA_COMUN, DEUDA, MANTENIMIENTO, PAGO, DETALLE_DEUDA, CAMARA, ZONA

class TipoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TIPO_EVENTO
        fields = '__all__'

class EventoSeguridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EVENTO_SEGURIDAD
        fields = '__all__'

class VehiculoAutorizadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VEHICULO_AUTORIZADO
        fields = '__all__'

class CredentialAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CREDENTIAL_ACCESO
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = USUARIO
        fields = '__all__'

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = ROL
        fields = '__all__'

class UsuarioRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = USUARIO_ROL
        fields = '__all__'

class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = REPORTE
        fields = '__all__'

class PersonaAutorizadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PERSONA_AUTORIZADA
        fields = '__all__'

class BitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = BITACORA
        fields = '__all__'

class ViviendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VIVIENDA
        fields = '__all__'

class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MASCOTA
        fields = '__all__'

class AvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AVISO
        fields = '__all__'

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RESERVA
        fields = '__all__'

class AreaComunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AREA_COMUN
        fields = '__all__'

class DeudaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DEUDA
        fields = '__all__'

class MantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MANTENIMIENTO
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PAGO
        fields = '__all__'

class DetalleDeudaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DETALLE_DEUDA
        fields = '__all__'

class CamaraSerializer(serializers.ModelSerializer):
    class Meta:
        model = CAMARA
        fields = '__all__'

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZONA
        fields = '__all__'