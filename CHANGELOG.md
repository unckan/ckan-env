# Release 0.6.0
2025-09-17

## Superset

 - Add trabslations (ES) [#53](https://github.com/unckan/ckanext-superset/pull/53)
 - Allow automatic sync resources [#52](https://github.com/unckan/ckanext-superset/pull/52)
 - Add filters to the charts list [#50](https://github.com/unckan/ckanext-superset/pull/50)
 - Remove SelfInfo extension [#83](https://github.com/unckan/ckan-env/pull/83)

# Release 0.5.2
2025-09-17

## CKAN

Actualizamos CKAN a la ultima version 2.11.3 desde 2.11.1
Hay cambios en la gestion interna de sesiones de usuarios (por eso algunos cambios en la config)
Se activo el plugin `activity`: comenzamos a registrar las acciones de los usuarios del portal

## Extension interna

Actualización en la extension interna
 - Se quito la imagen en la seccion promoted que no esta en uso
 - Se cambio la version debian de debian:stable-slim a debian:12-slim

## Extensiones

### Citeproc (nueva)

Ahora podemos citar en documentos académicos datasets y recursos segun todas las normas de citacion existentes.

### Selfinfo (Nueva)

Monitoreo del estado del servidor a nivel de RAM, CPU, disco y errores internos

### Superset
 - De 0.1.9 a 0.2.1: Bug reparado para la actualizacion desde superset (se rompian los nombres de los recursos).

### DBQuery
 - De 0.2.0 a 0.2.3: Capturar errores de consulta (si la consulta es incorrecta).

### API Tracking
 - De 0.5.1 a 0.5.2: 
   - Se agregaron traducciones
   - Refactor en consultas de datasets y organizaciones: ahora se usan acciones (`package_show`, `organization_show`) y helpers en lugar de acceso directo a los modelos, lo que mejora compatibilidad con tipos personalizados y la construcción de URLs.

### Push Errors
 - De 0.1.5 a 0.1.6:
   - Se agregaron **blueprints de prueba** para forzar y validar errores desde endpoints internos (`/push-error/test`, `/force-500`, `/force-critical`)
   - Se introdujo **rate limiting** configurable vía Redis para limitar la cantidad de notificaciones enviadas por minuto y por hora
   - Nuevos parámetros de configuración:
     - `ckanext.push_errors.traceback_length` (largo máximo del traceback, default 4000)
     - `ckanext.push_errors.max_messages_minute` (default 3)
     - `ckanext.push_errors.max_messages_hour` (default 10)
   - Refactor en el manejo de errores: se capturan todas las excepciones de la aplicación y se ignoran automáticamente ciertos errores esperables para usuarios anónimos (401, 403, 404)
   - Compatibilidad asegurada con CKAN 2.10 y 2.11 mediante nuevos workflows de CI, 
   además se añadieron tests específicos para las funciones internas de `push_errors`

### Announcements
 - De 0.1.4 a 0.1.6: 
   - Eliminado soporte para CKAN 2.9 (Py2 y Py3), ahora solo 2.10+.
   - Migración de modales y formularios a **Bootstrap 5**, con mejoras de accesibilidad (atributos `aria-*`, encabezados y roles).
   - Nuevos estilos para mensajes de error: se muestran como alertas y se hace scroll automático al mensaje.
   - Limpieza de estilos al cerrar modales y ajustes en `modal-backdrop`.
   - Actualización de CI: se eliminaron tests en CKAN 2.9 y se añadieron workflows para CKAN 2.10 y 2.11.
