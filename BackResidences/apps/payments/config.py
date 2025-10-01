"""
Configuración para integración con Stripe
Variables de entorno y configuraciones específicas
"""

# Configuración de Stripe
STRIPE_SETTINGS = {
    'TEST_MODE': True,  # Cambiar a False en producción
    'PUBLISHABLE_KEY': {
        'test': 'pk_test_51...',  # Clave pública de prueba
        'live': 'pk_live_51...'   # Clave pública de producción
    },
    'SECRET_KEY': {
        'test': 'sk_test_51...',  # Clave secreta de prueba
        'live': 'sk_live_51...'   # Clave secreta de producción
    },
    'WEBHOOK_SECRET': {
        'test': 'whsec_test_...',  # Webhook secret de prueba
        'live': 'whsec_live_...'   # Webhook secret de producción
    },
    'CURRENCY': 'cop',  # Moneda por defecto
    'COUNTRY': 'CO',    # País
    'PAYMENT_METHODS': [
        'card',
        'pse',  # PSE para Colombia
    ],
    'MIN_AMOUNT': 100,  # Monto mínimo en centavos (1 COP)
    'MAX_AMOUNT': 50000000,  # Monto máximo en centavos (500,000 COP)
}

# URLs de redirección
STRIPE_REDIRECT_URLS = {
    'success': '/payments/success/',
    'cancel': '/payments/cancel/',
    'webhook': '/api/payments/stripe/webhook/',
}

# Configuración de métodos de pago específicos para Colombia
PAYMENT_METHODS_CONFIG = {
    'stripe': {
        'name': 'Stripe',
        'code': 'stripe',
        'description': 'Pagos en línea con tarjeta de crédito/débito',
        'requires_reference': False,
        'requires_receipt': False,
        'commission_percentage': 3.4,  # Comisión típica de Stripe en Colombia
        'active': True,
        'configuration': {
            'provider': 'stripe',
            'payment_methods': ['card'],
            'automatic_capture': True,
            'statement_descriptor': 'CONDOMINIO',
        }
    },
    'pse_stripe': {
        'name': 'PSE',
        'code': 'pse_stripe',
        'description': 'Pagos Seguros en Línea (PSE)',
        'requires_reference': False,
        'requires_receipt': False,
        'commission_percentage': 2.5,
        'active': True,
        'configuration': {
            'provider': 'stripe',
            'payment_methods': ['pse'],
            'automatic_capture': True,
            'statement_descriptor': 'CONDOMINIO PSE',
        }
    },
    'transferencia': {
        'name': 'Transferencia Bancaria',
        'code': 'transferencia',
        'description': 'Transferencia a cuenta bancaria del condominio',
        'requires_reference': True,
        'requires_receipt': True,
        'commission_percentage': 0.0,
        'active': True,
        'configuration': {
            'banco': 'Banco de Bogotá',
            'numero_cuenta': '123456789',
            'tipo_cuenta': 'Ahorros',
            'titular': 'Conjunto Residencial',
            'nit': '900123456-1'
        }
    },
    'efectivo': {
        'name': 'Efectivo',
        'code': 'efectivo',
        'description': 'Pago en efectivo en administración',
        'requires_reference': False,
        'requires_receipt': True,
        'commission_percentage': 0.0,
        'active': True,
        'configuration': {
            'horarios': 'L-V 8:00-18:00, S 8:00-12:00',
            'ubicacion': 'Oficina de administración'
        }
    }
}

# Configuración de notificaciones
PAYMENT_NOTIFICATIONS = {
    'email': {
        'payment_confirmed': {
            'subject': 'Pago confirmado - Factura #{numero_factura}',
            'template': 'payments/emails/payment_confirmed.html'
        },
        'payment_failed': {
            'subject': 'Error en pago - Factura #{numero_factura}',
            'template': 'payments/emails/payment_failed.html'
        },
        'invoice_generated': {
            'subject': 'Nueva factura generada - #{numero_factura}',
            'template': 'payments/emails/invoice_generated.html'
        },
        'payment_reminder': {
            'subject': 'Recordatorio de pago - Factura #{numero_factura}',
            'template': 'payments/emails/payment_reminder.html'
        }
    },
    'sms': {
        'payment_confirmed': 'Su pago de ${monto} ha sido confirmado. Ref: {numero_pago}',
        'payment_failed': 'Su pago no pudo procesarse. Contacte administración.',
        'payment_reminder': 'Recordatorio: Factura #{numero_factura} vence {fecha_vencimiento}'
    }
}

# Configuración de reportes
REPORTS_CONFIG = {
    'dashboard_cache_minutes': 30,
    'export_formats': ['pdf', 'excel', 'csv'],
    'max_export_records': 10000,
    'morosidad_ranges': [
        {'name': '1-30 días', 'min_days': 1, 'max_days': 30},
        {'name': '31-60 días', 'min_days': 31, 'max_days': 60},
        {'name': '61-90 días', 'min_days': 61, 'max_days': 90},
        {'name': 'Más de 90 días', 'min_days': 91, 'max_days': 9999},
    ]
}

# Configuración de facturación
BILLING_CONFIG = {
    'auto_generate_invoice_number': True,
    'invoice_number_format': 'FAC-{year}-{month}-{sequence:06d}',
    'payment_number_format': 'PAG-{year}-{sequence:06d}',
    'paz_y_salvo_number_format': 'PYS-{year}-{sequence:06d}',
    'default_due_days': 15,
    'late_fee_percentage': 2.0,  # Porcentaje mensual de interés moratorio
    'grace_period_days': 3,      # Días de gracia antes de aplicar intereses
    'auto_calculate_interest': True,
    'bulk_billing_batch_size': 50,  # Procesar facturas en lotes
}

# Configuración de seguridad
SECURITY_CONFIG = {
    'max_payment_attempts': 3,
    'payment_session_timeout_minutes': 30,
    'require_admin_approval_over_amount': 1000000,  # 10,000 COP
    'audit_all_payments': True,
    'encrypt_payment_data': True,
    'webhook_signature_verification': True,
}

# Configuración de archivos
FILE_CONFIG = {
    'receipt_storage_path': 'receipts/{year}/{month}/',
    'invoice_storage_path': 'invoices/{year}/{month}/',
    'paz_y_salvo_storage_path': 'paz-y-salvo/{year}/',
    'max_file_size_mb': 10,
    'allowed_file_types': ['pdf', 'jpg', 'jpeg', 'png'],
    'auto_generate_pdf': True,
}