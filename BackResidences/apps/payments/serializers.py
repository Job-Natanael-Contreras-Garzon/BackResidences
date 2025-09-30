from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from apps.authentication.models import User
from apps.residences.models import Vivienda
from .models import (
    ConceptoPago, MetodoPago, Factura, Pago, PagoFactura, PazYSalvo,
    TipoPago, Deuda, DetalleDeuda
)


# ================== SERIALIZERS PRINCIPALES ==================

class ConceptoPagoListSerializer(serializers.ModelSerializer):
    """Serializer para listar conceptos de pago"""
    total_facturas_generadas = serializers.ReadOnlyField()
    total_recaudado = serializers.ReadOnlyField()
    
    class Meta:
        model = ConceptoPago
        fields = [
            'id', 'nombre', 'descripcion', 'tipo', 'valor_base', 
            'es_obligatorio', 'frecuencia', 'aplica_a_todos',
            'fecha_creacion', 'activo', 'total_facturas_generadas', 
            'total_recaudado'
        ]


class ConceptoPagoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para conceptos de pago"""
    total_facturas_generadas = serializers.ReadOnlyField()
    total_recaudado = serializers.ReadOnlyField()
    
    class Meta:
        model = ConceptoPago
        fields = '__all__'


class ConceptoPagoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear conceptos de pago"""
    
    class Meta:
        model = ConceptoPago
        fields = [
            'nombre', 'descripcion', 'tipo', 'valor_base', 
            'es_obligatorio', 'frecuencia', 'aplica_a_todos',
            'fecha_inicio', 'fecha_fin', 'criterios_aplicacion',
            'porcentaje_interes_mora'
        ]
        
    def validate_valor_base(self, value):
        """Validar que el valor base sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El valor base debe ser mayor a 0")
        return value


class MetodoPagoSerializer(serializers.ModelSerializer):
    """Serializer para métodos de pago"""
    
    class Meta:
        model = MetodoPago
        fields = '__all__'


# ================== FACTURAS ==================

class ViviendaBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para vivienda en facturas"""
    propietario = serializers.CharField(source='usuario_propietario.get_full_name', read_only=True)
    
    class Meta:
        model = Vivienda
        fields = ['id', 'identificador', 'bloque', 'propietario']


class ConceptoPagoBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para concepto en facturas"""
    
    class Meta:
        model = ConceptoPago
        fields = ['id', 'nombre', 'descripcion']


class FacturaListSerializer(serializers.ModelSerializer):
    """Serializer para listar facturas"""
    vivienda = ViviendaBasicSerializer(read_only=True)
    concepto = ConceptoPagoBasicSerializer(read_only=True)
    dias_vencido = serializers.ReadOnlyField()
    tiene_descuentos = serializers.ReadOnlyField()
    tiene_intereses = serializers.ReadOnlyField()
    
    class Meta:
        model = Factura
        fields = [
            'id', 'numero_factura', 'vivienda', 'concepto', 'periodo',
            'fecha_generacion', 'fecha_vencimiento', 'monto_total', 'estado',
            'dias_vencido', 'saldo_pendiente', 'tiene_descuentos', 'tiene_intereses'
        ]


class FacturaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para facturas"""
    vivienda = ViviendaBasicSerializer(read_only=True)
    concepto = ConceptoPagoBasicSerializer(read_only=True)
    dias_vencido = serializers.ReadOnlyField()
    tiene_descuentos = serializers.ReadOnlyField()
    tiene_intereses = serializers.ReadOnlyField()
    generada_por_nombre = serializers.CharField(source='generada_por.get_full_name', read_only=True)
    
    class Meta:
        model = Factura
        fields = '__all__'


class FacturaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear facturas"""
    
    class Meta:
        model = Factura
        fields = [
            'vivienda', 'concepto', 'periodo', 'fecha_vencimiento',
            'monto_original', 'descuentos', 'observaciones'
        ]
        
    def validate(self, data):
        """Validaciones generales"""
        # Verificar que no exista factura duplicada
        if Factura.objects.filter(
            vivienda=data['vivienda'],
            concepto=data['concepto'],
            periodo=data['periodo']
        ).exists():
            raise serializers.ValidationError(
                "Ya existe una factura para esta vivienda, concepto y período"
            )
        return data


# ================== PAGOS ==================

class PagoListSerializer(serializers.ModelSerializer):
    """Serializer para listar pagos"""
    vivienda = ViviendaBasicSerializer(read_only=True)
    metodo_pago_nombre = serializers.CharField(source='metodo_pago.nombre', read_only=True)
    registrado_por_nombre = serializers.CharField(source='registrado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id', 'numero_pago', 'vivienda', 'monto_total', 'metodo_pago_nombre',
            'fecha_pago', 'estado', 'numero_referencia', 'registrado_por_nombre'
        ]


class PagoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para pagos"""
    vivienda = ViviendaBasicSerializer(read_only=True)
    metodo_pago = MetodoPagoSerializer(read_only=True)
    registrado_por_nombre = serializers.CharField(source='registrado_por.get_full_name', read_only=True)
    confirmado_por_nombre = serializers.CharField(source='confirmado_por.get_full_name', read_only=True)
    reversado_por_nombre = serializers.CharField(source='reversado_por.get_full_name', read_only=True)
    facturas_aplicadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = '__all__'
        
    def get_facturas_aplicadas(self, obj):
        """Obtener facturas donde se aplicó este pago"""
        aplicaciones = PagoFactura.objects.filter(pago=obj)
        return [{
            'factura_id': app.factura.id,
            'numero_factura': app.factura.numero_factura,
            'monto_aplicado': str(app.monto_aplicado),
            'fecha_aplicacion': app.fecha_aplicacion
        } for app in aplicaciones]


class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos"""
    facturas = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    distribuciones = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    # Campos para integración con Stripe
    stripe_payment_intent_id = serializers.CharField(required=False, allow_blank=True)
    stripe_charge_id = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Pago
        fields = [
            'vivienda', 'monto_total', 'metodo_pago', 'numero_referencia',
            'fecha_pago', 'observaciones', 'archivo_comprobante',
            'facturas', 'distribuciones', 'stripe_payment_intent_id',
            'stripe_charge_id'
        ]
        
    def validate(self, data):
        """Validaciones del pago"""
        if data['monto_total'] <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
            
        # Si se especifican facturas, validar que existan y pertenezcan a la vivienda
        if 'facturas' in data:
            facturas = Factura.objects.filter(
                id__in=data['facturas'],
                vivienda=data['vivienda']
            )
            if facturas.count() != len(data['facturas']):
                raise serializers.ValidationError("Algunas facturas no existen o no pertenecen a la vivienda")
                
        return data
        
    def create(self, validated_data):
        """Crear pago y aplicar a facturas"""
        facturas_ids = validated_data.pop('facturas', [])
        distribuciones = validated_data.pop('distribuciones', [])
        stripe_payment_intent_id = validated_data.pop('stripe_payment_intent_id', '')
        stripe_charge_id = validated_data.pop('stripe_charge_id', '')
        
        # Agregar usuario que registra
        validated_data['registrado_por'] = self.context['request'].user
        
        # Generar número de pago único
        ultimo_numero = Pago.objects.filter(
            numero_pago__startswith=f'PAG-{timezone.now().year}-'
        ).count() + 1
        validated_data['numero_pago'] = f'PAG-{timezone.now().year}-{ultimo_numero:06d}'
        
        # Crear pago
        pago = Pago.objects.create(**validated_data)
        
        # Si hay distribuciones específicas, usarlas
        if distribuciones:
            for dist in distribuciones:
                PagoFactura.objects.create(
                    pago=pago,
                    factura_id=dist['factura_id'],
                    monto_aplicado=Decimal(str(dist['monto']))
                )
        # Si no, aplicar automáticamente a facturas pendientes
        elif facturas_ids:
            facturas = Factura.objects.filter(id__in=facturas_ids).order_by('fecha_vencimiento')
            monto_restante = pago.monto_total
            
            for factura in facturas:
                if monto_restante <= 0:
                    break
                    
                monto_aplicar = min(monto_restante, factura.saldo_pendiente)
                if monto_aplicar > 0:
                    PagoFactura.objects.create(
                        pago=pago,
                        factura=factura,
                        monto_aplicado=monto_aplicar
                    )
                    monto_restante -= monto_aplicar
        
        return pago


# ================== PAZ Y SALVO ==================

class PazYSalvoSerializer(serializers.ModelSerializer):
    """Serializer para paz y salvo"""
    vivienda = ViviendaBasicSerializer(read_only=True)
    generado_por_nombre = serializers.CharField(source='generado_por.get_full_name', read_only=True)
    es_valido = serializers.ReadOnlyField()
    
    class Meta:
        model = PazYSalvo
        fields = '__all__'


class PazYSalvoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear paz y salvo"""
    
    class Meta:
        model = PazYSalvo
        fields = ['fecha_corte', 'observaciones']
        
    def create(self, validated_data):
        """Crear paz y salvo"""
        vivienda_id = self.context['vivienda_id']
        vivienda = Vivienda.objects.get(id=vivienda_id)
        
        # Calcular saldo pendiente
        facturas_pendientes = Factura.objects.filter(
            vivienda=vivienda,
            fecha_generacion__lte=validated_data['fecha_corte']
        ).exclude(estado='pagada')
        
        saldo_pendiente = sum(f.saldo_pendiente for f in facturas_pendientes)
        
        # Generar número de documento
        ultimo_numero = PazYSalvo.objects.filter(
            numero_documento__startswith=f'PYS-{timezone.now().year}-'
        ).count() + 1
        numero_documento = f'PYS-{timezone.now().year}-{ultimo_numero:06d}'
        
        # Generar código de verificación
        import hashlib
        codigo_verificacion = hashlib.md5(
            f"{numero_documento}-{vivienda.id}-{timezone.now()}".encode()
        ).hexdigest()[:12].upper()
        
        validated_data.update({
            'vivienda': vivienda,
            'numero_documento': numero_documento,
            'saldo_pendiente': saldo_pendiente,
            'codigo_verificacion': codigo_verificacion,
            'generado_por': self.context['request'].user
        })
        
        return PazYSalvo.objects.create(**validated_data)


# ================== MODELOS LEGACY (COMPATIBILIDAD) ==================

class TipoPagoSerializer(serializers.ModelSerializer):
    """Serializer para tipos de pago (legacy)"""
    
    class Meta:
        model = TipoPago
        fields = '__all__'


class DeudaSerializer(serializers.ModelSerializer):
    """Serializer para deudas (legacy)"""
    
    class Meta:
        model = Deuda
        fields = '__all__'


class DetalleDeudaSerializer(serializers.ModelSerializer):
    """Serializer para detalles de deuda (legacy)"""
    
    class Meta:
        model = DetalleDeuda
        fields = '__all__'


# ================== SERIALIZERS PARA REPORTES ==================

class DashboardFinancieroSerializer(serializers.Serializer):
    """Serializer para dashboard financiero"""
    periodo = serializers.CharField()
    total_facturado = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_recaudado = serializers.DecimalField(max_digits=15, decimal_places=2)
    pendiente_cobro = serializers.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_recaudo = serializers.DecimalField(max_digits=5, decimal_places=2)
    facturas_generadas = serializers.IntegerField()
    facturas_pagadas = serializers.IntegerField()
    facturas_vencidas = serializers.IntegerField()
    pagos_procesados = serializers.IntegerField()


class EstadoCuentaSerializer(serializers.Serializer):
    """Serializer para estado de cuenta"""
    vivienda = ViviendaBasicSerializer()
    saldo_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    facturas_pendientes = serializers.IntegerField()
    facturas_vencidas = serializers.IntegerField()
    ultimo_pago = serializers.DateTimeField(allow_null=True)
    total_pagado_ano = serializers.DecimalField(max_digits=15, decimal_places=2)


# ================== SERIALIZERS PARA STRIPE ==================

class StripePaymentIntentSerializer(serializers.Serializer):
    """Serializer para crear PaymentIntent de Stripe"""
    amount = serializers.IntegerField(help_text="Monto en centavos")
    currency = serializers.CharField(default='cop')
    facturas = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    metadata = serializers.DictField(required=False)
    
    def validate_amount(self, value):
        if value < 50:  # Mínimo de Stripe
            raise serializers.ValidationError("El monto mínimo es 50 centavos")
        return value


class StripeWebhookSerializer(serializers.Serializer):
    """Serializer para webhooks de Stripe"""
    type = serializers.CharField()
    data = serializers.DictField()
    livemode = serializers.BooleanField()
    created = serializers.IntegerField()