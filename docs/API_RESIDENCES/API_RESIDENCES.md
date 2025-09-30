# API ENDPOINTS - RESIDENCES MODULE

## MÓDULO: GESTIÓN DE VIVIENDAS Y RESIDENTES

### Descripción
Este módulo maneja la administración de viviendas, propietarios, inquilinos, personas autorizadas y mascotas del condominio.

---

## 🏠 GESTIÓN DE VIVIENDAS

### 1. Listar Viviendas
**CU-WEB-003: Gestionar Viviendas y Propietarios**

```http
GET /api/residences/viviendas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20)
- `search`: Búsqueda por identificador o bloque
- `tipo`: Filtrar por tipo (apartamento, casa, local)
- `bloque`: Filtrar por bloque específico
- `piso`: Filtrar por piso
- `tiene_propietario`: Filtrar viviendas con/sin propietario (true/false)
- `tiene_inquilino`: Filtrar viviendas con/sin inquilino (true/false)
- `activo`: Estado activo (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 120,
    "next": "http://api.backresidences.com/api/residences/viviendas/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "identificador": "TORRE-A-101",
        "bloque": "TORRE-A",
        "piso": 1,
        "tipo": "apartamento",
        "metros_cuadrados": "85.50",
        "habitaciones": 3,
        "banos": 2,
        "cuota_administracion": "250000.00",
        "fecha_registro": "2025-01-15T10:00:00Z",
        "activo": true,
        "usuario_propietario": {
          "id": 15,
          "full_name": "Juan Pérez",
          "email": "juan.perez@email.com",
          "telefono": "+573001234567"
        },
        "usuario_inquilino": null,
        "personas_autorizadas_count": 2,
        "mascotas_count": 1,
        "estado_financiero": {
          "deudas_pendientes": 2,
          "monto_pendiente": "500000.00",
          "ultimo_pago": "2025-09-15T00:00:00Z"
        }
      }
    ]
  }
}
```

---

### 2. Obtener Detalles de Vivienda
```http
GET /api/residences/viviendas/{vivienda_id}/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "identificador": "TORRE-A-101",
    "bloque": "TORRE-A",
    "piso": 1,
    "tipo": "apartamento",
    "metros_cuadrados": "85.50",
    "habitaciones": 3,
    "banos": 2,
    "cuota_administracion": "250000.00",
    "fecha_registro": "2025-01-15T10:00:00Z",
    "activo": true,
    "usuario_propietario": {
      "id": 15,
      "full_name": "Juan Pérez",
      "email": "juan.perez@email.com",
      "telefono": "+573001234567",
      "documento_numero": "1234567890"
    },
    "usuario_inquilino": null,
    "personas_autorizadas": [
      {
        "id": 1,
        "nombre": "María",
        "apellido": "Pérez",
        "cedula": "0987654321",
        "parentesco": "esposa",
        "fecha_inicio": "2025-01-15T00:00:00Z",
        "fecha_fin": null,
        "activa": true
      }
    ],
    "mascotas": [
      {
        "id": 1,
        "nombre": "Max",
        "especie": "Perro",
        "raza": "Golden Retriever",
        "peso": "25.50",
        "activa": true
      }
    ],
    "vehiculos": [
      {
        "id": 1,
        "placa": "ABC123",
        "marca": "Toyota",
        "modelo": "Corolla",
        "activo": true
      }
    ]
  }
}
```

---

### 3. Crear Nueva Vivienda
```http
POST /api/residences/viviendas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "identificador": "TORRE-B-205",
  "bloque": "TORRE-B",
  "piso": 2,
  "tipo": "apartamento",
  "metros_cuadrados": "92.75",
  "habitaciones": 3,
  "banos": 2,
  "cuota_administracion": "275000.00",
  "usuario_propietario": 20
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Vivienda creada exitosamente",
  "data": {
    "id": 121,
    "identificador": "TORRE-B-205",
    "bloque": "TORRE-B",
    "piso": 2,
    "tipo": "apartamento",
    "metros_cuadrados": "92.75",
    "habitaciones": 3,
    "banos": 2,
    "cuota_administracion": "275000.00",
    "fecha_registro": "2025-09-29T17:00:00Z",
    "activo": true,
    "usuario_propietario": {
      "id": 20,
      "full_name": "María García"
    }
  }
}
```

---

### 4. Actualizar Vivienda
```http
PUT /api/residences/viviendas/{vivienda_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "cuota_administracion": "260000.00",
  "usuario_inquilino": 25,
  "habitaciones": 3,
  "banos": 2
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Vivienda actualizada exitosamente",
  "data": {
    "id": 1,
    "identificador": "TORRE-A-101",
    "cuota_administracion": "260000.00",
    "usuario_inquilino": {
      "id": 25,
      "full_name": "Carlos Rodríguez"
    }
  }
}
```

---

### 5. Asignar Propietario/Inquilino
```http
PATCH /api/residences/viviendas/{vivienda_id}/assign-resident/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "tipo_residente": "inquilino",
  "usuario": 30,
  "fecha_inicio": "2025-10-01T00:00:00Z",
  "fecha_fin": "2026-10-01T00:00:00Z"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Inquilino asignado exitosamente",
  "data": {
    "vivienda": "TORRE-A-101",
    "tipo_residente": "inquilino",
    "usuario": {
      "id": 30,
      "full_name": "Ana López"
    },
    "fecha_asignacion": "2025-09-29T17:30:00Z"
  }
}
```

---

## 👥 PERSONAS AUTORIZADAS

### 6. Listar Personas Autorizadas
```http
GET /api/residences/personas-autorizadas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `vivienda`: ID de vivienda específica
- `autorizado_por`: ID del usuario que autorizó
- `parentesco`: Tipo de parentesco
- `activa`: Estado activo (true/false)
- `vigente`: Solo personas con autorización vigente (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "vivienda": {
        "id": 1,
        "identificador": "TORRE-A-101"
      },
      "autorizado_por": {
        "id": 15,
        "full_name": "Juan Pérez"
      },
      "cedula": "0987654321",
      "nombre": "María",
      "apellido": "Pérez",
      "telefono": "+573009876543",
      "parentesco": "esposa",
      "fecha_inicio": "2025-01-15T00:00:00Z",
      "fecha_fin": null,
      "fecha_registro": "2025-01-15T10:30:00Z",
      "activa": true,
      "vigente": true,
      "credenciales_activas": 1
    }
  ]
}
```

---

### 7. Registrar Persona Autorizada
```http
POST /api/residences/personas-autorizadas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "vivienda": 1,
  "cedula": "1122334455",
  "nombre": "Carlos",
  "apellido": "Mendoza",
  "telefono": "+573005551234",
  "parentesco": "hijo",
  "fecha_inicio": "2025-09-29T00:00:00Z",
  "fecha_fin": "2025-12-31T23:59:59Z"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Persona autorizada registrada exitosamente",
  "data": {
    "id": 25,
    "vivienda": {
      "id": 1,
      "identificador": "TORRE-A-101"
    },
    "cedula": "1122334455",
    "nombre": "Carlos",
    "apellido": "Mendoza",
    "parentesco": "hijo",
    "fecha_inicio": "2025-09-29T00:00:00Z",
    "fecha_fin": "2025-12-31T23:59:59Z",
    "activa": true,
    "vigente": true
  }
}
```

---

### 8. Renovar Autorización
```http
PATCH /api/residences/personas-autorizadas/{persona_id}/renovar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "nueva_fecha_fin": "2026-12-31T23:59:59Z",
  "motivo": "Renovación anual estándar"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Autorización renovada exitosamente",
  "data": {
    "id": 25,
    "nombre": "Carlos Mendoza",
    "fecha_fin_anterior": "2025-12-31T23:59:59Z",
    "fecha_fin_nueva": "2026-12-31T23:59:59Z",
    "renovado_por": {
      "id": 15,
      "full_name": "Juan Pérez"
    },
    "fecha_renovacion": "2025-09-29T18:00:00Z"
  }
}
```

---

### 9. Revocar Autorización
```http
PATCH /api/residences/personas-autorizadas/{persona_id}/revocar/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "motivo": "Ya no vive en la vivienda",
  "fecha_revocacion": "2025-09-29T18:15:00Z"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Autorización revocada exitosamente",
  "data": {
    "id": 25,
    "nombre": "Carlos Mendoza",
    "activa": false,
    "fecha_revocacion": "2025-09-29T18:15:00Z",
    "motivo": "Ya no vive en la vivienda"
  }
}
```

---

## 🐕 GESTIÓN DE MASCOTAS

### 10. Listar Mascotas
```http
GET /api/residences/mascotas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `vivienda`: ID de vivienda específica
- `especie`: Filtrar por especie
- `activa`: Estado activo (true/false)
- `vacunas_al_dia`: Filtrar por estado de vacunas (true/false)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "vivienda": {
        "id": 1,
        "identificador": "TORRE-A-101",
        "propietario": "Juan Pérez"
      },
      "nombre": "Max",
      "especie": "Perro",
      "raza": "Golden Retriever",
      "peso": "25.50",
      "color": "Dorado",
      "fecha_nacimiento": "2022-03-15",
      "vacunas_al_dia": true,
      "foto_url": "https://storage.example.com/pets/max_1.jpg",
      "fecha_registro": "2025-01-20T14:30:00Z",
      "activa": true,
      "edad_meses": 42
    }
  ]
}
```

---

### 11. Registrar Nueva Mascota
```http
POST /api/residences/mascotas/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "vivienda": 1,
  "nombre": "Luna",
  "especie": "Gato",
  "raza": "Persa",
  "peso": "4.20",
  "color": "Blanco",
  "fecha_nacimiento": "2023-06-10",
  "vacunas_al_dia": true,
  "foto_url": "https://storage.example.com/pets/luna_1.jpg"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Mascota registrada exitosamente",
  "data": {
    "id": 15,
    "vivienda": {
      "id": 1,
      "identificador": "TORRE-A-101"
    },
    "nombre": "Luna",
    "especie": "Gato",
    "raza": "Persa",
    "peso": "4.20",
    "color": "Blanco",
    "fecha_nacimiento": "2023-06-10",
    "vacunas_al_dia": true,
    "fecha_registro": "2025-09-29T18:30:00Z",
    "activa": true
  }
}
```

---

### 12. Actualizar Información de Mascota
```http
PUT /api/residences/mascotas/{mascota_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "peso": "26.00",
  "vacunas_al_dia": true,
  "foto_url": "https://storage.example.com/pets/max_updated.jpg"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Información de mascota actualizada",
  "data": {
    "id": 1,
    "nombre": "Max",
    "peso": "26.00",
    "vacunas_al_dia": true,
    "foto_url": "https://storage.example.com/pets/max_updated.jpg",
    "fecha_actualizacion": "2025-09-29T18:45:00Z"
  }
}
```

---

### 13. Historial Veterinario de Mascota
```http
GET /api/residences/mascotas/{mascota_id}/historial-veterinario/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "mascota": {
      "id": 1,
      "nombre": "Max",
      "especie": "Perro"
    },
    "historial": [
      {
        "fecha": "2025-08-15",
        "tipo": "vacuna",
        "descripcion": "Vacuna antirrábica anual",
        "veterinario": "Dr. López",
        "clinica": "Veterinaria Central",
        "proxima_cita": "2026-08-15"
      },
      {
        "fecha": "2025-06-10",
        "tipo": "consulta",
        "descripcion": "Revisión general de rutina",
        "veterinario": "Dr. López",
        "clinica": "Veterinaria Central",
        "observaciones": "Mascota en excelente estado"
      }
    ]
  }
}
```

---

## 📊 REPORTES Y ESTADÍSTICAS

### 14. Dashboard de Residencias
```http
GET /api/residences/dashboard/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "viviendas": {
      "total": 120,
      "ocupadas": 115,
      "disponibles": 5,
      "con_inquilinos": 45,
      "solo_propietarios": 70
    },
    "residentes": {
      "total_propietarios": 115,
      "total_inquilinos": 45,
      "personas_autorizadas": 180,
      "credenciales_activas": 340
    },
    "mascotas": {
      "total": 85,
      "perros": 60,
      "gatos": 20,
      "otras": 5,
      "vacunas_al_dia": 78
    },
    "distribucion_por_tipo": {
      "apartamentos": 110,
      "casas": 8,
      "locales": 2
    },
    "ocupacion_por_bloque": [
      {
        "bloque": "TORRE-A",
        "total": 40,
        "ocupadas": 38,
        "porcentaje": 95.0
      },
      {
        "bloque": "TORRE-B",
        "total": 40,
        "ocupadas": 39,
        "porcentaje": 97.5
      }
    ]
  }
}
```

---

### 15. Reporte de Viviendas
```http
GET /api/residences/reports/viviendas/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `format`: Formato del reporte (json, pdf, excel)
- `incluir_financiero`: Incluir información financiera (true/false)
- `bloque`: Filtrar por bloque específico

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "fecha_generacion": "2025-09-29T19:00:00Z",
    "total_viviendas": 120,
    "resumen": {
      "ocupacion_general": "95.8%",
      "promedio_cuota": "265000.00",
      "total_metros_cuadrados": "10245.75"
    },
    "por_bloque": [
      {
        "bloque": "TORRE-A",
        "viviendas": 40,
        "ocupadas": 38,
        "promedio_m2": "87.25",
        "promedio_cuota": "260000.00"
      }
    ],
    "detalles": [
      {
        "identificador": "TORRE-A-101",
        "propietario": "Juan Pérez",
        "inquilino": null,
        "m2": "85.50",
        "cuota": "250000.00",
        "estado_financiero": "al_dia",
        "personas_autorizadas": 2,
        "mascotas": 1
      }
    ]
  }
}
```

---

### 16. Buscar Residentes
```http
GET /api/residences/search/residentes/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `q`: Término de búsqueda (nombre, email, documento, vivienda)
- `tipo`: Tipo de residente (propietario, inquilino, autorizado)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "tipo": "propietario",
      "usuario": {
        "id": 15,
        "full_name": "Juan Pérez",
        "email": "juan.perez@email.com",
        "documento": "1234567890"
      },
      "vivienda": {
        "id": 1,
        "identificador": "TORRE-A-101"
      },
      "fecha_relacion": "2025-01-15T00:00:00Z"
    },
    {
      "tipo": "autorizado",
      "persona": {
        "id": 1,
        "nombre": "María Pérez",
        "cedula": "0987654321",
        "parentesco": "esposa"
      },
      "vivienda": {
        "id": 1,
        "identificador": "TORRE-A-101"
      },
      "autorizado_por": "Juan Pérez",
      "vigente": true
    }
  ]
}
```

---

### 17. Viviendas Disponibles
```http
GET /api/residences/viviendas/disponibles/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `tipo`: Tipo de vivienda
- `min_habitaciones`: Mínimo de habitaciones
- `max_cuota`: Cuota máxima

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 85,
      "identificador": "TORRE-C-305",
      "bloque": "TORRE-C",
      "piso": 3,
      "tipo": "apartamento",
      "metros_cuadrados": "95.25",
      "habitaciones": 3,
      "banos": 2,
      "cuota_administracion": "285000.00",
      "disponible_desde": "2025-10-01T00:00:00Z",
      "caracteristicas": [
        "Balcón",
        "Parqueadero",
        "Depósito"
      ]
    }
  ]
}
```

---

### 18. Exportar Datos de Residentes
```http
POST /api/residences/export/residentes/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "formato": "excel",
  "incluir": [
    "propietarios",
    "inquilinos",
    "personas_autorizadas",
    "mascotas"
  ],
  "filtros": {
    "bloque": ["TORRE-A", "TORRE-B"],
    "solo_activos": true
  }
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Exportación generada exitosamente",
  "data": {
    "archivo_id": "EXP-RES-001-2025",
    "url_descarga": "https://storage.example.com/exports/residentes/EXP-RES-001-2025.xlsx",
    "fecha_generacion": "2025-09-29T19:15:00Z",
    "expira_en": "2025-10-06T19:15:00Z",
    "total_registros": 340
  }
}
```

---

## ⚠️ CÓDIGOS DE ERROR ESPECÍFICOS

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido |
| 403 | Forbidden - Sin permisos sobre vivienda |
| 404 | Not Found - Vivienda/Persona/Mascota no encontrada |
| 409 | Conflict - Identificador de vivienda duplicado |
| 422 | Unprocessable Entity - Validación de negocio fallida |
| 423 | Locked - Vivienda tiene procesos pendientes |
| 500 | Internal Server Error - Error del servidor |

---

## 🔒 PERMISOS REQUERIDOS

| Endpoint | Permiso Requerido |
|----------|-------------------|
| GET /viviendas/ | `residences.view_vivienda` |
| POST /viviendas/ | `residences.add_vivienda` |
| PUT /viviendas/{id}/ | `residences.change_vivienda` |
| GET /personas-autorizadas/ | `residences.view_personaautorizada` |
| POST /personas-autorizadas/ | `residences.add_personaautorizada` |
| GET /mascotas/ | `residences.view_mascota` |
| POST /mascotas/ | `residences.add_mascota` |

---

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Validaciones de Negocio**: Una vivienda no puede tener más de un propietario activo
2. **Soft Delete**: Las entidades se marcan como inactivas en lugar de eliminarse
3. **Historial**: Se mantiene historial de cambios de propietarios/inquilinos
4. **Notificaciones**: Cambios importantes generan notificaciones automáticas
5. **Integración**: Compatible con sistemas de facturación para cuotas
6. **Backup**: Respaldo automático de fotos de mascotas y documentos