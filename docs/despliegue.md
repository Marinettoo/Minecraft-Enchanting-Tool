# Despliegue de la App 1

La App 1 está desplegada en Vercel como **dos proyectos** del mismo repositorio. Cada push a `main` despliega de nuevo en producción; las demás ramas generan despliegues de vista previa.

| Parte | Proyecto Vercel | Directorio raíz | Dirección |
| --- | --- | --- | --- |
| Frontend (Vue + Vite) | `met-frontend` | `app1/frontend` | https://met-frontend-zeta.vercel.app |
| Backend (FastAPI) | `minecraft-enchanting-tool` | `app1/backend` | https://minecraft-enchanting-tool.vercel.app |

## Variables de entorno

**Backend** (se configuran en Vercel, nunca en el repositorio):

| Variable | Valor |
| --- | --- |
| `OPENROUTER_API_KEY` | Clave de OpenRouter (secreta). |
| `OPENROUTER_MODEL` | `poolside/laguna-s-2.1:free` |
| `AI_MODE` | `openrouter` |
| `AI_TIMEOUT_SECONDS` | `60` |
| `ALLOWED_ORIGINS` | `https://met-frontend-zeta.vercel.app` (sin `/` final) |

**Frontend:**

| Variable | Valor |
| --- | --- |
| `VITE_API_BASE_URL` | `https://minecraft-enchanting-tool.vercel.app` (sin `/` final). Es pública. |

La clave de la IA solo existe en el backend. Las variables de Vercel solo se aplican a partir del siguiente despliegue: tras cambiar una hay que hacer *Redeploy*.

## Configuración del backend
- `app1/backend/vercel.json` fija la duración máxima de la función en 60 s, igual que el tiempo de espera a la IA.
- Vercel detecta FastAPI por `app` en `main.py` y las dependencias por `requirements.txt`.

## Cómo repetir el despliegue
1. En vercel.com/new, importar el repositorio y elegir **Import single project** en la fila de `backend` (FastAPI). Añadir las variables del backend y desplegar.
2. Repetir con `frontend` (Vite) y la variable `VITE_API_BASE_URL` con la dirección del backend.
3. Poner en `ALLOWED_ORIGINS` del backend la dirección del frontend y hacer *Redeploy*.

## Limitaciones
- El modelo de IA es gratuito y compartido: puede responder lento, devolver errores 429 o fallar. La app lo muestra como error controlado (`IA_NO_DISPONIBLE`, `IA_TIMEOUT` o `RESPUESTA_INVALIDA`).
- CORS no es autenticación: cualquiera puede llamar a la API directamente y gastar peticiones del modelo. Conviene vigilar el consumo en OpenRouter.
- Despliegue en AWS EC2 con Docker (carpeta `infra/`): pendiente.
