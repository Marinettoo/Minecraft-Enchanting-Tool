# Constitución de MeT — Minecraft Enchanting Tool (App 2)

Estado: aprobada como base de trabajo para App 2 el 2026-10-19.
Referencias: enunciado PR01-UD1 y `docs/ERS-APP2.md`, versión 0.1 de 2026-10-19.
Las rutas de documentación se refieren a la raíz del repositorio MeT.

## Core Principles

### I. Una función, una pantalla y ninguna persistencia funcional

La aplicación DEBE proponer un orden de combinación de encantamientos para Minecraft Java.
DEBE tener una SPA, un formulario y el resultado en la misma pantalla. El acceso de Clerk
DEBE integrarse en esa pantalla o en un modal, sin rutas frontend adicionales.

NO DEBE incorporar bases de datos de ningún tipo, historial, cachés de resultados, CRUD,
paneles, estadísticas, perfiles, subida de archivos, chat, agentes encadenados ni servicios
funcionales extra. Las entradas y respuestas solo DEBEN existir temporalmente para la consulta
y su visualización; NO DEBEN guardarse en archivos, almacenamiento remoto, localStorage,
sessionStorage o IndexedDB. Una nueva consulta DEBE sustituir la anterior; recargar o cerrar
sesión DEBE retirar los datos funcionales mostrados. La sesión técnica de Clerk solo DEBE
utilizarse para autenticación. Estas restricciones mantienen el alcance académico y permiten
comparar ambas aplicaciones.

### II. Una sola consulta a IA y resultados comprobados

El flujo DEBE ser Vue → FastAPI → OpenRouter → FastAPI → Vue. FastAPI DEBE verificar el acceso
y validar la selección antes de consultar a IA. Cada envío autorizado y válido DEBE provocar
una sola petición al proveedor. NO DEBE haber reintentos automáticos, consultas complementarias
ni sustitución automática de modelo. El modelo acordado es `poolside/laguna-s-2.1:free`.

La entrada DEBE limitarse a un objeto y entre 1 y 8 encantamientos distintos del anexo A de la
ERS, con niveles enteros estrictos y compatibilidades comprobadas en backend. NO DEBEN aceptarse
texto libre, campos adicionales ni conversiones de texto o booleanos a niveles. Los objetos y
libros DEBEN ser nuevos, sin trabajos previos de yunque, y cada libro tendrá un encantamiento.
Quedan excluidos reparación, renombrado y combinación para aumentar niveles, según la ERS.

El backend DEBE validar estructura, elementos, resultados intermedios y suma de costes de la
respuesta. Cada combinación DEBE consumir dos elementos disponibles y producir uno; todos los
libros y el objeto inicial DEBEN utilizarse una vez y el resultado final DEBE contener los
encantamientos solicitados. Con N libros DEBE haber N pasos. Los costes DEBEN ser enteros no
negativos, con advertencia para pasos de 40 niveles o más. DEBEN mostrarse como estimaciones,
sin garantizar exactitud ni coste mínimo. Una respuesta inválida DEBE rechazarse sin realizar
una segunda consulta a IA.

### III. Autenticación y protección de información en backend

Clerk DEBE ser el único servicio de identidad. NO DEBEN existir usuarios, contraseñas, roles,
perfiles ni endpoints de gestión de cuentas propios. El frontend DEBE enviar el token de sesión
en `Authorization: Bearer ...`. FastAPI DEBE verificar firma, emisor, caducidad y las condiciones
de audiencia u origen aplicables mediante un mecanismo oficial compatible. Decodificar el token
sin verificarlo NO DEBE autorizar la petición. Un token ausente, inválido o caducado DEBE producir
401 sin llamada a IA. Si no puede verificarse la sesión, NO DEBE permitirse el procesamiento.

Las claves privadas DEBEN permanecer en backend, fuera del repositorio, imágenes Docker, prompts,
capturas y mensajes de error. Solo la clave publishable de Clerk y la configuración pública
necesaria pueden incluirse en frontend. Los registros DEBEN limitarse a estados y códigos técnicos,
sin entradas, respuestas, tokens ni secretos. Los despliegues públicos DEBEN usar HTTPS.
CORS DEBE admitir los orígenes acordados y Authorization cuando corresponda; NO DEBE sustituir
la autenticación. El contenido de IA DEBE mostrarse como texto, sin ejecutar HTML ni código.

### IV. Contrato verificable y pruebas con servicios simulados

La ERS y el contrato HTTP DEBEN describir campos, tipos, límites, reglas y errores antes de
implementar el comportamiento correspondiente. El endpoint DEBE ser `POST /api/procesar`;
solo puede añadirse un endpoint técnico de salud si es necesario. La respuesta DEBE contener
el resultado validado o el error controlado, sin metadatos privados del proveedor. Los códigos
acordados son 200, 401, 422, 502 y 504, con los esquemas de la ERS. El timeout al proveedor DEBE
ser de 60 segundos, conforme a RNF-01. Si el entorno exige cambiarlo, DEBEN actualizarse ERS,
contrato y pruebas antes del despliegue.

Las pruebas habituales DEBEN usar pytest y simular OpenRouter y la verificación de Clerk, sin
llamadas externas. DEBEN comprobar éxito, límites, tipos, incompatibilidades, acceso rechazado,
respuesta inválida, fallo y timeout. DEBEN contar una llamada para el envío autorizado y válido,
y cero para acceso o entrada rechazados. Las pruebas reales DEBEN realizarse por separado con
datos ficticios y resultados documentados. NO DEBE presentarse un mock como servicio real.

La interfaz DEBE mostrar espera y errores, impedir envíos duplicados mientras haya una petición
pendiente y permitir corregir o repetir manualmente. DEBE verificarse el uso con teclado,
Chrome y Edge, a 360 y 1280 píxeles de ancho, según RNF-04.

### V. Implementación nueva y revisión humana por fases

App 2 DEBE tener código y dependencias propios en `app2/`. Puede reutilizar conocimiento,
requisitos, contrato y referencias visuales de App 1; NO DEBE copiar su implementación.
La especificación, el plan y las tareas DEBEN quedar versionados antes del código correspondiente.
Spec Kit NO DEBE sustituir la ERS académica ni producir especificaciones retrospectivas.

El trabajo DEBE avanzar por fases: constitución, especificación, aclaraciones necesarias, plan,
tareas, análisis de coherencia e implementación por tareas. El agente DEBE explicar cada resultado
y esperar a la revisión del usuario antes de iniciar la siguiente fase. Las propuestas de IA
DEBEN revisarse y corregirse cuando contradigan el alcance o los requisitos.

Git DEBE reflejar evolución real y contribuciones identificables del equipo. El registro de IA
DEBE indicar herramienta/modelo, finalidad, prompt o resumen depurado, decisiones y comprobación
humana. La comparativa DEBE usar escenarios comunes y separar Clerk e infraestructura del flujo
base, sin inventar tiempos, pruebas, aprobaciones ni resultados favorables.

## Restricciones técnicas y despliegue

- Backend: Python y FastAPI. Frontend: Vue y Tailwind CSS, sin router ni pantallas nuevas.
- Preparación inicial: Spec Kit 1.2.1, Codex y scripts PowerShell. Las versiones utilizadas
  y sus cambios DEBEN registrarse.
- El diseño DEBE incorporar solo dependencias y componentes necesarios para el flujo.
  Las listas fijas NO DEBEN convertirse en un catálogo gestionable.
- Frontend y backend DEBEN desplegarse en Vercel. Después, App 2 DEBE funcionar en Docker local
  y en una instancia Linux de AWS EC2 con HTTPS, manteniendo alcance y autenticación.
- Docker DEBE excluir secretos y dependencias locales innecesarias. Los secretos DEBEN
  suministrarse al ejecutar, sin incluirlos en imágenes ni argumentos de compilación.
  El frontend compilado solo DEBE recibir configuración pública.
- Dependencias, versiones, variables sin secretos, instalación, pruebas, URLs, red, reinicio,
  actualización y retirada de recursos DEBEN documentarse. La infraestructura NO DEBE añadir
  bases de datos, volúmenes funcionales ni cachés de resultados.
- Cuentas, cuotas, región, presupuesto y nombre público para HTTPS DEBEN confirmarse antes
  de crear recursos. NO DEBE suponerse gratuidad por el nombre del modelo o del servicio.

## Flujo de trabajo y comprobaciones de revisión

Antes de cerrar cada fase, el equipo DEBE comprobar que el artefacto respeta los cinco principios,
es coherente con la ERS e identifica las decisiones pendientes que afectan a la siguiente fase.
La documentación DEBE redactarse en español, conservando los identificadores técnicos.

Los ejemplos genéricos de las plantillas NO DEBEN trasladarse como requisitos de MeT.
Las propuestas de bases de datos, gestión propia de cuentas, rutas adicionales o pruebas
opcionales DEBEN descartarse por contradecir las obligaciones de este proyecto.

Los pendientes PEN-01 a PEN-06 se gestionan en la ERS. Para cerrar la especificación, DEBE
sincronizarse el contrato con las listas, costes estimados, timeout de 60 segundos y representación
comprobable de elementos intermedios. Antes de cerrar el plan técnico, DEBE comprobarse el acceso
y el formato de respuesta del modelo. Antes de implementar la integración de identidad, DEBE
comprobarse el flujo de Clerk en la única pantalla. Estas comprobaciones NO DEBEN darse por
realizadas por figurar aquí ni ejecutarse como parte de la constitución.

## Governance

Esta constitución establece las reglas de Spec Kit para App 2 dentro del alcance del enunciado
y las decisiones revisadas del equipo. Una contradicción con la ERS o el contrato DEBE señalarse
y resolverse antes de implementar el comportamiento afectado; NO DEBE resolverse ampliando
el alcance obligatorio de la práctica.

Toda modificación DEBE explicar motivo e impacto en requisitos y artefactos, quedar revisada
por el equipo y registrarse en Git. El versionado DEBE seguir MAJOR.MINOR.PATCH: MAJOR para
cambios incompatibles de principios; MINOR para nuevas reglas o ampliaciones materiales; PATCH
para aclaraciones sin cambios de obligación. Ningún cambio puede autorizar funciones prohibidas
por el enunciado.

La versión 1.0.0 establece las reglas iniciales de trabajo de App 2.

**Versión**: 1.0.0 | **Ratificación**: 2026-10-19 | **Última modificación**: 2026-10-19
