"""
Comando para inicializar datos de métodos de pago
"""
from django.core.management.base import BaseCommand
from apps.payments.models import MetodoPago, ConceptoPago
from apps.payments.config import PAYMENT_METHODS_CONFIG
from decimal import Decimal


class Command(BaseCommand):
    help = 'Inicializa métodos de pago y conceptos básicos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar recreación de métodos existentes'
        )
    
    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('Inicializando métodos de pago y conceptos...')
        )
        
        # Crear métodos de pago
        for method_code, config in PAYMENT_METHODS_CONFIG.items():
            metodo, created = MetodoPago.objects.get_or_create(
                codigo=method_code,
                defaults={
                    'nombre': config['name'],
                    'descripcion': config['description'],
                    'requiere_referencia': config['requires_reference'],
                    'requiere_comprobante': config['requires_receipt'],
                    'comision_porcentaje': Decimal(str(config['commission_percentage'])),
                    'activo': config['active'],
                    'configuracion': config['configuration'],
                    'orden': list(PAYMENT_METHODS_CONFIG.keys()).index(method_code)
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creado método de pago: {config["name"]}')
                )
            elif force:
                # Actualizar configuración
                metodo.nombre = config['name']
                metodo.descripcion = config['description']
                metodo.requiere_referencia = config['requires_reference']
                metodo.requiere_comprobante = config['requires_receipt']
                metodo.comision_porcentaje = Decimal(str(config['commission_percentage']))
                metodo.activo = config['active']
                metodo.configuracion = config['configuration']
                metodo.save()
                
                self.stdout.write(
                    self.style.WARNING(f'↻ Actualizado método de pago: {config["name"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Ya existe método de pago: {config["name"]}')
                )
        
        # Crear conceptos de pago básicos
        conceptos_basicos = [
            {
                'nombre': 'Cuota de Administración',
                'descripcion': 'Cuota mensual por administración del condominio',
                'tipo': 'fijo',
                'valor_base': Decimal('250000.00'),
                'es_obligatorio': True,
                'frecuencia': 'mensual',
                'aplica_a_todos': True,
            },
            {
                'nombre': 'Fondo de Reserva',
                'descripcion': 'Aporte mensual al fondo de reserva',
                'tipo': 'fijo',
                'valor_base': Decimal('50000.00'),
                'es_obligatorio': True,
                'frecuencia': 'mensual',
                'aplica_a_todos': True,
            },
            {
                'nombre': 'Cuota Extraordinaria',
                'descripcion': 'Cuota extraordinaria para gastos especiales',
                'tipo': 'extraordinario',
                'valor_base': Decimal('100000.00'),
                'es_obligatorio': False,
                'frecuencia': 'unica',
                'aplica_a_todos': False,
            }
        ]
        
        for concepto_data in conceptos_basicos:
            concepto, created = ConceptoPago.objects.get_or_create(
                nombre=concepto_data['nombre'],
                defaults=concepto_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creado concepto: {concepto_data["nombre"]}')
                )
            elif force:
                # Actualizar concepto
                for key, value in concepto_data.items():
                    setattr(concepto, key, value)
                concepto.save()
                
                self.stdout.write(
                    self.style.WARNING(f'↻ Actualizado concepto: {concepto_data["nombre"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Ya existe concepto: {concepto_data["nombre"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Inicialización completada exitosamente!')
        )