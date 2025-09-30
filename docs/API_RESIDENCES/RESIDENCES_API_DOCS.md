# 🏠 Módulo de Residencias - BackResidences API

## 📋 Descripción
El módulo de residencias proporciona una API completa para la gestión de viviendas, residentes, personas autorizadas y mascotas en el condominio.

## 🔗 Endpoints Disponibles

### 🏠 Gestión de Viviendas
```
GET    /api/v1/residences/viviendas/                      # Listar viviendas
POST   /api/v1/residences/viviendas/crear/                # Crear nueva vivienda
GET    /api/v1/residences/viviendas/{id}/                 # Detalles de vivienda
PUT    /api/v1/residences/viviendas/{id}/actualizar/      # Actualizar vivienda
PATCH  /api/v1/residences/viviendas/{id}/asignar-residente/  # Asignar propietario/inquilino
GET    /api/v1/residences/viviendas/disponibles/          # Listar viviendas disponibles
```

### 👥 Personas Autorizadas
```
GET    /api/v1/residences/personas-autorizadas/           # Listar personas autorizadas
POST   /api/v1/residences/personas-autorizadas/crear/     # Registrar persona autorizada
PATCH  /api/v1/residences/personas-autorizadas/{id}/renovar/  # Renovar autorización
PATCH  /api/v1/residences/personas-autorizadas/{id}/revocar/  # Revocar autorización
```

### 🐕 Gestión de Mascotas
```
GET    /api/v1/residences/mascotas/                       # Listar mascotas
POST   /api/v1/residences/mascotas/registrar/             # Registrar nueva mascota
PUT    /api/v1/residences/mascotas/{id}/actualizar/       # Actualizar información de mascota
```

### 📊 Dashboard y Reportes
```
GET    /api/v1/residences/dashboard/                      # Estadísticas del condominio
```

### 🔍 Búsqueda
```
GET    /api/v1/residences/buscar/residentes/              # Buscar residentes
```

## 🔐 Autenticación
Todos los endpoints requieren autenticación JWT. Incluir en el header:
```
Authorization: Bearer <token>
```

## 📊 Filtros y Búsqueda

### Viviendas
- **Filtros**: `tipo`, `bloque`, `piso`, `activo`, `tiene_propietario`, `tiene_inquilino`
- **Búsqueda**: `search` (por identificador o bloque)
- **Ordenamiento**: `identificador`, `fecha_registro`, `cuota_administracion`

### Mascotas
- **Filtros**: `vivienda`, `especie`, `activo`, `vacunas_al_dia`
- **Búsqueda**: `search` (por nombre o raza)
- **Ordenamiento**: `nombre`, `fecha_registro`, `especie`

### Personas Autorizadas
- **Filtros**: `vivienda`, `parentesco`, `activo`, `vigente`
- **Búsqueda**: `search` (por nombre, apellido o cédula)
- **Ordenamiento**: `nombre`, `apellido`, `fecha_inicio`

## 🎯 Ejemplos de Uso

### 1. Listar Viviendas Disponibles
```bash
GET /api/v1/residences/viviendas/?tiene_propietario=false
```

### 2. Buscar Propietarios
```bash
GET /api/v1/residences/buscar/residentes/?q=juan&tipo=propietario
```

### 3. Obtener Dashboard
```bash
GET /api/v1/residences/dashboard/
```

### 4. Filtrar Mascotas por Especie
```bash
GET /api/v1/residences/mascotas/?especie=perro&vacunas_al_dia=true
```

### 5. Asignar Propietario a Vivienda
```bash
PATCH /api/v1/residences/viviendas/1/asignar-residente/
{
    "tipo_residente": "propietario",
    "usuario": 5
}
```

## 📋 Permisos Requeridos

### Por Funcionalidad:
- **Listar/Ver**: Usuario autenticado
- **Crear Viviendas**: Solo administradores
- **Actualizar Viviendas**: Administradores o propietarios
- **Asignar Residentes**: Solo administradores
- **Dashboard**: Solo administradores
- **Gestión de Mascotas**: Propietarios, inquilinos o administradores
- **Personas Autorizadas**: Propietarios, inquilinos o administradores

## 🎨 Documentación Swagger
La documentación completa con ejemplos está disponible en:
```
http://127.0.0.1:8000/docs/
```

## 📈 Dashboard - Estadísticas Incluidas

### Viviendas
- Total de viviendas
- Viviendas ocupadas vs disponibles
- Viviendas con inquilinos
- Distribución por tipo (apartamento, penthouse, etc.)
- Ocupación por bloque

### Residentes
- Total de propietarios
- Total de inquilinos
- Personas autorizadas activas
- Credenciales vigentes

### Mascotas
- Total de mascotas registradas
- Distribución por especie (perros, gatos, otras)
- Estado de vacunas
- Mascotas por vivienda

## 🚀 Características Técnicas
- ✅ Autenticación JWT integrada
- ✅ Filtros avanzados con django-filter
- ✅ Búsqueda de texto completo
- ✅ Paginación automática
- ✅ Validaciones de negocio
- ✅ Documentación Swagger completa
- ✅ Manejo de errores robusto
- ✅ Optimización de consultas con select_related
- ✅ Permisos granulares por endpoint