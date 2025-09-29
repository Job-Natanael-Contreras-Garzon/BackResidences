# API ENDPOINTS - COMMUNICATIONS MODULE

## MÓDULO: GESTIÓN DE COMUNICACIONES

### Descripción
Este módulo maneja la administración de comunicaciones internas del condominio, incluyendo anuncios, notificaciones, mensajería y comunicación con residentes.

---

## 📢 GESTIÓN DE ANUNCIOS

### 1. Listar Anuncios
**CU-WEB-008: Gestionar Comunicaciones**

```http
GET /api/communications/anuncios/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20)
- `search`: Búsqueda por título o contenido
- `categoria`: Filtrar por categoría
- `prioridad`: Filtrar por prioridad (baja, media, alta, urgente)
- `activo`: Estado activo (true/false)
- `vigente`: Solo anuncios vigentes (true/false)
- `autor`: ID del autor específico
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 45,
    "next": "http://api.backresidences.com/api/communications/anuncios/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "titulo": "Corte de Agua Programado",
        "categoria": "mantenimiento",
        "prioridad": "alta",
        "contenido_resumen": "Se realizará corte de agua el próximo martes de 8:00 AM a 2:00 PM...",
        "fecha_publicacion": "2025-09-27T08:00:00Z",
        "fecha_vencimiento": "2025-10-01T23:59:59Z",
        "autor": {
          "id": 5,
          "full_name": "Administrador Principal",
          "cargo": "Administrador"
        },
        "activo": true,
        "vigente": true,
        "visualizaciones": 145,
        "dirigido_a": "todos",
        "adjuntos_count": 1,
        "comentarios_count": 8,
        "imagen_destacada": "https://storage.example.com/anuncios/corte_agua_01.jpg"
      },
      {
        "id": 2,
        "titulo": "Reunión de Copropietarios - Octubre",
        "categoria": "administrativo",
        "prioridad": "media",
        "contenido_resumen": "Se convoca a todos los copropietarios a la reunión ordinaria...",
        "fecha_publicacion": "2025-09-25T14:30:00Z",
        "fecha_vencimiento": "2025-10-15T23:59:59Z",
        "autor": {
          "id": 5,
          "full_name": "Administrador Principal",
          "cargo": "Administrador"
        },
        "activo": true,
        "vigente": true,
        "visualizaciones": 89,
        "dirigido_a": "propietarios",
        "adjuntos_count": 2,
        "comentarios_count": 12
      }
    ]
  }
}
```

---

### 2. Obtener Detalles de Anuncio
```http
GET /api/communications/anuncios/{anuncio_id}/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "titulo": "Corte de Agua Programado",
    "categoria": "mantenimiento",
    "prioridad": "alta",
    "contenido": "Estimados residentes,\n\nInformamos que el próximo martes 1 de octubre se realizará un corte de agua programado de 8:00 AM a 2:00 PM para realizar trabajos de mantenimiento en la red principal.\n\nRecomendamos:\n- Almacenar agua suficiente\n- Evitar usar lavadoras y lavavajillas\n- Reportar cualquier irregularidad\n\nAgradecemos su comprensión.",
    "fecha_publicacion": "2025-09-27T08:00:00Z",
    "fecha_vencimiento": "2025-10-01T23:59:59Z",
    "autor": {
      "id": 5,
      "full_name": "Administrador Principal",
      "cargo": "Administrador",
      "email": "admin@torres-del-sol.com"
    },
    "activo": true,
    "vigente": true,
    "dirigido_a": "todos",
    "visualizaciones": 145,
    "fecha_ultima_edicion": "2025-09-27T08:15:00Z",
    "etiquetas": ["agua", "mantenimiento", "servicios"],
    "adjuntos": [
      {
        "id": 1,
        "nombre": "cronograma_mantenimiento.pdf",
        "tipo": "application/pdf",
        "tamaño": "245KB",
        "url": "https://storage.example.com/anuncios/adjuntos/cronograma_mantenimiento.pdf"
      }
    ],
    "imagenes": [
      "https://storage.example.com/anuncios/corte_agua_01.jpg",
      "https://storage.example.com/anuncios/corte_agua_02.jpg"
    ],
    "estadisticas": {
      "visualizaciones_por_dia": [
        {"fecha": "2025-09-27", "visualizaciones": 65},
        {"fecha": "2025-09-28", "visualizaciones": 45},
        {"fecha": "2025-09-29", "visualizaciones": 35}
      ],
      "visualizaciones_por_bloque": [
        {"bloque": "TORRE-A", "visualizaciones": 55},
        {"bloque": "TORRE-B", "visualizaciones": 50},
        {"bloque": "TORRE-C", "visualizaciones": 40}
      ]
    }
  }
}
```

---

### 3. Crear Nuevo Anuncio
```http
POST /api/communications/anuncios/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "titulo": "Nueva Política de Mascotas",
  "categoria": "normativo",
  "prioridad": "media",
  "contenido": "Se informa a todos los residentes sobre las nuevas políticas para el manejo de mascotas en áreas comunes:\n\n1. Uso obligatorio de correa en todas las áreas comunes\n2. Recoger los desechos de las mascotas\n3. Registro actualizado de vacunas\n4. Horarios específicos para uso de áreas verdes\n\nEsas políticas entran en vigencia a partir del 15 de octubre.",
  "dirigido_a": "todos",
  "fecha_vencimiento": "2025-11-15T23:59:59Z",
  "etiquetas": ["mascotas", "normativa", "areas_comunes"],
  "adjuntos": ["base64_encoded_policy_document"],
  "enviar_notificacion": true,
  "programar_publicacion": false
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Anuncio creado exitosamente",
  "data": {
    "id": 46,
    "titulo": "Nueva Política de Mascotas",
    "categoria": "normativo",
    "prioridad": "media",
    "fecha_publicacion": "2025-09-29T23:30:00Z",
    "fecha_vencimiento": "2025-11-15T23:59:59Z",
    "autor": {
      "id": 5,
      "full_name": "Administrador Principal"
    },
    "activo": true,
    "dirigido_a": "todos",
    "notificacion_enviada": true,
    "residentes_notificados": 340
  }
}
```

---

### 4. Actualizar Anuncio
```http
PUT /api/communications/anuncios/{anuncio_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "titulo": "Nueva Política de Mascotas - ACTUALIZADA",
  "contenido": "Se informa a todos los residentes sobre las nuevas políticas para el manejo de mascotas en áreas comunes:\n\n1. Uso obligatorio de correa en todas las áreas comunes\n2. Recoger los desechos de las mascotas\n3. Registro actualizado de vacunas\n4. Horarios específicos para uso de áreas verdes: 6:00-8:00 AM y 6:00-8:00 PM\n5. Máximo 2 mascotas por vivienda\n\nEsas políticas entran en vigencia a partir del 15 de octubre.",
  "prioridad": "alta",
  "enviar_notificacion_actualizacion": true
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Anuncio actualizado exitosamente",
  "data": {
    "id": 46,
    "titulo": "Nueva Política de Mascotas - ACTUALIZADA",
    "prioridad": "alta",
    "fecha_ultima_edicion": "2025-09-29T23:45:00Z",
    "cambios_realizados": [
      "Título actualizado",
      "Contenido expandido con horarios específicos",
      "Prioridad cambiada a alta",
      "Límite de mascotas agregado"
    ],
    "notificacion_actualizacion_enviada": true,
    "residentes_notificados": 340
  }
}
```

---

### 5. Comentar en Anuncio
```http
POST /api/communications/anuncios/{anuncio_id}/comentarios/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "contenido": "Excelente iniciativa. ¿Habrá algún área específica designada para el esparcimiento de mascotas?",
  "anonimo": false
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Comentario agregado exitosamente",
  "data": {
    "id": 125,
    "anuncio_id": 46,
    "autor": {
      "id": 15,
      "full_name": "Juan Pérez",
      "vivienda": "TORRE-A-101"
    },
    "contenido": "Excelente iniciativa. ¿Habrá algún área específica designada para el esparcimiento de mascotas?",
    "fecha_comentario": "2025-09-29T23:50:00Z",
    "anonimo": false,
    "respuestas_count": 0,
    "likes": 0
  }
}
```

---

## 📬 GESTIÓN DE NOTIFICACIONES

### 6. Listar Notificaciones
```http
GET /api/communications/notificaciones/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `tipo`: Tipo de notificación (anuncio, reserva, pago, sistema, emergencia)
- `leida`: Estado de lectura (true/false)
- `prioridad`: Prioridad (baja, media, alta, urgente)
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `destinatario`: ID del destinatario (si es administrador)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 25,
    "no_leidas": 8,
    "results": [
      {
        "id": 501,
        "tipo": "pago",
        "titulo": "Pago Recibido - Cuota Octubre",
        "mensaje": "Se ha recibido su pago de $250,000 correspondiente a la cuota de administración de octubre.",
        "prioridad": "media",
        "fecha_envio": "2025-09-29T15:30:00Z",
        "fecha_lectura": null,
        "leida": false,
        "origen": {
          "modulo": "payments",
          "referencia_id": 502,
          "referencia_tipo": "pago"
        },
        "acciones": [
          {
            "tipo": "ver_recibo",
            "url": "/api/payments/pagos/502/recibo/",
            "texto": "Ver Recibo"
          }
        ]
      },
      {
        "id": 502,
        "tipo": "reserva",
        "titulo": "Recordatorio: Reserva Salón Social Mañana",
        "mensaje": "Su reserva del Salón Social para mañana 30/09/2025 de 14:00 a 18:00 está confirmada.",
        "prioridad": "alta",
        "fecha_envio": "2025-09-28T18:00:00Z",
        "fecha_lectura": "2025-09-29T08:30:00Z",
        "leida": true,
        "origen": {
          "modulo": "common_areas",
          "referencia_id": 101,
          "referencia_tipo": "reserva"
        }
      }
    ]
  }
}
```

---

### 7. Marcar Notificación como Leída
```http
PATCH /api/communications/notificaciones/{notificacion_id}/marcar-leida/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Notificación marcada como leída",
  "data": {
    "id": 501,
    "leida": true,
    "fecha_lectura": "2025-09-29T23:55:00Z"
  }
}
```

---

### 8. Marcar Todas las Notificaciones como Leídas
```http
POST /api/communications/notificaciones/marcar-todas-leidas/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Todas las notificaciones marcadas como leídas",
  "data": {
    "notificaciones_actualizadas": 8,
    "fecha_actualizacion": "2025-09-30T00:00:00Z"
  }
}
```

---

### 9. Enviar Notificación Personalizada
```http
POST /api/communications/notificaciones/enviar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "destinatarios": {
    "tipo": "viviendas",
    "ids": [1, 5, 10, 15]
  },
  "titulo": "Reunión Extraordinaria Urgente",
  "mensaje": "Se convoca a reunión extraordinaria urgente para el día de mañana a las 7:00 PM en el salón social. Asunto: Aprobación de trabajos de emergencia.",
  "tipo": "emergencia",
  "prioridad": "urgente",
  "canales": ["app", "email", "sms"],
  "programar_envio": false,
  "requiere_confirmacion": true
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Notificación enviada exitosamente",
  "data": {
    "notificacion_id": 550,
    "destinatarios_total": 4,
    "enviados_exitosos": 4,
    "enviados_fallidos": 0,
    "canales_utilizados": ["app", "email", "sms"],
    "fecha_envio": "2025-09-30T00:05:00Z",
    "confirmaciones_pendientes": 4
  }
}
```

---

## 💬 MENSAJERÍA INTERNA

### 10. Listar Conversaciones
```http
GET /api/communications/conversaciones/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `estado`: Estado de conversación (activa, archivada, cerrada)
- `tipo`: Tipo de conversación (soporte, consulta, queja, sugerencia)
- `asignado_a`: ID del administrador asignado
- `vivienda`: ID de vivienda específica

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 15,
    "results": [
      {
        "id": 101,
        "asunto": "Problema con ruido en horas nocturnas",
        "tipo": "queja",
        "estado": "activa",
        "prioridad": "media",
        "iniciador": {
          "id": 15,
          "full_name": "Juan Pérez",
          "vivienda": "TORRE-A-101"
        },
        "asignado_a": {
          "id": 5,
          "full_name": "Administrador Principal"
        },
        "fecha_inicio": "2025-09-28T16:45:00Z",
        "ultima_actividad": "2025-09-29T14:20:00Z",
        "mensajes_count": 5,
        "mensajes_no_leidos": 2,
        "etiquetas": ["ruido", "vecinos", "nocturno"]
      },
      {
        "id": 102,
        "asunto": "Solicitud de certificado de residencia",
        "tipo": "consulta",
        "estado": "cerrada",
        "prioridad": "baja",
        "iniciador": {
          "id": 28,
          "full_name": "Ana López",
          "vivienda": "TORRE-B-205"
        },
        "asignado_a": {
          "id": 6,
          "full_name": "Asistente Administrativa"
        },
        "fecha_inicio": "2025-09-25T10:30:00Z",
        "fecha_cierre": "2025-09-26T15:45:00Z",
        "mensajes_count": 3,
        "resolucion": "Certificado emitido y entregado"
      }
    ]
  }
}
```

---

### 11. Iniciar Nueva Conversación
```http
POST /api/communications/conversaciones/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "asunto": "Solicitud de reparación en ascensor",
  "tipo": "soporte",
  "prioridad": "alta",
  "mensaje_inicial": "Buenos días. Reporto que el ascensor de la Torre B está presentando ruidos extraños y movimientos bruscos. Esta situación se viene presentando desde hace 3 días. Solicito revisión urgente.",
  "adjuntos": ["base64_encoded_video_file"],
  "etiquetas": ["ascensor", "mantenimiento", "urgente"]
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Conversación iniciada exitosamente",
  "data": {
    "id": 103,
    "numero_ticket": "CONV-2025-000103",
    "asunto": "Solicitud de reparación en ascensor",
    "tipo": "soporte",
    "prioridad": "alta",
    "estado": "activa",
    "fecha_inicio": "2025-09-30T00:10:00Z",
    "asignado_a": {
      "id": 7,
      "full_name": "Técnico de Mantenimiento"
    },
    "tiempo_respuesta_estimado": "4 horas",
    "mensaje_inicial": {
      "id": 301,
      "contenido": "Buenos días. Reporto que el ascensor de la Torre B está presentando ruidos extraños...",
      "adjuntos_count": 1
    }
  }
}
```

---

### 12. Responder en Conversación
```http
POST /api/communications/conversaciones/{conversacion_id}/mensajes/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "contenido": "Gracias por el reporte. Hemos programado una revisión técnica para mañana a las 9:00 AM. Mientras tanto, recomendamos usar el ascensor de la Torre A como alternativa.",
  "tipo": "respuesta",
  "adjuntos": ["base64_encoded_schedule_document"],
  "programar_seguimiento": "2025-10-02T09:00:00Z"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Mensaje enviado exitosamente",
  "data": {
    "id": 302,
    "conversacion_id": 103,
    "remitente": {
      "id": 7,
      "full_name": "Técnico de Mantenimiento"
    },
    "contenido": "Gracias por el reporte. Hemos programado una revisión técnica...",
    "fecha_envio": "2025-09-30T00:15:00Z",
    "tipo": "respuesta",
    "adjuntos_count": 1,
    "seguimiento_programado": "2025-10-02T09:00:00Z"
  }
}
```

---

### 13. Cerrar Conversación
```http
POST /api/communications/conversaciones/{conversacion_id}/cerrar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "resolucion": "Ascensor reparado exitosamente. Se reemplazaron los cables y se ajustó el sistema de frenado. Funcionamiento normalizado.",
  "satisfaccion_usuario": "alta",
  "tiempo_resolucion": "24 horas",
  "seguimiento_necesario": false
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Conversación cerrada exitosamente",
  "data": {
    "id": 103,
    "estado": "cerrada",
    "fecha_cierre": "2025-10-01T15:30:00Z",
    "resolucion": "Ascensor reparado exitosamente...",
    "tiempo_total_resolucion": "39 horas 20 minutos",
    "mensajes_total": 8,
    "satisfaccion_usuario": "alta",
    "encuesta_enviada": true
  }
}
```

---

## 📊 REPORTES DE COMUNICACIONES

### 14. Dashboard de Comunicaciones
```http
GET /api/communications/dashboard/
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
    "anuncios": {
      "total_publicados": 12,
      "activos": 8,
      "vencidos": 4,
      "visualizaciones_totales": 1850,
      "promedio_visualizaciones": 154.2,
      "comentarios_totales": 89,
      "categoria_mas_usada": "mantenimiento"
    },
    "notificaciones": {
      "total_enviadas": 2340,
      "entregadas_exitosamente": 2298,
      "porcentaje_entrega": 98.2,
      "promedio_tiempo_lectura": "4.5 horas",
      "tasa_lectura": 87.5
    },
    "conversaciones": {
      "total_iniciadas": 25,
      "activas": 8,
      "cerradas": 17,
      "tiempo_promedio_respuesta": "2.3 horas",
      "tiempo_promedio_resolucion": "18.5 horas",
      "satisfaccion_promedio": 4.2,
      "tipos_mas_comunes": [
        {"tipo": "soporte", "cantidad": 12},
        {"tipo": "consulta", "cantidad": 8},
        {"tipo": "queja", "cantidad": 5}
      ]
    },
    "engagement": {
      "usuarios_activos": 185,
      "porcentaje_participacion": 54.4,
      "horario_mayor_actividad": "18:00-21:00",
      "dia_mayor_actividad": "martes"
    }
  }
}
```

---

### 15. Reporte de Efectividad de Comunicaciones
```http
GET /api/communications/reportes/efectividad/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
- `tipo_comunicacion`: Tipo específico (anuncio, notificacion, mensaje)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "desde": "2025-09-01",
      "hasta": "2025-09-30"
    },
    "anuncios": {
      "total_publicados": 12,
      "alcance_promedio": 89.2,
      "tiempo_promedio_lectura": "3.2 minutos",
      "interaccion_promedio": 7.4,
      "categorias_efectivas": [
        {
          "categoria": "emergencia",
          "alcance": 98.5,
          "interaccion": 12.8
        },
        {
          "categoria": "mantenimiento",
          "alcance": 92.1,
          "interaccion": 8.3
        }
      ]
    },
    "notificaciones": {
      "canales_efectividad": [
        {"canal": "app", "entrega": 99.2, "lectura": 94.5},
        {"canal": "email", "entrega": 97.8, "lectura": 78.3},
        {"canal": "sms", "entrega": 98.9, "lectura": 85.7}
      ],
      "horarios_optimos": [
        {"hora": "08:00-10:00", "lectura": 91.2},
        {"hora": "18:00-20:00", "lectura": 89.8}
      ]
    },
    "mensajeria": {
      "tiempo_respuesta_promedio": "2.3 horas",
      "resolucion_primer_contacto": 68.5,
      "satisfaccion_promedio": 4.2,
      "temas_frecuentes": [
        {"tema": "mantenimiento", "cantidad": 35},
        {"tema": "pagos", "cantidad": 28},
        {"tema": "areas_comunes", "cantidad": 22}
      ]
    }
  }
}
```

---

### 16. Exportar Historial de Comunicaciones
```http
POST /api/communications/export/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "tipo_exportacion": "completo",
  "formato": "excel",
  "periodo": {
    "desde": "2025-01-01",
    "hasta": "2025-09-30"
  },
  "incluir": [
    "anuncios",
    "notificaciones",
    "conversaciones",
    "estadisticas"
  ],
  "filtros": {
    "solo_activos": false,
    "incluir_archivados": true,
    "tipos_conversacion": ["soporte", "queja", "consulta"]
  }
}
```

**Response 202 Accepted:**
```json
{
  "success": true,
  "message": "Exportación iniciada exitosamente",
  "data": {
    "exportacion_id": "EXP-COM-001-2025",
    "url_descarga": "https://storage.example.com/exports/comunicaciones/EXP-COM-001-2025.xlsx",
    "fecha_generacion": "2025-09-30T00:20:00Z",
    "expira_en": "2025-10-07T00:20:00Z",
    "total_registros": 1456,
    "url_seguimiento": "/api/communications/exports/EXP-COM-001-2025/estado/"
  }
}
```

---

## 🔔 CONFIGURACIONES DE NOTIFICACIONES

### 17. Obtener Preferencias de Notificación
```http
GET /api/communications/preferencias-notificacion/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "usuario_id": 15,
    "canales_preferidos": ["app", "email"],
    "frecuencia_resumen": "diario",
    "horario_no_molestar": {
      "inicio": "22:00:00",
      "fin": "07:00:00"
    },
    "tipos_notificacion": {
      "anuncios_generales": {
        "activo": true,
        "canales": ["app", "email"]
      },
      "anuncios_urgentes": {
        "activo": true,
        "canales": ["app", "email", "sms"]
      },
      "pagos_vencimientos": {
        "activo": true,
        "canales": ["app", "email"],
        "anticipacion_dias": 3
      },
      "reservas_recordatorios": {
        "activo": true,
        "canales": ["app"],
        "anticipacion_horas": 24
      },
      "mantenimiento_programado": {
        "activo": true,
        "canales": ["app", "email"]
      },
      "emergencias": {
        "activo": true,
        "canales": ["app", "email", "sms"],
        "no_respetar_horario": true
      }
    }
  }
}
```

---

### 18. Actualizar Preferencias de Notificación
```http
PUT /api/communications/preferencias-notificacion/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "canales_preferidos": ["app", "email", "sms"],
  "frecuencia_resumen": "semanal",
  "horario_no_molestar": {
    "inicio": "21:00:00",
    "fin": "08:00:00"
  },
  "tipos_notificacion": {
    "anuncios_generales": {
      "activo": true,
      "canales": ["app"]
    },
    "pagos_vencimientos": {
      "activo": true,
      "canales": ["app", "email", "sms"],
      "anticipacion_dias": 5
    }
  }
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Preferencias actualizadas exitosamente",
  "data": {
    "usuario_id": 15,
    "cambios_aplicados": [
      "SMS agregado como canal preferido",
      "Frecuencia de resumen cambiada a semanal",
      "Horario no molestar ajustado",
      "Anticipación de pagos aumentada a 5 días"
    ],
    "fecha_actualizacion": "2025-09-30T00:25:00Z"
  }
}
```

---

### 19. Plantillas de Mensajes
```http
GET /api/communications/plantillas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `tipo`: Tipo de plantilla (anuncio, notificacion, respuesta_automatica)
- `categoria`: Categoría específica
- `activa`: Solo plantillas activas (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Corte de Servicios",
      "tipo": "anuncio",
      "categoria": "mantenimiento",
      "plantilla": {
        "titulo": "Corte de {servicio} Programado",
        "contenido": "Estimados residentes,\n\nInformamos que el {fecha} se realizará un corte de {servicio} de {hora_inicio} a {hora_fin} para realizar {motivo}.\n\nRecomendaciones:\n{recomendaciones}\n\nAgradecemos su comprensión.",
        "variables": ["servicio", "fecha", "hora_inicio", "hora_fin", "motivo", "recomendaciones"]
      },
      "activa": true,
      "uso_frecuencia": 15
    },
    {
      "id": 2,
      "nombre": "Bienvenida Nuevo Residente",
      "tipo": "notificacion",
      "categoria": "administrativo",
      "plantilla": {
        "titulo": "¡Bienvenido a {conjunto}!",
        "contenido": "Estimado/a {nombre},\n\nLe damos la bienvenida a {conjunto}. Su vivienda {vivienda} está lista.\n\nInformación importante:\n- Administrador: {administrador}\n- Teléfono: {telefono}\n- Horarios de atención: {horarios}\n\n¡Esperamos que disfrute su nueva residencia!",
        "variables": ["conjunto", "nombre", "vivienda", "administrador", "telefono", "horarios"]
      },
      "activa": true,
      "uso_frecuencia": 8
    }
  ]
}
```

---

### 20. Estadísticas de Lectura
```http
GET /api/communications/estadisticas/lectura/{anuncio_id}/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "anuncio": {
      "id": 1,
      "titulo": "Corte de Agua Programado"
    },
    "estadisticas": {
      "total_destinatarios": 340,
      "visualizaciones": 285,
      "porcentaje_lectura": 83.8,
      "tiempo_promedio_lectura": "2.5 minutos",
      "interacciones": 25,
      "compartidos": 8
    },
    "lectura_por_bloque": [
      {
        "bloque": "TORRE-A",
        "destinatarios": 120,
        "leidos": 105,
        "porcentaje": 87.5
      },
      {
        "bloque": "TORRE-B",
        "destinatarios": 110,
        "leidos": 95,
        "porcentaje": 86.4
      },
      {
        "bloque": "TORRE-C",
        "destinatarios": 110,
        "leidos": 85,
        "porcentaje": 77.3
      }
    ],
    "lectura_por_tiempo": [
      {
        "periodo": "0-1 hora",
        "lecturas": 125,
        "porcentaje": 43.9
      },
      {
        "periodo": "1-6 horas",
        "lecturas": 95,
        "porcentaje": 33.3
      },
      {
        "periodo": "6-24 horas",
        "lecturas": 45,
        "porcentaje": 15.8
      },
      {
        "periodo": "Más de 24 horas",
        "lecturas": 20,
        "porcentaje": 7.0
      }
    ]
  }
}
```

---

## ⚠️ CÓDIGOS DE ERROR ESPECÍFICOS

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos de comunicación inválidos |
| 401 | Unauthorized - Token inválido |
| 403 | Forbidden - Sin permisos de comunicación |
| 404 | Not Found - Anuncio/Conversación no encontrada |
| 409 | Conflict - Conversación ya cerrada |
| 422 | Unprocessable Entity - Contenido no válido o destinatarios inválidos |
| 423 | Locked - Anuncio en proceso de edición |
| 429 | Too Many Requests - Límite de envío de mensajes excedido |
| 500 | Internal Server Error - Error del servidor |

---

## 🔒 PERMISOS REQUERIDOS

| Endpoint | Permiso Requerido |
|----------|-------------------|
| GET /anuncios/ | `communications.view_anuncio` |
| POST /anuncios/ | `communications.add_anuncio` |
| PUT /anuncios/{id}/ | `communications.change_anuncio` |
| GET /conversaciones/ | `communications.view_conversacion` |
| POST /conversaciones/ | `communications.add_conversacion` |
| POST /notificaciones/enviar/ | `communications.send_notification` |

---

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Delivery Garantizado**: Sistema de cola para garantizar entrega de notificaciones críticas
2. **Escalamiento**: Notificaciones urgentes escalan automáticamente si no son leídas
3. **Plantillas**: Sistema de plantillas para estandarizar comunicaciones frecuentes
4. **Analíticas**: Tracking completo de engagement y efectividad de comunicaciones
5. **Multicanal**: Soporte para app, email, SMS con preferencias por usuario
6. **Archivo**: Sistema automático de archivo de comunicaciones antiguas