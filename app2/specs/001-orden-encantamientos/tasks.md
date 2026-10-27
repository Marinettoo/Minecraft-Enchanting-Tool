# Tareas de App 2

**Fecha**: 26/10/2026

Base: [especificación](spec.md), [plan](plan.md), [decisiones](research.md), [datos](data-model.md) y [contrato](contracts/http.md).

Las rutas parten de la raíz del repositorio. Las casillas indican qué tareas están terminadas. `[US1]`, `[US2]` y `[US3]` corresponden a las tres historias de la especificación. `[P]` indica trabajos en archivos distintos que pueden hacerse a la vez cuando sus requisitos previos estén terminados.

Las pruebas con pytest son obligatorias según la ERS y la constitución. Se preparan antes del comportamiento que comprueban, usando Clerk y OpenRouter simulados. Los resultados reales se anotan aparte, sin secretos. El equipo hace los commits y revisa cada bloque antes de continuar.

## 1. Preparar el proyecto

- [x] T001 Crear la estructura nueva del backend con Python 3.12 y fijar dependencias en `app2/backend/requirements.txt` y `app2/backend/requirements-dev.txt`, incluyendo FastAPI, Pydantic 2, HTTPX, Uvicorn, Clerk y pytest; añadir `app2/backend/app/__init__.py`.
- [x] T002 [P] Preparar Vue 3, JavaScript, Vite y Tailwind 4 en `app2/frontend/package.json`, `app2/frontend/package-lock.json`, `app2/frontend/index.html`, `app2/frontend/vite.config.js` y `app2/frontend/src/style.css`, sin router.

**Resultado**: Las dos capas tienen sus propias dependencias, sin copiar código ni entornos de App 1.

## 2. Preparar la base común

- [x] T003 Definir las variables del plan y comprobar su configuración en `app2/backend/app/config.py`, `app2/backend/.env.example` y `app2/frontend/.env.example`; fijar 60 segundos de espera y mantener las claves privadas fuera del frontend.
- [x] T004 Crear datos ficticios, respuestas simuladas y sustituciones de Clerk y OpenRouter en `app2/backend/tests/conftest.py`, sin llamadas externas ni claves reales.
- [x] T005 Comprobar el acceso y cierre con el componente oficial de Clerk, navegación por hash y una única pantalla; registrar método, configuración pública y resultado real en `docs/pruebas-app2.md` antes de T007 y T015. La prueba aislada no se publica como aplicación terminada.
- [x] T006 Preparar pruebas de sesión válida, token ausente, firma incorrecta, caducidad, emisor, origen y audiencia cuando corresponda en `app2/backend/tests/test_auth.py`, usando tokens ficticios firmados y sin servicios reales.
- [x] T007 Implementar la verificación oficial de Clerk en `app2/backend/app/auth.py`: aceptar solo `session_token`, verificar firma y vigencia, comprobar emisor y los orígenes o audiencia configurados, y rechazar con 401 si no se puede autorizar. Depende de T003, T005 y T006.
- [x] T008 Recoger las listas del anexo A en `app2/backend/app/rules.py` y los tipos compartidos en `app2/backend/app/schemas.py`: `objeto`, «Identificador de uno de los 58 objetos del anexo A de la ERS»; `nombre`, «Identificador de uno de los 39 encantamientos, permitido para el objeto»; `nivel`, «Entero estricto desde 1 hasta el máximo del encantamiento»; `encantamientos`, «Lista de 1 a 8 elementos distintos». No admitir campos extra ni convertir texto o booleanos en niveles.
- [x] T009 Preparar la aplicación, CORS y el formato común de errores en `app2/backend/app/main.py`; admitir solo los orígenes configurados y los encabezados necesarios, con registros de estados y códigos sin datos privados.

**Resultado**: Hay configuración, datos de prueba y acceso verificable. No se añade ningún modo público que evite la autenticación.

## 3. Historia 1: consultar el orden de combinación [US1, P1]

**Objetivo**: Completar una consulta autorizada y ver la propuesta en la misma pantalla.

**Comprobación**: Con servicios simulados, las selecciones de 1 y 8 libros del anexo B generan una sola llamada y muestran todos los pasos y costes. La prueba real se hace por separado.

- [x] T010 [US1] Preparar pruebas del recorrido correcto, forma del contrato y una sola llamada por envío válido en `app2/backend/tests/test_process.py`; incluir las selecciones de 1 y 8 libros y los avisos con costes de 39 y 40.
- [x] T011 [P] [US1] Implementar la comprobación de la propuesta en `app2/backend/app/plan_validator.py`: dos referencias distintas disponibles por combinación, consumo único, creación de `paso_N`, objeto a la izquierda y resultado final con todos los libros. Exigir «Con N libros debe haber exactamente N pasos», orden «Entero consecutivo desde 1» y costes enteros no negativos con total igual a su suma. Convertir las referencias aceptadas en nombres y añadir los avisos acordados, sin recalcular costes del juego.
- [x] T012 [P] [US1] Crear el cliente y las instrucciones nuevas en `app2/backend/app/ai_client.py` a partir del contrato y las reglas: modelo acordado, referencias `objeto`, `libro_N` y `paso_N`, sin streaming ni razonamiento, sin reintentos ni cambios automáticos y con límite total de 60 segundos.
- [x] T013 [US1] Integrar `POST /api/procesar` en `app2/backend/app/main.py`: verificar acceso antes de leer y validar la selección, consultar una vez, comprobar el resultado y devolver solo el resultado público o el error controlado. Depende de T007 a T012.
- [x] T014 [P] [US1] Preparar los 58 objetos, 39 encantamientos, nombres españoles y niveles en `app2/frontend/src/data.js` y el selector en `app2/frontend/src/components/EnchantmentForm.vue`, según el anexo A.
- [x] T015 [US1] Integrar Clerk en `app2/frontend/src/main.js` y `app2/frontend/src/App.vue`, y el envío en `app2/frontend/src/api.js`: obtener el token al consultar, enviarlo como Bearer y mostrar la espera sin guardar el token manualmente. Depende de T005 y T014.
- [x] T016 [US1] Mostrar pasos, elementos, total y advertencias como texto en `app2/frontend/src/components/PlanResult.vue`; controlar en `app2/frontend/src/App.vue` el bloqueo del envío y la edición durante la espera, la sustitución del resultado y la retirada de datos al recargar o cerrar sesión.
- [x] T017 [US1] Ejecutar las pruebas de éxito y el recorrido de esta historia; anotar en `docs/pruebas-app2.md` la versión, el entorno y los resultados, diferenciando simulaciones y servicios reales.

**Resultado**: Primer recorrido completo para demostrar en local. Todavía no se publica: las tres historias son obligatorias.

## 4. Historia 2: corregir la selección o volver a acceder [US2, P1]

**Objetivo**: Rechazar los datos incorrectos y explicar cómo corregirlos, sin consultar a IA.

**Comprobación**: Peticiones directas con sesiones rechazadas producen 401; con sesión válida y entrada incorrecta producen 422. Ambas tienen cero llamadas al proveedor.

- [x] T018 [US2] Preparar casos de 0 y 9 libros, repetidos, niveles fuera de rango, decimales, textos, booleanos, campos adicionales, JSON ilegible, opciones desconocidas e incompatibilidades en `app2/backend/tests/test_validation.py`; comprobar también que el rechazo de acceso ocurre antes de validar el cuerpo y no llama a IA.
- [x] T019 [US2] Completar las validaciones de la selección en `app2/backend/app/schemas.py` y su tratamiento en `app2/backend/app/main.py`, usando `app2/backend/app/rules.py`; devolver 422 con `VALIDACION` para los casos rechazados y no consultar al proveedor.
- [x] T020 [US2] Añadir los avisos por selección obligatoria ausente e incompatibilidades en `app2/frontend/src/components/EnchantmentForm.vue`, y la petición de volver a acceder en `app2/frontend/src/App.vue`, sin sustituir la validación del backend.
- [x] T021 [P] [US2] Comparar los identificadores, niveles y compatibilidades de `app2/frontend/src/data.js` y `app2/backend/app/rules.py` en `app2/backend/tests/test_catalogue.py`, para comprobar que ambas capas usan las mismas opciones.
- [x] T022 [US2] Ejecutar los casos de rechazo y comprobar cierre de sesión y corrección del formulario; registrar resultados y cero llamadas en `docs/pruebas-app2.md`.

## 5. Historia 3: entender un fallo y poder continuar [US3, P1]

**Objetivo**: Terminar la espera con un mensaje comprensible, sin resultados parciales ni reintentos.

**Comprobación**: Los fallos simulados de proveedor, formato, pasos, tiempo y conexión dejan la pantalla utilizable y permiten otro intento manual.

- [x] T023 [P] [US3] Preparar pruebas de propuestas vacías, ilegibles, incompletas, referencias inventadas, libros omitidos o reutilizados, pasos futuros, orden incorrecto, costes negativos o no enteros y suma incorrecta en `app2/backend/tests/test_plan_validator.py`, incluyendo resultado final sin el objeto o sin todos los libros.
- [x] T024 [P] [US3] Preparar pruebas de fallo de red, rechazo del proveedor, terminación incompleta, JSON con bloque Markdown exterior y tiempo total agotado en `app2/backend/tests/test_ai_client.py`; simular el tiempo, comprobar el límite de 60 segundos y una sola llamada, sin esperar al proveedor real.
- [x] T025 [US3] Completar los rechazos y su traducción a `IA_NO_DISPONIBLE`, `RESPUESTA_INVALIDA` e `IA_TIMEOUT` en `app2/backend/app/ai_client.py`, `app2/backend/app/plan_validator.py` y `app2/backend/app/main.py`, según el contrato; no corregir JSON incompleto ni devolver partes de una propuesta rechazada.
- [x] T026 [US3] Tratar errores de acceso, entrada, proveedor, tiempo, conexión y respuestas no utilizables en `app2/frontend/src/api.js` y `app2/frontend/src/App.vue`; terminar la espera, permitir otro intento manual y descartar respuestas tardías tras cerrar sesión sin volver a consultar automáticamente.
- [x] T027 [US3] Comprobar los fallos de esta historia, textos con etiquetas HTML, doble pulsación y cierre de sesión durante la espera; registrar los resultados en `docs/pruebas-app2.md`.

## 6. Comprobaciones finales y despliegues

- [ ] T028 Revisar teclado, foco, etiquetas y textos largos en Chrome y Edge a 360 y 1280 píxeles; corregir `app2/frontend/src/style.css` y los componentes necesarios, y anotar las cuatro combinaciones en `docs/pruebas-app2.md`.
- [x] T029 Comprobar que no se conservan consultas tras nueva consulta, recarga, cierre y reinicio, y que no aparecen secretos ni datos funcionales en archivos públicos, registros o paquetes; registrar la revisión y los resultados de pytest y compilación en `docs/pruebas-app2.md`.
- [ ] T030 Preparar `app2/backend/vercel.json` con la entrada `app/main.py` y duración de 90 segundos si la cuenta lo permite; desplegar ambas capas con la CLI, configurar Clerk y CORS y documentar URLs HTTPS, consulta válida y rechazo sin token en `docs/despliegue-app2.md`.
- [x] T031 Crear `app2/backend/Dockerfile`, `app2/frontend/Dockerfile` y sus archivos `.dockerignore`, con Uvicorn en backend y compilación del frontend servida por Caddy; excluir secretos y dependencias locales, e incluir solo configuración pública al compilar.
- [x] T032 Configurar `app2/compose.yaml`, `app2/frontend/Caddyfile` y `app2/.env.example` con dos servicios, proxy `/api/*` sin quitar el prefijo, secretos del backend al ejecutar y reinicio `unless-stopped`; el único volumen será técnico para certificados.
- [x] T033 Ejecutar Docker local desde cero y tras reiniciar, comprobar acceso, consulta y errores, y registrar instrucciones y resultados en `docs/despliegue-app2.md`, sin conservar consultas.
- [ ] T034 Concretar con el equipo cuenta, región, presupuesto, nombre público e IP autorizadas para SSH antes de crear recursos de AWS; registrar las decisiones sin secretos en `docs/despliegue-app2.md`.
- [ ] T035 Desplegar la misma versión en EC2 con Docker y HTTPS, verificar DNS, puertos 80/443, backend sin puerto público y recuperación tras reinicio; documentar comprobaciones, actualización y retirada de recursos en `docs/despliegue-app2.md`. Depende de T033 y T034.
- [ ] T036 Actualizar `README.md`, `docs/ERS-APP2.md` y `app2/specs/001-orden-encantamientos/quickstart.md` con versiones, variables sin secretos, comandos y enlaces reales; comprobar la instalación y una consulta válida y un error en cada entorno con las credenciales de quien la ejecute.
- [ ] T037 Registrar el proceso de App 2 en `docs/proceso.md` y `docs/uso-ia.md`, con herramienta, modelo usado, resumen de instrucciones, decisiones y revisión humana; preparar `docs/comparativa-apps.md` con entradas comunes, tiempos, calidad, errores y mantenibilidad, separando Clerk e infraestructura y sin inventar resultados.
- [ ] T038 Preparar `docs/presentacion-proyecto.pptx` y `docs/guion-demo.md` con problema, arquitectura, proceso, comparación y demo; completar datos de la ERS, revisión del equipo y enlaces de entrega, sin secretos y con una evidencia de respaldo identificada como tal.

## Dependencias y orden

```text
Preparación → Base común → Historia 1 → Historia 2 → Historia 3
                                                     ↓
                                   Comprobaciones y despliegues → Entrega
```

Las historias comparten el mismo formulario y endpoint. Seguiremos ese orden para evitar cambios simultáneos en los mismos archivos, aunque cada una tenga su comprobación por separado.

T005 debe terminar antes de integrar Clerk. T013 necesita el backend completo del recorrido correcto. Los despliegues empiezan después de comprobar las tres historias. EC2 necesita antes Docker local y los recursos acordados. La documentación de T037 se actualiza durante el trabajo y se completa al final.

## Trabajos que pueden hacerse a la vez

- Preparación: T001 y T002.
- Historia 1: T011 y T012 después de T010; T014 puede avanzar con las listas de T008 mientras se completa el backend.
- Historia 2: T020 y T021 después de definir los casos de T018; modifican archivos distintos.
- Historia 3: T023 y T024, usando las mismas bases de prueba sin modificar `conftest.py` a la vez.

Estas posibilidades no obligan a trabajar en paralelo ni a usar agentes adicionales.

## Cómo avanzaremos

Primero revisaremos estas tareas y haremos el análisis de coherencia de Spec Kit, antes de implementar. Después se versionará la lista antes del código correspondiente. El primer objetivo será demostrar la historia 1 en local; luego completaremos los rechazos, los fallos y los despliegues. Ningún requisito de la entrega se elimina por llamar mínimo a ese primer recorrido.

Marcaremos una tarea solo cuando esté hecha y comprobada. No se considerarán realizadas las pruebas ni aprobados los documentos por figurar en esta lista.
