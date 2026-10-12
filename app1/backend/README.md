# MeT — Backend de App 1

FastAPI recibe un objeto y sus encantamientos, pide a OpenRouter un orden de
combinación de yunque y devuelve el JSON del contrato. Solo implementa el backend
de App 1: no incluye frontend, Clerk, App 2, base de datos ni historial.

## Configuración y ejecución (PowerShell)

Desde `app1/backend`, con Python 3.12 o 3.13:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

No sobrescribas `.env` si ya lo has configurado. Abre
<http://localhost:8000/docs> para probar el único endpoint funcional,
`POST /api/procesar`. `/docs` y `/openapi.json` son documentación técnica de FastAPI.

Edita **`.env`**, nunca pongas la clave en archivos del frontend:

| Variable | Qué poner |
| --- | --- |
| `AI_MODE` | `mock` para trabajar con ejemplos; `openrouter` para usar IA real. |
| `OPENROUTER_API_KEY` | Tu clave privada de OpenRouter. |
| `OPENROUTER_MODEL` | Identificador exacto del modelo elegido, copiado de OpenRouter. Modelo pendiente: no se selecciona automáticamente ni se garantiza gratuidad. |
| `AI_TIMEOUT_SECONDS` | `20` segundos por defecto, límite total de la llamada. |
| `ALLOWED_ORIGINS` | Origen del frontend, por defecto `http://localhost:5173`. Varios separados por comas, sin rutas ni comodines. |

Las variables del sistema tienen prioridad sobre `.env`. Sin `.env`, el modo por
defecto es `openrouter`; sin credenciales responde 502 de forma controlada. No
hay cambio automático a datos ficticios ante un fallo real.

**La plantilla `.env.example` activa `mock` expresamente:** devuelve costes de
1 nivel por paso, inventados, y una advertencia visible. No consulta servicios
externos y NO demuestra el requisito académico de una llamada real a IA. Cambia
a `openrouter`, configura clave/modelo y realiza la prueba manual antes de entregar.
Los datos ficticios se definen en `ai_client.py`, función `mock_plan`.

## Contrato para el frontend

```json
{
  "objeto": "diamond_sword",
  "encantamientos": [
    {"nombre": "sharpness", "nivel": 5},
    {"nombre": "mending", "nivel": 1}
  ]
}
```

Respuesta de ejemplo **simulada**, abreviando las advertencias:

```json
{
  "resultado": {
    "pasos": [
      {"orden": 1, "izquierda": "diamond_sword", "derecha": "Libro de sharpness 5", "coste_niveles": 1},
      {"orden": 2, "izquierda": "Resultado del paso 1", "derecha": "Libro de mending 1", "coste_niveles": 1}
    ],
    "coste_total_niveles": 2,
    "advertencias": ["MODO SIMULADO: costes ficticios; no se ha consultado ninguna IA."]
  }
}
```

Los nombres internos se mantienen en los textos para evitar traducciones
ambiguas; el frontend puede presentarlos como texto normal. Nunca usar HTML de
la IA, `v-html` o equivalentes. No guardar entradas ni resultados.

| HTTP | `error.codigo` | Situación |
| --- | --- | --- |
| 200 | — | Plan válido estructuralmente. |
| 422 | `VALIDACION` | JSON/campos/niveles/compatibilidad incorrectos, sin llamar a IA. |
| 502 | `IA_NO_DISPONIBLE` | Falta configuración, error HTTP o conexión al proveedor. |
| 502 | `RESPUESTA_INVALIDA` | Contenido truncado, JSON inválido, referencias u orden inválidos, suma incorrecta. |
| 504 | `IA_TIMEOUT` | Se supera el tiempo límite. |

Todos los errores del procesamiento tienen la forma:

```json
{"error":{"codigo":"IA_NO_DISPONIBLE","mensaje":"No se ha podido completar la petición. Inténtalo más tarde."}}
```

El 401/Clerk corresponde exclusivamente a App 2. No hay autenticación en esta app.
Una petición válida en modo real y con configuración correcta hace un solo POST
a OpenRouter, sin reintentos ni fallback. Los errores no exponen cuerpos del
proveedor, claves, entrada enviada ni detalles de excepciones.

Ejemplo manual desde PowerShell (con el servidor iniciado):

```powershell
$body = '{"objeto":"diamond_sword","encantamientos":[{"nombre":"sharpness","nivel":5},{"nombre":"mending","nivel":1}]}'
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/procesar -ContentType 'application/json' -Body $body
```

Tu compañero debe configurar la URL base del backend en su frontend, por ejemplo
`VITE_API_BASE_URL=http://localhost:8000`, y enviar el JSON a `/api/procesar`.
La clave de OpenRouter nunca debe ser una variable `VITE_...`.

## Listas y supuestos adoptados

Las listas están en `rules.py` y deben coordinarse con el frontend:

- Herramientas: `sword`, `axe`, `pickaxe`, `shovel`, `hoe` combinados con
  `wooden`, `stone`, `iron`, `golden`, `diamond`, `netherite` (ej.: `diamond_sword`).
- Armaduras: `helmet`, `chestplate`, `leggings`, `boots` con `leather`, `chainmail`,
  `iron`, `golden`, `diamond`, `netherite`.
- Sin prefijo de material: `bow`, `crossbow`, `fishing_rod`, `trident`.
- Encantamientos: exactamente los 17 de la sección 5 del contrato. Se rechazan
  los otros tipos de protección por no formar parte de esa lista inicial.
- De 1 a 8 entradas, niveles enteros estrictos (no booleanos ni cadenas), sin
  campos extra, duplicados ni combinaciones incompatibles.

Se asume Java, objeto sin encantamientos/trabajos previos y un libro nuevo por
encantamiento al nivel solicitado. No se cubren reparación, renombrado, mods ni
otros objetos. La tabla inicial procede del contrato y conocimiento de Java;
queda pendiente contrastarla en la versión concreta de Minecraft que acordéis.
La consulta a Minecraft Wiki durante la preparación no fue accesible; no se
presenta como verificada. No se añaden objetos recientes por inferencia.

Con las listas actuales el máximo compatible es 7 encantamientos (espada).
El límite de 8 se conserva para respetar el contrato, aunque no hay una petición
válida con 8 distintos en esta selección inicial.

## Qué se comprueba de la IA

Para comprobar el orden sin interpretar lenguaje natural, el prompt pide un
formato interno con referencias `objeto`, `libro_1`, `libro_2`, `paso_1`, etc.
No cambia el contrato del frontend: `schemas.py` transforma las referencias en
textos después de comprobar que cada recurso existe, se usa solo una vez y el
resultado contiene todos los libros y el objeto. Se permiten libros combinados.
También se valida el esquema, el orden consecutivo y la suma de costes.

**No se recalculan las mecánicas de coste ni se garantiza el mínimo global.**
Esto sigue pendiente en vuestro contrato (consulta al profesor). La respuesta
siempre incluye esta limitación en `advertencias`. Un plan estructuralmente
correcto todavía puede tener costes inventados por la IA. Por tanto, la promesa
de «menor coste» requiere validación adicional antes de considerarse demostrada.

## Archivos

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | FastAPI, CORS, endpoint y errores. |
| `config.py` | Carga y validación de variables de entorno. |
| `rules.py` | Objetos, niveles y compatibilidades. |
| `schemas.py` | Modelos de entrada/salida y comprobación del plan. |
| `ai_client.py` | Prompt, llamada a OpenRouter y modo simulado. |
| `tests/test_backend.py` | Pruebas aisladas del proveedor. |

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Se simula tanto la función de IA como el transporte HTTP (`httpx.MockTransport`):
éxito, una sola llamada, entrada inválida sin llamada, límites, incompatibilidades,
respuesta corrupta, consumo de libros, errores HTTP/conexión, timeout de HTTP y
deadline total, CORS y configuración ausente. No requieren créditos ni claves.

Verificación realizada el 8 de octubre de 2026: **46 pruebas superadas** con
Python 3.12.14. Se utilizó el Python disponible en el runtime local de Codex
porque el Python 3.13 del sistema no pudo crear correctamente el entorno.
Las pruebas requirieron ejecución fuera del sandbox (el TestClient se bloqueaba
en él); todas las llamadas al proveedor siguieron simuladas. Hubo un aviso de
deprecación de Starlette/AnyIO, sin fallos de pruebas.

La prueba real está pendiente de credenciales y modelo. Documentad fecha, modelo,
versión Git y resultado con datos ficticios, sin guardar secretos. No confundáis
una prueba simulada con una respuesta real.

## Preparación para Vercel

Crear el proyecto backend con raíz `app1/backend`. Exportamos `app` en `main.py`
y declaramos dependencias en `requirements.txt`, para la detección de FastAPI.
Configurar las cinco variables de entorno en Vercel, con `AI_MODE=openrouter` y
el origen HTTPS real del frontend. No subir `.env`. Usar Python 3.12/3.13 según
el runtime disponible. La duración de la función debe superar el timeout de IA.

```powershell
vercel login
vercel link
vercel env add OPENROUTER_API_KEY
vercel env add OPENROUTER_MODEL
vercel env add AI_MODE
vercel env add AI_TIMEOUT_SECONDS
vercel env add ALLOWED_ORIGINS
vercel deploy
# Tras comprobar preview y configurar Production:
vercel deploy --prod
```

El despliegue no se ha ejecutado. Falta verificar URL, CORS, petición real y error
desde el frontend publicado. CORS no es autenticación ni limita el gasto de
llamadas directas: configurad el presupuesto del proveedor para la demo.

Referencias técnicas consultadas el 8 de octubre de 2026:
[OpenRouter: Chat Completions](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion)
y [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi).

## Revisión académica pendiente

Este backend se ha generado con asistencia de IA a petición del usuario.
El profesor pide construcción progresiva y comprensión del código de App 1;
esta generación no acredita esos requisitos por sí sola. Revisad los módulos,
registrad esta asistencia en `docs/uso-ia.md` y trabajad los hitos reales sin
inventar commits retrospectivos ni evidencias. No se han generado ERS, frontend,
App 2, documentación de entrega global ni despliegues como si estuvieran hechos.
