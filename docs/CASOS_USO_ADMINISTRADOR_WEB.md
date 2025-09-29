# CASOS DE USO - ADMINISTRADOR (APLICACIÓN WEB)

## PERFIL DE USUARIO: ADMINISTRADOR
- **Plataforma**: Aplicación Web (Dashboard Administrativo)
- **Enfoque**: Gestión completa del condominio, administración, reportes, configuración
- **Permisos**: Acceso total a todas las funcionalidades del sistema

---

## MÓDULO 1: GESTIÓN DE USUARIOS Y ROLES

### CU-WEB-001: Registrar Nuevo Usuario en el Sistema
- **Actor(es)**: Administrador
- **Descripción**: Permite registrar nuevos usuarios (residentes, personal, etc.) en el sistema.
- **Flujo Principal**:
  1. El administrador accede al módulo de usuarios
  2. Selecciona "Nuevo Usuario"
  3. Ingresa datos personales completos
  4. Asigna credenciales de acceso iniciales
  5. Define tipo de usuario y roles
  6. Establece estado (activo/inactivo)
  7. Envía notificación de bienvenida
  8. Registra la acción en bitácora
- **Flujos Alternativos/Excepciones**:
  - Email ya registrado en el sistema
  - Datos obligatorios faltantes
  - Error en envío de notificación de bienvenida
  - Conflicto en asignación de roles

### CU-WEB-002: Gestionar Roles y Permisos
- **Actor(es)**: Administrador
- **Descripción**: Permite crear, modificar y asignar roles con permisos específicos.
- **Flujo Principal**:
  1. El administrador accede a "Gestión de Roles"
  2. Puede crear nuevo rol o modificar existente
  3. Define permisos específicos por módulo
  4. Establece restricciones de acceso
  5. Asigna roles a usuarios específicos
  6. Guarda configuración de permisos
  7. Notifica cambios a usuarios afectados
- **Flujos Alternativos/Excepciones**:
  - Rol con nombre duplicado
  - Permisos conflictivos
  - Usuario conectado con rol modificado
  - Error en aplicación de permisos

### CU-WEB-003: Gestionar Viviendas y Propietarios
- **Actor(es)**: Administrador
- **Descripción**: Permite administrar el registro completo de viviendas y sus propietarios.
- **Flujo Principal**:
  1. El administrador accede a "Gestión de Viviendas"
  2. Puede registrar nueva vivienda con todos sus datos
  3. Asigna propietario principal y residentes
  4. Define características específicas (área, tipo, cuotas)
  5. Establece estado de la vivienda
  6. Configura servicios asociados
  7. Actualiza información cuando hay cambios
- **Flujos Alternativos/Excepciones**:
  - Número de vivienda duplicado
  - Propietario ya asignado a otra vivienda
  - Datos de área o características inválidos
  - Error en cálculo de cuotas

### CU-WEB-004: Auditar Actividad de Usuarios
- **Actor(es)**: Administrador
- **Descripción**: Permite revisar y auditar la actividad de todos los usuarios del sistema.
- **Flujo Principal**:
  1. El administrador accede a "Auditoría de Usuarios"
  2. Selecciona criterios de búsqueda (usuario, fecha, acción)
  3. Filtra por tipo de actividad
  4. Genera reporte detallado de actividades
  5. Analiza patrones de uso sospechosos
  6. Puede tomar acciones correctivas
  7. Exporta reportes de auditoría
- **Flujos Alternativos/Excepciones**:
  - Demasiados registros para mostrar
  - Error en generación de reportes
  - Datos de auditoría corruptos

---

## MÓDULO 2: GESTIÓN FINANCIERA INTEGRAL

### CU-WEB-005: Configurar Estructura de Cuotas
- **Actor(es)**: Administrador
- **Descripción**: Permite configurar la estructura de cuotas de administración del condominio.
- **Flujo Principal**:
  1. El administrador accede a "Configuración Financiera"
  2. Define tipos de cuotas (administración, extraordinarias, etc.)
  3. Establece fórmulas de cálculo por tipo de vivienda
  4. Configura fechas de facturación y vencimiento
  5. Define intereses por mora
  6. Establece descuentos por pronto pago
  7. Activa la configuración
- **Flujos Alternativos/Excepciones**:
  - Fórmulas de cálculo incorrectas
  - Fechas de vencimiento inválidas
  - Configuración que genera montos negativos

### CU-WEB-006: Generar Facturación Masiva
- **Actor(es)**: Administrador
- **Descripción**: Permite generar la facturación mensual para todas las viviendas del condominio.
- **Flujo Principal**:
  1. El administrador inicia proceso de facturación
  2. Selecciona período a facturar
  3. El sistema calcula cuotas por vivienda
  4. Genera deudas automáticamente
  5. Aplica descuentos y recargos correspondientes
  6. Crea notificaciones para residentes
  7. Genera reporte de facturación
  8. Envía notificaciones masivas
- **Flujos Alternativos/Excepciones**:
  - Período ya facturado
  - Viviendas sin propietario asignado
  - Error en cálculos masivos
  - Fallo en envío de notificaciones

### CU-WEB-007: Gestionar Pagos y Conciliación
- **Actor(es)**: Administrador
- **Descripción**: Permite registrar, validar y conciliar pagos realizados por los residentes.
- **Flujo Principal**:
  1. El administrador accede a "Gestión de Pagos"
  2. Ve pagos pendientes de validación
  3. Verifica comprobantes subidos por residentes
  4. Concilia pagos con deudas existentes
  5. Aplica pagos a deudas específicas
  6. Genera recibos oficiales
  7. Actualiza estados financieros
  8. Notifica confirmación a residentes
- **Flujos Alternativos/Excepciones**:
  - Comprobante ilegible o inválido
  - Monto no coincide con deuda
  - Pago duplicado
  - Error en aplicación de pago

### CU-WEB-008: Generar Reportes Financieros
- **Actor(es)**: Administrador
- **Descripción**: Permite generar reportes financieros completos del condominio.
- **Flujo Principal**:
  1. El administrador selecciona tipo de reporte
  2. Define período y parámetros específicos
  3. Configura nivel de detalle requerido
  4. Genera reporte consolidado
  5. Analiza indicadores financieros
  6. Puede exportar en múltiples formatos
  7. Programa reportes automáticos
- **Flujos Alternativos/Excepciones**:
  - Sin datos para el período especificado
  - Error en cálculos consolidados
  - Parámetros de reporte inválidos

### CU-WEB-009: Gestionar Cartera y Cobranza
- **Actor(es)**: Administrador
- **Descripción**: Permite gestionar la cartera vencida y procesos de cobranza.
- **Flujo Principal**:
  1. El administrador accede a "Cartera Vencida"
  2. Analiza deudas por antigüedad
  3. Segmenta cartera por rangos de vencimiento
  4. Genera estrategias de cobranza
  5. Envía notificaciones de cobranza automatizadas
  6. Registra gestiones de cobro realizadas
  7. Programa cortes de servicios si aplica
- **Flujos Alternativos/Excepciones**:
  - Error en cálculo de intereses
  - Conflictos legales con deudores
  - Servicios críticos no cortables

---

## MÓDULO 3: SEGURIDAD Y CONTROL DE ACCESO

### CU-WEB-010: Administrar Sistema de Seguridad
- **Actor(es)**: Administrador
- **Descripción**: Permite gestionar todo el sistema de seguridad del condominio.
- **Flujo Principal**:
  1. El administrador accede a "Centro de Seguridad"
  2. Monitorea eventos de seguridad en tiempo real
  3. Gestiona cámaras y sensores del sistema
  4. Configura alertas automáticas
  5. Revisa reportes de guardias de seguridad
  6. Gestiona accesos de emergencia
  7. Coordina con autoridades si es necesario
- **Flujos Alternativos/Excepciones**:
  - Falla en sistema de cámaras
  - Evento de seguridad crítico
  - Comunicación perdida con guardia

### CU-WEB-011: Gestionar Vehículos Autorizados
- **Actor(es)**: Administrador
- **Descripción**: Permite administrar completamente el registro de vehículos autorizados.
- **Flujo Principal**:
  1. El administrador accede a "Vehículos Autorizados"
  2. Revisa solicitudes pendientes de aprobación
  3. Valida documentación de vehículos
  4. Aprueba o rechaza solicitudes
  5. Gestiona renovaciones automáticas
  6. Mantiene base de datos actualizada
  7. Genera reportes de vehículos por vivienda
- **Flujos Alternativos/Excepciones**:
  - Documentación de vehículo inválida
  - Límite de vehículos por vivienda excedido
  - Vehículo reportado como robado

### CU-WEB-012: Configurar Controles de Acceso
- **Actor(es)**: Administrador
- **Descripción**: Permite configurar políticas y controles de acceso al condominio.
- **Flujo Principal**:
  1. El administrador define horarios de acceso
  2. Configura restricciones por tipo de usuario
  3. Establece políticas para visitantes
  4. Define procedimientos de emergencia
  5. Configura sistemas biométricos si aplica
  6. Programa backup de sistemas de acceso
  7. Capacita personal de seguridad
- **Flujos Alternativos/Excepciones**:
  - Conflicto en políticas de acceso
  - Falla en sistemas biométricos
  - Personal no capacitado adecuadamente

---

## MÓDULO 4: COMUNICACIÓN Y AVISOS

### CU-WEB-013: Gestionar Comunicación Masiva
- **Actor(es)**: Administrador
- **Descripción**: Permite crear y gestionar toda la comunicación hacia los residentes.
- **Flujo Principal**:
  1. El administrador accede a "Centro de Comunicaciones"
  2. Crea nuevo aviso o comunicado
  3. Define audiencia objetivo (todos/específicos)
  4. Configura canales de distribución (app, email, SMS)
  5. Programa fecha y hora de envío
  6. Adjunta documentos o multimedia si necesario
  7. Envía comunicación y monitorea recepción
- **Flujos Alternativos/Excepciones**:
  - Error en envío masivo de notificaciones
  - Contenido multimedia muy pesado
  - Algunos usuarios sin medios de contacto

### CU-WEB-014: Administrar Reportes de Residentes
- **Actor(es)**: Administrador
- **Descripción**: Permite gestionar todos los reportes enviados por los residentes.
- **Flujo Principal**:
  1. El administrador recibe reporte de residente
  2. Categoriza y prioriza la incidencia
  3. Asigna responsable para atención
  4. Programa fecha estimada de resolución
  5. Monitorea progreso de la solución
  6. Notifica resolución al residente
  7. Registra satisfacción del servicio
- **Flujos Alternativos/Excepciones**:
  - Reporte duplicado o sin fundamento
  - Requiere contratación de servicios externos
  - Problema de competencia legal externa

### CU-WEB-015: Gestionar Encuestas y Votaciones
- **Actor(es)**: Administrador
- **Descripción**: Permite crear encuestas y votaciones para los residentes.
- **Flujo Principal**:
  1. El administrador crea nueva encuesta/votación
  2. Define preguntas y opciones de respuesta
  3. Establece criterios de participación
  4. Configura período de votación
  5. Publica encuesta a residentes elegibles
  6. Monitorea participación en tiempo real
  7. Genera resultados y estadísticas
  8. Publica resultados oficiales
- **Flujos Alternativos/Excepciones**:
  - Baja participación en votación
  - Empate en resultados críticos
  - Cuestionamiento legal de resultados

---

## MÓDULO 5: GESTIÓN DE ÁREAS COMUNES

### CU-WEB-016: Administrar Áreas Comunes
- **Actor(es)**: Administrador
- **Descripción**: Permite gestionar completamente las áreas comunes del condominio.
- **Flujo Principal**:
  1. El administrador configura nuevas áreas comunes
  2. Define capacidad, horarios y restricciones
  3. Establece tarifas y políticas de uso
  4. Configura equipamiento disponible
  5. Programa mantenimiento preventivo
  6. Gestiona calendarios de disponibilidad
  7. Monitorea uso y generar estadísticas
- **Flujos Alternativos/Excepciones**:
  - Área en mantenimiento (no disponible)
  - Conflicto en reservas simultáneas
  - Daños en equipamiento

### CU-WEB-017: Gestionar Reservas y Eventos
- **Actor(es)**: Administrador
- **Descripción**: Permite administrar todas las reservas y eventos en áreas comunes.
- **Flujo Principal**:
  1. El administrador ve dashboard de reservas
  2. Puede aprobar/rechazar reservas pendientes
  3. Gestiona conflictos de horarios
  4. Coordina servicios adicionales para eventos
  5. Monitorea cumplimiento de políticas
  6. Gestiona depósitos y pagos por daños
  7. Evalúa satisfacción post-evento
- **Flujos Alternativos/Excepciones**:
  - Evento excede capacidad permitida
  - Incumplimiento de políticas durante evento
  - Daños ocasionados durante uso

### CU-WEB-018: Generar Reportes de Uso
- **Actor(es)**: Administrador
- **Descripción**: Permite generar reportes detallados sobre el uso de áreas comunes.
- **Flujo Principal**:
  1. El administrador selecciona período de análisis
  2. Define métricas a analizar (ocupación, ingresos, etc.)
  3. Genera reportes por área o consolidados
  4. Analiza tendencias de uso
  5. Identifica áreas más/menos utilizadas
  6. Calcula ROI de inversiones en áreas
  7. Propone mejoras basadas en datos
- **Flujos Alternativos/Excepciones**:
  - Datos insuficientes para análisis
  - Error en cálculos de métricas
  - Períodos sin actividad registrada

---

## MÓDULO 6: MANTENIMIENTO INTEGRAL

### CU-WEB-019: Planificar Mantenimiento Preventivo
- **Actor(es)**: Administrador
- **Descripción**: Permite planificar y gestionar todo el mantenimiento preventivo del condominio.
- **Flujo Principal**:
  1. El administrador crea plan maestro de mantenimiento
  2. Define cronograma por equipos/áreas
  3. Asigna responsables y presupuestos
  4. Programa notificaciones automáticas
  5. Gestiona inventario de repuestos
  6. Monitorea cumplimiento del plan
  7. Evalúa efectividad de mantenimientos
- **Flujos Alternativos/Excepciones**:
  - Presupuesto insuficiente para plan completo
  - Proveedores no disponibles en fechas programadas
  - Equipos requieren mantenimiento especializado

### CU-WEB-020: Gestionar Órdenes de Trabajo
- **Actor(es)**: Administrador
- **Descripción**: Permite gestionar todas las órdenes de trabajo de mantenimiento.
- **Flujo Principal**:
  1. El administrador recibe solicitud de mantenimiento
  2. Evalúa prioridad y complejidad
  3. Asigna personal técnico apropiado
  4. Autoriza presupuesto necesario
  5. Monitorea progreso de trabajos
  6. Valida calidad de trabajos terminados
  7. Cierra orden y registra costos finales
- **Flujos Alternativos/Excepciones**:
  - Trabajo requiere especialista externo
  - Costos exceden presupuesto autorizado
  - Trabajo genera nuevos problemas

### CU-WEB-021: Administrar Proveedores y Contratos
- **Actor(es)**: Administrador
- **Descripción**: Permite gestionar la base de proveedores y contratos de servicios.
- **Flujo Principal**:
  1. El administrador mantiene directorio de proveedores
  2. Evalúa desempeño y calificaciones
  3. Negocia contratos y tarifas
  4. Gestiona renovaciones de contratos
  5. Monitorea cumplimiento de SLAs
  6. Gestiona pagos a proveedores
  7. Evalúa nuevos proveedores
- **Flujos Alternativos/Excepciones**:
  - Proveedor incumple contrato
  - Costos exceden presupuesto aprobado
  - Calidad de servicio insatisfactoria

---

## MÓDULO 7: REPORTES Y BUSINESS INTELLIGENCE

### CU-WEB-022: Dashboard Ejecutivo
- **Actor(es)**: Administrador
- **Descripción**: Proporciona vista ejecutiva con KPIs principales del condominio.
- **Flujo Principal**:
  1. El administrador accede al dashboard principal
  2. Ve métricas financieras en tiempo real
  3. Monitorea indicadores operacionales
  4. Revisa alertas y notificaciones críticas
  5. Analiza tendencias y proyecciones
  6. Puede profundizar en métricas específicas
  7. Programa reportes automáticos
- **Flujos Alternativos/Excepciones**:
  - Datos no actualizados por problemas técnicos
  - Métricas fuera de rangos normales
  - Error en cálculos de indicadores

### CU-WEB-023: Generar Reportes Personalizados
- **Actor(es)**: Administrador
- **Descripción**: Permite crear reportes personalizados según necesidades específicas.
- **Flujo Principal**:
  1. El administrador accede al generador de reportes
  2. Selecciona fuentes de datos necesarias
  3. Define filtros y parámetros específicos
  4. Configura formato y diseño del reporte
  5. Programa generación automática si necesario
  6. Genera y valida el reporte
  7. Distribuye a stakeholders correspondientes
- **Flujos Alternativos/Excepciones**:
  - Consulta muy compleja (timeout)
  - Datos inconsistentes entre fuentes
  - Error en formato de exportación

### CU-WEB-024: Análisis Predictivo y Tendencias
- **Actor(es)**: Administrador
- **Descripción**: Permite realizar análisis predictivo basado en datos históricos.
- **Flujo Principal**:
  1. El administrador selecciona área de análisis
  2. Define variables y período histórico
  3. Ejecuta algoritmos de predicción
  4. Analiza tendencias proyectadas
  5. Identifica patrones y anomalías
  6. Genera recomendaciones estratégicas
  7. Simula escenarios futuros
- **Flujos Alternativos/Excepciones**:
  - Datos históricos insuficientes
  - Variaciones externas afectan predicciones
  - Modelos predictivos requieren calibración

---

## MÓDULO 8: CONFIGURACIÓN Y ADMINISTRACIÓN DEL SISTEMA

### CU-WEB-025: Configurar Parámetros del Sistema
- **Actor(es)**: Administrador
- **Descripción**: Permite configurar todos los parámetros operativos del sistema.
- **Flujo Principal**:
  1. El administrador accede a configuración general
  2. Define parámetros financieros (intereses, descuentos)
  3. Configura políticas de acceso y seguridad
  4. Establece límites operacionales
  5. Configura integraciones con sistemas externos
  6. Define políticas de respaldo y archivos
  7. Valida y aplica configuraciones
- **Flujos Alternativos/Excepciones**:
  - Configuración genera conflictos operativos
  - Parámetros fuera de rangos válidos
  - Error en aplicación de cambios

### CU-WEB-026: Administrar Copias de Seguridad
- **Actor(es)**: Administrador
- **Descripción**: Permite gestionar el sistema de respaldos y recuperación de datos.
- **Flujo Principal**:
  1. El administrador configura políticas de backup
  2. Programa respaldos automáticos
  3. Monitorea ejecución de respaldos
  4. Valida integridad de backups
  5. Gestiona retención de respaldos históricos
  6. Puede ejecutar restauraciones si necesario
  7. Documenta procedimientos de recuperación
- **Flujos Alternativos/Excepciones**:
  - Falla en backup programado
  - Espacio insuficiente para respaldos
  - Corrupción en archivo de backup

### CU-WEB-027: Gestionar Integraciones Externas
- **Actor(es)**: Administrador
- **Descripción**: Permite gestionar integraciones con sistemas bancarios, gubernamentales, etc.
- **Flujo Principal**:
  1. El administrador configura APIs externas
  2. Establece credenciales y permisos
  3. Configura sincronización de datos
  4. Monitorea estado de integraciones
  5. Gestiona errores de comunicación
  6. Valida consistencia de datos
  7. Mantiene logs de transacciones
- **Flujos Alternativos/Excepciones**:
  - API externa no disponible
  - Cambios en formato de datos externos
  - Error en autenticación con sistemas externos

---

## CASOS DE USO TRANSVERSALES WEB

### CU-WEB-028: Gestionar Sesiones Administrativas
- **Actor(es)**: Sistema (Automático)
- **Descripción**: Gestiona sesiones y seguridad para usuarios administrativos.
- **Flujo Principal**:
  1. Valida credenciales de administrador
  2. Establece sesión con privilegios elevados
  3. Monitorea actividad administrativa
  4. Aplica políticas de timeout extendido
  5. Registra todas las acciones administrativas
  6. Permite sesiones concurrentes controladas
  7. Cierra sesión por seguridad
- **Flujos Alternativos/Excepciones**:
  - Múltiples intentos de acceso fallidos
  - Actividad sospechosa detectada
  - Sesión comprometida

### CU-WEB-029: Auditoría Completa del Sistema
- **Actor(es)**: Administrador
- **Descripción**: Permite realizar auditorías completas de todo el sistema.
- **Flujo Principal**:
  1. El administrador inicia auditoría del sistema
  2. Define alcance y criterios de auditoría
  3. Ejecuta verificaciones automáticas
  4. Genera reportes de cumplimiento
  5. Identifica vulnerabilidades o inconsistencias
  6. Propone acciones correctivas
  7. Documenta hallazgos de auditoría
- **Flujos Alternativos/Excepciones**:
  - Auditoría encuentra problemas críticos
  - Proceso de auditoría interrumpido
  - Datos de auditoría inconsistentes

---

## RESUMEN - APLICACIÓN WEB ADMINISTRADOR

**Total de Casos de Uso: 30**

| Módulo | Cantidad | Funcionalidades Principales |
|--------|----------|---------------------------|
| **Gestión de Usuarios y Roles** | 4 | Usuarios, roles, viviendas, auditoría |
| **Gestión Financiera Integral** | 5 | Cuotas, facturación, pagos, reportes, cartera |
| **Seguridad y Control de Acceso** | 3 | Sistema seguridad, vehículos, controles |
| **Comunicación y Avisos** | 3 | Comunicación masiva, reportes, votaciones |
| **Gestión de Áreas Comunes** | 3 | Administración áreas, reservas, reportes uso |
| **Mantenimiento Integral** | 3 | Preventivo, órdenes trabajo, proveedores |
| **Reportes y Business Intelligence** | 3 | Dashboard, reportes personalizados, análisis predictivo |
| **Configuración y Administración** | 3 | Parámetros, backups, integraciones |
| **Transversales** | 3 | Sesiones, auditoría, actualizaciones |

La aplicación web está enfocada en **gestión administrativa completa** con herramientas avanzadas para la administración integral del condominio, reportes ejecutivos y toma de decisiones estratégicas.