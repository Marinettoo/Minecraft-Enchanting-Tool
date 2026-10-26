# Guía de ejecución y comprobación de App 2

Esta guía se utilizará cuando se creen los archivos descritos en el plan. En esta fase solo existen los documentos de diseño. Los comandos siguientes no son pruebas ya ejecutadas sobre App 2.

## 1. Preparación

Necesitamos Python 3.12, Node compatible con Vite, npm y las credenciales de desarrollo de Clerk y OpenRouter. Para Docker y EC2 hará falta Docker con Compose. En los despliegues se comprobarán también las cuentas y los recursos indicados en la ERS.

Las versiones exactas se fijarán en los archivos de dependencias. Una instalación limpia usará esos archivos, sin tomar dependencias ni código de App 1.

## 2. Backend local

Desde la raíz del repositorio, en PowerShell:

```powershell
cd app2/backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Completar el archivo local con la configuración de esta tabla. No subirlo a Git.

| Variable | Uso |
| --- | --- |
| `OPENROUTER_API_KEY` | Clave privada del proveedor. Solo backend. |
| `OPENROUTER_MODEL` | `poolside/laguna-s-2.1:free`. |
| `AI_TIMEOUT_SECONDS` | `60`. |
| `CLERK_JWT_KEY` | Clave pública PEM de la instancia Clerk usada para verificar la firma localmente. Se copiará siguiendo el formato del archivo de ejemplo. |
| `CLERK_ISSUER` | Emisor exacto de esa instancia. |
| `CLERK_AUTHORIZED_PARTIES` | Orígenes del frontend, separados por comas. En local, `http://localhost:5173`. |
| `CLERK_AUDIENCE` | Solo si la configuración de la sesión utiliza audiencia. Si no la utiliza, se deja sin configurar. |
| `ALLOWED_ORIGINS` | Orígenes admitidos por CORS. En local, `http://localhost:5173`. |

Después:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

pytest debe usar servicios simulados y credenciales ficticias. No necesita la clave real del proveedor ni una sesión real de Clerk. Cada prueba comprobará el número de llamadas que corresponde al caso.

## 3. Frontend local

En otra terminal, desde la raíz:

```powershell
cd app2/frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Configurar `VITE_CLERK_PUBLISHABLE_KEY` con la clave pública de la instancia y `VITE_API_URL` con `http://localhost:8000`. No incluir claves privadas en variables `VITE_`.

La compilación se comprobará con:

```powershell
npm run build
```

Antes de integrar el acceso se probará el componente oficial de Clerk en la única pantalla, con su configuración real. Debe permitir acceder y salir sin añadir rutas de la aplicación. No se guardarán tokens manualmente.

## 4. Recorrido mínimo

| Comprobación | Resultado esperado |
| --- | --- |
| Petición directa sin token, con el cuerpo de ejemplo del contrato. | 401 y cero consultas a IA. |
| Acceso válido y selección válida de un libro. | Una consulta, un paso, total y advertencia de costes estimados. |
| Selección válida de ocho libros del anexo B. | Ocho pasos, todos los libros utilizados una vez y resultado final completo. |
| Selección incompatible o tipo incorrecto con sesión válida. | 422 y cero consultas a IA. |
| Respuesta simulada con un libro repetido, un paso inexistente o una suma incorrecta. | 502, sin resultado parcial ni nueva llamada. |
| Coste simulado de 39 y de 40 niveles. | El aviso de supervivencia aparece desde 40. |
| Fallo y tiempo agotado del proveedor. | Error controlado y fin de la espera, sin reintentos. |
| Doble pulsación durante la espera. | Una sola petición pendiente. |
| Cierre de sesión durante una consulta. | Se retiran los datos y una respuesta tardía no vuelve a mostrarse. |
| Recarga y nueva consulta. | No se recupera ni acumula el resultado anterior. |

Hacer también el recorrido con teclado en Chrome y Edge, a 360 y 1280 píxeles. Comprobar el foco, los textos largos y que los avisos se entiendan sin depender del color.

La prueba real con OpenRouter se ejecutará por separado, con datos ficticios y sin incluir secretos en las evidencias. Anotar fecha, versión de Git, entorno y resultado. No confundir un resultado simulado con una consulta real.

## 5. Vercel

Crear un proyecto con raíz `app2/frontend` y otro con raíz `app2/backend`, usando sus propios archivos. En el backend, comprobar la detección de `app/main.py` y la duración de 90 segundos que configure `vercel.json`. El límite de la consulta al proveedor sigue siendo de 60 segundos.

Configurar las variables de cada capa y los orígenes públicos en CORS y Clerk. Desplegar cada proyecto con la CLI de Vercel desde su carpeta y registrar las URLs reales. Comprobar una consulta válida y un rechazo sin token. El acceso público debe utilizar HTTPS.

## 6. Docker local y EC2

Desde `app2/`, preparar `.env` con los valores de ejemplo del futuro archivo de configuración. Además de las variables del backend, Compose utilizará `SITE_ADDRESS` para Caddy y las dos variables públicas del frontend. Para local: `SITE_ADDRESS=:80` y `VITE_API_URL` vacío, de modo que las peticiones usen el mismo origen.

```powershell
docker compose up --build -d
docker compose ps
```

El frontend se abrirá en el puerto 80 local. Los orígenes de Clerk y CORS deben coincidir con la dirección usada en el navegador. El backend estará disponible para el frontend dentro de la red de Compose.

En EC2 se usará el dominio real como `SITE_ADDRESS`, con DNS apuntando a la instancia. Antes de crearla se acordarán cuenta, región, presupuesto y dominio. Abrir 80 y 443; limitar SSH a las IP autorizadas. Verificar HTTPS y la recuperación de ambos servicios tras reiniciar.

Los secretos del backend se inyectarán al ejecutar. La compilación del frontend solo recibirá las variables públicas. Los archivos locales y las dependencias de desarrollo quedarán fuera de las imágenes.

Al terminar se documentará la retirada de los recursos utilizados, incluidos los que puedan seguir generando costes.

## Referencias

La forma exacta de los datos está en [contracts/http.md](contracts/http.md). Sus reglas y estados están en [data-model.md](data-model.md). Las decisiones técnicas y las fuentes están en [research.md](research.md).
