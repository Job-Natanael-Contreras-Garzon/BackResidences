# API ENDPOINTS - AUTHENTICATION MODULE

## MÓDULO: GESTIÓN DE USUARIOS Y ROLES

### Descripción
Este módulo maneja toda la autenticación, autorización y gestión de usuarios del sistema BackResidences. Incluye registro, login, gestión de roles y permisos.

---

## 🔐 AUTENTICACIÓN BÁSICA

### 1. Registro de Usuario
**CU-WEB-001: Registrar Nuevo Usuario en el Sistema**

```http
POST /api/auth/register/
```

**Request Body:**
```json
{
  "username": "user@example.com",
  "email": "user@example.com",
  "password": "securePassword123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "telefono": "+573001234567",
  "documento_tipo": "CC",
  "documento_numero": "1234567890"
}
```
            ('CC', 'Cédula de Ciudadanía'),
            ('CE', 'Cédula de Extranjería'),
            ('PAS', 'Pasaporte')
**Response 201 Created:**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "data": {
    "user": {
      "id": 1,
      "username": "user@example.com",
      "email": "user@example.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "telefono": "+573001234567",
      "documento_tipo": "CC",
      "documento_numero": "1234567890",
      "fecha_registro": "2025-09-29T10:30:00Z",
      "activo": true,
      "email_verificado": false
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}
```

**Response 400 Bad Request:**
```json
{
  "success": false,
  "message": "Error en los datos proporcionados",
  "errors": {
    "email": ["Este email ya está registrado"],
    "documento_numero": ["Este documento ya está registrado"],
    "password": ["La contraseña debe tener al menos 8 caracteres"]
  }
}
```

---

### 2. Inicio de Sesión
```http
POST /api/auth/login/
```

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "securePassword123"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "user": {
      "id": 1,
      "username": "user@example.com",
      "email": "user@example.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "roles": ["residente", "propietario"],
      "permissions": ["auth.view_user", "residences.view_vivienda"]
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}
```

**Response 401 Unauthorized:**
```json
{
  "success": false,
  "message": "Credenciales inválidas",
  "errors": {
    "non_field_errors": ["Email o contraseña incorrectos"]
  }
}
```

---

### 3. Cerrar Sesión
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Sesión cerrada exitosamente"
}
```

---

### 4. Renovar Token
```http
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

---

## 👥 GESTIÓN DE USUARIOS

### 5. Listar Usuarios (Solo Administradores)
**CU-WEB-004: Auditar Actividad de Usuarios**

```http
GET /api/auth/users/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20)
- `search`: Búsqueda por nombre, email o documento
- `is_active`: Filtrar por estado activo (true/false)
- `role`: Filtrar por rol específico

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "count": 150,
    "next": "http://api.backresidences.com/api/auth/users/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "username": "user1@example.com",
        "email": "user1@example.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "telefono": "+573001234567",
        "documento_tipo": "CC",
        "documento_numero": "1234567890",
        "fecha_registro": "2025-09-29T10:30:00Z",
        "ultimo_login": "2025-09-29T15:45:00Z",
        "activo": true,
        "email_verificado": true,
        "roles": ["residente"]
      }
    ]
  }
}
```

---

### 6. Obtener Detalles de Usuario
```http
GET /api/auth/users/{user_id}/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "telefono": "+573001234567",
    "documento_tipo": "CC",
    "documento_numero": "1234567890",
    "fecha_registro": "2025-09-29T10:30:00Z",
    "ultimo_login": "2025-09-29T15:45:00Z",
    "activo": true,
    "email_verificado": true,
    "roles": [
      {
        "id": 1,
        "nombre": "residente",
        "descripcion": "Usuario residente del condominio"
      }
    ],
    "permissions": [
      "auth.view_user",
      "residences.view_vivienda",
      "payments.view_deuda"
    ]
  }
}
```

---

### 7. Actualizar Usuario
```http
PUT /api/auth/users/{user_id}/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Juan Carlos",
  "last_name": "Pérez González",
  "telefono": "+573009876543",
  "activo": true
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Usuario actualizado exitosamente",
  "data": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "Juan Carlos",
    "last_name": "Pérez González",
    "telefono": "+573009876543",
    "activo": true
  }
}
```

---

## 🔑 GESTIÓN DE ROLES

### 8. Listar Roles
**CU-WEB-002: Gestionar Roles y Permisos**

```http
GET /api/auth/roles/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "administrador",
      "descripcion": "Administrador del sistema con acceso completo",
      "created_at": "2025-09-29T10:00:00Z",
      "activo": true,
      "usuarios_count": 2,
      "permisos_count": 25
    },
    {
      "id": 2,
      "nombre": "residente",
      "descripcion": "Usuario residente del condominio",
      "created_at": "2025-09-29T10:00:00Z",
      "activo": true,
      "usuarios_count": 120,
      "permisos_count": 8
    }
  ]
}
```

---

### 9. Crear Rol
```http
POST /api/auth/roles/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "nombre": "portero",
  "descripcion": "Personal de portería y seguridad",
  "permisos": [1, 5, 8, 12]
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Rol creado exitosamente",
  "data": {
    "id": 3,
    "nombre": "portero",
    "descripcion": "Personal de portería y seguridad",
    "created_at": "2025-09-29T16:30:00Z",
    "activo": true,
    "permisos": [
      {
        "id": 1,
        "codigo": "security.view_evento",
        "nombre": "Ver eventos de seguridad"
      }
    ]
  }
}
```

---

### 10. Asignar Rol a Usuario
```http
POST /api/auth/users/{user_id}/assign-role/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "rol_id": 2,
  "fecha_vencimiento": "2026-12-31T23:59:59Z"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Rol asignado exitosamente",
  "data": {
    "usuario": "Juan Pérez",
    "rol": "residente",
    "fecha_asignacion": "2025-09-29T16:45:00Z",
    "fecha_vencimiento": "2026-12-31T23:59:59Z",
    "asignado_por": "admin@backresidences.com"
  }
}
```

---

## 🛡️ GESTIÓN DE PERMISOS

### 11. Listar Permisos
```http
GET /api/auth/permissions/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `modulo`: Filtrar por módulo (auth, security, payments, etc.)

**Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "codigo": "auth.create_user",
      "nombre": "Crear usuarios",
      "descripcion": "Permite crear nuevos usuarios en el sistema",
      "modulo": "auth",
      "activo": true
    },
    {
      "id": 2,
      "codigo": "security.view_evento",
      "nombre": "Ver eventos de seguridad",
      "descripcion": "Permite visualizar eventos de seguridad",
      "modulo": "security",
      "activo": true
    }
  ]
}
```

---

### 12. Verificar Permisos de Usuario
```http
GET /api/auth/users/{user_id}/permissions/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "permissions": [
      {
        "codigo": "auth.view_user",
        "nombre": "Ver usuarios",
        "modulo": "auth",
        "origen": "rol_residente"
      },
      {
        "codigo": "payments.view_deuda",
        "nombre": "Ver deudas",
        "modulo": "payments",
        "origen": "rol_residente"
      }
    ],
    "roles": ["residente"]
  }
}
```

---

## 🔍 PERFIL Y AUDITORÍA

### 13. Obtener Perfil Actual
```http
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "telefono": "+573001234567",
    "documento_tipo": "CC",
    "documento_numero": "1234567890",
    "fecha_registro": "2025-09-29T10:30:00Z",
    "ultimo_login": "2025-09-29T15:45:00Z",
    "activo": true,
    "email_verificado": true,
    "viviendas": [
      {
        "id": 1,
        "identificador": "TORRE-A-101",
        "tipo": "apartamento",
        "rol": "propietario"
      }
    ]
  }
}
```

---

### 14. Actualizar Perfil
```http
PUT /api/auth/profile/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Juan Carlos",
  "last_name": "Pérez González",
  "telefono": "+573009876543"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Perfil actualizado exitosamente",
  "data": {
    "id": 1,
    "first_name": "Juan Carlos",
    "last_name": "Pérez González",
    "telefono": "+573009876543"
  }
}
```

---

### 15. Cambiar Contraseña
```http
POST /api/auth/change-password/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "currentPassword123",
  "new_password": "newSecurePassword456",
  "confirm_password": "newSecurePassword456"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Contraseña cambiada exitosamente"
}
```

---

### 16. Auditoría de Actividad de Usuario
**CU-WEB-004: Auditar Actividad de Usuarios**

```http
GET /api/auth/users/{user_id}/activity/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `start_date`: Fecha de inicio (YYYY-MM-DD)
- `end_date`: Fecha de fin (YYYY-MM-DD)
- `action`: Tipo de acción (LOGIN, CREATE, UPDATE, DELETE)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "user@example.com",
      "full_name": "Juan Pérez"
    },
    "activities": [
      {
        "id": 1,
        "accion": "LOGIN",
        "fecha_hora": "2025-09-29T15:45:00Z",
        "ip_origen": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "modulo": "authentication",
        "detalles": "Login exitoso desde aplicación web"
      },
      {
        "id": 2,
        "accion": "UPDATE",
        "fecha_hora": "2025-09-29T16:00:00Z",
        "tabla": "residences_vivienda",
        "id_registro_afectado": "1",
        "modulo": "residences",
        "detalles": "Actualización de información de vivienda"
      }
    ]
  }
}
```

---

## 📊 ENDPOINTS DE ESTADÍSTICAS

### 17. Estadísticas de Usuarios
```http
GET /api/auth/stats/users/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "total_usuarios": 150,
    "usuarios_activos": 142,
    "usuarios_inactivos": 8,
    "nuevos_este_mes": 12,
    "por_tipo": {
      "propietarios": 95,
      "inquilinos": 40,
      "administradores": 3,
      "personal": 12
    },
    "ultimo_login": {
      "hoy": 45,
      "esta_semana": 98,
      "este_mes": 130
    }
  }
}
```

---

## ⚠️ CÓDIGOS DE ERROR COMUNES

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Sin permisos suficientes |
| 404 | Not Found - Usuario/Rol no encontrado |
| 409 | Conflict - Email/Documento ya registrado |
| 422 | Unprocessable Entity - Error de validación |
| 500 | Internal Server Error - Error del servidor |

---

## 🔒 HEADERS REQUERIDOS

Para endpoints protegidos:
```
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json
```

---

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Tokens JWT**: Tiempo de vida de 1 hora para access tokens, 7 días para refresh tokens
2. **Rate Limiting**: 100 requests por minuto por usuario autenticado
3. **Validaciones**: Email único, documento único por tipo
4. **Auditoría**: Todas las acciones se registran automáticamente
5. **Permisos**: Sistema basado en roles con permisos granulares
6. **Contraseñas**: Mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número