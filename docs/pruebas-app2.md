# Comprobaciones de App 2

## 26/10/2026. Acceso con Clerk

Se ha preparado la prueba del componente oficial de Clerk en la pantalla principal, con navegación por hash y textos en español. Las claves se leen de los archivos locales excluidos de Git.

Comprobaciones realizadas:

- La clave pública de verificación tiene formato RSA válido de 2048 bits.
- `npm run build` termina correctamente con `@clerk/vue` 2.5.14 y `@clerk/localizations` 4.24.1.
- En `http://127.0.0.1:5173/` se ve el formulario real de Clerk para MeT App2, con campo de correo y botón Continuar.

El usuario ha confirmado que el acceso por correo termina con «Has iniciado sesión» y que «Cerrar sesión» devuelve al formulario. Se completa T005 con esta comprobación manual. La prueba del navegador no consulta OpenRouter.

El usuario ha comprobado también el acceso con Google y ha mostrado el mensaje «Has iniciado sesión». Al principio, el acceso por correo rechazaba una cuenta nueva. Al revisar `@clerk/vue` 2.5.14 se identificó que su comprobación de `withSignUp` exige esa clave en las propiedades iniciales; la forma `with-sign-up` no activaba el flujo combinado. Se corrigió el enlace de la propiedad en `App.vue` antes de repetir la comprobación.

## 26/10/2026. Base del backend

Se han preparado configuración, verificación de sesión, datos del anexo A, tipos estrictos y errores comunes. La configuración real de Clerk se carga correctamente. La clave de OpenRouter se añadirá antes de conectar la consulta a IA.

Ejecución: `python -m pytest -q -p no:cacheprovider`, desde el entorno propio de `app2/backend`. Resultado: **53 pruebas superadas** en 0,47 segundos, con un aviso de compatibilidad de TestClient con HTTPX. `pip check` no detecta conflictos de dependencias.

Las pruebas usan claves RSA ficticias y servicios simulados. Verifican sesiones válidas y rechazadas, firma, emisor, caducidad, audiencia, origen, fallo del verificador y ausencia de llamadas al proveedor en los rechazos. Una ruta disponible solo dentro de las pruebas comprueba la dependencia de acceso; no se añade al backend público.

También se comprueban las opciones y niveles de los 58 objetos y 39 encantamientos contra la ERS, los límites de selección, tipos incorrectos, duplicados, incompatibilidades, CORS y errores sin datos privados. Los registros no guardan tokens, selecciones ni respuestas.

El endpoint funcional y la integración real del backend con el navegador se comprobarán en la historia 1. Estas pruebas no se presentan como una consulta real de App 2 a IA.

## 26/10/2026. Formulario y primera consulta

Se han creado el formulario, el cliente de la API, la presentación de pasos y el endpoint protegido `POST /api/procesar`. El navegador obtiene el token con Clerk y el backend autoriza antes de leer la selección. No se guardan resultados y el cierre de sesión cancela la espera local.

Comprobaciones realizadas:

- **63 pruebas superadas** en 0,59 segundos, con servicios simulados. Incluyen el endpoint con 1 y 8 libros, combinación previa entre libros, avisos de 39 y 40 niveles, rechazo de una suma incorrecta, llamada única y fallo de tiempo sin reintentos.
- Las dos capas coinciden en los 58 objetos, 39 encantamientos, nombres, niveles, tipos admitidos y 8 grupos de incompatibilidades.
- `npm run build` termina correctamente.
- El servidor local responde 401 con `NO_AUTORIZADO` a una petición sin token, incluso si el cuerpo no es JSON válido.
- Una prueba real independiente del cliente de App 2 con una espada de diamante y Filo V recibió una propuesta de un paso y superó el validador en 5,53 segundos. Se hizo una llamada a `poolside/laguna-s-2.1:free`. No demuestra que los costes sean exactos ni mínimos.

La clave existente de OpenRouter se ha configurado en el archivo local del backend de App 2, excluido de Git. La prueba real anterior se ejecutó desde el cliente del backend. Después, el usuario ha confirmado el recorrido completo desde el formulario y ha mostrado el resultado de Espada de diamante con Filo V: un paso de 5 niveles y un total de 5. Se completa T017.

## 26/10/2026. Rechazos, fallos e interfaz

Resultado: **118 pruebas de backend y 15 de interfaz superadas**. Se ejecutan con `python -m pytest -q -p no:cacheprovider` y `npm test`. Las pruebas de interfaz usan Vitest, Vue Test Utils y jsdom; Clerk y la red están simulados.

La batería de backend comprueba los errores 401, 422, 502 y 504, cero llamadas al proveedor cuando se rechaza el acceso o la selección, y una sola llamada intentada ante fallos del proveedor. Incluye entradas ilegibles, campos extra, tipos incorrectos, incompatibilidades, elementos inventados o reutilizados, pasos futuros y costes o sumas incorrectos. El límite total de 60 segundos se prueba adelantando el tiempo, sin esperar al proveedor real.

Las pruebas de interfaz comprueban mensajes de error, repetición manual, doble envío, fin de la espera, sustitución del resultado, ausencia de token, cierre de sesión con respuesta tardía y etiquetas HTML mostradas como texto. También verifican que cambiar el tipo de objeto limpia los encantamientos y que se desactivan los incompatibles.

Una prueba detectó que se admitía un bloque Markdown sin cierre. Ahora solo se retira un bloque exterior completo; los incompletos se rechazan con `RESPUESTA_INVALIDA`. Todas las pruebas anteriores siguen pasando.

Se ha adaptado la pantalla a la referencia de Minecraft proporcionada por el usuario, con libro de pergamino, fondo estrellado y la tipografía Monocraft conservando su licencia. Se ha comprobado visualmente en el navegador integrado a 1280 y 360 píxeles, sin desbordamiento horizontal. Las páginas se muestran juntas en ordenador y apiladas en móvil. Esta revisión no sustituye la comprobación posterior en Chrome y Edge de T028.

En la pantalla nueva se ha realizado una consulta real de Pico de hierro con Eficiencia V. Se observó la espera, el bloqueo de los controles y el resultado de un paso de 5 niveles y total de 5. No se incluyen tokens ni datos personales en estas evidencias.

## 26/10/2026. Revisión antes del despliegue

La comprobación final termina con **118 pruebas de backend y 16 de interfaz superadas**. La prueba añadida comprueba que, después de una consulta, volver a montar la pantalla deja el objeto y el resultado vacíos y no escribe la consulta mediante la API de almacenamiento del navegador. La compilación termina correctamente y `pip check` no detecta conflictos.

Se ha revisado el código propio: las selecciones y resultados solo se usan en memoria durante la consulta y su visualización. No hay bases de datos, escrituras de consultas en archivos ni uso de localStorage, sessionStorage o IndexedDB. El estado compartido del backend contiene configuración, no resultados. El único mensaje de registro propio del verificador es un código de rechazo sin token ni datos de la petición. El backend ya se ha reiniciado durante las comprobaciones anteriores; no tiene un mecanismo para recuperar consultas.

Se ha comparado la clave privada real de OpenRouter con el contenido de los archivos que Git incluiría y con los archivos compilados del frontend, sin mostrar su valor. No se ha encontrado en ninguno. Los archivos locales de configuración y las dependencias permanecen excluidos de Git.

Se completa T029. T028 sigue sin marcar porque aún falta la revisión específica en Chrome y Edge. La publicación en Vercel se realizará en otra sesión.

## 27/10/2026. Docker local

Las imágenes se han construido con Docker Desktop 4.97.0, motor Linux 29.9.2 y Compose 5.6.1. Se han validado Compose, Caddy, las variables del backend y sus dependencias dentro de los contenedores.

Hugo ha confirmado el acceso y una consulta real desde `http://localhost:8080`: Pico de hierro con Eficiencia V, Fortuna III e Irrompibilidad III, tres pasos y total estimado de 24 niveles. Tras reiniciar los contenedores ha confirmado otra consulta con Azada de piedra, Eficiencia V y Fortuna III: dos pasos y total estimado de 13 niveles.

La comprobación directa devuelve HTTP 200 para la web y HTTP 401 con `NO_AUTORIZADO` para una petición a `/api/procesar` sin sesión, a través del proxy. No se ha consultado al proveedor en esta comprobación de rechazo. Los contenedores siguen activos y el backend solo está disponible en la red interna.

Se completa T033. Las consultas y el reinicio se han comprobado manualmente con Hugo; los errores de entrada y del proveedor siguen respaldados por las pruebas simuladas anteriores. Las instrucciones están en [despliegue-app2.md](despliegue-app2.md).

## 29/10/2026. Primera comprobación de EC2 por túnel SSH

Versión desplegada: `89719b6`, desde `main`. Entorno: Ubuntu 24.04.5 LTS x86_64, `t2.small`, Docker 29.9.2 y Compose 5.6.1. Ambas imágenes se han construido en la instancia y la configuración privada se ha suministrado al ejecutar.

Se ha reiniciado Ubuntu y comprobado el cambio de identificador de arranque. Docker y el servicio `met-app2.service` han arrancado automáticamente. La web responde HTTP 200 y la API rechaza una petición sin sesión con HTTP 401. El backend no publica puertos del host y Caddy solo escucha a través de los puertos vinculados a loopback.

Hugo ha confirmado el acceso con Clerk y el resultado de una consulta real desde el túnel `http://localhost:18080`. No se ha registrado una combinación concreta ni su tiempo en esta confirmación.

Una comprobación adicional ha simulado un fallo de `git fetch` en el actualizador: se han mantenido los mismos contenedores y la web ha seguido respondiendo HTTP 200. La sustitución temporal solo afecta a esa prueba, no al repositorio ni al servicio instalado.

Esta primera comprobación por túnel no completa T035. La prueba pública HTTPS se recoge en el apartado siguiente.

## 29/10/2026. HTTPS directo sobre la IP, sin Caddy

Por indicación de Hugo se ha preparado `Dockerfile.ec2` y `compose.ec2.yaml`: una imagen compila Vue y sirve la web y la API con FastAPI/Uvicorn. La base es `89719b6` más los archivos HTTPS de esta entrega, instalados antes de que el equipo haga el commit. Los contenedores anteriores con Caddy se han detenido.

Certbot 5.8.0 ha obtenido primero un certificado de prueba y después uno público válido de Let’s Encrypt para `54.87.43.68`. Desde Windows, `https://54.87.43.68` devuelve HTTP 200 con validación normal del certificado. La API pública sin sesión devuelve HTTP 401. No se han usado excepciones TLS ni certificados autofirmados.

Hugo ha confirmado que el acceso con Clerk y el cálculo funcionan desde la URL HTTPS, sin túnel ni avisos de certificado. No se ha registrado el contenido de la consulta ni su duración.

La renovación simulada de Certbot con `--dry-run --run-deploy-hooks --no-random-sleep-on-renew` termina correctamente. Se ha comprobado que el temporizador de renovación está habilitado. La acción de renovación copia el certificado al directorio técnico y reinicia el contenedor para volver a cargarlo.

Después se ha reiniciado Ubuntu. Ha cambiado su identificador de arranque, `met-app2.service` ha finalizado correctamente y solo queda activo el contenedor HTTPS. La web vuelve a responder HTTP 200 y la API sin sesión HTTP 401. La IP se ha detectado mediante IMDSv2; en esta prueba de reinicio se ha conservado la misma IP, no se ha simulado una reasignación.

Las **121 pruebas de backend** pasan, incluidas tres pruebas nuevas que comprueban la publicación del frontend compilado, que la API sigue protegida y que no se pueden leer archivos fuera de la carpeta pública. La compilación del frontend también se ha completado dentro de la nueva imagen de EC2.

Se completan T034 y T035. El acceso es por IP con HTTPS, sin dominio externo. Las instrucciones y límites de la actualización están en [despliegue-app2.md](despliegue-app2.md).

