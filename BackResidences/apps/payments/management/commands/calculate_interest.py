"""
Comando para calcular intereses de mora automáticamente
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.payments.models import Factura
from decimal import Decimal


class Command(BaseCommand):
    help = 'Calcula automáticamente los intereses de mora para facturas vencidas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo simulación sin guardar cambios'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODO SIMULACIÓN - No se guardarán cambios')
            )
        
        self.stdout.write('Calculando intereses de mora...')
        
        # Obtener facturas vencidas pendientes
        facturas_vencidas = Factura.objects.filter(
            fecha_vencimiento__lt=timezone.now(),
            estado__in=['pendiente', 'parcialmente_pagada'],
            saldo_pendiente__gt=0
        )
        
        total_facturas = facturas_vencidas.count()
        facturas_procesadas = 0
        total_intereses_calculados = Decimal('0.00')
        
        self.stdout.write(f'Encontradas {total_facturas} facturas vencidas')
        
        for factura in facturas_vencidas:
            intereses_anteriores = factura.intereses
            dias_vencido = (timezone.now().date() - factura.fecha_vencimiento.date()).days
            
            if dias_vencido > 0:
                # Calcular intereses
                interes_diario = factura.concepto.porcentaje_interes_mora / Decimal('30')
                nuevos_intereses = factura.monto_original * (interes_diario / Decimal('100')) * dias_vencido
                
                if nuevos_intereses != intereses_anteriores:
                    if not dry_run:
                        factura.intereses = nuevos_intereses
                        factura.save()
                    
                    diferencia = nuevos_intereses - intereses_anteriores
                    total_intereses_calculados += diferencia
                    facturas_procesadas += 1
                    
                    if verbose:
                        self.stdout.write(
                            f'  • Factura {factura.numero_factura}: '
                            f'{dias_vencido} días vencidos, '
                            f'intereses: ${intereses_anteriores:,.2f} → ${nuevos_intereses:,.2f} '
                            f'(+${diferencia:,.2f})'
                        )
        
        # Marcar facturas como vencidas si no lo están
        facturas_pendientes_vencidas = Factura.objects.filter(
            fecha_vencimiento__lt=timezone.now(),
            estado='pendiente',
            saldo_pendiente__gt=0
        )
        
        if not dry_run:
            count_vencidas = facturas_pendientes_vencidas.update(estado='vencida')
        else:
            count_vencidas = facturas_pendientes_vencidas.count()
        
        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESUMEN DE PROCESAMIENTO:')
        self.stdout.write(f'  • Total facturas vencidas: {total_facturas}')
        self.stdout.write(f'  • Facturas con intereses actualizados: {facturas_procesadas}')
        self.stdout.write(f'  • Facturas marcadas como vencidas: {count_vencidas}')
        self.stdout.write(f'  • Total intereses calculados: ${total_intereses_calculados:,.2f}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Esto fue una simulación. Para aplicar cambios ejecute sin --dry-run')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Cálculo de intereses completado exitosamente!')
            )