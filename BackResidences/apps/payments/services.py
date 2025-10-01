"""
Servicios para el módulo de pagos
Incluye integración con Stripe y lógica de negocio
"""
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from .models import Pago, Factura, PagoFactura, ConceptoPago, MetodoPago

logger = logging.getLogger(__name__)


class StripeService:
    """Servicio para integración con Stripe"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        self.publishable_key = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', None)
        self.webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        self.is_test_mode = getattr(settings, 'STRIPE_TEST_MODE', True)
        
        # En modo de prueba, no inicializamos Stripe real
        if not self.is_test_mode and self.api_key:
            try:
                import stripe
                stripe.api_key = self.api_key
                self.stripe = stripe
            except ImportError:
                logger.warning("Stripe library not installed. Install with: pip install stripe")
                self.stripe = None
        else:
            self.stripe = None
    
    def create_payment_intent(self, amount: int, currency: str = 'cop', 
                            metadata: Dict = None) -> Dict[str, Any]:
        """
        Crear un PaymentIntent en Stripe
        
        Args:
            amount: Monto en centavos
            currency: Moneda (default: cop)
            metadata: Metadatos adicionales
            
        Returns:
            Dict con información del PaymentIntent
        """
        if self.is_test_mode:
            # Simulación para desarrollo
            return {
                'id': f'pi_test_{timezone.now().timestamp()}',
                'client_secret': f'pi_test_client_secret_{timezone.now().timestamp()}',
                'amount': amount,
                'currency': currency,
                'status': 'requires_payment_method',
                'metadata': metadata or {}
            }
        
        if not self.stripe:
            raise Exception("Stripe not configured properly")
            
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'id': intent.id,
                'client_secret': intent.client_secret,
                'amount': intent.amount,
                'currency': intent.currency,
                'status': intent.status,
                'metadata': intent.metadata
            }
            
        except Exception as e:
            logger.error(f"Error creating Stripe PaymentIntent: {str(e)}")
            raise Exception(f"Error procesando pago: {str(e)}")
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirmar un pago en Stripe
        
        Args:
            payment_intent_id: ID del PaymentIntent
            
        Returns:
            Dict con información del pago confirmado
        """
        if self.is_test_mode:
            # Simulación para desarrollo
            return {
                'id': payment_intent_id,
                'status': 'succeeded',
                'amount_received': 100000,  # Ejemplo: 1000.00 COP
                'currency': 'cop',
                'charges': {
                    'data': [{
                        'id': f'ch_test_{timezone.now().timestamp()}',
                        'amount': 100000,
                        'currency': 'cop',
                        'status': 'succeeded'
                    }]
                }
            }
            
        if not self.stripe:
            raise Exception("Stripe not configured properly")
            
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'id': intent.id,
                'status': intent.status,
                'amount_received': intent.amount_received,
                'currency': intent.currency,
                'charges': intent.charges
            }
        except Exception as e:
            logger.error(f"Error confirming Stripe payment: {str(e)}")
            raise Exception(f"Error confirmando pago: {str(e)}")
    
    def process_webhook(self, payload: str, sig_header: str) -> Dict[str, Any]:
        """
        Procesar webhook de Stripe
        
        Args:
            payload: Payload del webhook
            sig_header: Signature header
            
        Returns:
            Dict con el evento procesado
        """
        if self.is_test_mode:
            # En modo de prueba, simular evento
            import json
            try:
                event_data = json.loads(payload)
                return {
                    'type': event_data.get('type', 'payment_intent.succeeded'),
                    'data': event_data.get('data', {}),
                    'livemode': False
                }
            except json.JSONDecodeError:
                return {
                    'type': 'test_event',
                    'data': {'object': {'id': 'test_id'}},
                    'livemode': False
                }
        
        if not self.stripe or not self.webhook_secret:
            raise Exception("Stripe webhook not configured properly")
            
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {str(e)}")
            raise Exception(f"Error procesando webhook: {str(e)}")


class PaymentService:
    """Servicio para lógica de negocio de pagos"""
    
    def __init__(self):
        self.stripe_service = StripeService()
    
    @transaction.atomic
    def create_payment_with_stripe(self, pago_data: Dict, user) -> Pago:
        """
        Crear pago con integración de Stripe
        
        Args:
            pago_data: Datos del pago
            user: Usuario que registra el pago
            
        Returns:
            Instancia de Pago creada
        """
        try:
            # Obtener facturas a pagar
            facturas_ids = pago_data.get('facturas', [])
            facturas = Factura.objects.filter(
                id__in=facturas_ids,
                vivienda=pago_data['vivienda']
            )
            
            if not facturas.exists():
                raise Exception("No se encontraron facturas válidas")
            
            # Calcular monto total si no se especifica
            if 'monto_total' not in pago_data:
                monto_total = sum(f.saldo_pendiente for f in facturas)
                pago_data['monto_total'] = monto_total
            
            # Crear PaymentIntent en Stripe si es pago online
            stripe_data = {}
            metodo_pago = MetodoPago.objects.get(id=pago_data['metodo_pago'])
            
            if metodo_pago.codigo in ['stripe', 'tarjeta_credito', 'pse_stripe']:
                amount_cents = int(pago_data['monto_total'] * 100)  # Convertir a centavos
                metadata = {
                    'vivienda_id': str(pago_data['vivienda'].id),
                    'facturas': ','.join(map(str, facturas_ids)),
                    'user_id': str(user.id)
                }
                
                stripe_intent = self.stripe_service.create_payment_intent(
                    amount=amount_cents,
                    metadata=metadata
                )
                
                stripe_data = {
                    'stripe_payment_intent_id': stripe_intent['id'],
                    'client_secret': stripe_intent['client_secret']
                }
            
            # Generar número de pago
            ultimo_numero = Pago.objects.filter(
                numero_pago__startswith=f'PAG-{timezone.now().year}-'
            ).count() + 1
            numero_pago = f'PAG-{timezone.now().year}-{ultimo_numero:06d}'
            
            # Crear pago
            pago = Pago.objects.create(
                numero_pago=numero_pago,
                vivienda=pago_data['vivienda'],
                monto_total=pago_data['monto_total'],
                metodo_pago=metodo_pago,
                numero_referencia=pago_data.get('numero_referencia', ''),
                fecha_pago=pago_data.get('fecha_pago', timezone.now()),
                observaciones=pago_data.get('observaciones', ''),
                archivo_comprobante=pago_data.get('archivo_comprobante', ''),
                registrado_por=user,
                estado='pendiente' if stripe_data else 'confirmado'
            )
            
            # Aplicar pago a facturas
            self._apply_payment_to_invoices(pago, facturas)
            
            # Agregar datos de Stripe a la respuesta
            pago.stripe_data = stripe_data
            
            return pago
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            raise Exception(f"Error creando pago: {str(e)}")
    
    def _apply_payment_to_invoices(self, pago: Pago, facturas):
        """Aplicar pago a facturas"""
        monto_restante = pago.monto_total
        
        for factura in facturas.order_by('fecha_vencimiento'):
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
    
    @transaction.atomic
    def confirm_stripe_payment(self, payment_intent_id: str) -> Optional[Pago]:
        """
        Confirmar pago de Stripe y actualizar estado
        
        Args:
            payment_intent_id: ID del PaymentIntent de Stripe
            
        Returns:
            Pago confirmado o None si no se encuentra
        """
        try:
            # Buscar pago por payment_intent_id
            # Nota: Necesitaríamos agregar este campo al modelo Pago
            # Por ahora usamos numero_referencia o agregamos campo específico
            
            stripe_payment = self.stripe_service.confirm_payment(payment_intent_id)
            
            if stripe_payment['status'] == 'succeeded':
                # Buscar y actualizar pago
                # Por ahora simulamos la búsqueda
                # En implementación real, agregar campo stripe_payment_intent_id al modelo
                
                logger.info(f"Stripe payment confirmed: {payment_intent_id}")
                return None  # Retornar el pago encontrado y actualizado
            
        except Exception as e:
            logger.error(f"Error confirming Stripe payment: {str(e)}")
            return None
    
    def generate_payment_reports(self, periodo: str = None) -> Dict[str, Any]:
        """
        Generar reportes de pagos
        
        Args:
            periodo: Período en formato YYYY-MM
            
        Returns:
            Dict con datos del reporte
        """
        if not periodo:
            periodo = timezone.now().strftime('%Y-%m')
        
        year, month = periodo.split('-')
        
        # Obtener facturas del período
        facturas = Factura.objects.filter(
            periodo=periodo
        )
        
        # Obtener pagos del período
        pagos = Pago.objects.filter(
            fecha_pago__year=year,
            fecha_pago__month=month,
            estado='confirmado'
        )
        
        total_facturado = sum(f.monto_total for f in facturas)
        total_recaudado = sum(p.monto_total for p in pagos)
        
        return {
            'periodo': periodo,
            'total_facturado': total_facturado,
            'total_recaudado': total_recaudado,
            'porcentaje_recaudo': (total_recaudado / total_facturado * 100) if total_facturado > 0 else 0,
            'facturas_generadas': facturas.count(),
            'pagos_procesados': pagos.count(),
            'facturas_pendientes': facturas.exclude(estado='pagada').count(),
            'facturas_vencidas': facturas.filter(
                fecha_vencimiento__lt=timezone.now(),
                estado__in=['pendiente', 'parcialmente_pagada']
            ).count()
        }


class InvoiceService:
    """Servicio para gestión de facturas"""
    
    @transaction.atomic
    def generate_bulk_invoices(self, conceptos_ids: List[int], periodo: str, 
                              fecha_vencimiento, filtros: Dict = None, 
                              user=None) -> Dict[str, Any]:
        """
        Generar facturas masivas
        
        Args:
            conceptos_ids: IDs de conceptos a facturar
            periodo: Período en formato YYYY-MM
            fecha_vencimiento: Fecha de vencimiento
            filtros: Filtros para viviendas
            user: Usuario que genera las facturas
            
        Returns:
            Dict con resultado del proceso
        """
        try:
            from apps.residences.models import Vivienda
            
            # Obtener conceptos
            conceptos = ConceptoPago.objects.filter(
                id__in=conceptos_ids,
                activo=True
            )
            
            if not conceptos.exists():
                raise Exception("No se encontraron conceptos válidos")
            
            # Obtener viviendas según filtros
            viviendas = Vivienda.objects.filter(activo=True)
            
            if filtros:
                if 'bloques' in filtros:
                    viviendas = viviendas.filter(bloque__in=filtros['bloques'])
                if 'solo_ocupadas' in filtros and filtros['solo_ocupadas']:
                    viviendas = viviendas.exclude(usuario_propietario__isnull=True)
                if 'excluir_morosos' in filtros and filtros['excluir_morosos']:
                    # Excluir viviendas con facturas vencidas
                    morosos = Factura.objects.filter(
                        fecha_vencimiento__lt=timezone.now(),
                        estado__in=['pendiente', 'parcialmente_pagada']
                    ).values_list('vivienda_id', flat=True)
                    viviendas = viviendas.exclude(id__in=morosos)
            
            facturas_creadas = 0
            errores = []
            
            for vivienda in viviendas:
                for concepto in conceptos:
                    try:
                        # Verificar si ya existe factura
                        if Factura.objects.filter(
                            vivienda=vivienda,
                            concepto=concepto,
                            periodo=periodo
                        ).exists():
                            continue
                        
                        # Calcular monto según criterios del concepto
                        monto = self._calculate_invoice_amount(concepto, vivienda)
                        
                        if monto > 0:
                            # Generar número de factura
                            ultimo_numero = Factura.objects.filter(
                                numero_factura__startswith=f'FAC-{timezone.now().year}-'
                            ).count() + 1
                            numero_factura = f'FAC-{timezone.now().year}-{periodo.replace("-", "")}-{ultimo_numero:06d}'
                            
                            Factura.objects.create(
                                numero_factura=numero_factura,
                                vivienda=vivienda,
                                concepto=concepto,
                                periodo=periodo,
                                fecha_vencimiento=fecha_vencimiento,
                                monto_original=monto,
                                monto_total=monto,
                                saldo_pendiente=monto,
                                generada_por=user
                            )
                            facturas_creadas += 1
                            
                    except Exception as e:
                        errores.append(f"Error en {vivienda.identificador}: {str(e)}")
            
            return {
                'facturas_creadas': facturas_creadas,
                'viviendas_procesadas': viviendas.count(),
                'errores': errores,
                'conceptos_aplicados': conceptos.count()
            }
            
        except Exception as e:
            logger.error(f"Error generating bulk invoices: {str(e)}")
            raise Exception(f"Error generando facturas masivas: {str(e)}")
    
    def _calculate_invoice_amount(self, concepto: ConceptoPago, vivienda) -> Decimal:
        """
        Calcular monto de factura según concepto y vivienda
        
        Args:
            concepto: Concepto de pago
            vivienda: Vivienda
            
        Returns:
            Monto calculado
        """
        monto_base = concepto.valor_base
        
        # Aplicar criterios específicos si existen
        if concepto.criterios_aplicacion:
            criterios = concepto.criterios_aplicacion
            
            # Ejemplo: aplicar según metros cuadrados
            if 'por_metro_cuadrado' in criterios:
                monto_base = vivienda.metros_cuadrados * Decimal(str(criterios['por_metro_cuadrado']))
            
            # Ejemplo: aplicar según tipo de vivienda
            if 'factor_tipo' in criterios and vivienda.tipo in criterios['factor_tipo']:
                factor = Decimal(str(criterios['factor_tipo'][vivienda.tipo]))
                monto_base *= factor
        
        return monto_base


# Instancias globales de servicios
payment_service = PaymentService()
invoice_service = InvoiceService()
stripe_service = StripeService()