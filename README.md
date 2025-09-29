# BackResidences

## Sistema de Gestión Integral para Condominios

### Documentación de Casos de Uso

Este proyecto contiene la documentación completa de casos de uso para el desarrollo del backend del Sistema de Gestión Integral para Condominios, separados por tipo de usuario y plataforma:

#### 📱 **RESIDENTES (Aplicación Móvil)**
- **Archivo**: `CASOS_USO_RESIDENTES_MOVIL.md`
- **Total de CU**: 23 casos de uso
- **Enfoque**: Autogestión del residente, servicios esenciales del día a día
- **Módulos principales**:
  - Autenticación y Perfil
  - Gestión de Vehículos
  - Personas Autorizadas
  - Consultas Financieras
  - Reservas de Áreas Comunes
  - Comunicación
  - Seguridad y Accesos
  - Configuración y Soporte

#### 🖥️ **ADMINISTRADOR (Aplicación Web)**
- **Archivo**: `CASOS_USO_ADMINISTRADOR_WEB.md`
- **Total de CU**: 30 casos de uso
- **Enfoque**: Gestión administrativa completa, reportes ejecutivos, configuración
- **Módulos principales**:
  - Gestión de Usuarios y Roles
  - Gestión Financiera Integral
  - Seguridad y Control de Acceso
  - Comunicación y Avisos
  - Gestión de Áreas Comunes
  - Mantenimiento Integral
  - Reportes y Business Intelligence
  - Configuración y Administración del Sistema

#### 📋 **DOCUMENTACIÓN ORIGINAL**
- **Archivo**: `CASOS_DE_USO.md`
- **Contenido**: Lista completa original de 36 casos de uso sin separación por plataforma

### Estructura del Análisis

El análisis se basó en el esquema de base de datos proporcionado, identificando:
- **Entidades principales** y sus relaciones
- **Procesos de negocio complejos** (no solo CRUD)
- **Diferentes roles de usuario** y sus permisos
- **Flujos alternativos y excepciones** realistas
- **Funcionalidades transversales** necesarias

### Próximos Pasos

Esta documentación servirá como base para:
1. **Diseño de APIs REST** para el backend
2. **Desarrollo de la aplicación móvil** para residentes
3. **Desarrollo del dashboard web** para administradores
4. **Implementación de la base de datos** según el esquema analizado
5. **Definición de arquitectura de microservicios** si es necesario