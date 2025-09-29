# API ENDPOINTS - PAYMENTS MODULE

## MÓDULO: GESTIÓN DE PAGOS Y FACTURACIÓN

### Descripción
Este módulo maneja la administración de pagos, facturación, conceptos de cobro, métodos de pago y gestión financiera del condominio.

---

## 💰 GESTIÓN DE CONCEPTOS DE PAGO

### 1. Listar Conceptos de Pago
**CU-WEB-004: Gestionar Conceptos de Pago**

```http
GET /api/payments/conceptos/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20)
- `search`: Búsqueda por nombre o descripción
- `tipo`: Filtrar por tipo (fijo, variable, extraordinario)
- `activo`: Estado activo (true/false)
- `obligatorio`: Solo conceptos obligatorios (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "nombre": "Cuota de Administración",
        "descripcion": "Cuota mensual por administración del condominio",
        "tipo": "fijo",
        "valor_base": "250000.00",
        "es_obligatorio": true,
        "frecuencia": "mensual",
        "aplica_a_todos": true,
        "fecha_creacion": "2025-01-01T00:00:00Z",
        "activo": true,
        "total_facturas_generadas": 1440,
        "total_recaudado": "360000000.00"
      },
      {
        "id": 2,
        "nombre": "Fondo de Reserva",
        "descripcion": "Aporte mensual al fondo de reserva",
        "tipo": "fijo",
        "valor_base": "50000.00",
        "es_obligatorio": true,
        "frecuencia": "mensual",
        "aplica_a_todos": true,
        "fecha_creacion": "2025-01-01T00:00:00Z",
        "activo": true,
        "total_facturas_generadas": 1440,
        "total_recaudado": "72000000.00"
      }
    ]
  }
}
```

---

### 2. Crear Nuevo Concepto de Pago
```http
POST /api/payments/conceptos/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "nombre": "Mantenimiento Ascensor",
  "descripcion": "Cuota especial para mantenimiento de ascensores",
  "tipo": "extraordinario",
  "valor_base": "75000.00",
  "es_obligatorio": true,
  "frecuencia": "unica",
  "aplica_a_todos": false,
  "fecha_inicio": "2025-10-01T00:00:00Z",
  "fecha_fin": "2025-10-31T23:59:59Z",
  "criterios_aplicacion": {
    "pisos_minimo": 2,
    "torres": ["TORRE-A", "TORRE-B"]
  }
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Concepto de pago creado exitosamente",
  "data": {
    "id": 16,
    "nombre": "Mantenimiento Ascensor",
    "descripcion": "Cuota especial para mantenimiento de ascensores",
    "tipo": "extraordinario",
    "valor_base": "75000.00",
    "es_obligatorio": true,
    "frecuencia": "unica",
    "aplica_a_todos": false,
    "fecha_creacion": "2025-09-29T20:00:00Z",
    "activo": true,
    "viviendas_aplicables": 80
  }
}
```

---

### 3. Actualizar Concepto de Pago
```http
PUT /api/payments/conceptos/{concepto_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "valor_base": "260000.00",
  "descripcion": "Cuota mensual por administración del condominio - Actualizada 2025",
  "fecha_vigencia": "2025-11-01T00:00:00Z"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Concepto de pago actualizado exitosamente",
  "data": {
    "id": 1,
    "nombre": "Cuota de Administración",
    "valor_base": "260000.00",
    "valor_anterior": "250000.00",
    "fecha_actualizacion": "2025-09-29T20:15:00Z",
    "fecha_vigencia": "2025-11-01T00:00:00Z",
    "viviendas_afectadas": 120
  }
}
```

---

## 🧾 GESTIÓN DE FACTURAS

### 4. Listar Facturas
**CU-WEB-005: Consultar Estados de Cuenta**

```http
GET /api/payments/facturas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `vivienda`: ID de vivienda específica
- `estado`: Estado de factura (pendiente, pagada, vencida, anulada)
- `periodo`: Periodo específico (YYYY-MM)
- `concepto`: ID de concepto de pago
- `fecha_vencimiento_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_vencimiento_hasta`: Fecha hasta (YYYY-MM-DD)
- `monto_minimo`: Monto mínimo
- `monto_maximo`: Monto máximo

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 2880,
    "next": "http://api.backresidences.com/api/payments/facturas/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1001,
        "numero_factura": "FAC-2025-10-001001",
        "vivienda": {
          "id": 1,
          "identificador": "TORRE-A-101",
          "propietario": "Juan Pérez"
        },
        "concepto": {
          "id": 1,
          "nombre": "Cuota de Administración"
        },
        "periodo": "2025-10",
        "fecha_generacion": "2025-10-01T00:00:00Z",
        "fecha_vencimiento": "2025-10-15T23:59:59Z",
        "monto": "250000.00",
        "estado": "pendiente",
        "dias_vencido": 0,
        "saldo_pendiente": "250000.00",
        "tiene_descuentos": false,
        "tiene_intereses": false,
        "pagos_parciales": []
      },
      {
        "id": 1002,
        "numero_factura": "FAC-2025-09-001002",
        "vivienda": {
          "id": 1,
          "identificador": "TORRE-A-101",
          "propietario": "Juan Pérez"
        },
        "concepto": {
          "id": 1,
          "nombre": "Cuota de Administración"
        },
        "periodo": "2025-09",
        "fecha_generacion": "2025-09-01T00:00:00Z",
        "fecha_vencimiento": "2025-09-15T23:59:59Z",
        "monto": "250000.00",
        "estado": "pagada",
        "fecha_pago": "2025-09-10T14:30:00Z",
        "saldo_pendiente": "0.00",
        "tiene_descuentos": false,
        "tiene_intereses": false,
        "pagos_aplicados": [
          {
            "id": 501,
            "monto": "250000.00",
            "fecha": "2025-09-10T14:30:00Z",
            "metodo": "transferencia"
          }
        ]
      }
    ]
  }
}
```

---

### 5. Generar Facturas Masivas
```http
POST /api/payments/facturas/generar-masivas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "conceptos": [1, 2],
  "periodo": "2025-11",
  "fecha_vencimiento": "2025-11-15T23:59:59Z",
  "filtros": {
    "bloques": ["TORRE-A", "TORRE-B"],
    "excluir_morosos": true,
    "solo_ocupadas": true
  },
  "observaciones": "Facturación noviembre 2025 - Incremento cuota administración"
}
```

**Response 202 Accepted:**
```json
{
  "success": true,
  "message": "Proceso de facturación masiva iniciado",
  "data": {
    "proceso_id": "FACT-MASIVA-2025-11-001",
    "total_viviendas": 115,
    "conceptos_aplicar": 2,
    "fecha_inicio": "2025-09-29T20:30:00Z",
    "estado": "en_proceso",
    "url_seguimiento": "/api/payments/procesos/FACT-MASIVA-2025-11-001/estado/"
  }
}
```

---

### 6. Detalle de Factura
```http
GET /api/payments/facturas/{factura_id}/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "id": 1001,
    "numero_factura": "FAC-2025-10-001001",
    "vivienda": {
      "id": 1,
      "identificador": "TORRE-A-101",
      "bloque": "TORRE-A",
      "propietario": {
        "id": 15,
        "full_name": "Juan Pérez",
        "email": "juan.perez@email.com",
        "telefono": "+573001234567"
      }
    },
    "concepto": {
      "id": 1,
      "nombre": "Cuota de Administración",
      "descripcion": "Cuota mensual por administración del condominio"
    },
    "periodo": "2025-10",
    "fecha_generacion": "2025-10-01T00:00:00Z",
    "fecha_vencimiento": "2025-10-15T23:59:59Z",
    "monto_original": "250000.00",
    "descuentos": "0.00",
    "intereses": "0.00",
    "monto_total": "250000.00",
    "estado": "pendiente",
    "saldo_pendiente": "250000.00",
    "pagos_aplicados": [],
    "historial_estados": [
      {
        "estado": "generada",
        "fecha": "2025-10-01T00:00:00Z",
        "usuario": "Sistema"
      }
    ],
    "archivo_pdf": "https://storage.example.com/facturas/FAC-2025-10-001001.pdf"
  }
}
```

---

## 💳 GESTIÓN DE PAGOS

### 7. Registrar Pago
**CU-WEB-006: Procesar Pagos**

```http
POST /api/payments/pagos/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "vivienda": 1,
  "facturas": [1001, 1002],
  "monto_total": "500000.00",
  "metodo_pago": "transferencia",
  "numero_referencia": "TRF-20250929-001234",
  "fecha_pago": "2025-09-29T15:00:00Z",
  "observaciones": "Pago dos cuotas octubre y noviembre",
  "archivo_comprobante": "base64_encoded_receipt_file"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Pago registrado exitosamente",
  "data": {
    "id": 502,
    "numero_pago": "PAG-2025-000502",
    "vivienda": {
      "id": 1,
      "identificador": "TORRE-A-101"
    },
    "monto_total": "500000.00",
    "metodo_pago": "transferencia",
    "numero_referencia": "TRF-20250929-001234",
    "fecha_pago": "2025-09-29T15:00:00Z",
    "fecha_registro": "2025-09-29T20:45:00Z",
    "estado": "confirmado",
    "facturas_aplicadas": [
      {
        "factura_id": 1001,
        "monto_aplicado": "250000.00",
        "estado_factura": "pagada"
      },
      {
        "factura_id": 1002,
        "monto_aplicado": "250000.00",
        "estado_factura": "pagada"
      }
    ],
    "recibo_url": "https://storage.example.com/recibos/PAG-2025-000502.pdf"
  }
}
```

---

### 8. Listar Pagos
```http
GET /api/payments/pagos/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `vivienda`: ID de vivienda específica
- `metodo_pago`: Método de pago específico
- `estado`: Estado del pago (pendiente, confirmado, rechazado)
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
- `monto_minimo`: Monto mínimo
- `monto_maximo`: Monto máximo

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 1250,
    "next": "http://api.backresidences.com/api/payments/pagos/?page=2",
    "previous": null,
    "results": [
      {
        "id": 502,
        "numero_pago": "PAG-2025-000502",
        "vivienda": {
          "id": 1,
          "identificador": "TORRE-A-101",
          "propietario": "Juan Pérez"
        },
        "monto_total": "500000.00",
        "metodo_pago": "transferencia",
        "fecha_pago": "2025-09-29T15:00:00Z",
        "estado": "confirmado",
        "facturas_cubiertas": 2,
        "numero_referencia": "TRF-20250929-001234"
      }
    ]
  }
}
```

---

### 9. Aplicar Pago a Facturas
```http
POST /api/payments/pagos/{pago_id}/aplicar-facturas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "distribuciones": [
    {
      "factura_id": 1003,
      "monto": "150000.00"
    },
    {
      "factura_id": 1004,
      "monto": "100000.00"
    }
  ],
  "criterio_aplicacion": "manual",
  "observaciones": "Aplicación manual según solicitud del propietario"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Pago aplicado a facturas exitosamente",
  "data": {
    "pago_id": 502,
    "monto_aplicado": "250000.00",
    "facturas_actualizadas": [
      {
        "factura_id": 1003,
        "monto_aplicado": "150000.00",
        "saldo_anterior": "200000.00",
        "saldo_nuevo": "50000.00",
        "estado": "parcialmente_pagada"
      },
      {
        "factura_id": 1004,
        "monto_aplicado": "100000.00",
        "saldo_anterior": "100000.00",
        "saldo_nuevo": "0.00",
        "estado": "pagada"
      }
    ]
  }
}
```

---

### 10. Reversar Pago
```http
POST /api/payments/pagos/{pago_id}/reversar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "motivo": "Error en el monto registrado",
  "observaciones": "El pago real fue por un monto menor"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Pago reversado exitosamente",
  "data": {
    "pago_id": 502,
    "estado_anterior": "confirmado",
    "estado_nuevo": "reversado",
    "fecha_reverso": "2025-09-29T21:00:00Z",
    "facturas_afectadas": [
      {
        "factura_id": 1001,
        "estado_restaurado": "pendiente",
        "saldo_restaurado": "250000.00"
      }
    ]
  }
}
```

---

## 💰 MÉTODOS DE PAGO

### 11. Listar Métodos de Pago
```http
GET /api/payments/metodos-pago/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Transferencia Bancaria",
      "codigo": "transferencia",
      "descripcion": "Transferencia a cuenta del condominio",
      "requiere_referencia": true,
      "requiere_comprobante": true,
      "activo": true,
      "configuracion": {
        "banco": "Banco de Bogotá",
        "numero_cuenta": "123456789",
        "tipo_cuenta": "Ahorros",
        "titular": "Conjunto Residencial Torres del Sol"
      }
    },
    {
      "id": 2,
      "nombre": "PSE",
      "codigo": "pse",
      "descripcion": "Pago en línea PSE",
      "requiere_referencia": false,
      "requiere_comprobante": false,
      "activo": true,
      "configuracion": {
        "proveedor": "PayU",
        "comision": "3.5"
      }
    }
  ]
}
```

---

### 12. Configurar Método de Pago
```http
POST /api/payments/metodos-pago/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "nombre": "Tarjeta de Crédito",
  "codigo": "tarjeta_credito",
  "descripcion": "Pago con tarjeta de crédito en línea",
  "requiere_referencia": false,
  "requiere_comprobante": false,
  "activo": true,
  "configuracion": {
    "proveedor": "Mercado Pago",
    "comision": "3.99",
    "cuotas_disponibles": [1, 3, 6, 12]
  }
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Método de pago configurado exitosamente",
  "data": {
    "id": 5,
    "nombre": "Tarjeta de Crédito",
    "codigo": "tarjeta_credito",
    "activo": true,
    "fecha_configuracion": "2025-09-29T21:15:00Z"
  }
}
```

---

## 📊 REPORTES FINANCIEROS

### 13. Dashboard Financiero
```http
GET /api/payments/dashboard/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `periodo`: Periodo específico (YYYY-MM, default: mes actual)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": "2025-10",
    "resumen": {
      "total_facturado": "30000000.00",
      "total_recaudado": "27500000.00",
      "pendiente_cobro": "2500000.00",
      "porcentaje_recaudo": 91.67,
      "facturas_generadas": 240,
      "facturas_pagadas": 220,
      "facturas_vencidas": 15,
      "pagos_procesados": 185
    },
    "recaudo_por_concepto": [
      {
        "concepto": "Cuota de Administración",
        "facturado": "25000000.00",
        "recaudado": "23750000.00",
        "porcentaje": 95.0
      },
      {
        "concepto": "Fondo de Reserva",
        "facturado": "5000000.00",
        "recaudado": "3750000.00",
        "porcentaje": 75.0
      }
    ],
    "recaudo_por_metodo": [
      {
        "metodo": "transferencia",
        "cantidad": 120,
        "monto": "18500000.00",
        "porcentaje": 67.27
      },
      {
        "metodo": "pse",
        "cantidad": 45,
        "monto": "6500000.00",
        "porcentaje": 23.64
      }
    ],
    "morosidad": {
      "viviendas_morosas": 15,
      "deuda_total": "3750000.00",
      "promedio_deuda": "250000.00",
      "facturas_vencidas": 28
    }
  }
}
```

---

### 14. Estado de Cuenta por Vivienda
```http
GET /api/payments/estado-cuenta/{vivienda_id}/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `periodo_desde`: Periodo desde (YYYY-MM)
- `periodo_hasta`: Periodo hasta (YYYY-MM)
- `incluir_pagadas`: Incluir facturas pagadas (true/false, default: true)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "vivienda": {
      "id": 1,
      "identificador": "TORRE-A-101",
      "propietario": {
        "full_name": "Juan Pérez",
        "email": "juan.perez@email.com"
      }
    },
    "resumen": {
      "saldo_total": "250000.00",
      "facturas_pendientes": 1,
      "facturas_vencidas": 0,
      "ultimo_pago": "2025-09-10T14:30:00Z",
      "total_pagado_ano": "2250000.00"
    },
    "facturas": [
      {
        "id": 1001,
        "numero_factura": "FAC-2025-10-001001",
        "concepto": "Cuota de Administración",
        "periodo": "2025-10",
        "fecha_vencimiento": "2025-10-15T23:59:59Z",
        "monto": "250000.00",
        "estado": "pendiente",
        "dias_vencimiento": -1
      }
    ],
    "pagos": [
      {
        "id": 501,
        "numero_pago": "PAG-2025-000501",
        "fecha": "2025-09-10T14:30:00Z",
        "monto": "250000.00",
        "metodo": "transferencia",
        "concepto_aplicado": "Cuota de Administración - Sep 2025"
      }
    ]
  }
}
```

---

### 15. Reporte de Morosidad
```http
GET /api/payments/reportes/morosidad/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `dias_vencimiento`: Filtrar por días de vencimiento mínimo
- `monto_minimo`: Deuda mínima para incluir
- `bloque`: Filtrar por bloque específico

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "fecha_corte": "2025-09-29T21:30:00Z",
    "resumen": {
      "total_viviendas": 120,
      "viviendas_morosas": 15,
      "porcentaje_morosidad": 12.5,
      "deuda_total": "3750000.00",
      "promedio_deuda": "250000.00"
    },
    "detalle_morosidad": [
      {
        "vivienda": {
          "id": 25,
          "identificador": "TORRE-B-205",
          "propietario": "María García"
        },
        "facturas_vencidas": 3,
        "deuda_total": "750000.00",
        "dias_vencimiento_mayor": 45,
        "ultimo_pago": "2025-06-15T00:00:00Z",
        "contacto": {
          "email": "maria.garcia@email.com",
          "telefono": "+573009876543"
        }
      }
    ],
    "distribucion_por_rango": [
      {
        "rango": "1-30 días",
        "viviendas": 8,
        "monto": "1500000.00"
      },
      {
        "rango": "31-60 días",
        "viviendas": 4,
        "monto": "1250000.00"
      },
      {
        "rango": "Más de 60 días",
        "viviendas": 3,
        "monto": "1000000.00"
      }
    ]
  }
}
```

---

### 16. Reporte de Recaudo
```http
GET /api/payments/reportes/recaudo/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `periodo_desde`: Periodo desde (YYYY-MM)
- `periodo_hasta`: Periodo hasta (YYYY-MM)
- `agrupar_por`: Agrupación (concepto, metodo_pago, vivienda, periodo)
- `formato`: Formato del reporte (json, pdf, excel)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "desde": "2025-01",
      "hasta": "2025-09"
    },
    "resumen_general": {
      "total_facturado": "270000000.00",
      "total_recaudado": "247500000.00",
      "porcentaje_recaudo": 91.67,
      "facturas_generadas": 2160,
      "pagos_procesados": 1665
    },
    "recaudo_mensual": [
      {
        "periodo": "2025-09",
        "facturado": "30000000.00",
        "recaudado": "27500000.00",
        "porcentaje": 91.67
      }
    ],
    "top_pagadores": [
      {
        "vivienda": "TORRE-A-101",
        "propietario": "Juan Pérez",
        "total_pagado": "2250000.00",
        "pagos_a_tiempo": 9,
        "total_pagos": 9
      }
    ],
    "metodos_mas_usados": [
      {
        "metodo": "transferencia",
        "cantidad_pagos": 1080,
        "monto_total": "166500000.00",
        "porcentaje": 67.27
      }
    ]
  }
}
```

---

### 17. Proyección de Ingresos
```http
GET /api/payments/proyecciones/ingresos/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `periodo_inicio`: Periodo de inicio para proyección (YYYY-MM)
- `meses_proyeccion`: Número de meses a proyectar (default: 12)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo_proyeccion": {
      "inicio": "2025-10",
      "fin": "2026-09",
      "meses": 12
    },
    "proyeccion_mensual": [
      {
        "periodo": "2025-10",
        "ingresos_proyectados": "31200000.00",
        "base_calculo": {
          "cuotas_administracion": "26000000.00",
          "fondo_reserva": "5200000.00"
        },
        "factores": {
          "incremento_anual": 4.0,
          "ocupacion_estimada": 98.0
        }
      }
    ],
    "resumen_anual": {
      "total_proyectado": "374400000.00",
      "promedio_mensual": "31200000.00",
      "incremento_vs_ano_anterior": "4.0%"
    },
    "alertas": [
      {
        "tipo": "incremento_cuota",
        "fecha": "2025-11-01",
        "descripcion": "Aplicación de incremento anual del 4%"
      }
    ]
  }
}
```

---

### 18. Exportar Datos Financieros
```http
POST /api/payments/export/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "tipo_reporte": "estado_cuenta_general",
  "formato": "excel",
  "periodo": {
    "desde": "2025-01",
    "hasta": "2025-09"
  },
  "incluir": [
    "facturas",
    "pagos",
    "morosidad",
    "proyecciones"
  ],
  "filtros": {
    "solo_morosos": false,
    "conceptos": [1, 2],
    "bloques": ["TORRE-A", "TORRE-B"]
  }
}
```

**Response 202 Accepted:**
```json
{
  "success": true,
  "message": "Exportación iniciada exitosamente",
  "data": {
    "exportacion_id": "EXP-FIN-001-2025",
    "url_descarga": "https://storage.example.com/exports/financiero/EXP-FIN-001-2025.xlsx",
    "fecha_generacion": "2025-09-29T21:45:00Z",
    "expira_en": "2025-10-06T21:45:00Z",
    "total_registros": 5280,
    "url_seguimiento": "/api/payments/exports/EXP-FIN-001-2025/estado/"
  }
}
```

---

### 19. Generar Paz y Salvo
```http
POST /api/payments/paz-y-salvo/{vivienda_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "fecha_corte": "2025-09-29T23:59:59Z",
  "incluir_proyecciones": false,
  "observaciones": "Paz y salvo para trámite de venta"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Paz y salvo generado exitosamente",
  "data": {
    "numero_documento": "PYS-2025-000045",
    "vivienda": {
      "id": 1,
      "identificador": "TORRE-A-101",
      "propietario": "Juan Pérez"
    },
    "fecha_corte": "2025-09-29T23:59:59Z",
    "estado_financiero": {
      "saldo_pendiente": "0.00",
      "facturas_pendientes": 0,
      "ultimo_pago": "2025-09-10T14:30:00Z"
    },
    "validez": "30 días",
    "fecha_vencimiento": "2025-10-29T23:59:59Z",
    "archivo_pdf": "https://storage.example.com/paz-y-salvos/PYS-2025-000045.pdf",
    "codigo_verificacion": "PYS45-9A8B-2025"
  }
}
```

---

## ⚠️ CÓDIGOS DE ERROR ESPECÍFICOS

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos de pago inválidos |
| 401 | Unauthorized - Token inválido |
| 403 | Forbidden - Sin permisos financieros |
| 404 | Not Found - Factura/Pago no encontrado |
| 409 | Conflict - Factura ya pagada o referencia duplicada |
| 422 | Unprocessable Entity - Monto insuficiente o distribución inválida |
| 423 | Locked - Proceso de facturación en curso |
| 424 | Failed Dependency - Error en procesador de pagos |
| 500 | Internal Server Error - Error del servidor |

---

## 🔒 PERMISOS REQUERIDOS

| Endpoint | Permiso Requerido |
|----------|-------------------|
| GET /conceptos/ | `payments.view_conceptopago` |
| POST /conceptos/ | `payments.add_conceptopago` |
| GET /facturas/ | `payments.view_factura` |
| POST /facturas/generar-masivas/ | `payments.facturar_masivo` |
| POST /pagos/ | `payments.add_pago` |
| GET /reportes/morosidad/ | `payments.view_reportes_financieros` |

---

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Transaccionalidad**: Todos los pagos se procesan en transacciones atómicas
2. **Auditoria**: Se mantiene historial completo de cambios financieros
3. **Conciliación**: Sistema de conciliación automática con extractos bancarios
4. **Notificaciones**: Alertas automáticas por vencimientos y pagos recibidos
5. **Integraciones**: Compatible con PSE, tarjetas de crédito y bancos
6. **Reportería**: Generación automática de reportes financieros mensuales