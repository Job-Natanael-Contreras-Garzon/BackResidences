# API ENDPOINTS - SECURITY MODULE

## MÓDULO: SEGURIDAD Y CONTROL DE ACCESO

### Descripción
Este módulo maneja todo el sistema de seguridad del condominio incluyendo eventos de seguridad, control de vehículos, gestión de cámaras, zonas de seguridad y credenciales de acceso.

---

## 🛡️ EVENTOS DE SEGURIDAD

### 1. Listar Eventos de Seguridad
**CU-WEB-010: Administrar Sistema de Seguridad**

```http
GET /api/security/events/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20)
- `start_date`: Fecha de inicio (YYYY-MM-DD)
- `end_date`: Fecha de fin (YYYY-MM-DD)
- `tipo_evento`: ID del tipo de evento
- `severidad`: Nivel de severidad (1-4)
- `revisado`: Filtrar por eventos revisados (true/false)
- `zona`: ID de la zona
- `camara`: ID de la cámara

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 45,
    "next": "http://api.backresidences.com/api/security/events/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "tipo_evento": {
          "id": 1,
          "nombre": "Acceso No Autorizado",
          "severidad": 3
        },
        "camara": {
          "id": 1,
          "nombre": "Cámara Entrada Principal",
          "zona": "Entrada Principal"
        },
        "usuario": {
          "id": 15,
          "full_name": "Juan Pérez",
          "documento": "1234567890"
        },
        "vehiculo_autorizado": null,
        "fecha_hora": "2025-09-29T14:30:00Z",
        "descripcion": "Intento de acceso con tarjeta vencida",
        "evidencia_url": "https://storage.example.com/evidence/event_1.jpg",
        "severidad": 3,
        "revisado": false,
        "resuelto_por": null,
        "fecha_resolucion": null,
        "notas_resolucion": null
      }
    ]
  }
}
```

---

### 2. Crear Evento de Seguridad
```http
POST /api/security/events/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "tipo_evento": 1,
  "camara": 1,
  "usuario": 15,
  "vehiculo_autorizado": null,
  "descripcion": "Intento de acceso con tarjeta vencida",
  "evidencia_url": "https://storage.example.com/evidence/event_new.jpg",
  "severidad": 3
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Evento de seguridad registrado exitosamente",
  "data": {
    "id": 46,
    "tipo_evento": {
      "id": 1,
      "nombre": "Acceso No Autorizado"
    },
    "fecha_hora": "2025-09-29T16:45:00Z",
    "descripcion": "Intento de acceso con tarjeta vencida",
    "severidad": 3,
    "revisado": false
  }
}
```

---

### 3. Marcar Evento como Revisado
```http
PATCH /api/security/events/{event_id}/review/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "revisado": true,
  "notas_resolucion": "Evento verificado, usuario notificado para renovar tarjeta"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Evento marcado como revisado",
  "data": {
    "id": 1,
    "revisado": true,
    "resuelto_por": {
      "id": 2,
      "full_name": "Admin Sistema"
    },
    "fecha_resolucion": "2025-09-29T17:00:00Z",
    "notas_resolucion": "Evento verificado, usuario notificado para renovar tarjeta"
  }
}
```

---

## 🚗 GESTIÓN DE VEHÍCULOS

### 4. Listar Vehículos Autorizados
**CU-WEB-011: Gestionar Vehículos Autorizados**

```http
GET /api/security/vehicles/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Número de página
- `search`: Búsqueda por placa, marca o modelo
- `usuario`: ID del usuario propietario
- `tipo_vehiculo`: Tipo (auto, moto, bicicleta)
- `activo`: Estado activo (true/false)
- `aprobado`: Estado de aprobación (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 85,
    "results": [
      {
        "id": 1,
        "usuario": {
          "id": 15,
          "full_name": "Juan Pérez",
          "vivienda": "TORRE-A-101"
        },
        "placa": "ABC123",
        "marca": "Toyota",
        "modelo": "Corolla",
        "anio": 2020,
        "color": "Blanco",
        "tipo_vehiculo": "auto",
        "fecha_registro": "2025-09-15T10:30:00Z",
        "aprobado_por": {
          "id": 2,
          "full_name": "Admin Sistema"
        },
        "fecha_aprobacion": "2025-09-16T09:00:00Z",
        "activo": true
      }
    ]
  }
}
```

---

### 5. Registrar Nuevo Vehículo
```http
POST /api/security/vehicles/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "usuario": 15,
  "placa": "XYZ789",
  "marca": "Mazda",
  "modelo": "CX-5",
  "anio": 2022,
  "color": "Negro",
  "tipo_vehiculo": "auto"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Vehículo registrado exitosamente. Pendiente de aprobación.",
  "data": {
    "id": 86,
    "placa": "XYZ789",
    "marca": "Mazda",
    "modelo": "CX-5",
    "fecha_registro": "2025-09-29T17:15:00Z",
    "aprobado_por": null,
    "fecha_aprobacion": null,
    "activo": true
  }
}
```

---

### 6. Aprobar/Rechazar Vehículo
```http
PATCH /api/security/vehicles/{vehicle_id}/approve/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "aprobado": true,
  "notas": "Documentación verificada correctamente"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Vehículo aprobado exitosamente",
  "data": {
    "id": 86,
    "placa": "XYZ789",
    "aprobado_por": {
      "id": 2,
      "full_name": "Admin Sistema"
    },
    "fecha_aprobacion": "2025-09-29T17:30:00Z",
    "activo": true
  }
}
```

---

### 7. Vehículos Pendientes de Aprobación
```http
GET /api/security/vehicles/pending/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 87,
      "usuario": {
        "id": 20,
        "full_name": "María García",
        "vivienda": "TORRE-B-205"
      },
      "placa": "DEF456",
      "marca": "Honda",
      "modelo": "Civic",
      "anio": 2021,
      "color": "Azul",
      "tipo_vehiculo": "auto",
      "fecha_registro": "2025-09-29T16:00:00Z",
      "dias_pendiente": 0
    }
  ]
}
```

---

## 🎥 GESTIÓN DE CÁMARAS Y ZONAS

### 8. Listar Zonas de Seguridad
```http
GET /api/security/zones/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Entrada Principal",
      "tipo": "entrada",
      "descripcion": "Zona de acceso principal del condominio",
      "nivel_seguridad": "alto",
      "activa": true,
      "camaras_count": 3,
      "eventos_hoy": 5
    },
    {
      "id": 2,
      "nombre": "Parqueadero Nivel 1",
      "tipo": "parqueadero",
      "descripcion": "Parqueadero subterráneo nivel 1",
      "nivel_seguridad": "medio",
      "activa": true,
      "camaras_count": 6,
      "eventos_hoy": 2
    }
  ]
}
```

---

### 9. Listar Cámaras
```http
GET /api/security/cameras/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `zona`: ID de la zona
- `activa`: Estado activo (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "zona": {
        "id": 1,
        "nombre": "Entrada Principal"
      },
      "nombre": "Cámara Entrada Principal",
      "ubicacion": "Puerta principal, lado derecho",
      "direccion_ip": "192.168.1.100",
      "puerto": 80,
      "url_stream": "rtsp://192.168.1.100:554/stream1",
      "modelo": "Hikvision DS-2CD2142FWD-I",
      "resolucion": "1080p",
      "vision_nocturna": true,
      "angulo_vision": 90,
      "fecha_instalacion": "2025-01-15",
      "ultimo_mantenimiento": "2025-08-15",
      "activa": true,
      "estado_conexion": "online"
    }
  ]
}
```

---

### 10. Crear Nueva Zona
```http
POST /api/security/zones/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "nombre": "Zona Piscina",
  "tipo": "piscina",
  "descripcion": "Área de piscina y zona húmeda",
  "nivel_seguridad": "medio"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Zona creada exitosamente",
  "data": {
    "id": 5,
    "nombre": "Zona Piscina",
    "tipo": "piscina",
    "descripcion": "Área de piscina y zona húmeda",
    "nivel_seguridad": "medio",
    "activa": true
  }
}
```

---

### 11. Registrar Nueva Cámara
```http
POST /api/security/cameras/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "zona": 5,
  "nombre": "Cámara Piscina Norte",
  "ubicacion": "Esquina norte de la piscina",
  "direccion_ip": "192.168.1.105",
  "puerto": 80,
  "url_stream": "rtsp://192.168.1.105:554/stream1",
  "modelo": "Dahua IPC-HFW2231S-S-S2",
  "resolucion": "1080p",
  "vision_nocturna": true,
  "angulo_vision": 110
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Cámara registrada exitosamente",
  "data": {
    "id": 12,
    "nombre": "Cámara Piscina Norte",
    "zona": {
      "id": 5,
      "nombre": "Zona Piscina"
    },
    "direccion_ip": "192.168.1.105",
    "activa": true,
    "estado_conexion": "pending"
  }
}
```

---

## 🔑 CREDENCIALES DE ACCESO

### 12. Listar Credenciales de Acceso
**CU-WEB-012: Configurar Controles de Acceso**

```http
GET /api/security/credentials/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `usuario`: ID del usuario
- `tipo`: Tipo de credencial (tarjeta, pin, biometrico, app)
- `estado`: Estado (activo, bloqueado, vencido)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "usuario": {
        "id": 15,
        "full_name": "Juan Pérez",
        "vivienda": "TORRE-A-101"
      },
      "vehiculo_autorizado": {
        "id": 1,
        "placa": "ABC123"
      },
      "identificador": "CARD-001-2025",
      "tipo": "tarjeta",
      "estado": "activo",
      "fecha_emision": "2025-09-01T10:00:00Z",
      "fecha_vencimiento": "2026-09-01T10:00:00Z",
      "ultimo_uso": "2025-09-29T08:30:00Z",
      "dias_para_vencer": 337
    }
  ]
}
```

---

### 13. Emitir Nueva Credencial
```http
POST /api/security/credentials/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "usuario": 15,
  "vehiculo_autorizado": 1,
  "identificador": "CARD-002-2025",
  "tipo": "tarjeta",
  "fecha_vencimiento": "2026-09-29T23:59:59Z"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Credencial emitida exitosamente",
  "data": {
    "id": 45,
    "identificador": "CARD-002-2025",
    "tipo": "tarjeta",
    "estado": "activo",
    "fecha_emision": "2025-09-29T17:45:00Z",
    "fecha_vencimiento": "2026-09-29T23:59:59Z"
  }
}
```

---

### 14. Bloquear/Desbloquear Credencial
```http
PATCH /api/security/credentials/{credential_id}/toggle-status/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "estado": "bloqueado",
  "motivo": "Tarjeta reportada como perdida"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Credencial bloqueada exitosamente",
  "data": {
    "id": 1,
    "identificador": "CARD-001-2025",
    "estado": "bloqueado",
    "motivo_cambio": "Tarjeta reportada como perdida",
    "fecha_cambio": "2025-09-29T18:00:00Z"
  }
}
```

---

### 15. Registrar Uso de Credencial
```http
POST /api/security/credentials/{credential_id}/register-use/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "zona": 1,
  "tipo_acceso": "entrada",
  "exitoso": true
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Uso de credencial registrado",
  "data": {
    "credencial": "CARD-001-2025",
    "zona": "Entrada Principal",
    "fecha_uso": "2025-09-29T18:15:00Z",
    "exitoso": true
  }
}
```

---

## 📊 TIPOS DE EVENTOS

### 16. Listar Tipos de Eventos
```http
GET /api/security/event-types/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Acceso No Autorizado",
      "descripcion": "Intento de acceso con credenciales inválidas o vencidas",
      "severidad": 3,
      "eventos_count": 25,
      "activo": true
    },
    {
      "id": 2,
      "nombre": "Movimiento Detectado",
      "descripcion": "Detección de movimiento en zona restringida",
      "severidad": 2,
      "eventos_count": 120,
      "activo": true
    }
  ]
}
```

---

### 17. Crear Tipo de Evento
```http
POST /api/security/event-types/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "nombre": "Emergencia Médica",
  "descripcion": "Evento de emergencia médica en las instalaciones",
  "severidad": 4
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Tipo de evento creado exitosamente",
  "data": {
    "id": 8,
    "nombre": "Emergencia Médica",
    "descripcion": "Evento de emergencia médica en las instalaciones",
    "severidad": 4,
    "activo": true
  }
}
```

---

## 📈 REPORTES Y ESTADÍSTICAS

### 18. Dashboard de Seguridad
```http
GET /api/security/dashboard/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `period`: Período de análisis (today, week, month, year)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "resumen": {
      "eventos_hoy": 12,
      "eventos_pendientes": 3,
      "vehiculos_registrados": 85,
      "vehiculos_pendientes": 2,
      "camaras_activas": 24,
      "camaras_offline": 1,
      "credenciales_activas": 150,
      "credenciales_por_vencer": 8
    },
    "eventos_por_severidad": {
      "baja": 45,
      "media": 20,
      "alta": 8,
      "critica": 2
    },
    "eventos_por_zona": [
      {
        "zona": "Entrada Principal",
        "eventos": 25
      },
      {
        "zona": "Parqueadero",
        "eventos": 18
      }
    ],
    "tendencias": {
      "eventos_ultima_semana": [5, 8, 12, 6, 15, 10, 12],
      "accesos_exitosos": 245,
      "accesos_denegados": 12
    }
  }
}
```

---

### 19. Reporte de Eventos por Período
```http
GET /api/security/reports/events/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `start_date`: Fecha de inicio (YYYY-MM-DD)
- `end_date`: Fecha de fin (YYYY-MM-DD)
- `format`: Formato de reporte (json, pdf, excel)
- `zona`: ID de zona específica
- `severidad`: Nivel de severidad

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "inicio": "2025-09-01",
      "fin": "2025-09-29"
    },
    "resumen": {
      "total_eventos": 175,
      "eventos_resueltos": 170,
      "eventos_pendientes": 5,
      "promedio_diario": 6.03
    },
    "por_tipo": [
      {
        "tipo": "Acceso No Autorizado",
        "cantidad": 45,
        "porcentaje": 25.7
      },
      {
        "tipo": "Movimiento Detectado",
        "cantidad": 80,
        "porcentaje": 45.7
      }
    ],
    "por_zona": [
      {
        "zona": "Entrada Principal",
        "eventos": 75,
        "porcentaje": 42.9
      }
    ]
  }
}
```

---

### 20. Exportar Reporte
```http
POST /api/security/reports/export/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "tipo_reporte": "eventos",
  "formato": "pdf",
  "filtros": {
    "start_date": "2025-09-01",
    "end_date": "2025-09-29",
    "zona": [1, 2],
    "severidad": [3, 4]
  },
  "incluir_graficos": true
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Reporte generado exitosamente",
  "data": {
    "reporte_id": "RPT-SEC-001-2025",
    "url_descarga": "https://storage.example.com/reports/security/RPT-SEC-001-2025.pdf",
    "fecha_generacion": "2025-09-29T18:30:00Z",
    "expira_en": "2025-10-06T18:30:00Z"
  }
}
```

---

## ⚠️ CÓDIGOS DE ERROR ESPECÍFICOS

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido |
| 403 | Forbidden - Sin permisos de seguridad |
| 404 | Not Found - Evento/Vehículo/Cámara no encontrado |
| 409 | Conflict - Placa de vehículo duplicada |
| 422 | Unprocessable Entity - Credencial inválida |
| 424 | Failed Dependency - Cámara offline |
| 500 | Internal Server Error - Error del servidor |

---

## 🔒 PERMISOS REQUERIDOS

| Endpoint | Permiso Requerido |
|----------|-------------------|
| GET /events/ | `security.view_eventoseguridad` |
| POST /events/ | `security.add_eventoseguridad` |
| PATCH /events/{id}/review/ | `security.change_eventoseguridad` |
| GET /vehicles/ | `security.view_vehiculoautorizado` |
| POST /vehicles/ | `security.add_vehiculoautorizado` |
| PATCH /vehicles/{id}/approve/ | `security.approve_vehiculoautorizado` |
| GET /cameras/ | `security.view_camara` |
| POST /cameras/ | `security.add_camara` |
| GET /credentials/ | `security.view_credentialacceso` |
| POST /credentials/ | `security.add_credentialacceso` |

---

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Tiempo Real**: Los eventos de seguridad se pueden recibir via WebSocket
2. **Almacenamiento**: Las evidencias se almacenan en S3 compatible
3. **Integraciones**: Compatible con sistemas ONVIF para cámaras IP
4. **Notificaciones**: Eventos críticos generan notificaciones push automáticas
5. **Backup**: Los videos se respaldan automáticamente por 30 días
6. **Acceso de Emergencia**: Códigos maestros para situaciones de emergencia