"""Entrada de EC2: API y frontend compilado en el mismo servidor HTTPS."""

import os
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from app.config import Settings
from app.main import create_app


def create_web_app(directory: Path | None = None, settings: Settings | None = None):
    application = create_app(settings)
    frontend = directory or Path(os.environ.get("FRONTEND_DIR", "/app/frontend"))
    # Se monta después de la API para conservar su autenticación y sus errores.
    application.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
    return application
