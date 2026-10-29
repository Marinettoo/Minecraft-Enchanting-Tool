# MeT · Minecraft Enchanting Tool

Mini aplicación web que, dado un objeto de Minecraft y los encantamientos deseados, devuelve el orden de combinación en el yunque que gasta menos niveles.

Proyecto de la práctica PR01-UD1 (curso de especialización en Aprendizaje automático, módulo de Desarrollo de componentes software).

## Integrantes
- Jesús Pérez Marinetto (GitHub: Marinettoo): frontend.
- Hugo Cáceres (GitHub: HugoCaceres22): backend.

## Aplicación publicada
- Web: https://met-frontend-zeta.vercel.app
- API: https://minecraft-enchanting-tool.vercel.app (ruta `POST /api/procesar`)

Detalles en [`docs/despliegue.md`](docs/despliegue.md).

## Tecnologías
- Frontend: Vue 3 (`<script setup>`), Vite, Tailwind CSS 4, tipografía Monocraft (licencia OFL).
- Backend: FastAPI, pydantic, httpx.
- IA: OpenRouter con el modelo gratuito `poolside/laguna-s-2.1:free`. El orden del yunque lo calcula solo la IA.
- Despliegue: Vercel (dos proyectos, frontend y backend).

## Estructura
- `app1/`: aplicación 1 (FastAPI + Vue/React + Tailwind), construida a mano.
- `app2/`: aplicación 2, creada desde cero con GitHub Spec Kit y Clerk.
- `docs/`: documentación del proyecto:
  - [`contrato-api.md`](docs/contrato-api.md): contrato entre frontend y backend.
  - [`despliegue.md`](docs/despliegue.md): cómo está desplegada la App 1.
  - [`uso-ia.md`](docs/uso-ia.md): uso de la IA en la app y en el desarrollo.
  - [`pruebas.md`](docs/pruebas.md): pruebas automáticas y manuales.
- `infra/`: Docker y despliegue en AWS EC2.
- `presentacion/`: PowerPoint de la defensa.

## Cómo ejecutar App 1

Hacen falta dos terminales. Requisitos: Python 3.12 o 3.13 (el backend no funciona con 3.9) y Node 20+.

**Backend** (desde `app1/backend`):

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # en Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cp .env.example .env               # edita .env: ver abajo
uvicorn main:app --reload          # http://localhost:8000/docs
```

En `.env`: `AI_MODE=mock` usa datos ficticios; para IA real pon `AI_MODE=openrouter`,
tu `OPENROUTER_API_KEY` y `OPENROUTER_MODEL` (id exacto de un modelo gratuito de OpenRouter).
El `.env` no se sube a Git.

**Frontend** (desde `app1/frontend`):

```bash
npm install
npm run dev                        # http://localhost:5173
```

## Cómo ejecutar App 2

App 2 incorpora Clerk y tiene su propio código en `app2/`. La configuración de las variables, las pruebas y los pasos de instalación están en [la guía de App 2](app2/specs/001-orden-encantamientos/quickstart.md).

Con Docker Desktop abierto y los archivos de variables configurados, desde `app2/`:

```bash
docker compose up --build -d
```

La versión local se abre en `http://localhost:8080`. Si las imágenes ya están construidas y no hay cambios, basta con `docker compose up -d`.

El despliegue de EC2 comprobado el 29/10/2026 está en [https://54.87.43.68](https://54.87.43.68). Usa FastAPI/Uvicorn con un certificado de IP de Let’s Encrypt gestionado por Certbot. La dirección cambia si AWS asigna otra IP al encender la instancia. El arranque automático, la renovación y el cierre se explican en [despliegue-app2.md](docs/despliegue-app2.md).

La creación de la instancia se recoge en [Markdown](docs/creacion-instancia-aws.md) y [PDF](docs/creacion-instancia-aws.pdf).

## Estado

App 1 está terminada y desplegada en Vercel. App 2 funciona con Clerk, Docker local y EC2 con HTTPS. El equipo se encarga de su publicación en Vercel. Las comprobaciones específicas de Chrome y Edge, la documentación final, la comparativa y la presentación se completan según la [lista de tareas](app2/specs/001-orden-encantamientos/tasks.md).
