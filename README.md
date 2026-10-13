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

## Estado
App 1 terminada y desplegada en Vercel. Pendiente: App 2, ERS (`plantillaERS.md`), despliegue en AWS/Docker (`infra/`) y presentación.
