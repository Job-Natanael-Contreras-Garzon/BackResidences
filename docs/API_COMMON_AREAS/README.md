# Módulo de Áreas Comunes - BackResidences

## Descripción

El módulo de áreas comunes proporciona un sistema completo para la gestión de espacios compartidos en condominios residenciales, incluyendo reservas, disponibilidad, horarios y estadísticas.

## Características principales

### 🏊 Gestión de Áreas Comunes
- **Registro completo de áreas**: Salón social, piscina, gimnasio, BBQ, etc.
- **Configuración flexible**: Capacidad, precios, horarios, equipamiento
- **Gestión de tipos de reserva**: Por horas, por días, eventos especiales
- **Control de disponibilidad**: Sistema en tiempo real

### 📅 Sistema de Reservas
- **Reservas inteligentes**: Validación automática de conflictos
- **Cálculo automático de precios**: Basado en duración y tipo de área
- **Estados de reserva**: Pendiente, confirmada, cancelada, completada
- **Gestión de cancelaciones**: Con políticas de tiempo mínimo
- **Control de pagos**: Montos, depósitos de garantía

### ⏰ Gestión de Horarios
- **Horarios personalizados**: Por día de la semana
- **Flexibilidad total**: Diferentes horarios para cada área
- **Validación automática**: Reservas solo en horarios permitidos

### 📊 Dashboard y Estadísticas
- **Dashboard completo**: Resumen de áreas, reservas activas, próximas
- **Estadísticas detalladas**: Uso por períodos, áreas populares, ingresos
- **Reportes personalizados**: Por mes, trimestre, año

## Estructura del módulo

```
apps/common_areas/
├── models.py          # Modelos: AreaComun, HorarioArea, Reserva
├── serializers.py     # 15+ serializadores especializados
├── views.py           # Vistas con lógica de negocio completa
├── urls.py            # 13 endpoints organizados
├── apps.py            # Configuración de la aplicación
└── migrations/        # Migraciones de base de datos
```

## API Endpoints

### 🏊 Áreas Comunes
- `GET /api/v1/common-areas/areas/` - Listar áreas comunes
- `GET /api/v1/common-areas/areas/{id}/` - Detalles de área
- `POST /api/v1/common-areas/areas/crear/` - Crear área (admin)
- `PUT /api/v1/common-areas/areas/{id}/actualizar/` - Actualizar área (admin)
- `GET /api/v1/common-areas/areas/{id}/disponibilidad/` - Consultar disponibilidad

### 📅 Reservas
- `GET /api/v1/common-areas/reservas/` - Listar reservas
- `POST /api/v1/common-areas/reservas/crear/` - Crear reserva
- `GET /api/v1/common-areas/reservas/{id}/` - Detalles de reserva
- `POST /api/v1/common-areas/reservas/{id}/cancelar/` - Cancelar reserva

### ⏰ Horarios
- `GET /api/v1/common-areas/areas/{id}/horarios/` - Horarios de área
- `POST /api/v1/common-areas/areas/{id}/horarios/` - Crear horario (admin)

### 📊 Dashboard
- `GET /api/v1/common-areas/dashboard/` - Dashboard principal
- `GET /api/v1/common-areas/configuracion/` - Configuración del sistema
- `GET /api/v1/common-areas/estadisticas/` - Estadísticas de uso

## Modelos principales

### AreaComun
```python
- nombre: CharField(100)
- descripcion: TextField
- capacidad: IntegerField
- precio_hora: DecimalField
- precio_dia: DecimalField (opcional)
- tipo_reserva: CharField (por_horas, por_dias, eventos)
- deposito_garantia: DecimalField
- servicios_incluidos: JSONField
- normas_uso: TextField
```

### Reserva
```python
- usuario: ForeignKey(User)
- area_comun: ForeignKey(AreaComun)
- fecha_inicio/fin: DateField
- hora_inicio/fin: TimeField
- monto_total: DecimalField
- estado: CharField (pendiente, confirmada, cancelada, completada)
- motivo_evento: CharField
- numero_personas: IntegerField
```

### HorarioArea
```python
- area_comun: ForeignKey(AreaComun)
- dia_semana: IntegerField (1-7)
- hora_inicio/fin: TimeField
- activo: BooleanField
```

## Lógica de negocio implementada

### ✅ Validaciones automáticas
- **Conflictos de horario**: No permite reservas superpuestas
- **Capacidad**: Validación del número de personas
- **Horarios permitidos**: Solo en horarios configurados
- **Fechas válidas**: No permite reservas en el pasado
- **Duración máxima**: Control de tiempo máximo de reserva

### 💰 Cálculo de precios
- **Automático por duración**: Horas o días según configuración
- **Aplicación de depósitos**: Cuando corresponda
- **Descuentos por tipo**: Según políticas del condominio

### 🔐 Control de permisos
- **Usuarios**: Solo sus propias reservas
- **Administradores**: Acceso completo
- **Validación JWT**: En todos los endpoints

## Tecnologías utilizadas

- **Django 4.2.7**: Framework web principal
- **Django REST Framework**: API REST
- **django-filters**: Filtrado avanzado
- **drf-yasg**: Documentación automática
- **PostgreSQL**: Base de datos optimizada

## Documentación API

La documentación completa de la API está disponible en:
- **Swagger UI**: `/docs/`
- **ReDoc**: `/redoc/`

## Instalación y configuración

1. **Asegurar que la app esté en settings.py**:
```python
LOCAL_APPS = [
    # ... otras apps
    'apps.common_areas',
]
```

2. **URLs configuradas en el proyecto principal**:
```python
path('api/v1/common-areas/', include(('apps.common_areas.urls', 'common_areas'), namespace='api_common_areas')),
```

3. **Aplicar migraciones**:
```bash
python manage.py makemigrations common_areas
python manage.py migrate
```

## Casos de uso principales

### 👤 Residente típico
1. **Consultar áreas disponibles** para una fecha específica
2. **Hacer reserva** de salón social para evento familiar
3. **Ver sus reservas** activas y próximas
4. **Cancelar reserva** con 48 horas de anticipación

### 👨‍💼 Administrador
1. **Gestionar áreas comunes** (crear, actualizar, configurar)
2. **Configurar horarios** de funcionamiento
3. **Ver dashboard** con estadísticas completas
4. **Generar reportes** de uso e ingresos

## Ventajas de la implementación

### 🔧 Sofisticada pero sencilla
- **Código limpio y mantenible**: Siguiendo mejores prácticas Django
- **Lógica de negocio centralizada**: En serializadores y vistas
- **Validaciones robustas**: Pero sin complicaciones innecesarias
- **API intuitiva**: Endpoints organizados y bien documentados

### 📈 Escalable y eficiente
- **Consultas optimizadas**: Con select_related y prefetch_related
- **Filtrado eficiente**: Con django-filters
- **Paginación automática**: Para listas grandes
- **Cache-friendly**: Diseño que permite implementar cache fácilmente

### 🔒 Segura y confiable
- **Autenticación JWT**: En todos los endpoints
- **Validación completa**: De datos y permisos
- **Manejo de errores**: Respuestas consistentes y útiles
- **Logging implícito**: Para auditoría y debugging

## Siguiente paso

El módulo está **completamente implementado y listo para uso**. Se integra perfectamente con el sistema de autenticación existente y sigue los mismos patrones establecidos en el módulo de residencias.

Para comenzar a usarlo, simplemente iniciar el servidor Django y acceder a la documentación en `/docs/` para explorar todos los endpoints disponibles.