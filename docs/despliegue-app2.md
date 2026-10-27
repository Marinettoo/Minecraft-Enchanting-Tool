# Despliegue de App 2

## Preparación comprobada el 26/10/2026

Se ha preparado la configuración local para publicar las dos capas en Vercel. No se han creado proyectos ni realizado despliegues.

| Parte | Carpeta | Configuración |
| --- | --- | --- |
| Backend | `app2/backend` | `app/main.py`, Python 3.12 y función con duración de 90 segundos. La consulta a IA mantiene su límite de 60 segundos. |
| Frontend | `app2/frontend` | Vite, instalación con `npm ci`, compilación con `npm run build` y salida en `dist`. |

Cada carpeta tiene su propio `vercel.json` y `.vercelignore`. Los archivos `.env`, entornos locales, pruebas y dependencias instaladas no se envían. Las variables se configuran en el proyecto correspondiente de Vercel.

La CLI comprobada es Vercel 65.3.1, ejecutada con Node 24.21.0. `vercel whoami` indica que no hay sesión iniciada en esta CLI.

Comprobaciones locales:

- 118 pruebas de backend superadas y dependencias sin conflictos.
- 16 pruebas de interfaz superadas y compilación correcta.
- La clave privada de OpenRouter no aparece en los archivos que Git incluiría ni en los archivos compilados del frontend.
- Los archivos locales de configuración, `.venv`, `node_modules` y `dist` están excluidos de Git.
- La configuración JSON de Vercel tiene la entrada, la duración y la carpeta de salida previstas.

La revisión del diseño a 360 y 1280 píxeles se ha realizado en el navegador integrado. La comprobación específica en Chrome y Edge de T028 se realizará por separado.

## Orden para publicar

1. Registrar en Git la implementación y la configuración que se van a publicar. El commit lo hace el equipo.
2. Iniciar sesión en la CLI:

   ```powershell
   npx --yes vercel@65.3.1 login
   ```

3. Crear o vincular un proyecto desde `app2/backend` y otro desde `app2/frontend` con `npx --yes vercel@65.3.1 link`. Confirmar cuenta, plan y nombres de los proyectos antes de continuar.
4. Confirmar las direcciones públicas de ambos proyectos. Configurar en el backend las variables de su `.env.example`, con los valores privados proporcionados fuera del repositorio. `ALLOWED_ORIGINS` y `CLERK_AUTHORIZED_PARTIES` deben incluir la URL exacta del frontend, sin comodines. Comprobar que la cuenta admite los 90 segundos de duración.
5. Publicar el backend desde su carpeta con `npx --yes vercel@65.3.1 --prod` y registrar su URL real.
6. Configurar en el frontend `VITE_API_URL` con la URL HTTPS del backend y `VITE_CLERK_PUBLISHABLE_KEY` con la clave pública de la misma instancia de Clerk. Publicarlo desde su carpeta con `npx --yes vercel@65.3.1 --prod`.
7. Comprobar el acceso, el cierre y una consulta válida desde la URL pública. Verificar también el rechazo 401 de una petición directa sin sesión y el error 422 de una entrada incorrecta con sesión válida.
8. Registrar URLs, fecha, versión de Git y resultados reales. Solo entonces se completa T030 y se actualizan los enlaces del README.

La demo local utiliza una instancia Development de Clerk. Al preparar Vercel se comprobará su funcionamiento en el dominio público y se mantendrán coordinadas las claves y el emisor. No se crea una instancia de producción ni se mezclan sus claves con las de desarrollo como parte de esta preparación.

## Docker local

El 27/10/2026 se adelanta Docker por indicación de Hugo mientras el propietario del repositorio prepara la conexión con Vercel. La publicación y sus comprobaciones siguen formando parte de la entrega.

Docker Desktop 4.97.0 utiliza el motor Linux 29.9.2 y Compose 5.6.1.

| Archivo | Para qué sirve |
| --- | --- |
| `app2/backend/Dockerfile` | Instala las dependencias de producción y arranca Uvicorn como usuario sin permisos de administrador. |
| `app2/frontend/Dockerfile` | Compila Vue con Node 24 y copia la web compilada a Caddy. |
| `.dockerignore` de cada carpeta | Excluye configuración local, claves, pruebas y dependencias instaladas. |
| `app2/frontend/Caddyfile` | Sirve la web y envía `/api/*` al backend sin quitar el prefijo. |
| `app2/compose.yaml` | Une los dos servicios, configura la red interna y aplica `restart: unless-stopped`. |
| `app2/.env.example` | Describe la configuración pública de Docker local. |

### Configuración

Desde `app2/`, copiar `.env.example` como `.env` y completar `VITE_CLERK_PUBLISHABLE_KEY` con la misma clave pública del frontend local. En el equipo de Hugo se ha preparado este archivo a partir de la configuración existente.

Las credenciales de Clerk y OpenRouter se leen de `backend/.env` al arrancar el backend. No se copian a las imágenes ni se pasan como argumentos de compilación. Compose sustituye `ALLOWED_ORIGINS` y `CLERK_AUTHORIZED_PARTIES` por los orígenes locales del puerto 8080.

El frontend se compila con la clave pública de Clerk y `VITE_API_URL` vacío. No necesita conocer la dirección interna del backend. Si cambia la clave pública hay que volver a construir su imagen.

### Arrancar y parar

Desde `app2/`:

```powershell
docker compose up --build -d
docker compose ps
```

Abrir `http://localhost:8080`. Solo Caddy publica puertos, limitados al propio ordenador con `HOST_BIND=127.0.0.1`. El backend se comunica por la red interna de Compose.

Para parar y volver a arrancar conservando las imágenes:

```powershell
docker compose stop
docker compose start
```

Para retirar los contenedores y la red de esta aplicación:

```powershell
docker compose down
```

El único volumen propio es `caddy_data`, destinado a los certificados HTTPS cuando se configure un dominio. `/config` usa memoria temporal y se desactiva el guardado automático de configuración de Caddy. No se guardan consultas ni resultados.

Comprobaciones del 27/10/2026:

- `docker compose config --quiet` acepta la configuración.
- Las dos imágenes se construyen correctamente; el frontend se compila dentro de Linux con sus dependencias fijadas.
- `caddy validate` acepta el archivo de configuración. En local se usa HTTP de forma intencionada.
- Un contenedor temporal de backend carga las credenciales y los orígenes del puerto 8080 correctamente. No tiene `/app/.env` y se ejecuta sin ser root.
- `pip check` no encuentra conflictos dentro de la imagen.
- Los contenedores de comprobación se han retirado automáticamente. No se han publicado puertos ni realizado consultas a IA en estas comprobaciones.

Hugo ha arrancado ambos servicios desde cero y confirmado el acceso y una consulta real en `http://localhost:8080`: Pico de hierro con Eficiencia V, Fortuna III e Irrompibilidad III, tres pasos y total estimado de 24 niveles.

Después de ejecutar `docker compose restart`, ha confirmado otra consulta: Azada de piedra con Eficiencia V y Fortuna III, dos pasos y total estimado de 13 niveles. Son resultados observados del proveedor, sin comprobar aquí sus costes frente al juego.

La comprobación directa posterior devuelve HTTP 200 en la web y HTTP 401 con `NO_AUTORIZADO` al enviar una selección sin sesión a través de Caddy. Ambos contenedores están activos y el backend no publica un puerto propio. Se completa T033 con estas comprobaciones y la confirmación manual de Hugo. Los casos de entrada incorrecta y fallos del proveedor mantienen las pruebas simuladas documentadas en `pruebas-app2.md`; no se han provocado fallos reales del proveedor en Docker.

## AWS

Antes de crear recursos se concretarán cuenta, región, presupuesto y nombre público para HTTPS. La misma configuración admite el dominio en `SITE_ADDRESS`, puertos 80 y 443, `HOST_BIND=0.0.0.0` y el origen HTTPS en `DOCKER_ALLOWED_ORIGINS`. Esto todavía no crea ni publica recursos de AWS.

Referencias de configuración: [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [runtime Python](https://vercel.com/docs/functions/runtimes/python) y [duración de funciones](https://vercel.com/docs/functions/configuring-functions/duration).
