# Plan técnico de App 2

**Funcionalidad**: `001-orden-encantamientos` | **Fecha**: 20/10/2026

**Especificación**: [spec.md](spec.md) | **Rama actual de Git**: `main`

## Resumen

Crearemos una aplicación nueva dentro de `app2/`. El jugador accederá con Clerk, elegirá el objeto y los libros y recibirá una propuesta en la misma pantalla. FastAPI comprobará el acceso, la selección y la respuesta de IA.

El flujo será Vue → FastAPI → OpenRouter → FastAPI → Vue. No guardaremos las consultas. Las decisiones y la comprobación del modelo están en [research.md](research.md).

## Contexto técnico

| Parte | Decisión |
| --- | --- |
| Backend | Python 3.12, FastAPI y Pydantic 2. |
| Frontend | JavaScript, Vue 3 y Vite. Tailwind CSS 4 con su complemento de Vite. Sin Vue Router. |
| Identidad | `@clerk/vue` en la pantalla y `clerk-backend-api` en el backend. |
| Peticiones a IA | HTTPX, sin reintentos, sin streaming y con un límite total de 60 segundos. |
| Modelo | `poolside/laguna-s-2.1:free`, a través de OpenRouter. |
| Ejecución | Uvicorn en local y Docker. Node 22.12 o posterior compatible con las dependencias elegidas para compilar el frontend. |
| Pruebas | pytest y servicios simulados; revisión manual del recorrido, teclado y tamaños de pantalla. |
| Almacenamiento | Solo datos en memoria durante la consulta. Ninguna base de datos ni historial. |
| Entornos | Local, frontend y backend en Vercel, Docker local y Docker en EC2 con HTTPS. |
| Alcance | Una pantalla, un objeto y de 1 a 8 libros. Las opciones son las del anexo A de la ERS. |

Las versiones exactas se fijarán al preparar las dependencias, con `package-lock.json` y archivos de requisitos de Python. No damos por comprobada su instalación por aparecer en este plan.

## Comprobación de la constitución

| Principio | Cómo lo cumple el diseño |
| --- | --- |
| Una función y una pantalla | Formulario, acceso, resultado y errores en `App.vue`, con componentes pequeños de apoyo. No habrá router ni almacenamiento funcional. |
| Una consulta a IA | El backend verifica el acceso y valida la selección antes de llamar a OpenRouter. Solo una llamada, sin reintentos ni cambios de modelo. |
| Acceso protegido | Clerk comprueba la sesión en backend. Las claves privadas se reciben mediante variables de entorno. |
| Contrato y pruebas | [contracts/http.md](contracts/http.md) concreta la interfaz. pytest comprobará éxito, rechazos, fallos, tiempo agotado y número de llamadas. |
| Implementación nueva | Se escribirán archivos propios en App 2. Especificación, plan y tareas quedarán en Git antes del código correspondiente. |

La revisión antes y después del diseño no encuentra excepciones a estos principios. El acceso al modelo y el formato básico se comprobaron con datos ficticios, como recoge la investigación. La prueba real de Clerk se hará antes de implementar su integración, según la constitución.

## Estructura del proyecto

### Documentos de esta funcionalidad

```text
app2/specs/001-orden-encantamientos/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── http.md
└── checklists/
    └── requirements.md
```

`tasks.md` se preparará en la fase de tareas, después de revisar este plan.

### Archivos que crearemos al implementar

```text
app2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── auth.py
│   │   ├── schemas.py
│   │   ├── rules.py
│   │   ├── ai_client.py
│   │   └── plan_validator.py
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env.example
│   ├── .dockerignore
│   ├── Dockerfile
│   └── vercel.json
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── style.css
│   │   ├── data.js
│   │   ├── api.js
│   │   └── components/
│   │       ├── EnchantmentForm.vue
│   │       └── PlanResult.vue
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── .env.example
│   ├── .dockerignore
│   ├── Dockerfile
│   └── Caddyfile
├── compose.yaml
└── .env.example
```

`main.py` coordina el recorrido y adapta los errores. `auth.py` verifica la sesión. `schemas.py` describe los datos y sus tipos; `rules.py` recoge las opciones de la ERS. `ai_client.py` consulta al proveedor y `plan_validator.py` comprueba los pasos. Esta separación permite probar cada parte sin llamar a servicios reales.

`data.js` contiene las opciones y los nombres que muestra el formulario. Una prueba comparará sus identificadores, niveles y compatibilidades con los del backend. Las listas son datos fijos, no un catálogo gestionable.

## Recorrido técnico

1. El frontend obtiene el token de sesión con Clerk y envía la selección al endpoint protegido.
2. Una dependencia de FastAPI verifica el token. Solo después se lee y valida la selección. Así una petición sin acceso no alcanza ni la validación funcional ni la IA.
3. HTTPX envía una sola petición al modelo. Un límite total de 60 segundos controla toda la operación con el proveedor, además de los tiempos de red.
4. El backend lee el contenido de la respuesta y valida su estructura, referencias y suma. Solo acepta una respuesta terminada correctamente. Puede retirar un bloque Markdown exterior que contenga únicamente JSON; no buscará ni completará JSON entre explicaciones.
5. Convierte las referencias válidas en nombres comprensibles y añade los avisos de costes estimados y del límite de supervivencia cuando correspondan.
6. El frontend muestra el resultado como texto. Durante la espera bloquea el envío y la edición de la selección. Al cerrar sesión, cancela la espera local y descarta cualquier respuesta tardía. Esto no genera otra consulta al proveedor.

## Pruebas previstas

| Qué comprobaremos | Requisitos |
| --- | --- |
| Sesión válida, ausente, manipulada, caducada o de otro emisor u origen. Cero llamadas en los rechazos. | RF-01, RNF-02 |
| Listas completas, límites de 1 y 8, tipos estrictos, campos extra, repetidos e incompatibilidades. | RF-02, RF-03 |
| Una sola llamada con acceso y entrada válidos, sin reintentos ni otro modelo. | RF-04 |
| Uso de elementos, pasos consecutivos, resultado final, suma y rechazos sin resultados parciales. | RF-05 |
| Costes de 39 y 40, texto sin ejecutar, espera, sustitución del resultado y cierre de sesión. | RF-06, RNF-03 |
| Errores controlados y conexión interrumpida. Límite total de 60 segundos con reloj o espera simulados. | RF-07, RNF-01 |
| Recorrido con teclado en Chrome y Edge a 360 y 1280 píxeles. | RNF-04 |
| Instalación limpia, servicios simulados, funcionamiento real separado y recuperación tras reinicio. | RNF-05 |

Las pruebas de backend simularán tanto Clerk como OpenRouter. El verificador de identidad también tendrá pruebas específicas con credenciales ficticias firmadas, sin depender de una cuenta real. No se introducirá un modo público que desactive la autenticación.

## Despliegues

En Vercel habrá un proyecto para `app2/frontend` y otro para `app2/backend`. El backend usará `app/main.py` como entrada. Configuraremos 90 segundos de duración de función, si la cuenta lo permite, para que el límite propio de 60 segundos pueda devolver un error controlado. Se comprobará la configuración real antes de publicar.

En Docker habrá dos servicios: backend con Uvicorn y frontend compilado servido por Caddy. Caddy enviará `/api/*` al backend conservando la ruta. En local servirá HTTP; en EC2 usará el nombre público acordado y HTTPS. Solo los certificados necesitan un volumen técnico; no se guardarán consultas.

Los secretos se proporcionarán al ejecutar el backend. El frontend solo recibirá configuración pública durante la compilación. Los servicios usarán `restart: unless-stopped`. En EC2 se publicarán 80 y 443; SSH quedará limitado a las IP acordadas y el backend no tendrá un puerto público propio.

## Complejidad

No se necesitan excepciones a la constitución, capas de repositorio, base de datos, colas ni servicios funcionales adicionales.
