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

## Docker y AWS

Se prepararán después de comprobar App 2 en Vercel, según el plan. Antes de crear recursos de AWS se concretarán cuenta, región, presupuesto y nombre público para HTTPS.

Referencias de configuración: [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [runtime Python](https://vercel.com/docs/functions/runtimes/python) y [duración de funciones](https://vercel.com/docs/functions/configuring-functions/duration).
