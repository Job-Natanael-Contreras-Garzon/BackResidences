# CASOS DE USO - RESIDENTES (APLICACIÓN MÓVIL)

## PERFIL DE USUARIO: RESIDENTE
- **Plataforma**: Aplicación Móvil (iOS/Android)
- **Enfoque**: Autogestión, consultas personales, servicios básicos
- **Permisos**: Limitados a sus propias viviendas y servicios asociados

---

## MÓDULO 1: AUTENTICACIÓN Y PERFIL

### CU-MOV-001: Iniciar Sesión en App Móvil
- **Actor(es)**: Residente
- **Descripción**: Permite al residente autenticarse en la aplicación móvil del condominio.
- **Flujo Principal**:
  1. El residente abre la aplicación móvil
  2. Ingresa sus credenciales (email/usuario y contraseña)
  3. El sistema valida las credenciales
  4. Se establece la sesión móvil
  5. Se cargan los datos básicos del residente
- **Flujos Alternativos/Excepciones**:
  - Credenciales incorrectas
  - Sin conexión a internet
  - Primera vez (requiere activación)

### CU-MOV-002: Gestionar Perfil Personal
- **Actor(es)**: Residente
- **Descripción**: Permite al residente actualizar su información personal básica.
- **Flujo Principal**:
  1. El residente accede a su perfil
  2. Modifica datos permitidos (teléfono, email, foto)
  3. Valida los cambios
  4. Guarda la información actualizada
  5. Recibe confirmación del cambio
- **Flujos Alternativos/Excepciones**:
  - Email ya registrado por otro usuario
  - Formato de datos inválido
  - Error de conectividad

### CU-MOV-003: Cambiar Contraseña
- **Actor(es)**: Residente
- **Descripción**: Permite cambiar la contraseña de acceso desde la app móvil.
- **Flujo Principal**:
  1. El residente accede a configuración de cuenta
  2. Ingresa contraseña actual
  3. Define nueva contraseña
  4. Confirma la nueva contraseña
  5. El sistema actualiza las credenciales
- **Flujos Alternativos/Excepciones**:
  - Contraseña actual incorrecta
  - Nueva contraseña no cumple políticas
  - Error en validación

---

## MÓDULO 2: GESTIÓN DE VEHÍCULOS

### CU-MOV-004: Registrar Vehículo Personal
- **Actor(es)**: Residente
- **Descripción**: Permite registrar un nuevo vehículo autorizado desde la app móvil.
- **Flujo Principal**:
  1. El residente accede a "Mis Vehículos"
  2. Selecciona "Agregar Nuevo Vehículo"
  3. Ingresa datos del vehículo (placa, marca, modelo, color)
  4. Toma foto del vehículo (opcional)
  5. Envía solicitud de autorización
  6. Recibe notificación de aprobación/rechazo
- **Flujos Alternativos/Excepciones**:
  - Placa ya registrada
  - Límite de vehículos alcanzado
  - Foto no se puede cargar

### CU-MOV-005: Consultar Mis Vehículos Autorizados
- **Actor(es)**: Residente
- **Descripción**: Permite consultar la lista de vehículos autorizados del residente.
- **Flujo Principal**:
  1. El residente accede a "Mis Vehículos"
  2. Ve la lista de vehículos registrados
  3. Consulta estado de cada vehículo (activo/pendiente/vencido)
  4. Puede ver detalles de cada vehículo
- **Flujos Alternativos/Excepciones**:
  - Sin vehículos registrados
  - Error al cargar información

---

## MÓDULO 3: PERSONAS AUTORIZADAS

### CU-MOV-007: Registrar Persona Autorizada
- **Actor(es)**: Residente
- **Descripción**: Permite registrar personas autorizadas para acceder a la vivienda.
- **Flujo Principal**:
  1. El residente accede a "Personas Autorizadas"
  2. Selecciona "Agregar Persona"
  3. Ingresa datos de la persona (nombre, teléfono, relación)
  4. Define tipo de autorización (temporal/permanente)
  5. Establece vigencia si es temporal
  6. Toma foto de la persona (opcional)
  7. Envía registro
- **Flujos Alternativos/Excepciones**:
  - Datos incompletos
  - Límite de personas autorizadas alcanzado
  - Error al tomar foto

### CU-MOV-008: Gestionar Autorizaciones Temporales
- **Actor(es)**: Residente
- **Descripción**: Permite crear autorizaciones rápidas para visitantes.
- **Flujo Principal**:
  1. El residente selecciona "Autorización Rápida"
  2. Ingresa nombre del visitante
  3. Define fecha y hora de la visita
  4. Genera código QR temporal
  5. Comparte código con el visitante
- **Flujos Alternativos/Excepciones**:
  - Horario fuera de las políticas del condominio
  - Error en generación de código QR
  - Sin conexión para generar código

---

## MÓDULO 4: CONSULTAS FINANCIERAS

### CU-MOV-009: Consultar Estado de Cuenta Personal
- **Actor(es)**: Residente
- **Descripción**: Permite consultar el estado financiero de su vivienda.
- **Flujo Principal**:
  1. El residente accede a "Mi Estado de Cuenta"
  2. Ve resumen de deudas pendientes
  3. Consulta historial de pagos realizados
  4. Revisa detalle de cada concepto
  5. Puede descargar comprobantes
- **Flujos Alternativos/Excepciones**:
  - Sin movimientos para mostrar
  - Error al generar comprobantes
  - Problema de conectividad

### CU-MOV-010: Recibir Notificaciones de Pagos
- **Actor(es)**: Residente
- **Descripción**: Recibe notificaciones sobre vencimientos y nuevas deudas.
- **Flujo Principal**:
  1. El sistema genera deuda mensual
  2. Envía push notification al residente
  3. El residente ve la notificación
  4. Puede acceder directamente al detalle
  5. Ve fecha de vencimiento y monto
- **Flujos Alternativos/Excepciones**:
  - Notificaciones deshabilitadas
  - Error en envío de notificación
  - App cerrada o no instalada

### CU-MOV-011: Reportar Pago Realizado
- **Actor(es)**: Residente
- **Descripción**: Permite reportar pagos realizados por otros medios.
- **Flujo Principal**:
  1. El residente accede a la deuda a reportar
  2. Selecciona "Reportar Pago"
  3. Ingresa datos del pago (fecha, monto, referencia)
  4. Adjunta comprobante fotográfico
  5. Envía reporte para validación
- **Flujos Alternativos/Excepciones**:
  - Foto de comprobante no legible
  - Monto no coincide con deuda
  - Error al enviar comprobante

---

## MÓDULO 5: RESERVAS DE ÁREAS COMUNES

### CU-MOV-012: Consultar Áreas Comunes Disponibles
- **Actor(es)**: Residente
- **Descripción**: Permite ver las áreas comunes disponibles para reserva.
- **Flujo Principal**:
  1. El residente accede a "Reservas"
  2. Ve lista de áreas comunes
  3. Consulta disponibilidad por fecha
  4. Revisa tarifas y políticas de cada área
  5. Selecciona área para reservar
- **Flujos Alternativos/Excepciones**:
  - Todas las áreas ocupadas
  - Residente con pagos pendientes
  - Área fuera de servicio

### CU-MOV-013: Realizar Reserva de Área Común
- **Actor(es)**: Residente
- **Descripción**: Permite hacer reserva de un área común específica.
- **Flujo Principal**:
  1. El residente selecciona área y fecha
  2. Elige horario disponible
  3. Especifica tipo de evento
  4. Ingresa número estimado de personas
  5. Confirma términos y condiciones
  6. Realiza el pago si es requerido
  7. Recibe confirmación de reserva
- **Flujos Alternativos/Excepciones**:
  - Horario ya ocupado
  - Excede límite mensual de reservas
  - Error en procesamiento de pago

### CU-MOV-014: Gestionar Mis Reservas
- **Actor(es)**: Residente
- **Descripción**: Permite consultar y gestionar reservas activas.
- **Flujo Principal**:
  1. El residente accede a "Mis Reservas"
  2. Ve reservas próximas y pasadas
  3. Puede cancelar reservas según políticas
  4. Consulta detalles de cada reserva
  5. Recibe recordatorios automáticos
- **Flujos Alternativos/Excepciones**:
  - Reserva muy próxima (no cancelable)
  - Error al cancelar reserva
  - Sin reservas para mostrar

---

## MÓDULO 6: COMUNICACIÓN

### CU-MOV-015: Consultar Avisos del Condominio
- **Actor(es)**: Residente
- **Descripción**: Permite consultar avisos generales publicados por la administración.
- **Flujo Principal**:
  1. El residente accede a "Avisos"
  2. Ve lista de avisos ordenados por fecha
  3. Puede filtrar por tipo o importancia
  4. Selecciona aviso para leer completo
  5. Marca como leído automáticamente
- **Flujos Alternativos/Excepciones**:
  - Sin avisos disponibles
  - Error al cargar contenido
  - Aviso con contenido multimedia no disponible

### CU-MOV-016: Reportar Incidencia o Problema
- **Actor(es)**: Residente
- **Descripción**: Permite reportar problemas o incidencias en el condominio.
- **Flujo Principal**:
  1. El residente accede a "Reportar Problema"
  2. Selecciona categoría del problema
  3. Describe detalladamente la incidencia
  4. Especifica ubicación (puede usar GPS)
  5. Adjunta fotos si es necesario
  6. Define nivel de urgencia
  7. Envía el reporte
  8. Recibe número de seguimiento
- **Flujos Alternativos/Excepciones**:
  - GPS no disponible
  - Error al subir fotos
  - Descripción insuficiente

### CU-MOV-017: Recibir Notificaciones Push
- **Actor(es)**: Residente
- **Descripción**: Recibe notificaciones importantes del condominio.
- **Flujo Principal**:
  1. El sistema genera evento notificable
  2. Envía push notification al dispositivo
  3. El residente recibe la notificación
  4. Puede acceder directamente al contenido
  5. La notificación se marca como vista
- **Flujos Alternativos/Excepciones**:
  - Dispositivo sin conexión
  - Notificaciones deshabilitadas por el usuario
  - Error en servicio de notificaciones

---

## MÓDULO 7: SEGURIDAD Y ACCESOS

### CU-MOV-018: Consultar Eventos de Seguridad Personales
- **Actor(es)**: Residente
- **Descripción**: Permite consultar eventos de seguridad relacionados con su vivienda.
- **Flujo Principal**:
  1. El residente accede a "Mi Seguridad"
  2. Ve eventos relacionados con su vivienda
  3. Consulta accesos de vehículos autorizados
  4. Revisa reportes de visitantes
  5. Puede filtrar por fechas
- **Flujos Alternativos/Excepciones**:
  - Sin eventos para mostrar
  - Error al filtrar información
  - Datos de seguridad no disponibles

### CU-MOV-019: Generar Código QR de Acceso
- **Actor(es)**: Residente
- **Descripción**: Permite generar códigos QR temporales para visitantes.
- **Flujo Principal**:
  1. El residente selecciona "Generar Acceso"
  2. Ingresa datos básicos del visitante
  3. Define vigencia del código
  4. Genera código QR único
  5. Comparte código con visitante
  6. El código se registra en el sistema
- **Flujos Alternativos/Excepciones**:
  - Error en generación de código
  - Sin conexión a internet
  - Código no se puede compartir

---

## MÓDULO 8: CONFIGURACIÓN Y SOPORTE
### CU-MOV-021: Contactar Soporte Técnico
- **Actor(es)**: Residente
- **Descripción**: Permite contactar con soporte para problemas técnicos.
- **Flujo Principal**:
  1. El residente accede a "Ayuda"
  2. Selecciona tipo de problema
  3. Describe el inconveniente
  4. Adjunta capturas de pantalla si es necesario
  5. Envía solicitud de soporte
  6. Recibe número de ticket
- **Flujos Alternativos/Excepciones**:
  - Error al enviar solicitud
  - Capturas de pantalla muy pesadas
  - Sin conexión para enviar

---

## CASOS DE USO TRANSVERSALES MÓVIL

### CU-MOV-022: Sincronizar Datos Offline
- **Actor(es)**: Sistema (Automático)
- **Descripción**: Sincroniza datos cuando se recupera la conexión.
- **Flujo Principal**:
  1. La app detecta pérdida de conexión
  2. Almacena acciones del usuario localmente
  3. Al recuperar conexión, sincroniza automáticamente
  4. Notifica al usuario sobre sincronización
  5. Actualiza interfaz con datos más recientes
- **Flujos Alternativos/Excepciones**:
  - Conflictos en sincronización
  - Datos locales corruptos
  - Error en servidor durante sync

---

## RESUMEN - APLICACIÓN MÓVIL RESIDENTES

**Total de Casos de Uso: 23**

| Módulo | Cantidad | Funcionalidades Principales |
|--------|----------|---------------------------|
| **Autenticación y Perfil** | 3 | Login, perfil, contraseña |
| **Gestión de Vehículos** | 3 | Registro, consulta, renovación |
| **Personas Autorizadas** | 2 | Registro, autorizaciones temporales |
| **Consultas Financieras** | 3 | Estado cuenta, notificaciones, reportes |
| **Reservas Áreas Comunes** | 3 | Consulta, reserva, gestión |
| **Comunicación** | 3 | Avisos, reportes, notificaciones |
| **Seguridad y Accesos** | 2 | Consulta eventos, códigos QR |
| **Configuración y Soporte** | 2 | Configuración, soporte |
| **Transversales** | 2 | Sync offline, actualizaciones |

La aplicación móvil está enfocada en **autogestión del residente** con funcionalidades esenciales para su día a día en el condominio.