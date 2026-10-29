# Decisiones técnicas de App 2

**Fecha**: 21/10/2026

## 1. Pantalla y estilos

**Decisión**: Vue 3 con JavaScript, Vite y Tailwind CSS 4. Usaremos el complemento `@tailwindcss/vite` y componentes pequeños, sin router.

**Motivo**: Es la tecnología elegida en la ERS y permite mantener todo el recorrido en una pantalla.

**Alternativa considerada**: Cambiar de framework o añadir rutas. No aporta nada al alcance acordado.

Fuentes: [Tailwind con Vite](https://tailwindcss.com/docs/installation/using-vite) y [requisitos de Vite](https://vite.dev/guide/).

## 2. Acceso con Clerk

**Decisión**: Usar `@clerk/vue` y su componente `SignIn` con navegación por hash y el flujo de acceso y registro integrado. Al tener sesión se mostrará el formulario y una acción de cierre. No añadiremos un perfil ni una pantalla de cuentas. El método de acceso se configurará y probará antes de implementar la integración; proponemos correo con código para mantenerlo sencillo.

El frontend obtendrá un token nuevo mediante `useAuth` al enviar, sin guardarlo manualmente. El backend usará `clerk-backend-api` con verificación local mediante la clave pública de la instancia (`CLERK_JWT_KEY`). Se limitarán los tipos aceptados a `session_token` y los orígenes autorizados con `authorized_parties`.

Después de verificar la firma y los tiempos del token, se comprobará que el emisor coincide con `CLERK_ISSUER`. Si se configura una audiencia, también debe coincidir. No se confiará en datos simplemente decodificados. Si falta la clave, la configuración es incorrecta o falla la verificación, no se procesa la consulta. Una rotación de la clave requiere actualizar la configuración y volver a comprobar el acceso.

**Motivo**: Cumple el acceso externo y evita crear cuentas, contraseñas o comprobaciones criptográficas propias.

**Alternativa considerada**: Consultar los usuarios de Clerk en cada petición o usar un formulario propio. No necesitamos datos del perfil para autorizar esta función.

Fuentes: [Vue](https://clerk.com/docs/vue/getting-started/quickstart), [SignIn](https://clerk.com/docs/vue/reference/components/authentication/sign-in), [useAuth](https://clerk.com/docs/vue/reference/composables/use-auth) y [verificación en Python y FastAPI](https://clerk.com/articles/how-to-add-authentication-to-a-python-backend-2). De la documentación de Python solo necesitamos la autenticación; sus ejemplos de roles, perfiles y bases de datos quedan fuera de nuestro proyecto.

## 3. OpenRouter y formato

**Decisión**: Usar HTTPX directamente con `poolside/laguna-s-2.1:free`. Petición sin streaming, temperatura 0, razonamiento desactivado y `provider.allow_fallbacks=false`. No habrá bucles de reintento ni lista de modelos alternativos.

Pediremos JSON con las referencias `objeto`, `libro_N` y `paso_N`. La salida se validará en backend. Las instrucciones se escribirán para App 2 a partir de las reglas y el contrato; no copiaremos la implementación de App 1. El límite total al proveedor será de 60 segundos.

**Motivo**: Mantiene el modelo elegido y la única llamada de la práctica. Una respuesta válida en una prueba no garantiza que las siguientes también lo sean.

**Alternativa considerada**: Depender de salida estructurada obligatoria del proveedor, añadir un SDK de IA o repetir la consulta si el formato falla. La validación propia es necesaria en cualquier caso y los reintentos contradicen la ERS.

Fuentes: [modelo elegido](https://openrouter.ai/poolside/laguna-s-2.1%3Afree/) y [selección de proveedor](https://openrouter.ai/docs/guides/routing/provider-selection).

### Comprobación real del modelo

Se hicieron dos consultas reales independientes con instrucciones nuevas y datos ficticios, sin reintentos automáticos. No se guardaron claves, entradas completas ni respuestas completas. Los tiempos son los observados en esta comprobación, no una medida de rendimiento de App 2.

| Consulta | Resultado observado |
| --- | --- |
| Instrucción breve sin ejemplo completo | HTTP 200 en 3,59 segundos. Modelo devuelto: `poolside/laguna-s-2.1:free`. Terminación normal, pero no superó la comprobación mínima del formato. |
| Instrucción con ejemplo explícito de estructura para un objeto y un libro | HTTP 200 en 5,45 segundos. Mismo modelo, terminación normal y JSON legible sin bloque Markdown. Un paso, referencias correctas, coste entero no negativo y total coincidente. |

La segunda consulta confirma acceso y formato básico. No prueba la futura integración de App 2, las selecciones complejas ni la exactitud del coste en Minecraft. Los casos de 1 a 8 libros y las respuestas inválidas siguen formando parte de las pruebas de implementación.

Un intento inicial desde el entorno restringido no llegó a obtener respuesta HTTP. Una comprobación propuesta con el prompt de App 1 fue rechazada antes de ejecutarse; ese contenido no se envió. Las dos respuestas HTTP de la tabla corresponden solo a las instrucciones nuevas.

## 4. Backend y datos temporales

**Decisión**: Python 3.12, FastAPI, Pydantic 2, HTTPX, Uvicorn y carga local de variables con `python-dotenv`. Validación estricta y errores con una forma única. Las reglas y las referencias de pasos se comprobarán por separado del cliente de IA.

**Motivo**: Permite simular las dependencias y comprobar el recorrido completo con pytest.

**Alternativa considerada**: Base de datos, historial o un servicio adicional para procesar resultados. Están fuera del alcance y no hacen falta.

La sesión técnica de Clerk es independiente de los datos de la consulta. No guardaremos entradas ni respuestas en archivos, navegador o registros.

Fuentes: [validación estricta de Pydantic](https://docs.pydantic.dev/latest/concepts/strict_mode/) y [límite de tiempo de asyncio](https://docs.python.org/3.12/library/asyncio-task.html#asyncio.timeout).

## 5. Vercel, Docker y EC2

**Decisión**: Dos proyectos en Vercel, uno por capa. Configuraremos la función de FastAPI con 90 segundos de duración para dejar margen al límite propio de 60 segundos. Este valor es una decisión de despliegue, no un cambio del timeout del proveedor. La cuenta y la configuración efectiva se verificarán antes de publicar.

Para Docker local usaremos Uvicorn en el backend y Caddy para servir el frontend y dirigir `/api/*` al backend. El volumen de Caddy es técnico, no almacena consultas.

**Decisión de despliegue revisada con Hugo el 29/10/2026:** en EC2 se prescinde de Caddy y de un dominio. Se usa un certificado de IP de Let’s Encrypt obtenido con Certbot 5.8.0. Uvicorn sirve directamente HTTPS y FastAPI publica el frontend compilado después de registrar las rutas de la API. Una imagen multietapa reúne los archivos de ambas capas en el contenedor de EC2. Esto conserva la pantalla, la autenticación y el contrato.

Let’s Encrypt admite certificados públicos de IP con el perfil `shortlived`, de unos seis días. Se ha configurado la renovación de Certbot y una acción que recarga el contenedor después de copiar el certificado renovado. Si cambia la IP al encender, se detecta por IMDSv2 y se solicita el certificado correspondiente. La URL cambia con la IP; no se utiliza Elastic IP ni DNS externo.

Fuentes de esta decisión: [certificados de IP con Certbot](https://letsencrypt.org/2026/03/11/shorter-certs-certbot), [archivos estáticos en FastAPI](https://fastapi.tiangolo.com/tutorial/static-files/) y [HTTPS de Uvicorn](https://uvicorn.dev/settings/#https).

**Motivo**: Reduce la infraestructura a las dos capas necesarias y permite repetir la instalación.

**Alternativas consideradas**: un dominio con Caddy, DNS dinámico y un nombre que incorpore la IP. Se elige IP con Certbot porque Hugo ha pedido evitar Caddy y los servicios externos de nombres. Se necesita mantener la renovación automática y comprobar el certificado para la IP actual.

Fuentes: [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [duración de funciones](https://vercel.com/docs/functions/configuring-functions/duration), [proxy de Caddy](https://caddyserver.com/docs/quick-starts/reverse-proxy), [HTTPS de Caddy](https://caddyserver.com/docs/automatic-https), [reinicio de Docker](https://docs.docker.com/engine/containers/start-containers-automatically/) y [reglas de EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules-reference.html).

## 6. Alcance de esta fase

El diseño está definido. Aquí no se ha instalado App 2, probado una cuenta de Clerk ni publicado ningún servicio. Las versiones exactas se fijarán al instalar las dependencias. Las cuentas, el nombre público, la región y el presupuesto se concretarán antes de crear recursos, como establece la ERS.

Se ha utilizado Codex para preparar estos documentos y contrastar las decisiones con las fuentes oficiales. La petición fue elaborar el plan desde la especificación aprobada, con lenguaje sencillo y sin avanzar a tareas ni implementación. Los resultados observados del proveedor se han separado de las pruebas que corresponderán a la aplicación.
