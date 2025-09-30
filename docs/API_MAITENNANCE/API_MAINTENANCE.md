# API ENDPOINTS - MAINTENANCE MODULE

## MÓDULO: GESTIÓN DE MANTENIMIENTO

### Descripción
Este módulo maneja la administración de solicitudes de mantenimiento, órdenes de trabajo, proveedores, inventario y reportes de mantenimiento del condominio.

---

## 🔧 GESTIÓN DE SOLICITUDES DE MANTENIMIENTO

### 1. Listar Solicitudes de Mantenimiento
**CU-WEB-009: Gestionar Mantenimiento**

```http
GET /api/maintenance/solicitudes/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20)
- `search`: Búsqueda por descripción o ubicación
- `categoria`: Filtrar por categoría
- `prioridad`: Filtrar por prioridad (baja, media, alta, urgente)
- `estado`: Estado de solicitud (pendiente, asignada, en_proceso, completada, cancelada)
- `solicitante`: ID del solicitante
- `ubicacion`: Filtrar por ubicación
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 85,
    "next": "http://api.backresidences.com/api/maintenance/solicitudes/?page=2",
    "previous": null,
    "results": [
      {
        "id": 101,
        "numero_solicitud": "SOL-2025-000101",
        "categoria": "plomeria",
        "subcategoria": "fuga_agua",
        "prioridad": "alta",
        "estado": "asignada",
        "descripcion": "Fuga de agua en tubería principal del baño de la vivienda 101",
        "ubicacion": {
          "tipo": "vivienda",
          "vivienda": {
            "id": 1,
            "identificador": "TORRE-A-101"
          }
        },
        "solicitante": {
          "id": 15,
          "full_name": "Juan Pérez",
          "telefono": "+573001234567",
          "tipo": "propietario"
        },
        "fecha_solicitud": "2025-09-29T08:30:00Z",
        "fecha_programada": "2025-09-30T14:00:00Z",
        "tecnico_asignado": {
          "id": 8,
          "full_name": "Carlos Martínez",
          "especialidad": "plomeria",
          "telefono": "+573009876543"
        },
        "costo_estimado": "85000.00",
        "imagenes_count": 2,
        "comentarios_count": 3,
        "orden_trabajo": {
          "id": 205,
          "numero": "OT-2025-000205"
        }
      },
      {
        "id": 102,
        "numero_solicitud": "SOL-2025-000102",
        "categoria": "electricidad",
        "subcategoria": "corto_circuito",
        "prioridad": "urgente",
        "estado": "completada",
        "descripcion": "Corto circuito en panel eléctrico del ascensor Torre B",
        "ubicacion": {
          "tipo": "area_comun",
          "descripcion": "Ascensor Torre B - Sala de máquinas"
        },
        "solicitante": {
          "id": 5,
          "full_name": "Administrador Principal",
          "tipo": "administrador"
        },
        "fecha_solicitud": "2025-09-28T15:45:00Z",
        "fecha_completada": "2025-09-29T11:30:00Z",
        "tecnico_asignado": {
          "id": 9,
          "full_name": "Miguel Rodríguez",
          "especialidad": "electricidad"
        },
        "costo_real": "320000.00",
        "tiempo_resolucion": "19 horas 45 minutos"
      }
    ]
  }
}
```

---

### 2. Obtener Detalles de Solicitud
```http
GET /api/maintenance/solicitudes/{solicitud_id}/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "id": 101,
    "numero_solicitud": "SOL-2025-000101",
    "categoria": "plomeria",
    "subcategoria": "fuga_agua",
    "prioridad": "alta",
    "estado": "asignada",
    "descripcion": "Fuga de agua en tubería principal del baño de la vivienda 101. El agua sale constantemente del acople entre la tubería y el lavamanos. Se observa humedad en la pared adyacente.",
    "ubicacion": {
      "tipo": "vivienda",
      "vivienda": {
        "id": 1,
        "identificador": "TORRE-A-101",
        "propietario": "Juan Pérez"
      },
      "ubicacion_especifica": "Baño principal"
    },
    "solicitante": {
      "id": 15,
      "full_name": "Juan Pérez",
      "email": "juan.perez@email.com",
      "telefono": "+573001234567",
      "tipo": "propietario"
    },
    "fecha_solicitud": "2025-09-29T08:30:00Z",
    "fecha_programada": "2025-09-30T14:00:00Z",
    "fecha_limite": "2025-10-02T23:59:59Z",
    "tecnico_asignado": {
      "id": 8,
      "full_name": "Carlos Martínez",
      "especialidad": "plomeria",
      "telefono": "+573009876543",
      "calificacion_promedio": 4.8
    },
    "costo_estimado": "85000.00",
    "materiales_estimados": [
      {
        "item": "Acople PVC 1/2 pulgada",
        "cantidad": 2,
        "costo_unitario": "15000.00"
      },
      {
        "item": "Silicona sellante",
        "cantidad": 1,
        "costo_unitario": "12000.00"
      }
    ],
    "imagenes": [
      {
        "id": 1,
        "url": "https://storage.example.com/mantenimiento/fuga_bano_1.jpg",
        "descripcion": "Vista general de la fuga",
        "fecha_subida": "2025-09-29T08:35:00Z"
      },
      {
        "id": 2,
        "url": "https://storage.example.com/mantenimiento/fuga_bano_2.jpg",
        "descripcion": "Detalle del acople dañado",
        "fecha_subida": "2025-09-29T08:36:00Z"
      }
    ],
    "historial": [
      {
        "fecha": "2025-09-29T08:30:00Z",
        "accion": "solicitud_creada",
        "usuario": "Juan Pérez",
        "descripcion": "Solicitud de mantenimiento creada"
      },
      {
        "fecha": "2025-09-29T10:15:00Z",
        "accion": "asignacion_tecnico",
        "usuario": "Administrador Principal",
        "descripcion": "Técnico Carlos Martínez asignado"
      },
      {
        "fecha": "2025-09-29T10:20:00Z",
        "accion": "programacion",
        "usuario": "Carlos Martínez",
        "descripcion": "Visita programada para el 30/09 a las 14:00"
      }
    ]
  }
}
```

---

### 3. Crear Nueva Solicitud
```http
POST /api/maintenance/solicitudes/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "categoria": "carpinteria",
  "subcategoria": "reparacion_puerta",
  "prioridad": "media",
  "descripcion": "La puerta del balcón no cierra correctamente. La chapa no encaja bien en el marco y permite entrada de aire y ruido.",
  "ubicacion": {
    "tipo": "vivienda",
    "vivienda": 1,
    "ubicacion_especifica": "Balcón principal"
  },
  "fecha_preferida": "2025-10-02T09:00:00Z",
  "disponibilidad": [
    "2025-10-02T09:00:00Z",
    "2025-10-02T14:00:00Z",
    "2025-10-03T09:00:00Z"
  ],
  "imagenes": ["base64_encoded_image_1", "base64_encoded_image_2"],
  "contacto_alternativo": {
    "nombre": "María Pérez",
    "telefono": "+573009876543",
    "relacion": "esposa"
  }
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Solicitud de mantenimiento creada exitosamente",
  "data": {
    "id": 103,
    "numero_solicitud": "SOL-2025-000103",
    "categoria": "carpinteria",
    "subcategoria": "reparacion_puerta",
    "prioridad": "media",
    "estado": "pendiente",
    "fecha_solicitud": "2025-09-30T00:30:00Z",
    "fecha_limite": "2025-10-07T23:59:59Z",
    "tiempo_respuesta_estimado": "48 horas",
    "costo_estimado": "65000.00",
    "proceso_siguiente": "asignacion_tecnico"
  }
}
```

---

### 4. Actualizar Solicitud
```http
PUT /api/maintenance/solicitudes/{solicitud_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "prioridad": "alta",
  "descripcion": "La puerta del balcón no cierra correctamente. La chapa no encaja bien en el marco y permite entrada de aire y ruido. ACTUALIZACIÓN: Además se observa que el marco está ligeramente deformado.",
  "fecha_preferida": "2025-10-01T09:00:00Z",
  "observaciones_adicionales": "Requiere atención urgente debido a las lluvias"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Solicitud actualizada exitosamente",
  "data": {
    "id": 103,
    "prioridad": "alta",
    "fecha_limite_nueva": "2025-10-04T23:59:59Z",
    "fecha_actualizacion": "2025-09-30T00:35:00Z",
    "cambios_aplicados": [
      "Prioridad elevada a alta",
      "Descripción expandida",
      "Fecha límite ajustada",
      "Observaciones adicionales agregadas"
    ]
  }
}
```

---

## 📋 GESTIÓN DE ÓRDENES DE TRABAJO

### 5. Listar Órdenes de Trabajo
```http
GET /api/maintenance/ordenes-trabajo/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `estado`: Estado de orden (pendiente, en_proceso, completada, cancelada)
- `tecnico`: ID del técnico asignado
- `categoria`: Categoría de trabajo
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
- `costo_minimo`: Costo mínimo
- `costo_maximo`: Costo máximo

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 42,
    "results": [
      {
        "id": 205,
        "numero_orden": "OT-2025-000205",
        "solicitud": {
          "id": 101,
          "numero": "SOL-2025-000101",
          "descripcion": "Fuga de agua en tubería principal del baño"
        },
        "tecnico_asignado": {
          "id": 8,
          "full_name": "Carlos Martínez",
          "especialidad": "plomeria"
        },
        "estado": "en_proceso",
        "fecha_creacion": "2025-09-29T10:30:00Z",
        "fecha_programada": "2025-09-30T14:00:00Z",
        "fecha_inicio": "2025-09-30T14:15:00Z",
        "costo_estimado": "85000.00",
        "costo_real": null,
        "tiempo_estimado": "2 horas",
        "progreso_porcentaje": 45,
        "materiales_utilizados": [
          {
            "item": "Acople PVC 1/2 pulgada",
            "cantidad_usada": 1,
            "costo": "15000.00"
          }
        ],
        "ultima_actualizacion": "2025-09-30T15:30:00Z"
      }
    ]
  }
}
```

---

### 6. Crear Orden de Trabajo
```http
POST /api/maintenance/ordenes-trabajo/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "solicitud": 103,
  "tecnico_asignado": 10,
  "fecha_programada": "2025-10-01T09:00:00Z",
  "tiempo_estimado": "3 horas",
  "materiales_requeridos": [
    {
      "item": "Bisagra para puerta",
      "cantidad": 2,
      "especificaciones": "Bisagra de seguridad 4 pulgadas"
    },
    {
      "item": "Chapa de seguridad",
      "cantidad": 1,
      "especificaciones": "Chapa multipunto para puerta balcón"
    }
  ],
  "herramientas_requeridas": [
    "Taladro",
    "Destornilladores",
    "Nivel"
  ],
  "instrucciones_especiales": "Verificar alineación del marco antes de instalar nueva chapa"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Orden de trabajo creada exitosamente",
  "data": {
    "id": 206,
    "numero_orden": "OT-2025-000206",
    "solicitud": {
      "id": 103,
      "numero": "SOL-2025-000103"
    },
    "tecnico_asignado": {
      "id": 10,
      "full_name": "Luis Herrera",
      "especialidad": "carpinteria"
    },
    "estado": "pendiente",
    "fecha_creacion": "2025-09-30T00:40:00Z",
    "fecha_programada": "2025-10-01T09:00:00Z",
    "costo_estimado": "125000.00",
    "notificacion_enviada": true
  }
}
```

---

### 7. Iniciar Trabajo
```http
POST /api/maintenance/ordenes-trabajo/{orden_id}/iniciar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "hora_inicio": "2025-10-01T09:15:00Z",
  "observaciones_iniciales": "Materiales verificados, trabajo iniciado según programación",
  "fotos_antes": ["base64_encoded_before_image"]
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Trabajo iniciado exitosamente",
  "data": {
    "id": 206,
    "estado": "en_proceso",
    "fecha_inicio": "2025-10-01T09:15:00Z",
    "progreso_porcentaje": 10,
    "tiempo_transcurrido": "0 horas",
    "siguiente_reporte": "2025-10-01T11:15:00Z"
  }
}
```

---

### 8. Actualizar Progreso
```http
PATCH /api/maintenance/ordenes-trabajo/{orden_id}/progreso/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "progreso_porcentaje": 75,
  "descripcion_avance": "Chapa antigua removida, marco ajustado, instalando nueva chapa",
  "materiales_utilizados": [
    {
      "item": "Bisagra para puerta",
      "cantidad": 2,
      "costo": "35000.00"
    }
  ],
  "tiempo_adicional_estimado": "30 minutos",
  "fotos_progreso": ["base64_encoded_progress_image"]
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Progreso actualizado exitosamente",
  "data": {
    "id": 206,
    "progreso_porcentaje": 75,
    "tiempo_transcurrido": "2 horas 30 minutos",
    "costo_acumulado": "85000.00",
    "tiempo_estimado_restante": "30 minutos",
    "fecha_actualizacion": "2025-10-01T11:45:00Z"
  }
}
```

---

### 9. Completar Trabajo
```http
POST /api/maintenance/ordenes-trabajo/{orden_id}/completar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "hora_finalizacion": "2025-10-01T12:30:00Z",
  "descripcion_trabajo_realizado": "Puerta del balcón reparada exitosamente. Se ajustó el marco, se instaló nueva chapa multipunto y se verificó el funcionamiento correcto.",
  "materiales_finales": [
    {
      "item": "Bisagra para puerta",
      "cantidad": 2,
      "costo": "35000.00"
    },
    {
      "item": "Chapa multipunto",
      "cantidad": 1,
      "costo": "65000.00"
    }
  ],
  "costo_mano_obra": "50000.00",
  "garantia_dias": 90,
  "fotos_despues": ["base64_encoded_after_image"],
  "recomendaciones": "Lubricar chapa cada 6 meses para mantener funcionamiento óptimo"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Trabajo completado exitosamente",
  "data": {
    "id": 206,
    "estado": "completada",
    "fecha_finalizacion": "2025-10-01T12:30:00Z",
    "tiempo_total": "3 horas 15 minutos",
    "costo_total": "150000.00",
    "desglose_costos": {
      "materiales": "100000.00",
      "mano_obra": "50000.00"
    },
    "garantia_hasta": "2025-12-30T23:59:59Z",
    "solicitud_actualizada": true,
    "encuesta_satisfaccion_enviada": true
  }
}
```

---

## 🏢 GESTIÓN DE PROVEEDORES

### 10. Listar Proveedores
```http
GET /api/maintenance/proveedores/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `categoria`: Categoría de servicios
- `activo`: Estado activo (true/false)
- `calificacion_minima`: Calificación mínima
- `ciudad`: Ciudad del proveedor

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Servicios Técnicos Martínez",
      "categoria_principal": "plomeria",
      "servicios": ["plomeria", "gasfiteria", "reparaciones_generales"],
      "contacto": {
        "telefono": "+573001234567",
        "email": "servicios@martinez.com",
        "direccion": "Calle 45 #12-34, Bogotá"
      },
      "calificacion_promedio": 4.8,
      "trabajos_realizados": 45,
      "activo": true,
      "disponibilidad": {
        "horarios": "Lunes a Sábado 7:00 AM - 6:00 PM",
        "emergencias": true
      },
      "tarifas": {
        "hora_tecnico": "35000.00",
        "visita_diagnostico": "25000.00",
        "emergencia_recargo": "50%"
      }
    }
  ]
}
```

---

### 11. Registrar Nuevo Proveedor
```http
POST /api/maintenance/proveedores/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "nombre": "ElectroServicios del Norte",
  "categoria_principal": "electricidad",
  "servicios": ["electricidad", "iluminacion", "sistemas_electricos"],
  "contacto": {
    "telefono": "+573009876543",
    "email": "info@electroservicios.com",
    "direccion": "Carrera 30 #45-67, Bogotá",
    "contacto_principal": "Miguel Rodríguez"
  },
  "documentacion": {
    "rut": "900123456-7",
    "camara_comercio": "12345678",
    "poliza_responsabilidad": "RC-2025-001234"
  },
  "tarifas": {
    "hora_tecnico": "40000.00",
    "visita_diagnostico": "30000.00",
    "emergencia_recargo": "75%"
  },
  "disponibilidad": {
    "horarios": "Lunes a Viernes 8:00 AM - 5:00 PM",
    "emergencias": true,
    "tiempo_respuesta_emergencia": "2 horas"
  }
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Proveedor registrado exitosamente",
  "data": {
    "id": 15,
    "nombre": "ElectroServicios del Norte",
    "categoria_principal": "electricidad",
    "fecha_registro": "2025-09-30T00:50:00Z",
    "estado": "pendiente_validacion",
    "codigo_proveedor": "PROV-2025-015",
    "documentos_pendientes": [
      "Certificado de competencias técnicas",
      "Referencias comerciales"
    ]
  }
}
```

---

## 📦 GESTIÓN DE INVENTARIO

### 12. Listar Inventario
```http
GET /api/maintenance/inventario/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `categoria`: Categoría de material
- `stock_minimo`: Solo items con stock bajo (true/false)
- `activo`: Estado activo (true/false)
- `proveedor`: ID del proveedor

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 150,
    "alertas_stock": 8,
    "results": [
      {
        "id": 1,
        "codigo": "PVC-AC-050",
        "nombre": "Acople PVC 1/2 pulgada",
        "categoria": "plomeria",
        "stock_actual": 15,
        "stock_minimo": 20,
        "stock_maximo": 100,
        "unidad_medida": "unidad",
        "costo_unitario": "15000.00",
        "valor_total": "225000.00",
        "proveedor": {
          "id": 3,
          "nombre": "Distribuidora Hidráulica"
        },
        "ubicacion": "Bodega A - Estante 3",
        "alerta_stock": true,
        "ultima_compra": "2025-09-15T00:00:00Z",
        "rotacion": "alta"
      },
      {
        "id": 2,
        "codigo": "ELEC-CAB-120",
        "nombre": "Cable eléctrico 12 AWG",
        "categoria": "electricidad",
        "stock_actual": 250,
        "stock_minimo": 100,
        "stock_maximo": 500,
        "unidad_medida": "metro",
        "costo_unitario": "2500.00",
        "valor_total": "625000.00",
        "proveedor": {
          "id": 5,
          "nombre": "ElectroMaterial Ltda"
        },
        "ubicacion": "Bodega B - Rollo 1",
        "alerta_stock": false,
        "rotacion": "media"
      }
    ]
  }
}
```

---

### 13. Registrar Entrada de Inventario
```http
POST /api/maintenance/inventario/entradas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "items": [
    {
      "item_id": 1,
      "cantidad": 50,
      "costo_unitario": "14500.00",
      "lote": "LOTE-2025-10-001",
      "fecha_vencimiento": "2027-10-01T00:00:00Z"
    },
    {
      "item_id": 2,
      "cantidad": 100,
      "costo_unitario": "2400.00",
      "lote": "LOTE-2025-10-002"
    }
  ],
  "proveedor": 3,
  "numero_factura": "FAC-001234",
  "fecha_compra": "2025-09-30T00:00:00Z",
  "valor_total": "965000.00",
  "observaciones": "Compra programada por stock bajo"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Entrada de inventario registrada exitosamente",
  "data": {
    "id": 25,
    "numero_entrada": "ENT-2025-000025",
    "fecha_registro": "2025-09-30T00:55:00Z",
    "items_actualizados": 2,
    "valor_total": "965000.00",
    "alertas_resueltas": 1,
    "stock_actualizado": [
      {
        "item": "Acople PVC 1/2 pulgada",
        "stock_anterior": 15,
        "stock_nuevo": 65,
        "alerta_stock": false
      },
      {
        "item": "Cable eléctrico 12 AWG",
        "stock_anterior": 250,
        "stock_nuevo": 350
      }
    ]
  }
}
```

---

### 14. Registrar Salida de Inventario
```http
POST /api/maintenance/inventario/salidas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "orden_trabajo": 206,
  "items": [
    {
      "item_id": 5,
      "cantidad": 2,
      "motivo": "uso_trabajo"
    },
    {
      "item_id": 8,
      "cantidad": 1,
      "motivo": "uso_trabajo"
    }
  ],
  "observaciones": "Materiales utilizados en reparación puerta balcón OT-206"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Salida de inventario registrada exitosamente",
  "data": {
    "id": 35,
    "numero_salida": "SAL-2025-000035",
    "orden_trabajo": {
      "id": 206,
      "numero": "OT-2025-000206"
    },
    "fecha_registro": "2025-10-01T10:30:00Z",
    "items_afectados": 2,
    "valor_total": "100000.00",
    "stock_actualizado": [
      {
        "item": "Bisagra para puerta",
        "cantidad_usada": 2,
        "stock_restante": 18
      },
      {
        "item": "Chapa multipunto",
        "cantidad_usada": 1,
        "stock_restante": 5,
        "alerta_stock": true
      }
    ]
  }
}
```

---

## 📊 REPORTES DE MANTENIMIENTO

### 15. Dashboard de Mantenimiento
```http
GET /api/maintenance/dashboard/
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
    "solicitudes": {
      "total": 45,
      "pendientes": 8,
      "en_proceso": 12,
      "completadas": 22,
      "canceladas": 3,
      "tiempo_promedio_resolucion": "2.5 días",
      "satisfaccion_promedio": 4.3
    },
    "ordenes_trabajo": {
      "total": 38,
      "activas": 15,
      "completadas": 20,
      "canceladas": 3,
      "costo_total": "2850000.00",
      "costo_promedio": "75000.00"
    },
    "categorias_frecuentes": [
      {
        "categoria": "plomeria",
        "solicitudes": 18,
        "porcentaje": 40.0
      },
      {
        "categoria": "electricidad",
        "solicitudes": 12,
        "porcentaje": 26.7
      },
      {
        "categoria": "carpinteria",
        "solicitudes": 8,
        "porcentaje": 17.8
      }
    ],
    "tecnicos_productivos": [
      {
        "tecnico": "Carlos Martínez",
        "trabajos_completados": 12,
        "calificacion_promedio": 4.9,
        "tiempo_promedio": "3.2 horas"
      },
      {
        "tecnico": "Miguel Rodríguez",
        "trabajos_completados": 8,
        "calificacion_promedio": 4.7,
        "tiempo_promedio": "4.1 horas"
      }
    ],
    "inventario": {
      "items_total": 150,
      "items_stock_bajo": 8,
      "valor_total": "5250000.00",
      "rotacion_promedio": "alta"
    }
  }
}
```

---

### 16. Reporte de Mantenimiento Preventivo
```http
GET /api/maintenance/reportes/preventivo/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `area`: Área específica (areas_comunes, viviendas, infraestructura)
- `equipo`: Tipo de equipo específico
- `vencimiento_dias`: Días hasta vencimiento

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "mantenimientos_programados": [
      {
        "id": 1,
        "equipo": "Ascensor Torre A",
        "tipo_mantenimiento": "Revisión mensual",
        "frecuencia": "mensual",
        "ultima_ejecucion": "2025-09-01T00:00:00Z",
        "proxima_ejecucion": "2025-10-01T00:00:00Z",
        "dias_restantes": 1,
        "proveedor": "Ascensores Técnicos S.A.",
        "costo_estimado": "350000.00",
        "estado": "programado"
      },
      {
        "id": 2,
        "equipo": "Bomba de agua principal",
        "tipo_mantenimiento": "Mantenimiento trimestral",
        "frecuencia": "trimestral",
        "ultima_ejecucion": "2025-07-15T00:00:00Z",
        "proxima_ejecucion": "2025-10-15T00:00:00Z",
        "dias_restantes": 15,
        "proveedor": "Bombas y Equipos Ltda",
        "costo_estimado": "180000.00",
        "estado": "pendiente"
      }
    ],
    "vencimientos_proximos": [
      {
        "equipo": "Sistema contraincendios",
        "tipo": "Certificación anual",
        "fecha_vencimiento": "2025-10-05T00:00:00Z",
        "dias_restantes": 5,
        "criticidad": "alta"
      }
    ],
    "resumen": {
      "total_equipos": 25,
      "mantenimientos_mes": 8,
      "costo_estimado_mes": "2100000.00",
      "vencimientos_30_dias": 3
    }
  }
}
```

---

### 17. Reporte de Costos
```http
GET /api/maintenance/reportes/costos/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
- `categoria`: Categoría específica
- `tipo_costo`: Tipo de costo (materiales, mano_obra, proveedores)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "desde": "2025-09-01",
      "hasta": "2025-09-30"
    },
    "resumen_costos": {
      "total_periodo": "2850000.00",
      "materiales": "1650000.00",
      "mano_obra": "850000.00",
      "servicios_externos": "350000.00",
      "promedio_por_trabajo": "75000.00"
    },
    "costos_por_categoria": [
      {
        "categoria": "plomeria",
        "trabajos": 18,
        "costo_total": "1250000.00",
        "costo_promedio": "69444.44",
        "materiales": "750000.00",
        "mano_obra": "500000.00"
      },
      {
        "categoria": "electricidad",
        "trabajos": 12,
        "costo_total": "980000.00",
        "costo_promedio": "81666.67",
        "materiales": "580000.00",
        "mano_obra": "400000.00"
      }
    ],
    "proveedores_utilizados": [
      {
        "proveedor": "Servicios Técnicos Martínez",
        "trabajos": 15,
        "costo_total": "1100000.00",
        "calificacion_promedio": 4.8
      }
    ],
    "tendencias": {
      "variacion_mes_anterior": "+12.5%",
      "categoria_mayor_gasto": "plomeria",
      "mes_proyectado": "3100000.00"
    }
  }
}
```

---

### 18. Reporte de Satisfacción
```http
GET /api/maintenance/reportes/satisfaccion/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": "2025-09",
    "resumen_general": {
      "trabajos_evaluados": 22,
      "calificacion_promedio": 4.3,
      "porcentaje_satisfaccion": 86.0,
      "encuestas_respondidas": 20,
      "tasa_respuesta": 90.9
    },
    "calificacion_por_categoria": [
      {
        "categoria": "plomeria",
        "trabajos": 15,
        "calificacion_promedio": 4.5,
        "satisfaccion": 90.0
      },
      {
        "categoria": "electricidad",
        "trabajos": 7,
        "calificacion_promedio": 3.9,
        "satisfaccion": 78.6
      }
    ],
    "tecnicos_mejor_calificados": [
      {
        "tecnico": "Carlos Martínez",
        "trabajos": 12,
        "calificacion_promedio": 4.9,
        "comentarios_positivos": 11
      }
    ],
    "areas_mejora": [
      {
        "aspecto": "Tiempo de respuesta",
        "calificacion": 3.8,
        "comentarios": 5
      },
      {
        "aspecto": "Limpieza post-trabajo",
        "calificacion": 4.1,
        "comentarios": 3
      }
    ],
    "comentarios_destacados": [
      {
        "trabajo": "OT-2025-000205",
        "calificacion": 5,
        "comentario": "Excelente trabajo, muy profesional y rápido"
      }
    ]
  }
}
```

---

### 19. Exportar Datos de Mantenimiento
```http
POST /api/maintenance/export/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "tipo_reporte": "completo",
  "formato": "excel",
  "periodo": {
    "desde": "2025-01-01",
    "hasta": "2025-09-30"
  },
  "incluir": [
    "solicitudes",
    "ordenes_trabajo",
    "inventario",
    "costos",
    "satisfaccion"
  ],
  "filtros": {
    "categorias": ["plomeria", "electricidad"],
    "solo_completados": false,
    "incluir_cancelados": true
  }
}
```

**Response 202 Accepted:**
```json
{
  "success": true,
  "message": "Exportación iniciada exitosamente",
  "data": {
    "exportacion_id": "EXP-MNT-001-2025",
    "url_descarga": "https://storage.example.com/exports/mantenimiento/EXP-MNT-001-2025.xlsx",
    "fecha_generacion": "2025-09-30T01:00:00Z",
    "expira_en": "2025-10-07T01:00:00Z",
    "total_registros": 1250,
    "url_seguimiento": "/api/maintenance/exports/EXP-MNT-001-2025/estado/"
  }
}
```

---

### 20. Programar Mantenimiento Preventivo
```http
POST /api/maintenance/preventivo/programar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "equipo": "Sistema de riego jardines",
  "tipo_mantenimiento": "Revisión y limpieza semestral",
  "descripcion": "Revisión general del sistema de riego, limpieza de filtros, verificación de aspersores y temporizadores",
  "frecuencia": "semestral",
  "fecha_inicio": "2025-10-15T09:00:00Z",
  "proveedor": 8,
  "costo_estimado": "150000.00",
  "materiales_requeridos": [
    {
      "item": "Filtros de agua",
      "cantidad": 4
    },
    {
      "item": "Aspersores repuesto",
      "cantidad": 2
    }
  ],
  "recordatorios": {
    "dias_antes": [30, 7, 1],
    "responsables": [5, 7]
  }
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Mantenimiento preventivo programado exitosamente",
  "data": {
    "id": 15,
    "codigo": "PREV-2025-015",
    "equipo": "Sistema de riego jardines",
    "proxima_ejecucion": "2025-10-15T09:00:00Z",
    "frecuencia": "semestral",
    "proveedor": {
      "id": 8,
      "nombre": "Jardines y Paisajismo Verde"
    },
    "recordatorios_programados": [
      "2025-09-15T09:00:00Z",
      "2025-10-08T09:00:00Z",
      "2025-10-14T09:00:00Z"
    ],
    "estado": "programado"
  }
}
```

---

## ⚠️ CÓDIGOS DE ERROR ESPECÍFICOS

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos de mantenimiento inválidos |
| 401 | Unauthorized - Token inválido |
| 403 | Forbidden - Sin permisos de mantenimiento |
| 404 | Not Found - Solicitud/Orden no encontrada |
| 409 | Conflict - Técnico no disponible o trabajo en proceso |
| 422 | Unprocessable Entity - Validación de inventario fallida |
| 423 | Locked - Orden de trabajo bloqueada |
| 424 | Failed Dependency - Proveedor no disponible |
| 500 | Internal Server Error - Error del servidor |

---

## 🔒 PERMISOS REQUERIDOS

| Endpoint | Permiso Requerido |
|----------|-------------------|
| GET /solicitudes/ | `maintenance.view_solicitudmantenimiento` |
| POST /solicitudes/ | `maintenance.add_solicitudmantenimiento` |
| GET /ordenes-trabajo/ | `maintenance.view_ordentrabajo` |
| POST /ordenes-trabajo/ | `maintenance.add_ordentrabajo` |
| GET /inventario/ | `maintenance.view_inventario` |
| POST /inventario/entradas/ | `maintenance.add_entrada_inventario` |
| GET /proveedores/ | `maintenance.view_proveedor` |

---

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Flujo Automatizado**: Las solicitudes se convierten automáticamente en órdenes de trabajo
2. **Integración Inventario**: Descuento automático de materiales al completar trabajos
3. **Notificaciones**: Alertas automáticas para mantenimiento preventivo y stock bajo
4. **Garantías**: Sistema de seguimiento de garantías por trabajo realizado
5. **Evaluaciones**: Encuestas automáticas de satisfacción post-servicio
6. **Reportería**: Generación automática de reportes de gestión mensual