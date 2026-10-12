# MeT · Minecraft Enchanting Tool

Mini aplicación web que, dado un objeto de Minecraft y los encantamientos deseados, devuelve el orden de combinación en el yunque que gasta menos niveles.

Proyecto de la práctica PR01-UD1 (curso de especialización en Aprendizaje automático, módulo de Desarrollo de componentes software).

## Integrantes
- Jesús Pérez Marinetto
- (compañero/a)

## Estructura
- `app1/`: aplicación 1 (FastAPI + Vue/React + Tailwind), construida a mano.
- `app2/`: aplicación 2, creada desde cero con GitHub Spec Kit y Clerk.
- `docs/`: ERS, contrato de la API, pruebas, comparativa, despliegues y uso de IA.
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
Hito H0 (inicio). Pendiente: versiones exactas y URLs de despliegue.
