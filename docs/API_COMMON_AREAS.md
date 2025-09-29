# API ENDPOINTS - COMMON AREAS MODULE

## MÓDULO: GESTIÓN DE ÁREAS COMUNES Y RESERVAS

### Descripción
Este módulo maneja la administración de áreas comunes, reservas, tarifas de uso y reportes de utilización en el condominio.

---

## 🏢 GESTIÓN DE ÁREAS COMUNES

### 1. Listar Áreas Comunes
**CU-WEB-007: Gestionar Áreas Comunes y Reservas**

```http
GET /api/common-areas/areas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20)
- `search`: Búsqueda por nombre o descripción
- `tipo`: Filtrar por tipo de área
- `activa`: Estado activo (true/false)
- `requiere_pago`: Areas que requieren pago (true/false)
- `disponible`: Solo áreas disponibles para reserva (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "nombre": "Salón Social",
        "descripcion": "Salón principal para eventos y reuniones",
        "tipo": "salon_eventos",
        "capacidad_maxima": 80,
        "horario_inicio": "08:00:00",
        "horario_fin": "22:00:00",
        "tarifa_uso": "150000.00",
        "requiere_pago": true,
        "tiempo_minimo_reserva": 4,
        "tiempo_maximo_reserva": 8,
        "activa": true,
        "disponible_hoy": true,
        "proxima_disponibilidad": "2025-09-30T08:00:00Z",
        "reservas_activas": 2,
        "total_reservas_mes": 15,
        "equipamiento": [
          "Sistema de sonido",
          "Proyector",
          "Aire acondicionado",
          "Cocina auxiliar"
        ],
        "imagen_principal": "https://storage.example.com/areas/salon_social_1.jpg"
      },
      {
        "id": 2,
        "nombre": "Piscina",
        "descripcion": "Piscina adultos y niños",
        "tipo": "piscina",
        "capacidad_maxima": 50,
        "horario_inicio": "06:00:00",
        "horario_fin": "20:00:00",
        "tarifa_uso": "0.00",
        "requiere_pago": false,
        "tiempo_minimo_reserva": 2,
        "tiempo_maximo_reserva": 6,
        "activa": true,
        "disponible_hoy": true,
        "reservas_activas": 0,
        "total_reservas_mes": 45,
        "equipamiento": [
          "Salvavidas",
          "Equipos de limpieza",
          "Zona BBQ adyacente"
        ]
      }
    ]
  }
}
```

---

### 2. Obtener Detalles de Área Común
```http
GET /api/common-areas/areas/{area_id}/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "nombre": "Salón Social",
    "descripcion": "Salón principal para eventos y reuniones sociales del condominio",
    "tipo": "salon_eventos",
    "capacidad_maxima": 80,
    "horario_inicio": "08:00:00",
    "horario_fin": "22:00:00",
    "tarifa_uso": "150000.00",
    "requiere_pago": true,
    "tiempo_minimo_reserva": 4,
    "tiempo_maximo_reserva": 8,
    "dias_anticipacion_max": 30,
    "dias_anticipacion_min": 2,
    "activa": true,
    "fecha_creacion": "2025-01-15T10:00:00Z",
    "equipamiento": [
      "Sistema de sonido profesional",
      "Proyector Full HD",
      "Aire acondicionado",
      "Cocina auxiliar equipada",
      "Mesas y sillas para 80 personas",
      "Vajilla completa"
    ],
    "normas_uso": [
      "Prohibido fumar en el interior",
      "Música máximo hasta las 22:00",
      "Dejar el área limpia y ordenada",
      "Reportar cualquier daño inmediatamente"
    ],
    "imagenes": [
      "https://storage.example.com/areas/salon_social_1.jpg",
      "https://storage.example.com/areas/salon_social_2.jpg",
      "https://storage.example.com/areas/salon_social_3.jpg"
    ],
    "contacto_administracion": {
      "responsable": "María González",
      "telefono": "+573008765432",
      "extension": "101"
    },
    "estadisticas": {
      "reservas_mes_actual": 15,
      "reservas_mes_anterior": 12,
      "promedio_duracion": 5.5,
      "ocupacion_porcentaje": 68.5
    }
  }
}
```

---

### 3. Crear Nueva Área Común
```http
POST /api/common-areas/areas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "nombre": "Gimnasio",
  "descripcion": "Gimnasio equipado para uso de residentes",
  "tipo": "gimnasio",
  "capacidad_maxima": 20,
  "horario_inicio": "05:00:00",
  "horario_fin": "23:00:00",
  "tarifa_uso": "25000.00",
  "requiere_pago": true,
  "tiempo_minimo_reserva": 1,
  "tiempo_maximo_reserva": 3,
  "dias_anticipacion_max": 7,
  "dias_anticipacion_min": 1,
  "equipamiento": [
    "Máquinas cardiovasculares",
    "Pesas libres",
    "Colchonetas",
    "Aire acondicionado"
  ],
  "normas_uso": [
    "Uso obligatorio de toalla",
    "Limpiar equipos después del uso",
    "Máximo 1 hora en horarios pico"
  ]
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Área común creada exitosamente",
  "data": {
    "id": 13,
    "nombre": "Gimnasio",
    "descripcion": "Gimnasio equipado para uso de residentes",
    "tipo": "gimnasio",
    "capacidad_maxima": 20,
    "tarifa_uso": "25000.00",
    "requiere_pago": true,
    "activa": true,
    "fecha_creacion": "2025-09-29T22:00:00Z",
    "disponible_desde": "2025-10-01T05:00:00Z"
  }
}
```

---

### 4. Actualizar Área Común
```http
PUT /api/common-areas/areas/{area_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "tarifa_uso": "175000.00",
  "capacidad_maxima": 85,
  "equipamiento": [
    "Sistema de sonido profesional actualizado",
    "Proyector 4K",
    "Aire acondicionado",
    "Cocina auxiliar equipada",
    "Mesas y sillas para 85 personas",
    "Vajilla completa",
    "Sistema de iluminación LED"
  ]
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Área común actualizada exitosamente",
  "data": {
    "id": 1,
    "nombre": "Salón Social",
    "tarifa_uso": "175000.00",
    "capacidad_maxima": 85,
    "fecha_actualizacion": "2025-09-29T22:15:00Z",
    "cambios_aplicados": [
      "Actualización de tarifa",
      "Incremento de capacidad",
      "Nuevo equipamiento agregado"
    ]
  }
}
```

---

### 5. Consultar Disponibilidad
```http
GET /api/common-areas/areas/{area_id}/disponibilidad/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `fecha_inicio`: Fecha inicio consulta (YYYY-MM-DD)
- `fecha_fin`: Fecha fin consulta (YYYY-MM-DD)
- `duracion_horas`: Duración deseada en horas

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "area": {
      "id": 1,
      "nombre": "Salón Social"
    },
    "periodo_consulta": {
      "fecha_inicio": "2025-09-30",
      "fecha_fin": "2025-10-06"
    },
    "disponibilidad_por_dia": [
      {
        "fecha": "2025-09-30",
        "dia_semana": "lunes",
        "disponible": true,
        "horarios_libres": [
          {
            "inicio": "08:00:00",
            "fin": "14:00:00"
          },
          {
            "inicio": "18:00:00",
            "fin": "22:00:00"
          }
        ],
        "reservas_existentes": [
          {
            "inicio": "14:00:00",
            "fin": "18:00:00",
            "evento": "Reunión de Copropietarios"
          }
        ]
      }
    ],
    "sugerencias": [
      {
        "fecha": "2025-10-01",
        "hora_inicio": "08:00:00",
        "hora_fin": "12:00:00",
        "disponibilidad": "completa"
      }
    ]
  }
}
```

---

## 📅 GESTIÓN DE RESERVAS

### 6. Listar Reservas
```http
GET /api/common-areas/reservas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `area`: ID de área específica
- `usuario`: ID de usuario específico
- `vivienda`: ID de vivienda específica
- `estado`: Estado de reserva (pendiente, confirmada, cancelada, completada)
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
- `proximas`: Solo reservas próximas (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 45,
    "next": "http://api.backresidences.com/api/common-areas/reservas/?page=2",
    "previous": null,
    "results": [
      {
        "id": 101,
        "area": {
          "id": 1,
          "nombre": "Salón Social",
          "tipo": "salon_eventos"
        },
        "usuario": {
          "id": 15,
          "full_name": "Juan Pérez",
          "vivienda": "TORRE-A-101"
        },
        "fecha_reserva": "2025-10-05",
        "hora_inicio": "14:00:00",
        "hora_fin": "18:00:00",
        "duracion_horas": 4,
        "proposito": "Cumpleaños infantil",
        "numero_asistentes": 25,
        "estado": "confirmada",
        "monto_total": "150000.00",
        "estado_pago": "pagado",
        "fecha_solicitud": "2025-09-25T10:30:00Z",
        "fecha_confirmacion": "2025-09-25T14:00:00Z",
        "dias_restantes": 6,
        "puede_cancelar": true,
        "observaciones": "Decoración con globos permitida"
      },
      {
        "id": 102,
        "area": {
          "id": 2,
          "nombre": "Piscina",
          "tipo": "piscina"
        },
        "usuario": {
          "id": 28,
          "full_name": "Ana López",
          "vivienda": "TORRE-B-205"
        },
        "fecha_reserva": "2025-09-30",
        "hora_inicio": "10:00:00",
        "hora_fin": "14:00:00",
        "duracion_horas": 4,
        "proposito": "Reunión familiar",
        "numero_asistentes": 15,
        "estado": "confirmada",
        "monto_total": "0.00",
        "estado_pago": "no_aplica",
        "fecha_solicitud": "2025-09-28T16:45:00Z",
        "dias_restantes": 1
      }
    ]
  }
}
```

---

### 7. Crear Nueva Reserva
```http
POST /api/common-areas/reservas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "area": 1,
  "fecha_reserva": "2025-10-12",
  "hora_inicio": "15:00:00",
  "hora_fin": "20:00:00",
  "proposito": "Fiesta de graduación",
  "numero_asistentes": 45,
  "observaciones": "Requiere equipo de sonido especial",
  "contacto_emergencia": {
    "nombre": "María Pérez",
    "telefono": "+573009876543"
  },
  "servicios_adicionales": ["decoracion", "limpieza_especial"]
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Reserva creada exitosamente",
  "data": {
    "id": 103,
    "numero_reserva": "RES-2025-000103",
    "area": {
      "id": 1,
      "nombre": "Salón Social"
    },
    "fecha_reserva": "2025-10-12",
    "hora_inicio": "15:00:00",
    "hora_fin": "20:00:00",
    "duracion_horas": 5,
    "proposito": "Fiesta de graduación",
    "numero_asistentes": 45,
    "estado": "pendiente",
    "monto_total": "187500.00",
    "desglose_costo": {
      "tarifa_base": "150000.00",
      "hora_adicional": "37500.00",
      "servicios_adicionales": "0.00"
    },
    "estado_pago": "pendiente",
    "fecha_limite_pago": "2025-10-05T23:59:59Z",
    "instrucciones_pago": {
      "metodo": "transferencia",
      "cuenta": "123456789",
      "referencia": "RES-103-2025"
    }
  }
}
```

---

### 8. Actualizar Reserva
```http
PUT /api/common-areas/reservas/{reserva_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "numero_asistentes": 50,
  "observaciones": "Requiere equipo de sonido especial y micrófono inalámbrico",
  "servicios_adicionales": ["decoracion", "limpieza_especial", "seguridad"]
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Reserva actualizada exitosamente",
  "data": {
    "id": 103,
    "numero_asistentes": 50,
    "monto_anterior": "187500.00",
    "monto_nuevo": "225000.00",
    "diferencia": "37500.00",
    "estado_pago": "diferencia_pendiente",
    "fecha_actualizacion": "2025-09-29T22:45:00Z"
  }
}
```

---

### 9. Cancelar Reserva
```http
POST /api/common-areas/reservas/{reserva_id}/cancelar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "motivo": "Cambio de fecha del evento",
  "solicitar_reembolso": true
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Reserva cancelada exitosamente",
  "data": {
    "id": 103,
    "estado_anterior": "confirmada",
    "estado_nuevo": "cancelada",
    "fecha_cancelacion": "2025-09-29T22:50:00Z",
    "motivo": "Cambio de fecha del evento",
    "reembolso": {
      "aplica": true,
      "monto": "187500.00",
      "descuento_penalizacion": "18750.00",
      "monto_reembolso": "168750.00",
      "tiempo_procesamiento": "5-7 días hábiles"
    }
  }
}
```

---

### 10. Confirmar Pago de Reserva
```http
POST /api/common-areas/reservas/{reserva_id}/confirmar-pago/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "metodo_pago": "transferencia",
  "numero_referencia": "TRF-20250929-005678",
  "monto_pagado": "187500.00",
  "fecha_pago": "2025-09-29T20:00:00Z",
  "comprobante": "base64_encoded_receipt_file"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Pago confirmado y reserva activada",
  "data": {
    "reserva_id": 103,
    "estado_anterior": "pendiente",
    "estado_nuevo": "confirmada",
    "pago": {
      "id": 205,
      "monto": "187500.00",
      "metodo": "transferencia",
      "referencia": "TRF-20250929-005678",
      "fecha": "2025-09-29T20:00:00Z"
    },
    "confirmacion": {
      "numero_confirmacion": "CONF-RES-103-2025",
      "fecha_confirmacion": "2025-09-29T23:00:00Z"
    }
  }
}
```

---

### 11. Check-in de Reserva
```http
POST /api/common-areas/reservas/{reserva_id}/checkin/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "hora_llegada": "14:45:00",
  "asistentes_reales": 42,
  "observaciones_llegada": "Todo en orden, área limpia y preparada"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Check-in registrado exitosamente",
  "data": {
    "reserva_id": 103,
    "estado": "en_uso",
    "checkin": {
      "hora_programada": "15:00:00",
      "hora_real": "14:45:00",
      "puntualidad": "15 minutos anticipado",
      "asistentes_estimados": 45,
      "asistentes_reales": 42
    },
    "proximos_pasos": [
      "Check-out programado para las 20:00",
      "Inspección final del área"
    ]
  }
}
```

---

### 12. Check-out de Reserva
```http
POST /api/common-areas/reservas/{reserva_id}/checkout/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "hora_salida": "20:15:00",
  "estado_area": "excelente",
  "danos_reportados": [],
  "observaciones_salida": "Área entregada limpia y en orden",
  "elementos_faltantes": [],
  "calificacion_servicio": 5
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Check-out completado exitosamente",
  "data": {
    "reserva_id": 103,
    "estado": "completada",
    "checkout": {
      "hora_programada": "20:00:00",
      "hora_real": "20:15:00",
      "duracion_real": "5 horas 30 minutos",
      "estado_area": "excelente",
      "penalizaciones": "ninguna",
      "deposito_devuelto": true
    },
    "resumen_uso": {
      "puntualidad_llegada": "anticipado",
      "puntualidad_salida": "15 minutos tarde",
      "calificacion": 5,
      "usuario_confiable": true
    }
  }
}
```

---

## 💰 GESTIÓN DE TARIFAS

### 13. Listar Tarifas
```http
GET /api/common-areas/tarifas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `area`: ID de área específica
- `tipo`: Tipo de tarifa (base, especial, promocional)
- `vigente`: Solo tarifas vigentes (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "area": {
        "id": 1,
        "nombre": "Salón Social"
      },
      "tipo": "base",
      "nombre": "Tarifa Regular",
      "valor_hora": "37500.00",
      "valor_minimo": "150000.00",
      "horas_minimas": 4,
      "fecha_vigencia_inicio": "2025-01-01T00:00:00Z",
      "fecha_vigencia_fin": null,
      "activa": true,
      "aplicable_dias": ["lunes", "martes", "miercoles", "jueves", "domingo"],
      "aplicable_horas": {
        "inicio": "08:00:00",
        "fin": "22:00:00"
      }
    },
    {
      "id": 2,
      "area": {
        "id": 1,
        "nombre": "Salón Social"
      },
      "tipo": "especial",
      "nombre": "Tarifa Fin de Semana",
      "valor_hora": "45000.00",
      "valor_minimo": "180000.00",
      "horas_minimas": 4,
      "fecha_vigencia_inicio": "2025-01-01T00:00:00Z",
      "fecha_vigencia_fin": null,
      "activa": true,
      "aplicable_dias": ["viernes", "sabado"],
      "recargo_porcentaje": 20.0
    }
  ]
}
```

---

### 14. Crear Nueva Tarifa
```http
POST /api/common-areas/tarifas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "area": 1,
  "tipo": "promocional",
  "nombre": "Tarifa Promocional Navidad",
  "valor_hora": "30000.00",
  "valor_minimo": "120000.00",
  "horas_minimas": 4,
  "fecha_vigencia_inicio": "2025-12-01T00:00:00Z",
  "fecha_vigencia_fin": "2025-12-31T23:59:59Z",
  "aplicable_dias": ["lunes", "martes", "miercoles", "jueves"],
  "descuento_porcentaje": 20.0,
  "condiciones": "Válida solo para eventos familiares"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Tarifa creada exitosamente",
  "data": {
    "id": 15,
    "area": {
      "id": 1,
      "nombre": "Salón Social"
    },
    "tipo": "promocional",
    "nombre": "Tarifa Promocional Navidad",
    "valor_hora": "30000.00",
    "descuento_porcentaje": 20.0,
    "fecha_vigencia_inicio": "2025-12-01T00:00:00Z",
    "fecha_vigencia_fin": "2025-12-31T23:59:59Z",
    "activa": true
  }
}
```

---

## 📊 REPORTES Y ESTADÍSTICAS

### 15. Dashboard de Áreas Comunes
```http
GET /api/common-areas/dashboard/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `periodo`: Periodo específico (YYYY-MM, default: mes actual)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": "2025-09",
    "resumen_general": {
      "total_areas": 12,
      "areas_activas": 11,
      "total_reservas": 89,
      "reservas_confirmadas": 82,
      "reservas_canceladas": 7,
      "ingresos_generados": "12750000.00",
      "ocupacion_promedio": 72.5
    },
    "areas_mas_usadas": [
      {
        "area": "Salón Social",
        "reservas": 25,
        "ingresos": "4500000.00",
        "ocupacion": 85.5
      },
      {
        "area": "Piscina",
        "reservas": 35,
        "ingresos": "0.00",
        "ocupacion": 78.2
      },
      {
        "area": "BBQ Zone",
        "reservas": 18,
        "ingresos": "1350000.00",
        "ocupacion": 65.8
      }
    ],
    "ocupacion_por_dia": [
      {
        "dia": "lunes",
        "porcentaje": 45.2
      },
      {
        "dia": "sabado",
        "porcentaje": 95.8
      }
    ],
    "horarios_pico": [
      {
        "hora": "15:00-19:00",
        "reservas": 35,
        "porcentaje": 39.3
      },
      {
        "hora": "10:00-14:00",
        "reservas": 28,
        "porcentaje": 31.5
      }
    ]
  }
}
```

---

### 16. Reporte de Utilización
```http
GET /api/common-areas/reportes/utilizacion/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `area_id`: ID de área específica
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
- `agrupar_por`: Agrupación (dia, semana, mes, area)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "desde": "2025-09-01",
      "hasta": "2025-09-30"
    },
    "resumen": {
      "total_horas_reservadas": 445,
      "total_horas_disponibles": 6200,
      "porcentaje_ocupacion": 7.18,
      "ingresos_totales": "12750000.00",
      "promedio_duracion_reserva": 5.0
    },
    "detalle_por_area": [
      {
        "area": {
          "id": 1,
          "nombre": "Salón Social"
        },
        "reservas_total": 25,
        "horas_utilizadas": 125,
        "horas_disponibles": 465,
        "ocupacion": 26.9,
        "ingresos": "4500000.00",
        "usuario_frecuente": {
          "vivienda": "TORRE-A-205",
          "propietario": "Carlos Mendoza",
          "reservas": 4
        }
      }
    ],
    "tendencias": {
      "crecimiento_mensual": 15.2,
      "dia_mas_popular": "sabado",
      "hora_mas_popular": "15:00-16:00"
    }
  }
}
```

---

### 17. Reporte Financiero de Áreas
```http
GET /api/common-areas/reportes/financiero/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `periodo_desde`: Periodo desde (YYYY-MM)
- `periodo_hasta`: Periodo hasta (YYYY-MM)
- `incluir_proyecciones`: Incluir proyecciones (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "desde": "2025-01",
      "hasta": "2025-09"
    },
    "resumen_financiero": {
      "ingresos_totales": "89250000.00",
      "ingresos_promedio_mensual": "9916667.00",
      "crecimiento_anual": 12.8,
      "areas_rentables": 8,
      "areas_sin_ingresos": 4
    },
    "ingresos_por_area": [
      {
        "area": "Salón Social",
        "ingresos_periodo": "45750000.00",
        "promedio_mensual": "5083333.00",
        "reservas_periodo": 183,
        "precio_promedio": "250000.00"
      },
      {
        "area": "BBQ Zone",
        "ingresos_periodo": "18900000.00",
        "promedio_mensual": "2100000.00",
        "reservas_periodo": 126,
        "precio_promedio": "150000.00"
      }
    ],
    "proyecciones": {
      "ingresos_proyectados_año": "119000000.00",
      "crecimiento_esperado": 15.0,
      "areas_expansion": ["Gimnasio", "Sala de Juegos"]
    }
  }
}
```

---

### 18. Exportar Datos de Reservas
```http
POST /api/common-areas/export/reservas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "formato": "excel",
  "periodo": {
    "desde": "2025-01-01",
    "hasta": "2025-09-30"
  },
  "incluir": [
    "datos_reserva",
    "informacion_usuario",
    "detalles_pago",
    "calificaciones"
  ],
  "filtros": {
    "areas": [1, 2, 3],
    "estados": ["confirmada", "completada"],
    "solo_pagadas": true
  }
}
```

**Response 202 Accepted:**
```json
{
  "success": true,
  "message": "Exportación iniciada exitosamente",
  "data": {
    "exportacion_id": "EXP-AC-001-2025",
    "url_descarga": "https://storage.example.com/exports/areas_comunes/EXP-AC-001-2025.xlsx",
    "fecha_generacion": "2025-09-29T23:15:00Z",
    "expira_en": "2025-10-06T23:15:00Z",
    "total_registros": 289,
    "url_seguimiento": "/api/common-areas/exports/EXP-AC-001-2025/estado/"
  }
}
```

---

### 19. Calendarios de Disponibilidad
```http
GET /api/common-areas/calendario/{area_id}/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `mes`: Mes específico (YYYY-MM, default: mes actual)
- `vista`: Tipo de vista (mensual, semanal, diaria)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "area": {
      "id": 1,
      "nombre": "Salón Social"
    },
    "mes": "2025-10",
    "calendario": [
      {
        "fecha": "2025-10-01",
        "dia_semana": "martes",
        "disponible": true,
        "reservas": [],
        "horarios_libres": [
          "08:00-22:00"
        ]
      },
      {
        "fecha": "2025-10-05",
        "dia_semana": "sabado",
        "disponible": true,
        "reservas": [
          {
            "id": 101,
            "hora_inicio": "14:00:00",
            "hora_fin": "18:00:00",
            "usuario": "Juan Pérez",
            "proposito": "Cumpleaños infantil"
          }
        ],
        "horarios_libres": [
          "08:00-14:00",
          "18:00-22:00"
        ]
      }
    ],
    "estadisticas_mes": {
      "dias_totales": 31,
      "dias_con_reservas": 18,
      "ocupacion_porcentaje": 68.5
    }
  }
}
```

---

### 20. Notificaciones de Reservas
```http
GET /api/common-areas/notificaciones/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `tipo`: Tipo de notificación (recordatorio, confirmacion, cancelacion)
- `usuario`: ID de usuario específico
- `leidas`: Solo notificaciones leídas (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 501,
      "tipo": "recordatorio",
      "titulo": "Recordatorio: Reserva Salón Social Mañana",
      "mensaje": "Su reserva del Salón Social para el 05/10/2025 de 14:00 a 18:00 está confirmada. No olvide llegar puntualmente.",
      "reserva": {
        "id": 101,
        "area": "Salón Social",
        "fecha": "2025-10-05",
        "hora": "14:00-18:00"
      },
      "fecha_envio": "2025-10-04T18:00:00Z",
      "leida": false,
      "urgente": false
    },
    {
      "id": 502,
      "tipo": "confirmacion",
      "titulo": "Reserva Confirmada - Pago Recibido",
      "mensaje": "Su pago de $187,500 ha sido confirmado. Su reserva del Salón Social está activa.",
      "reserva": {
        "id": 103,
        "area": "Salón Social",
        "fecha": "2025-10-12",
        "hora": "15:00-20:00"
      },
      "fecha_envio": "2025-09-29T23:00:00Z",
      "leida": true,
      "urgente": false
    }
  ]
}
```

---

## ⚠️ CÓDIGOS DE ERROR ESPECÍFICOS

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos de reserva inválidos |
| 401 | Unauthorized - Token inválido |
| 403 | Forbidden - Sin permisos sobre área común |
| 404 | Not Found - Área/Reserva no encontrada |
| 409 | Conflict - Horario no disponible o reserva duplicada |
| 422 | Unprocessable Entity - Validación de horarios fallida |
| 423 | Locked - Área temporalmente no disponible |
| 424 | Failed Dependency - Error en procesamiento de pago |
| 500 | Internal Server Error - Error del servidor |

---

## 🔒 PERMISOS REQUERIDOS

| Endpoint | Permiso Requerido |
|----------|-------------------|
| GET /areas/ | `common_areas.view_areacomun` |
| POST /areas/ | `common_areas.add_areacomun` |
| GET /reservas/ | `common_areas.view_reserva` |
| POST /reservas/ | `common_areas.add_reserva` |
| POST /reservas/{id}/cancelar/ | `common_areas.cancel_reserva` |
| GET /reportes/ | `common_areas.view_reportes` |

---

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Concurrencia**: Sistema de bloqueos para evitar reservas simultáneas del mismo horario
2. **Notificaciones**: Recordatorios automáticos 24h antes de la reserva
3. **Pagos**: Integración con sistema de pagos para tarifas automáticas
4. **Historial**: Mantenimiento de historial completo de uso y calificaciones
5. **Mantenimiento**: Bloqueo automático de áreas en mantenimiento
6. **Políticas**: Sistema flexible de políticas de cancelación y reembolsos