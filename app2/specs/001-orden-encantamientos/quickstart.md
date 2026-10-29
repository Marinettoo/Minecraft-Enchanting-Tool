# Guía de ejecución y comprobación de App 2

La estructura básica de App 2 ya está creada. El resto de esta guía se completará al implementar el acceso, el formulario, la consulta y los despliegues.

## Base comprobada el 26/10/2026

Se han completado T001 y T002 sobre la base del commit `0a5bacf`. El entorno propio utiliza Python 3.12.14 y la comprobación del frontend se ha hecho con Node 24.21.0 y npm 11.19.0. Las versiones de los paquetes quedan fijadas en los archivos de requisitos y en `package-lock.json`.

En este equipo se ha creado `.venv` con el Python disponible en Codex, porque `py -3.12` no encuentra una instalación. Para repetir la instalación se necesita un Python 3.12 disponible; una vez creado el entorno, los comandos usan su propio ejecutable.

Desde `app2/backend`, el backend básico arranca con:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Desde `app2/frontend`, la pantalla inicial arranca con:

```powershell
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Comprobaciones iniciales: dependencias de Python sin conflictos, pytest instalado, frontend compilado y servido con HTTP 200, y arranque correcto de Uvicorn. El backend aún no tiene rutas funcionales, por lo que `/` devuelve 404.

Después se ha comprobado con el usuario el acceso y cierre de sesión de Clerk en la pantalla. Ya existen el formulario de encantamientos y el endpoint de consulta. Hay 118 pruebas de backend y 16 de interfaz superadas con servicios simulados, una comprobación real del cliente de IA con un libro y un recorrido completo desde el navegador confirmado por el usuario. Los resultados y el alcance de cada prueba están en [pruebas-app2.md](../../../docs/pruebas-app2.md).

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

Las pruebas de interfaz y la compilación se ejecutan con:

```powershell
npm test
npm run build
```

Las pruebas de interfaz simulan Clerk y la red, sin iniciar sesiones ni consultar a IA. Para ejecutar toda la batería de pytest también se necesita Node, porque una prueba compara las opciones de JavaScript con las de Python.

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

Desde `app2/`, copiar `.env.example` como `.env` y completar la clave pública de Clerk. El backend utiliza su archivo `backend/.env`, con las mismas credenciales de la ejecución local. Compose sustituye sus orígenes de desarrollo por `DOCKER_ALLOWED_ORIGINS`.

Para local, mantener `SITE_ADDRESS=:80`, `HOST_BIND=127.0.0.1` y `HTTP_PORT=8080`. El frontend se compila con `VITE_API_URL` vacío, de modo que las peticiones usen el mismo origen. Los archivos `.env` quedan fuera de Git y de las imágenes.

```powershell
docker compose up --build -d
docker compose ps
```

Abrir `http://localhost:8080`. Caddy sirve la web y dirige `/api/*` al backend conservando la ruta. El backend no publica su puerto en Windows.

En EC2 se utiliza `compose.ec2.yaml` y `Dockerfile.ec2`: un contenedor con FastAPI/Uvicorn sirve la API y el frontend compilado directamente por HTTPS en 443. Certbot, instalado en Ubuntu, solicita y renueva el certificado de la IP. El puerto 80 permite su validación; SSH sigue limitado a las IP autorizadas. No se usa Caddy en EC2.

Los secretos del backend se inyectarán al ejecutar. La compilación del frontend solo recibirá las variables públicas. Los archivos locales y las dependencias de desarrollo quedarán fuera de las imágenes.

En EC2 se ha comprobado el 29/10/2026 el arranque automático con `app2/deploy/met-app2.service`, `app2/deploy/update-on-boot.sh` y `app2/deploy/certificate-ip.sh`. Al encender Ubuntu se descarga `main`, se detecta la IP actual, se prepara su certificado, se construye y se arranca App2. Las variables y los certificados se conservan fuera del repositorio, en `/home/ubuntu/.config/met-app2`. Para actualizar con la instancia encendida: `sudo systemctl restart met-app2.service`.

El acceso público comprobado es `https://54.87.43.68`. Si cambia la IP al parar y encender la instancia, cambia la dirección de acceso. No se necesita un túnel SSH. Las instrucciones completas y las pruebas están en [despliegue-app2.md](../../../docs/despliegue-app2.md).

Al terminar se documentará la retirada de los recursos utilizados, incluidos los que puedan seguir generando costes.

## Referencias

La forma exacta de los datos está en [contracts/http.md](contracts/http.md). Sus reglas y estados están en [data-model.md](data-model.md). Las decisiones técnicas y las fuentes están en [research.md](research.md).
