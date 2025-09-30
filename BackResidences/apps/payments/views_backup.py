"""
Views para el módulo de pagos
Incluye toda la funcionalidad de la API de payments
"""
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Type, Any
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import BaseSerializer
from django_filters.rest_framework import DjangoFilterBackend

from apps.residences.models import Vivienda
from .models import (
    ConceptoPago, MetodoPago, Factura, Pago, PagoFactura, PazYSalvo,
    TipoPago, Deuda, DetalleDeuda
)
from .serializers import (
    # Conceptos de Pago
    ConceptoPagoListSerializer, ConceptoPagoDetailSerializer, ConceptoPagoCreateSerializer,
    # Métodos de Pago
    MetodoPagoSerializer,
    # Facturas
    FacturaListSerializer, FacturaDetailSerializer, FacturaCreateSerializer,
    # Pagos
    PagoListSerializer, PagoDetailSerializer, PagoCreateSerializer,
    # Paz y Salvo
    PazYSalvoSerializer, PazYSalvoCreateSerializer,
    # Reportes
    DashboardFinancieroSerializer, EstadoCuentaSerializer,
    # Stripe
    StripePaymentIntentSerializer, StripeWebhookSerializer,
    # Legacy
    TipoPagoSerializer, DeudaSerializer, DetalleDeudaSerializer
)
from .services import payment_service, invoice_service, stripe_service

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para el módulo de pagos"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ================== CONCEPTOS DE PAGO ==================

class ConceptoPagoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de conceptos de pago"""
    queryset = ConceptoPago.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'activo', 'es_obligatorio', 'frecuencia']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'valor_base', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConceptoPagoListSerializer
        elif self.action == 'create':
            return ConceptoPagoCreateSerializer
        return ConceptoPagoDetailSerializer


# ================== MÉTODOS DE PAGO ==================

class MetodoPagoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de métodos de pago"""
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['orden', 'nombre']


# ================== FACTURAS ==================

class FacturaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de facturas"""
    queryset = Factura.objects.select_related('vivienda', 'concepto', 'generada_por')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'periodo', 'concepto', 'vivienda']
    search_fields = ['numero_factura', 'vivienda__identificador']
    ordering_fields = ['fecha_generacion', 'fecha_vencimiento', 'monto_total']
    ordering = ['-fecha_generacion']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FacturaListSerializer
        elif self.action == 'create':
            return FacturaCreateSerializer
        return FacturaDetailSerializer
    
    def get_queryset(self):
        """Filtrar facturas según usuario"""
        queryset = super().get_queryset()
        
        # Si es residente, solo sus facturas
        if not self.request.user.is_staff:
            viviendas_usuario = Vivienda.objects.filter(
                Q(usuario_propietario=self.request.user) | 
                Q(usuario_inquilino=self.request.user)
            )
            queryset = queryset.filter(vivienda__in=viviendas_usuario)
        
        # Filtros adicionales por query params
        vivienda = self.request.query_params.get('vivienda')
        if vivienda:
            queryset = queryset.filter(vivienda_id=vivienda)
            
        fecha_venc_desde = self.request.query_params.get('fecha_vencimiento_desde')
        if fecha_venc_desde:
            queryset = queryset.filter(fecha_vencimiento__gte=fecha_venc_desde)
            
        fecha_venc_hasta = self.request.query_params.get('fecha_vencimiento_hasta')
        if fecha_venc_hasta:
            queryset = queryset.filter(fecha_vencimiento__lte=fecha_venc_hasta)
            
        monto_min = self.request.query_params.get('monto_minimo')
        if monto_min:
            queryset = queryset.filter(monto_total__gte=monto_min)
            
        monto_max = self.request.query_params.get('monto_maximo')
        if monto_max:
            queryset = queryset.filter(monto_total__lte=monto_max)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='generar-masivas')
    def generar_masivas(self, request):
        """Generar facturas masivas"""
        try:
            conceptos = request.data.get('conceptos', [])
            periodo = request.data.get('periodo')
            fecha_vencimiento = request.data.get('fecha_vencimiento')
            filtros = request.data.get('filtros', {})
            
            if not conceptos or not periodo or not fecha_vencimiento:
                return Response({
                    'success': False,
                    'message': 'Faltan datos requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            resultado = invoice_service.generate_bulk_invoices(
                conceptos_ids=conceptos,
                periodo=periodo,
                fecha_vencimiento=fecha_vencimiento,
                filtros=filtros,
                user=request.user
            )
            
            return Response({
                'success': True,
                'message': 'Proceso de facturación masiva completado',
                'data': {
                    'proceso_id': f'FACT-MASIVA-{periodo}-{timezone.now().strftime("%Y%m%d%H%M")}',
                    'facturas_creadas': resultado['facturas_creadas'],
                    'total_viviendas': resultado['viviendas_procesadas'],
                    'conceptos_aplicados': resultado['conceptos_aplicados'],
                    'fecha_inicio': timezone.now(),
                    'estado': 'completado',
                    'errores': resultado['errores']
                }
            })
            
        except Exception as e:
            logger.error(f"Error en facturación masiva: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error en facturación masiva: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================== PAGOS ==================

class PagoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pagos"""
    queryset = Pago.objects.select_related('vivienda', 'metodo_pago', 'registrado_por')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'metodo_pago', 'vivienda']
    search_fields = ['numero_pago', 'numero_referencia', 'vivienda__identificador']
    ordering_fields = ['fecha_pago', 'fecha_registro', 'monto_total']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PagoListSerializer
        elif self.action == 'create':
            return PagoCreateSerializer
        return PagoDetailSerializer
    
    def get_queryset(self):
        """Filtrar pagos según usuario"""
        queryset = super().get_queryset()
        
        # Si es residente, solo sus pagos
        if not self.request.user.is_staff:
            viviendas_usuario = Vivienda.objects.filter(
                Q(usuario_propietario=self.request.user) | 
                Q(usuario_inquilino=self.request.user)
            )
            queryset = queryset.filter(vivienda__in=viviendas_usuario)
        
        # Filtros adicionales
        fecha_desde = self.request.query_params.get('fecha_desde')
        if fecha_desde:
            queryset = queryset.filter(fecha_pago__gte=fecha_desde)
            
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        if fecha_hasta:
            queryset = queryset.filter(fecha_pago__lte=fecha_hasta)
            
        monto_min = self.request.query_params.get('monto_minimo')
        if monto_min:
            queryset = queryset.filter(monto_total__gte=monto_min)
            
        monto_max = self.request.query_params.get('monto_maximo')
        if monto_max:
            queryset = queryset.filter(monto_total__lte=monto_max)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Crear pago con integración de Stripe"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Crear pago usando el servicio
            pago = payment_service.create_payment_with_stripe(
                serializer.validated_data,
                request.user
            )
            
            # Preparar respuesta
            response_data = PagoDetailSerializer(pago).data
            
            # Agregar datos de Stripe si existen
            if hasattr(pago, 'stripe_data') and pago.stripe_data:
                response_data['stripe_data'] = pago.stripe_data
            
            return Response({
                'success': True,
                'message': 'Pago registrado exitosamente',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creando pago: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error registrando pago: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='aplicar-facturas')
    def aplicar_facturas(self, request, pk=None):
        """Aplicar pago a facturas específicas"""
        try:
            pago = self.get_object()
            distribuciones = request.data.get('distribuciones', [])
            
            if not distribuciones:
                return Response({
                    'success': False,
                    'message': 'Debe especificar distribuciones'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            facturas_actualizadas = []
            monto_aplicado_total = Decimal('0.00')
            
            for dist in distribuciones:
                factura = Factura.objects.get(id=dist['factura_id'])
                monto = Decimal(str(dist['monto']))
                
                # Validar que el monto no exceda el saldo
                if monto > factura.saldo_pendiente:
                    return Response({
                        'success': False,
                        'message': f'Monto excede saldo pendiente de factura {factura.numero_factura}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                saldo_anterior = factura.saldo_pendiente
                
                # Crear aplicación de pago
                PagoFactura.objects.create(
                    pago=pago,
                    factura=factura,
                    monto_aplicado=monto
                )
                
                monto_aplicado_total += monto
                
                facturas_actualizadas.append({
                    'factura_id': factura.pk,
                    'monto_aplicado': str(monto),
                    'saldo_anterior': str(saldo_anterior),
                    'saldo_nuevo': str(factura.saldo_pendiente),
                    'estado': factura.estado
                })
            
            return Response({
                'success': True,
                'message': 'Pago aplicado a facturas exitosamente',
                'data': {
                    'pago_id': pago.pk,
                    'monto_aplicado': str(monto_aplicado_total),
                    'facturas_actualizadas': facturas_actualizadas
                }
            })
            
        except Exception as e:
            logger.error(f"Error aplicando pago: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error aplicando pago: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reversar(self, request, pk=None):
        """Reversar un pago"""
        try:
            pago = self.get_object()
            
            if pago.estado == 'reversado':
                return Response({
                    'success': False,
                    'message': 'El pago ya está reversado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            estado_anterior = pago.estado
            facturas_afectadas = []
            
            # Reversar aplicaciones de pago
            aplicaciones = PagoFactura.objects.filter(pago=pago)
            for aplicacion in aplicaciones:
                factura = aplicacion.factura
                saldo_anterior = factura.saldo_pendiente
                
                # Restaurar saldo de factura
                factura.saldo_pendiente += aplicacion.monto_aplicado
                
                # Actualizar estado de factura
                if factura.saldo_pendiente >= factura.monto_total:
                    factura.estado = 'pendiente'
                elif factura.saldo_pendiente > 0:
                    factura.estado = 'parcialmente_pagada'
                
                factura.save()
                
                facturas_afectadas.append({
                    'factura_id': factura.pk,
                    'estado_restaurado': factura.estado,
                    'saldo_restaurado': str(factura.saldo_pendiente)
                })
                
                # Eliminar aplicación
                aplicacion.delete()
            
            # Actualizar pago
            pago.estado = 'reversado'
            pago.reversado_por = request.user
            pago.fecha_reverso = timezone.now()
            pago.motivo_reverso = request.data.get('motivo', '')
            pago.save()
            
            return Response({
                'success': True,
                'message': 'Pago reversado exitosamente',
                'data': {
                    'pago_id': pago.pk,
                    'estado_anterior': estado_anterior,
                    'estado_nuevo': 'reversado',
                    'fecha_reverso': pago.fecha_reverso,
                    'facturas_afectadas': facturas_afectadas
                }
            })
            
        except Exception as e:
            logger.error(f"Error reversando pago: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error reversando pago: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


# ================== PAZ Y SALVO ==================

class PazYSalvoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de paz y salvos"""
    queryset = PazYSalvo.objects.select_related('vivienda', 'generado_por')
    serializer_class = PazYSalvoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['vivienda']
    ordering = ['-fecha_generacion']
    
    @action(detail=False, methods=['post'], url_path='(?P<vivienda_id>[^/.]+)')
    def generar_paz_y_salvo(self, request, vivienda_id=None):
        """Generar paz y salvo para una vivienda"""
        try:
            vivienda = Vivienda.objects.get(pk=vivienda_id)
            
            serializer = PazYSalvoCreateSerializer(
                data=request.data,
                context={'vivienda_id': vivienda_id, 'request': request}
            )
            serializer.is_valid(raise_exception=True)
            
            paz_y_salvo = serializer.save()
            
            response_data = PazYSalvoSerializer(paz_y_salvo).data
            
            return Response({
                'success': True,
                'message': 'Paz y salvo generado exitosamente',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
            
        except Vivienda.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Vivienda no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generando paz y salvo: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error generando paz y salvo: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


# ================== REPORTES ==================

class ReportesFinancierosViewSet(viewsets.ViewSet):
    """ViewSet para reportes financieros"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard financiero"""
        try:
            periodo = request.query_params.get('periodo', timezone.now().strftime('%Y-%m'))
            
            datos = payment_service.generate_payment_reports(periodo)
            
            # Agregar datos adicionales del dashboard
            year, month = periodo.split('-')
            
            # Recaudo por concepto
            conceptos_recaudo = []
            for concepto in ConceptoPago.objects.filter(activo=True):
                facturas = Factura.objects.filter(
                    concepto=concepto,
                    periodo=periodo
                )
                pagos = Pago.objects.filter(
                    fecha_pago__year=year,
                    fecha_pago__month=month,
                    estado='confirmado',
                    pagofactura__factura__concepto=concepto
                ).distinct()
                
                facturado = sum(f.monto_total for f in facturas)
                recaudado = sum(p.monto_total for p in pagos)
                
                if facturado > 0:
                    conceptos_recaudo.append({
                        'concepto': concepto.nombre,
                        'facturado': str(facturado),
                        'recaudado': str(recaudado),
                        'porcentaje': round((recaudado / facturado * 100), 2)
                    })
            
            # Recaudo por método
            metodos_recaudo = []
            for metodo in MetodoPago.objects.filter(activo=True):
                pagos = Pago.objects.filter(
                    fecha_pago__year=year,
                    fecha_pago__month=month,
                    metodo_pago=metodo,
                    estado='confirmado'
                )
                
                if pagos.exists():
                    cantidad = pagos.count()
                    monto = sum(p.monto_total for p in pagos)
                    porcentaje = (monto / datos['total_recaudado'] * 100) if datos['total_recaudado'] > 0 else 0
                    
                    metodos_recaudo.append({
                        'metodo': metodo.nombre,
                        'cantidad': cantidad,
                        'monto': str(monto),
                        'porcentaje': round(porcentaje, 2)
                    })
            
            # Datos de morosidad
            facturas_vencidas = Factura.objects.filter(
                fecha_vencimiento__lt=timezone.now(),
                estado__in=['pendiente', 'parcialmente_pagada']
            )
            
            viviendas_morosas = facturas_vencidas.values('vivienda').distinct().count()
            deuda_total = sum(f.saldo_pendiente for f in facturas_vencidas)
            promedio_deuda = deuda_total / viviendas_morosas if viviendas_morosas > 0 else 0
            
            response_data = {
                'periodo': periodo,
                'resumen': datos,
                'recaudo_por_concepto': conceptos_recaudo,
                'recaudo_por_metodo': metodos_recaudo,
                'morosidad': {
                    'viviendas_morosas': viviendas_morosas,
                    'deuda_total': str(deuda_total),
                    'promedio_deuda': str(promedio_deuda),
                    'facturas_vencidas': facturas_vencidas.count()
                }
            }
            
            return Response({
                'success': True,
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"Error en dashboard financiero: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error generando dashboard: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='estado-cuenta/(?P<vivienda_id>[^/.]+)')
    def estado_cuenta(self, request, vivienda_id=None):
        """Estado de cuenta por vivienda"""
        try:
            vivienda = Vivienda.objects.get(pk=vivienda_id)
            
            # Filtros de período
            periodo_desde = request.query_params.get('periodo_desde')
            periodo_hasta = request.query_params.get('periodo_hasta')
            incluir_pagadas = request.query_params.get('incluir_pagadas', 'true').lower() == 'true'
            
            # Obtener facturas
            facturas = Factura.objects.filter(vivienda=vivienda)
            
            if periodo_desde:
                facturas = facturas.filter(periodo__gte=periodo_desde)
            if periodo_hasta:
                facturas = facturas.filter(periodo__lte=periodo_hasta)
            if not incluir_pagadas:
                facturas = facturas.exclude(estado='pagada')
            
            # Calcular resumen
            saldo_total = sum(f.saldo_pendiente for f in facturas.exclude(estado='pagada'))
            facturas_pendientes = facturas.exclude(estado='pagada').count()
            facturas_vencidas = facturas.filter(
                fecha_vencimiento__lt=timezone.now(),
                estado__in=['pendiente', 'parcialmente_pagada']
            ).count()
            
            # Último pago
            ultimo_pago = Pago.objects.filter(
                vivienda=vivienda,
                estado='confirmado'
            ).order_by('-fecha_pago').first()
            
            # Total pagado en el año
            total_pagado_ano = Pago.objects.filter(
                vivienda=vivienda,
                fecha_pago__year=timezone.now().year,
                estado='confirmado'
            ).aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
            
            # Obtener pagos
            pagos = Pago.objects.filter(vivienda=vivienda, estado='confirmado')
            if periodo_desde and periodo_hasta:
                # Convertir período a fechas
                fecha_desde = datetime.strptime(periodo_desde + '-01', '%Y-%m-%d')
                fecha_hasta = datetime.strptime(periodo_hasta + '-01', '%Y-%m-%d')
                fecha_hasta = fecha_hasta.replace(day=28) + timedelta(days=4)
                fecha_hasta = fecha_hasta - timedelta(days=fecha_hasta.day)
                
                pagos = pagos.filter(fecha_pago__range=[fecha_desde, fecha_hasta])
            
            response_data = {
                'vivienda': {
                    'id': vivienda.pk,
                    'identificador': vivienda.identificador,
                    'propietario': {
                        'full_name': vivienda.usuario_propietario.get_full_name() if vivienda.usuario_propietario else '',
                        'email': vivienda.usuario_propietario.email if vivienda.usuario_propietario else ''
                    }
                },
                'resumen': {
                    'saldo_total': str(saldo_total),
                    'facturas_pendientes': facturas_pendientes,
                    'facturas_vencidas': facturas_vencidas,
                    'ultimo_pago': ultimo_pago.fecha_pago if ultimo_pago else None,
                    'total_pagado_ano': str(total_pagado_ano)
                },
                'facturas': FacturaListSerializer(facturas.order_by('-fecha_generacion'), many=True).data,
                'pagos': PagoListSerializer(pagos.order_by('-fecha_pago'), many=True).data
            }
            
            return Response({
                'success': True,
                'data': response_data
            })
            
        except Vivienda.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Vivienda no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error en estado de cuenta: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error generando estado de cuenta: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def morosidad(self, request):
        """Reporte de morosidad"""
        try:
            # Filtros
            dias_vencimiento = int(request.query_params.get('dias_vencimiento', 0))
            monto_minimo = request.query_params.get('monto_minimo', 0)
            bloque = request.query_params.get('bloque')
            
            # Facturas vencidas
            facturas_vencidas = Factura.objects.filter(
                fecha_vencimiento__lt=timezone.now() - timedelta(days=dias_vencimiento),
                estado__in=['pendiente', 'parcialmente_pagada'],
                saldo_pendiente__gte=monto_minimo
            )
            
            if bloque:
                facturas_vencidas = facturas_vencidas.filter(vivienda__bloque=bloque)
            
            # Agrupar por vivienda
            viviendas_morosas = {}
            for factura in facturas_vencidas:
                vivienda_pk = factura.vivienda.pk
                if vivienda_pk not in viviendas_morosas:
                    viviendas_morosas[vivienda_pk] = {
                        'vivienda': factura.vivienda,
                        'facturas': [],
                        'deuda_total': Decimal('0.00'),
                        'dias_vencimiento_mayor': 0
                    }
                
                viviendas_morosas[vivienda_pk]['facturas'].append(factura)
                viviendas_morosas[vivienda_pk]['deuda_total'] += factura.saldo_pendiente
                
                dias_vencido = (timezone.now().date() - factura.fecha_vencimiento.date()).days
                if dias_vencido > viviendas_morosas[vivienda_pk]['dias_vencimiento_mayor']:
                    viviendas_morosas[vivienda_pk]['dias_vencimiento_mayor'] = dias_vencido
            
            # Preparar respuesta
            detalle_morosidad = []
            total_viviendas = Vivienda.objects.filter(activo=True).count()
            viviendas_morosas_count = len(viviendas_morosas)
            deuda_total_general = Decimal('0.00')
            
            for data in viviendas_morosas.values():
                vivienda = data['vivienda']
                deuda_total_general += data['deuda_total']
                
                # Último pago
                ultimo_pago = Pago.objects.filter(
                    vivienda=vivienda,
                    estado='confirmado'
                ).order_by('-fecha_pago').first()
                
                detalle_morosidad.append({
                    'vivienda': {
                        'id': vivienda.pk,
                        'identificador': vivienda.identificador,
                        'propietario': vivienda.usuario_propietario.get_full_name() if vivienda.usuario_propietario else ''
                    },
                    'facturas_vencidas': len(data['facturas']),
                    'deuda_total': str(data['deuda_total']),
                    'dias_vencimiento_mayor': data['dias_vencimiento_mayor'],
                    'ultimo_pago': ultimo_pago.fecha_pago if ultimo_pago else None,
                    'contacto': {
                        'email': vivienda.usuario_propietario.email if vivienda.usuario_propietario else '',
                        'telefono': vivienda.usuario_propietario.telefono if vivienda.usuario_propietario else ''
                    }
                })
            
            # Distribución por rangos
            rangos = [
                {'rango': '1-30 días', 'min': 1, 'max': 30},
                {'rango': '31-60 días', 'min': 31, 'max': 60},
                {'rango': 'Más de 60 días', 'min': 61, 'max': 999999}
            ]
            
            distribucion_rangos = []
            for rango in rangos:
                viviendas_rango = [v for v in viviendas_morosas.values() 
                                 if rango['min'] <= v['dias_vencimiento_mayor'] <= rango['max']]
                
                if viviendas_rango:
                    monto_rango = sum(v['deuda_total'] for v in viviendas_rango)
                    distribucion_rangos.append({
                        'rango': rango['rango'],
                        'viviendas': len(viviendas_rango),
                        'monto': str(monto_rango)
                    })
            
            promedio_deuda = deuda_total_general / viviendas_morosas_count if viviendas_morosas_count > 0 else Decimal('0.00')
            porcentaje_morosidad = (viviendas_morosas_count / total_viviendas * 100) if total_viviendas > 0 else 0
            
            response_data = {
                'fecha_corte': timezone.now(),
                'resumen': {
                    'total_viviendas': total_viviendas,
                    'viviendas_morosas': viviendas_morosas_count,
                    'porcentaje_morosidad': round(porcentaje_morosidad, 2),
                    'deuda_total': str(deuda_total_general),
                    'promedio_deuda': str(promedio_deuda)
                },
                'detalle_morosidad': detalle_morosidad,
                'distribucion_por_rango': distribucion_rangos
            }
            
            return Response({
                'success': True,
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"Error en reporte de morosidad: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error generando reporte de morosidad: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================== STRIPE INTEGRATION ==================

class StripeViewSet(viewsets.ViewSet):
    """ViewSet para integración con Stripe"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='create-payment-intent')
    def create_payment_intent(self, request):
        """Crear PaymentIntent en Stripe"""
        try:
            serializer = StripePaymentIntentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            validated_data = serializer.validated_data
            
            # Validar facturas
            facturas = Factura.objects.filter(
                id__in=validated_data['facturas']
            )
            
            if not facturas.exists():
                return Response({
                    'success': False,
                    'message': 'No se encontraron facturas válidas'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear PaymentIntent
            metadata = {
                'facturas': ','.join(map(str, validated_data['facturas'])),
                'user_id': str(request.user.pk),
                **validated_data.get('metadata', {})
            }
            
            intent_data = stripe_service.create_payment_intent(
                amount=validated_data['amount'],
                currency=validated_data['currency'],
                metadata=metadata
            )
            
            return Response({
                'success': True,
                'data': intent_data
            })
            
        except Exception as e:
            logger.error(f"Error creando PaymentIntent: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error creando PaymentIntent: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """Webhook de Stripe"""
        try:
            payload = request.body.decode('utf-8')
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
            
            event = stripe_service.process_webhook(payload, sig_header)
            
            # Procesar evento según tipo
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                # Aquí procesar el pago exitoso
                logger.info(f"Payment succeeded: {payment_intent.get('id', 'unknown')}")
                
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                # Aquí procesar el pago fallido
                logger.warning(f"Payment failed: {payment_intent.get('id', 'unknown')}")
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {str(e)}")
            return JsonResponse({'success': False}, status=400)


# ================== LEGACY VIEWS (COMPATIBILIDAD) ==================

class TipoPagoViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de pago (legacy)"""
    queryset = TipoPago.objects.all()
    serializer_class = TipoPagoSerializer
    permission_classes = [IsAuthenticated]


class DeudaViewSet(viewsets.ModelViewSet):
    """ViewSet para deudas (legacy)"""
    queryset = Deuda.objects.all()
    serializer_class = DeudaSerializer
    permission_classes = [IsAuthenticated]


class DetalleDeudaViewSet(viewsets.ModelViewSet):
    """ViewSet para detalles de deuda (legacy)"""
    queryset = DetalleDeuda.objects.all()
    serializer_class = DetalleDeudaSerializer
    permission_classes = [IsAuthenticated]
from .models import (
    ConceptoPago, MetodoPago, Factura, Pago, PagoFactura, PazYSalvo,
    TipoPago, Deuda, DetalleDeuda
)
from .serializers import (
    # Conceptos de Pago
    ConceptoPagoListSerializer, ConceptoPagoDetailSerializer, ConceptoPagoCreateSerializer,
    # Métodos de Pago
    MetodoPagoSerializer,
    # Facturas
    FacturaListSerializer, FacturaDetailSerializer, FacturaCreateSerializer,
    # Pagos
    PagoListSerializer, PagoDetailSerializer, PagoCreateSerializer,
    # Paz y Salvo
    PazYSalvoSerializer, PazYSalvoCreateSerializer,
    # Reportes
    DashboardFinancieroSerializer, EstadoCuentaSerializer,
    # Stripe
    StripePaymentIntentSerializer, StripeWebhookSerializer,
    # Legacy
    TipoPagoSerializer, DeudaSerializer, DetalleDeudaSerializer
)
from .services import payment_service, invoice_service, stripe_service

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para el módulo de pagos"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ================== CONCEPTOS DE PAGO ==================

@extend_schema(tags=['Conceptos de Pago'])
class ConceptoPagoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de conceptos de pago"""
    queryset = ConceptoPago.objects.all()
    permission_classes = [IsAuthenticated, HasModulePermission]
    required_permissions = ['payments.view_conceptopago']
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'activo', 'es_obligatorio', 'frecuencia']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'valor_base', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConceptoPagoListSerializer
        elif self.action == 'create':
            return ConceptoPagoCreateSerializer
        return ConceptoPagoDetailSerializer
    
    def get_permissions(self):
        """Permisos según acción"""
        if self.action == 'create':
            self.required_permissions = ['payments.add_conceptopago']
        elif self.action in ['update', 'partial_update']:
            self.required_permissions = ['payments.change_conceptopago']
        elif self.action == 'destroy':
            self.required_permissions = ['payments.delete_conceptopago']
        return super().get_permissions()


# ================== MÉTODOS DE PAGO ==================

@extend_schema(tags=['Métodos de Pago'])
class MetodoPagoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de métodos de pago"""
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    required_permissions = ['payments.view_metodopago']
    filter_backends = [filters.OrderingFilter]
    ordering = ['orden', 'nombre']
    
    def get_permissions(self):
        if self.action == 'create':
            self.required_permissions = ['payments.add_metodopago']
        elif self.action in ['update', 'partial_update']:
            self.required_permissions = ['payments.change_metodopago']
        elif self.action == 'destroy':
            self.required_permissions = ['payments.delete_metodopago']
        return super().get_permissions()


# ================== FACTURAS ==================

@extend_schema(tags=['Facturas'])
class FacturaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de facturas"""
    queryset = Factura.objects.select_related('vivienda', 'concepto', 'generada_por')
    permission_classes = [IsAuthenticated, HasModulePermission]
    required_permissions = ['payments.view_factura']
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'periodo', 'concepto', 'vivienda']
    search_fields = ['numero_factura', 'vivienda__identificador']
    ordering_fields = ['fecha_generacion', 'fecha_vencimiento', 'monto_total']
    ordering = ['-fecha_generacion']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FacturaListSerializer
        elif self.action == 'create':
            return FacturaCreateSerializer
        return FacturaDetailSerializer
    
    def get_queryset(self):
        """Filtrar facturas según usuario"""
        queryset = super().get_queryset()
        
        # Si es residente, solo sus facturas
        if not self.request.user.is_staff:
            viviendas_usuario = Vivienda.objects.filter(
                Q(usuario_propietario=self.request.user) | 
                Q(usuario_inquilino=self.request.user)
            )
            queryset = queryset.filter(vivienda__in=viviendas_usuario)
        
        # Filtros adicionales por query params
        vivienda = self.request.query_params.get('vivienda')
        if vivienda:
            queryset = queryset.filter(vivienda_id=vivienda)
            
        fecha_venc_desde = self.request.query_params.get('fecha_vencimiento_desde')
        if fecha_venc_desde:
            queryset = queryset.filter(fecha_vencimiento__gte=fecha_venc_desde)
            
        fecha_venc_hasta = self.request.query_params.get('fecha_vencimiento_hasta')
        if fecha_venc_hasta:
            queryset = queryset.filter(fecha_vencimiento__lte=fecha_venc_hasta)
            
        monto_min = self.request.query_params.get('monto_minimo')
        if monto_min:
            queryset = queryset.filter(monto_total__gte=monto_min)
            
        monto_max = self.request.query_params.get('monto_maximo')
        if monto_max:
            queryset = queryset.filter(monto_total__lte=monto_max)
        
        return queryset
    
    def get_permissions(self):
        if self.action == 'create':
            self.required_permissions = ['payments.add_factura']
        elif self.action in ['update', 'partial_update']:
            self.required_permissions = ['payments.change_factura']
        elif self.action == 'destroy':
            self.required_permissions = ['payments.delete_factura']
        elif self.action == 'generar_masivas':
            self.required_permissions = ['payments.facturar_masivo']
        return super().get_permissions()
    
    @extend_schema(
        operation_id='facturas_generar_masivas',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'conceptos': {'type': 'array', 'items': {'type': 'integer'}},
                    'periodo': {'type': 'string', 'pattern': r'^\d{4}-\d{2}$'},
                    'fecha_vencimiento': {'type': 'string', 'format': 'date-time'},
                    'filtros': {'type': 'object'},
                    'observaciones': {'type': 'string'}
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='generar-masivas')
    def generar_masivas(self, request):
        """Generar facturas masivas"""
        try:
            conceptos = request.data.get('conceptos', [])
            periodo = request.data.get('periodo')
            fecha_vencimiento = request.data.get('fecha_vencimiento')
            filtros = request.data.get('filtros', {})
            
            if not conceptos or not periodo or not fecha_vencimiento:
                return Response({
                    'success': False,
                    'message': 'Faltan datos requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            resultado = invoice_service.generate_bulk_invoices(
                conceptos_ids=conceptos,
                periodo=periodo,
                fecha_vencimiento=fecha_vencimiento,
                filtros=filtros,
                user=request.user
            )
            
            return Response({
                'success': True,
                'message': 'Proceso de facturación masiva completado',
                'data': {
                    'proceso_id': f'FACT-MASIVA-{periodo}-{timezone.now().strftime("%Y%m%d%H%M")}',
                    'facturas_creadas': resultado['facturas_creadas'],
                    'total_viviendas': resultado['viviendas_procesadas'],
                    'conceptos_aplicados': resultado['conceptos_aplicados'],
                    'fecha_inicio': timezone.now(),
                    'estado': 'completado',
                    'errores': resultado['errores']
                }
            })
            
        except Exception as e:
            logger.error(f"Error en facturación masiva: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error en facturación masiva: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================== PAGOS ==================

@extend_schema(tags=['Pagos'])
class PagoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pagos"""
    queryset = Pago.objects.select_related('vivienda', 'metodo_pago', 'registrado_por')
    permission_classes = [IsAuthenticated, HasModulePermission]
    required_permissions = ['payments.view_pago']
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'metodo_pago', 'vivienda']
    search_fields = ['numero_pago', 'numero_referencia', 'vivienda__identificador']
    ordering_fields = ['fecha_pago', 'fecha_registro', 'monto_total']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PagoListSerializer
        elif self.action == 'create':
            return PagoCreateSerializer
        return PagoDetailSerializer
    
    def get_queryset(self):
        """Filtrar pagos según usuario"""
        queryset = super().get_queryset()
        
        # Si es residente, solo sus pagos
        if not self.request.user.is_staff:
            viviendas_usuario = Vivienda.objects.filter(
                Q(usuario_propietario=self.request.user) | 
                Q(usuario_inquilino=self.request.user)
            )
            queryset = queryset.filter(vivienda__in=viviendas_usuario)
        
        # Filtros adicionales
        fecha_desde = self.request.query_params.get('fecha_desde')
        if fecha_desde:
            queryset = queryset.filter(fecha_pago__gte=fecha_desde)
            
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        if fecha_hasta:
            queryset = queryset.filter(fecha_pago__lte=fecha_hasta)
            
        monto_min = self.request.query_params.get('monto_minimo')
        if monto_min:
            queryset = queryset.filter(monto_total__gte=monto_min)
            
        monto_max = self.request.query_params.get('monto_maximo')
        if monto_max:
            queryset = queryset.filter(monto_total__lte=monto_max)
        
        return queryset
    
    def get_permissions(self):
        if self.action == 'create':
            self.required_permissions = ['payments.add_pago']
        elif self.action in ['update', 'partial_update']:
            self.required_permissions = ['payments.change_pago']
        elif self.action == 'destroy':
            self.required_permissions = ['payments.delete_pago']
        elif self.action in ['aplicar_facturas', 'reversar']:
            self.required_permissions = ['payments.change_pago']
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """Crear pago con integración de Stripe"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Crear pago usando el servicio
            pago = payment_service.create_payment_with_stripe(
                serializer.validated_data,
                request.user
            )
            
            # Preparar respuesta
            response_data = PagoDetailSerializer(pago).data
            
            # Agregar datos de Stripe si existen
            if hasattr(pago, 'stripe_data') and pago.stripe_data:
                response_data['stripe_data'] = pago.stripe_data
            
            return Response({
                'success': True,
                'message': 'Pago registrado exitosamente',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creando pago: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error registrando pago: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        operation_id='pagos_aplicar_facturas',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'distribuciones': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'factura_id': {'type': 'integer'},
                                'monto': {'type': 'string'}
                            }
                        }
                    },
                    'criterio_aplicacion': {'type': 'string'},
                    'observaciones': {'type': 'string'}
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='aplicar-facturas')
    def aplicar_facturas(self, request, pk=None):
        """Aplicar pago a facturas específicas"""
        try:
            pago = self.get_object()
            distribuciones = request.data.get('distribuciones', [])
            
            if not distribuciones:
                return Response({
                    'success': False,
                    'message': 'Debe especificar distribuciones'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            facturas_actualizadas = []
            monto_aplicado_total = Decimal('0.00')
            
            for dist in distribuciones:
                factura = Factura.objects.get(id=dist['factura_id'])
                monto = Decimal(str(dist['monto']))
                
                # Validar que el monto no exceda el saldo
                if monto > factura.saldo_pendiente:
                    return Response({
                        'success': False,
                        'message': f'Monto excede saldo pendiente de factura {factura.numero_factura}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                saldo_anterior = factura.saldo_pendiente
                
                # Crear aplicación de pago
                PagoFactura.objects.create(
                    pago=pago,
                    factura=factura,
                    monto_aplicado=monto
                )
                
                monto_aplicado_total += monto
                
                facturas_actualizadas.append({
                    'factura_id': factura.id,
                    'monto_aplicado': str(monto),
                    'saldo_anterior': str(saldo_anterior),
                    'saldo_nuevo': str(factura.saldo_pendiente),
                    'estado': factura.estado
                })
            
            return Response({
                'success': True,
                'message': 'Pago aplicado a facturas exitosamente',
                'data': {
                    'pago_id': pago.id,
                    'monto_aplicado': str(monto_aplicado_total),
                    'facturas_actualizadas': facturas_actualizadas
                }
            })
            
        except Exception as e:
            logger.error(f"Error aplicando pago: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error aplicando pago: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        operation_id='pagos_reversar',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'motivo': {'type': 'string'},
                    'observaciones': {'type': 'string'}
                }
            }
        }
    )
    @action(detail=True, methods=['post'])
    def reversar(self, request, pk=None):
        """Reversar un pago"""
        try:
            pago = self.get_object()
            
            if pago.estado == 'reversado':
                return Response({
                    'success': False,
                    'message': 'El pago ya está reversado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            estado_anterior = pago.estado
            facturas_afectadas = []
            
            # Reversar aplicaciones de pago
            aplicaciones = PagoFactura.objects.filter(pago=pago)
            for aplicacion in aplicaciones:
                factura = aplicacion.factura
                saldo_anterior = factura.saldo_pendiente
                
                # Restaurar saldo de factura
                factura.saldo_pendiente += aplicacion.monto_aplicado
                
                # Actualizar estado de factura
                if factura.saldo_pendiente >= factura.monto_total:
                    factura.estado = 'pendiente'
                elif factura.saldo_pendiente > 0:
                    factura.estado = 'parcialmente_pagada'
                
                factura.save()
                
                facturas_afectadas.append({
                    'factura_id': factura.id,
                    'estado_restaurado': factura.estado,
                    'saldo_restaurado': str(factura.saldo_pendiente)
                })
                
                # Eliminar aplicación
                aplicacion.delete()
            
            # Actualizar pago
            pago.estado = 'reversado'
            pago.reversado_por = request.user
            pago.fecha_reverso = timezone.now()
            pago.motivo_reverso = request.data.get('motivo', '')
            pago.save()
            
            return Response({
                'success': True,
                'message': 'Pago reversado exitosamente',
                'data': {
                    'pago_id': pago.id,
                    'estado_anterior': estado_anterior,
                    'estado_nuevo': 'reversado',
                    'fecha_reverso': pago.fecha_reverso,
                    'facturas_afectadas': facturas_afectadas
                }
            })
            
        except Exception as e:
            logger.error(f"Error reversando pago: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error reversando pago: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


# ================== PAZ Y SALVO ==================

@extend_schema(tags=['Paz y Salvo'])
class PazYSalvoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de paz y salvos"""
    queryset = PazYSalvo.objects.select_related('vivienda', 'generado_por')
    serializer_class = PazYSalvoSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    required_permissions = ['payments.view_pazybalvo']
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['vivienda']
    ordering = ['-fecha_generacion']
    
    def get_permissions(self):
        if self.action == 'create':
            self.required_permissions = ['payments.add_pazybalvo']
        return super().get_permissions()
    
    @extend_schema(
        operation_id='generar_paz_y_salvo',
        request=PazYSalvoCreateSerializer
    )
    @action(detail=False, methods=['post'], url_path='(?P<vivienda_id>[^/.]+)')
    def generar_paz_y_salvo(self, request, vivienda_id=None):
        """Generar paz y salvo para una vivienda"""
        try:
            vivienda = Vivienda.objects.get(id=vivienda_id)
            
            serializer = PazYSalvoCreateSerializer(
                data=request.data,
                context={'vivienda_id': vivienda_id, 'request': request}
            )
            serializer.is_valid(raise_exception=True)
            
            paz_y_salvo = serializer.save()
            
            response_data = PazYSalvoSerializer(paz_y_salvo).data
            
            return Response({
                'success': True,
                'message': 'Paz y salvo generado exitosamente',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
            
        except Vivienda.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Vivienda no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generando paz y salvo: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error generando paz y salvo: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


# ================== REPORTES ==================

@extend_schema(tags=['Reportes Financieros'])
class ReportesFinancierosViewSet(viewsets.ViewSet):
    """ViewSet para reportes financieros"""
    permission_classes = [IsAuthenticated, HasModulePermission]
    required_permissions = ['payments.view_reportes_financieros']
    
    @extend_schema(
        operation_id='dashboard_financiero',
        parameters=[
            OpenApiParameter('periodo', str, description='Período YYYY-MM')
        ]
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard financiero"""
        try:
            periodo = request.query_params.get('periodo', timezone.now().strftime('%Y-%m'))
            
            datos = payment_service.generate_payment_reports(periodo)
            
            # Agregar datos adicionales del dashboard
            year, month = periodo.split('-')
            
            # Recaudo por concepto
            conceptos_recaudo = []
            for concepto in ConceptoPago.objects.filter(activo=True):
                facturas = Factura.objects.filter(
                    concepto=concepto,
                    periodo=periodo
                )
                pagos = Pago.objects.filter(
                    fecha_pago__year=year,
                    fecha_pago__month=month,
                    estado='confirmado',
                    pagofactura__factura__concepto=concepto
                ).distinct()
                
                facturado = sum(f.monto_total for f in facturas)
                recaudado = sum(p.monto_total for p in pagos)
                
                if facturado > 0:
                    conceptos_recaudo.append({
                        'concepto': concepto.nombre,
                        'facturado': str(facturado),
                        'recaudado': str(recaudado),
                        'porcentaje': round((recaudado / facturado * 100), 2)
                    })
            
            # Recaudo por método
            metodos_recaudo = []
            for metodo in MetodoPago.objects.filter(activo=True):
                pagos = Pago.objects.filter(
                    fecha_pago__year=year,
                    fecha_pago__month=month,
                    metodo_pago=metodo,
                    estado='confirmado'
                )
                
                if pagos.exists():
                    cantidad = pagos.count()
                    monto = sum(p.monto_total for p in pagos)
                    porcentaje = (monto / datos['total_recaudado'] * 100) if datos['total_recaudado'] > 0 else 0
                    
                    metodos_recaudo.append({
                        'metodo': metodo.nombre,
                        'cantidad': cantidad,
                        'monto': str(monto),
                        'porcentaje': round(porcentaje, 2)
                    })
            
            # Datos de morosidad
            facturas_vencidas = Factura.objects.filter(
                fecha_vencimiento__lt=timezone.now(),
                estado__in=['pendiente', 'parcialmente_pagada']
            )
            
            viviendas_morosas = facturas_vencidas.values('vivienda').distinct().count()
            deuda_total = sum(f.saldo_pendiente for f in facturas_vencidas)
            promedio_deuda = deuda_total / viviendas_morosas if viviendas_morosas > 0 else 0
            
            response_data = {
                'periodo': periodo,
                'resumen': datos,
                'recaudo_por_concepto': conceptos_recaudo,
                'recaudo_por_metodo': metodos_recaudo,
                'morosidad': {
                    'viviendas_morosas': viviendas_morosas,
                    'deuda_total': str(deuda_total),
                    'promedio_deuda': str(promedio_deuda),
                    'facturas_vencidas': facturas_vencidas.count()
                }
            }
            
            return Response({
                'success': True,
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"Error en dashboard financiero: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error generando dashboard: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(operation_id='estado_cuenta_vivienda')
    @action(detail=False, methods=['get'], url_path='estado-cuenta/(?P<vivienda_id>[^/.]+)')
    def estado_cuenta(self, request, vivienda_id=None):
        """Estado de cuenta por vivienda"""
        try:
            vivienda = Vivienda.objects.get(id=vivienda_id)
            
            # Filtros de período
            periodo_desde = request.query_params.get('periodo_desde')
            periodo_hasta = request.query_params.get('periodo_hasta')
            incluir_pagadas = request.query_params.get('incluir_pagadas', 'true').lower() == 'true'
            
            # Obtener facturas
            facturas = Factura.objects.filter(vivienda=vivienda)
            
            if periodo_desde:
                facturas = facturas.filter(periodo__gte=periodo_desde)
            if periodo_hasta:
                facturas = facturas.filter(periodo__lte=periodo_hasta)
            if not incluir_pagadas:
                facturas = facturas.exclude(estado='pagada')
            
            # Calcular resumen
            saldo_total = sum(f.saldo_pendiente for f in facturas.exclude(estado='pagada'))
            facturas_pendientes = facturas.exclude(estado='pagada').count()
            facturas_vencidas = facturas.filter(
                fecha_vencimiento__lt=timezone.now(),
                estado__in=['pendiente', 'parcialmente_pagada']
            ).count()
            
            # Último pago
            ultimo_pago = Pago.objects.filter(
                vivienda=vivienda,
                estado='confirmado'
            ).order_by('-fecha_pago').first()
            
            # Total pagado en el año
            total_pagado_ano = Pago.objects.filter(
                vivienda=vivienda,
                fecha_pago__year=timezone.now().year,
                estado='confirmado'
            ).aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
            
            # Obtener pagos
            pagos = Pago.objects.filter(vivienda=vivienda, estado='confirmado')
            if periodo_desde and periodo_hasta:
                # Convertir período a fechas
                fecha_desde = datetime.strptime(periodo_desde + '-01', '%Y-%m-%d')
                fecha_hasta = datetime.strptime(periodo_hasta + '-01', '%Y-%m-%d')
                fecha_hasta = fecha_hasta.replace(day=28) + timedelta(days=4)
                fecha_hasta = fecha_hasta - timedelta(days=fecha_hasta.day)
                
                pagos = pagos.filter(fecha_pago__range=[fecha_desde, fecha_hasta])
            
            response_data = {
                'vivienda': {
                    'id': vivienda.id,
                    'identificador': vivienda.identificador,
                    'propietario': {
                        'full_name': vivienda.usuario_propietario.get_full_name() if vivienda.usuario_propietario else '',
                        'email': vivienda.usuario_propietario.email if vivienda.usuario_propietario else ''
                    }
                },
                'resumen': {
                    'saldo_total': str(saldo_total),
                    'facturas_pendientes': facturas_pendientes,
                    'facturas_vencidas': facturas_vencidas,
                    'ultimo_pago': ultimo_pago.fecha_pago if ultimo_pago else None,
                    'total_pagado_ano': str(total_pagado_ano)
                },
                'facturas': FacturaListSerializer(facturas.order_by('-fecha_generacion'), many=True).data,
                'pagos': PagoListSerializer(pagos.order_by('-fecha_pago'), many=True).data
            }
            
            return Response({
                'success': True,
                'data': response_data
            })
            
        except Vivienda.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Vivienda no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error en estado de cuenta: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error generando estado de cuenta: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(operation_id='reporte_morosidad')
    @action(detail=False, methods=['get'])
    def morosidad(self, request):
        """Reporte de morosidad"""
        try:
            # Filtros
            dias_vencimiento = int(request.query_params.get('dias_vencimiento', 0))
            monto_minimo = request.query_params.get('monto_minimo', 0)
            bloque = request.query_params.get('bloque')
            
            # Facturas vencidas
            facturas_vencidas = Factura.objects.filter(
                fecha_vencimiento__lt=timezone.now() - timedelta(days=dias_vencimiento),
                estado__in=['pendiente', 'parcialmente_pagada'],
                saldo_pendiente__gte=monto_minimo
            )
            
            if bloque:
                facturas_vencidas = facturas_vencidas.filter(vivienda__bloque=bloque)
            
            # Agrupar por vivienda
            viviendas_morosas = {}
            for factura in facturas_vencidas:
                vivienda_id = factura.vivienda.id
                if vivienda_id not in viviendas_morosas:
                    viviendas_morosas[vivienda_id] = {
                        'vivienda': factura.vivienda,
                        'facturas': [],
                        'deuda_total': Decimal('0.00'),
                        'dias_vencimiento_mayor': 0
                    }
                
                viviendas_morosas[vivienda_id]['facturas'].append(factura)
                viviendas_morosas[vivienda_id]['deuda_total'] += factura.saldo_pendiente
                
                dias_vencido = (timezone.now().date() - factura.fecha_vencimiento.date()).days
                if dias_vencido > viviendas_morosas[vivienda_id]['dias_vencimiento_mayor']:
                    viviendas_morosas[vivienda_id]['dias_vencimiento_mayor'] = dias_vencido
            
            # Preparar respuesta
            detalle_morosidad = []
            total_viviendas = Vivienda.objects.filter(activo=True).count()
            viviendas_morosas_count = len(viviendas_morosas)
            deuda_total_general = Decimal('0.00')
            
            for data in viviendas_morosas.values():
                vivienda = data['vivienda']
                deuda_total_general += data['deuda_total']
                
                # Último pago
                ultimo_pago = Pago.objects.filter(
                    vivienda=vivienda,
                    estado='confirmado'
                ).order_by('-fecha_pago').first()
                
                detalle_morosidad.append({
                    'vivienda': {
                        'id': vivienda.id,
                        'identificador': vivienda.identificador,
                        'propietario': vivienda.usuario_propietario.get_full_name() if vivienda.usuario_propietario else ''
                    },
                    'facturas_vencidas': len(data['facturas']),
                    'deuda_total': str(data['deuda_total']),
                    'dias_vencimiento_mayor': data['dias_vencimiento_mayor'],
                    'ultimo_pago': ultimo_pago.fecha_pago if ultimo_pago else None,
                    'contacto': {
                        'email': vivienda.usuario_propietario.email if vivienda.usuario_propietario else '',
                        'telefono': vivienda.usuario_propietario.telefono if vivienda.usuario_propietario else ''
                    }
                })
            
            # Distribución por rangos
            rangos = [
                {'rango': '1-30 días', 'min': 1, 'max': 30},
                {'rango': '31-60 días', 'min': 31, 'max': 60},
                {'rango': 'Más de 60 días', 'min': 61, 'max': 999999}
            ]
            
            distribucion_rangos = []
            for rango in rangos:
                viviendas_rango = [v for v in viviendas_morosas.values() 
                                 if rango['min'] <= v['dias_vencimiento_mayor'] <= rango['max']]
                
                if viviendas_rango:
                    monto_rango = sum(v['deuda_total'] for v in viviendas_rango)
                    distribucion_rangos.append({
                        'rango': rango['rango'],
                        'viviendas': len(viviendas_rango),
                        'monto': str(monto_rango)
                    })
            
            promedio_deuda = deuda_total_general / viviendas_morosas_count if viviendas_morosas_count > 0 else Decimal('0.00')
            porcentaje_morosidad = (viviendas_morosas_count / total_viviendas * 100) if total_viviendas > 0 else 0
            
            response_data = {
                'fecha_corte': timezone.now(),
                'resumen': {
                    'total_viviendas': total_viviendas,
                    'viviendas_morosas': viviendas_morosas_count,
                    'porcentaje_morosidad': round(porcentaje_morosidad, 2),
                    'deuda_total': str(deuda_total_general),
                    'promedio_deuda': str(promedio_deuda)
                },
                'detalle_morosidad': detalle_morosidad,
                'distribucion_por_rango': distribucion_rangos
            }
            
            return Response({
                'success': True,
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"Error en reporte de morosidad: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error generando reporte de morosidad: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================== STRIPE INTEGRATION ==================

@extend_schema(tags=['Integración Stripe'])
class StripeViewSet(viewsets.ViewSet):
    """ViewSet para integración con Stripe"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        operation_id='crear_payment_intent',
        request=StripePaymentIntentSerializer
    )
    @action(detail=False, methods=['post'], url_path='create-payment-intent')
    def create_payment_intent(self, request):
        """Crear PaymentIntent en Stripe"""
        try:
            serializer = StripePaymentIntentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Validar facturas
            facturas = Factura.objects.filter(
                id__in=serializer.validated_data['facturas']
            )
            
            if not facturas.exists():
                return Response({
                    'success': False,
                    'message': 'No se encontraron facturas válidas'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear PaymentIntent
            metadata = {
                'facturas': ','.join(map(str, serializer.validated_data['facturas'])),
                'user_id': str(request.user.id),
                **serializer.validated_data.get('metadata', {})
            }
            
            intent_data = stripe_service.create_payment_intent(
                amount=serializer.validated_data['amount'],
                currency=serializer.validated_data['currency'],
                metadata=metadata
            )
            
            return Response({
                'success': True,
                'data': intent_data
            })
            
        except Exception as e:
            logger.error(f"Error creando PaymentIntent: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error creando PaymentIntent: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """Webhook de Stripe"""
        try:
            payload = request.body.decode('utf-8')
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
            
            event = stripe_service.process_webhook(payload, sig_header)
            
            # Procesar evento según tipo
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                # Aquí procesar el pago exitoso
                logger.info(f"Payment succeeded: {payment_intent.get('id', 'unknown')}")
                
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                # Aquí procesar el pago fallido
                logger.warning(f"Payment failed: {payment_intent.get('id', 'unknown')}")
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {str(e)}")
            return JsonResponse({'success': False}, status=400)


# ================== LEGACY VIEWS (COMPATIBILIDAD) ==================

@extend_schema(tags=['Legacy - Compatibilidad'])
class TipoPagoViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de pago (legacy)"""
    queryset = TipoPago.objects.all()
    serializer_class = TipoPagoSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['Legacy - Compatibilidad'])
class DeudaViewSet(viewsets.ModelViewSet):
    """ViewSet para deudas (legacy)"""
    queryset = Deuda.objects.all()
    serializer_class = DeudaSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['Legacy - Compatibilidad'])
class DetalleDeudaViewSet(viewsets.ModelViewSet):
    """ViewSet para detalles de deuda (legacy)"""
    queryset = DetalleDeuda.objects.all()
    serializer_class = DetalleDeudaSerializer
    permission_classes = [IsAuthenticated]