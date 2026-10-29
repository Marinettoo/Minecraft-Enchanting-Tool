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

### Instancia y acceso comprobados el 29/10/2026

Se utiliza la instancia `met-app2` creada por Hugo en AWS Academy Learner Lab: región Norte de Virginia (`us-east-1`) por indicación del profesor, Ubuntu 24.04.5 LTS x86_64, `t2.small` y disco de 16 GiB gp3. El panel del laboratorio mostraba inicialmente 50 dólares de presupuesto y 0 consumidos; no se presenta esa cifra como saldo actual. La creación y el acceso inicial están en [creacion-instancia-aws.md](creacion-instancia-aws.md).

El grupo `met-app2-sg` permite SSH desde la IP autorizada del equipo. Se ha conectado usando la clave local y la huella previamente comprobada. La IPv4 pública había cambiado tras parar y encender EC2. La clave privada permanece en Windows; no se ha copiado al servidor.

### Instalación y arranque

Se ha instalado Docker desde su repositorio oficial para Ubuntu, siguiendo G17 del profesor. Versiones comprobadas: motor 29.9.2 y Compose 5.6.1. La prueba `hello-world` funciona y `systemctl enable --now docker` deja el motor iniciado y habilitado al arrancar Ubuntu.

Se ha clonado la rama `main` de `https://github.com/Marinettoo/Minecraft-Enchanting-Tool.git` en `/home/ubuntu/practicas-aws/Minecraft-Enchanting-Tool`. La base descargada es `89719b6`. Sobre ella se han instalado los archivos de HTTPS de esta entrega, todavía sin commit durante la comprobación. El repositorio se ha descargado sin credenciales adicionales.

Las variables existentes del equipo se han transferido por SSH sin mostrar su contenido. En el servidor se guardan fuera del repositorio:

| Archivo | Uso |
| --- | --- |
| `/home/ubuntu/.config/met-app2/backend.env` | Configuración privada del backend. |
| `/home/ubuntu/.config/met-app2/compose.env` | Configuración pública de Compose y Clerk. |

El directorio tiene permisos `700` y los archivos `600`. Dentro de `app2` se han creado enlaces simbólicos `.env` y `backend/.env` hacia esos archivos; ambos nombres están ignorados por Git. Actualizar código no los sustituye.

Por indicación de Hugo se utiliza HTTPS directamente sobre la IP, sin Caddy ni un dominio. `Dockerfile.ec2` compila Vue y prepara una imagen con FastAPI/Uvicorn, que sirve los archivos estáticos y la API. `compose.ec2.yaml` publica únicamente 443 hacia el puerto 8443 del contenedor. No se publica el puerto 8000. Docker local conserva sus dos contenedores originales.

Certbot 5.8.0 se ha instalado mediante su paquete snap oficial. Ha obtenido un certificado público de Let’s Encrypt para `54.87.43.68`, con el perfil `shortlived`. El certificado comprobado es válido hasta el 05/11/2026. La renovación está programada con `snap.certbot.renew.timer`.

`certificate-ip.sh` consulta la IPv4 pública mediante IMDSv2. Si cambia, solicita un certificado para la nueva IP; si sigue siendo la misma, conserva o renueva el existente según su vigencia. El archivo `compose.env` mantiene la clave pública de Clerk y actualiza `DOCKER_ALLOWED_ORIGINS` al origen `https://IP_ACTUAL`.

Certbot guarda el original en `/etc/letsencrypt/live/met-app2-ip`. El contenedor recibe una copia técnica en `/home/ubuntu/.config/met-app2/tls`, montada en solo lectura. El directorio tiene permisos `750`, los archivos `640` y grupo `10001`, correspondiente al usuario sin privilegios del contenedor. No hay claves de certificados en las imágenes ni en Git.

### Actualización automática al encender

Los archivos [update-on-boot.sh](../app2/deploy/update-on-boot.sh), [certificate-ip.sh](../app2/deploy/certificate-ip.sh) y [met-app2.service](../app2/deploy/met-app2.service) recogen la configuración instalada. Para repetir su instalación, una vez descargada la versión con estos archivos y configuradas las variables y los enlaces anteriores:

```bash
cd /home/ubuntu/practicas-aws/Minecraft-Enchanting-Tool
sudo snap install --classic certbot
sudo install -m 0755 app2/deploy/certificate-ip.sh /usr/local/bin/met-app2-certificate
sudo install -m 0755 app2/deploy/update-on-boot.sh /usr/local/bin/met-app2-update
sudo install -m 0644 app2/deploy/met-app2.service /etc/systemd/system/met-app2.service
sudo install -d -m 0755 /etc/letsencrypt/renewal-hooks/deploy
printf '%s\n' '#!/usr/bin/env bash' 'exec /usr/local/bin/met-app2-certificate deploy' | sudo tee /etc/letsencrypt/renewal-hooks/deploy/met-app2 >/dev/null
sudo chmod 0755 /etc/letsencrypt/renewal-hooks/deploy/met-app2
touch /home/ubuntu/.config/met-app2/https-ip
sudo systemctl daemon-reload
sudo systemctl enable --now met-app2.service
```

El servicio espera a Docker y a la red. Descarga `main`, avanza solo si puede hacerlo sin mezclar cambios, prepara el certificado de la IP, valida Compose y construye la imagen antes de sustituir el contenedor. Comprueba después HTTP 200 en la web y HTTP 401 en la API sin sesión, con validación normal del certificado. La construcción se limita a una operación de Compose a la vez para reducir el consumo de memoria.

Se construye desde una copia temporal creada con `git archive`, sin copiar variables ni dependencias locales. Para esta primera instalación se han guardado cuatro archivos de apoyo en `~/.config/met-app2/bootstrap`, porque Hugo hace los commits. Una vez presentes en GitHub, se utilizan los archivos de Git; el apoyo solo se aplica a archivos que todavía no estén en la versión descargada. La copia temporal se elimina al terminar.

Si falla la descarga o la construcción, intenta mantener o arrancar los contenedores existentes y registra el fallo. No borra cambios locales ni ejecuta `git reset --hard`. Esto no es un sistema de reversión completo ante cualquier error después de sustituir contenedores.

La actualización ocurre al encender Ubuntu, no inmediatamente después de cada push. Para actualizar sin reiniciar la máquina:

```bash
sudo systemctl restart met-app2.service
```

Para revisar su estado:

```bash
systemctl status met-app2.service --no-pager
sudo journalctl -u met-app2.service -n 30 --no-pager
```

La copia del script instalada en `/usr/local/bin` no se sustituye al descargar código. Si se modifican estos archivos de despliegue, hay que repetir su instalación y `daemon-reload`. Las imágenes y la aplicación sí se reconstruyen con el código descargado.

### Abrir la aplicación desde Windows

Abrir directamente en el navegador:

```text
https://54.87.43.68
```

No se necesita túnel SSH. Si la IP cambia al detener y encender EC2, cambia la URL. La IPv4 actual se consulta en EC2 y la detectada por el servicio queda en `~/.config/met-app2/public-ip`. Es necesario escribir `https://`: el puerto 80 queda libre para Certbot y no se ha añadido un servidor de redirecciones HTTP.

Para comprobar la renovación sin reemplazar el certificado válido por uno de pruebas:

```bash
sudo /snap/bin/certbot renew --cert-name met-app2-ip --dry-run --run-deploy-hooks --no-random-sleep-on-renew
```

La acción de despliegue copia el certificado y reinicia el contenedor para que Uvicorn lo vuelva a cargar. La renovación automática usa la programación de Certbot; no depende de que se reinicie EC2.

### Comprobaciones realizadas

- Se ha construido la imagen de EC2 y arrancado un único contenedor HTTPS. Los contenedores anteriores con Caddy están detenidos.
- Primero se obtuvo un certificado de pruebas y después uno público válido de Let’s Encrypt. El certificado identifica la IP, no un nombre DNS.
- Desde Windows, HTTPS devuelve HTTP 200 sin desactivar la validación TLS; la API sin sesión devuelve HTTP 401.
- Hugo ha confirmado que el acceso con Clerk y el cálculo funcionan en `https://54.87.43.68`, sin avisos de certificado.
- La prueba de renovación con `--dry-run --run-deploy-hooks` termina correctamente. El temporizador de renovación está habilitado y programado.
- Se ha reiniciado Ubuntu con la configuración HTTPS y comprobado un identificador de arranque distinto. Docker y `met-app2.service` han vuelto a arrancar automáticamente. HTTPS sigue respondiendo 200 y la API sin sesión 401.
- Las 121 pruebas del backend pasan. Las tres nuevas comprueban archivos estáticos, acceso protegido y rechazo de rutas que intentan salir de la carpeta pública.
- Antes de cambiar a HTTPS se probó un fallo simulado de descarga: se conservaron los contenedores anteriores. No se ha provocado una caída real de GitHub ni simulado un cambio de IP durante la prueba de reinicio HTTPS.

### Acceso público y cierre

Hugo ha abierto 80 y 443 en el grupo de seguridad, conservando SSH desde la IP autorizada. Certbot escucha temporalmente en 80 durante la validación; App2 escucha en 443. No se utiliza un dominio, DNS externo, Caddy ni Elastic IP. Se completan T034 y T035 con la elección de acceso por IP y las comprobaciones HTTPS anteriores.

Para terminar la sesión, detener EC2 desde la consola y finalizar el Learner Lab según G01. El servicio queda preparado para arrancar App2 en el siguiente encendido y obtener el certificado de la IP que corresponda. Detener no equivale a terminar la instancia y el disco puede seguir consumiendo presupuesto. La retirada definitiva se hará después de conservar la entrega y revisar los recursos propios.

Referencias de configuración: [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [runtime Python](https://vercel.com/docs/functions/runtimes/python), [duración de funciones](https://vercel.com/docs/functions/configuring-functions/duration), [Docker en Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [servicios systemd](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html), [Certbot para IP](https://letsencrypt.org/2026/03/11/shorter-certs-certbot) y [HTTPS de Uvicorn](https://uvicorn.dev/settings/#https).
