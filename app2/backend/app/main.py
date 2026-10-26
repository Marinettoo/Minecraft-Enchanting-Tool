"""Punto de entrada del backend."""

from contextlib import asynccontextmanager
import json

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from pydantic import ValidationError

from app.ai_client import AIError, get_ai_client
from app.auth import require_session
from app.config import Settings, load_settings
from app.plan_validator import validate_plan
from app.schemas import ProcessRequest


def create_app(settings: Settings | None = None) -> FastAPI:
    origins = list(settings.allowed_origins) if settings is not None else []

    @asynccontextmanager
    async def lifespan(application):
        if application.state.settings is None:
            application.state.settings = load_settings()
        # CORS conserva esta lista; se completa antes de aceptar peticiones.
        origins[:] = application.state.settings.allowed_origins
        yield

    application = FastAPI(
        title="MeT App 2", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan
    )
    application.state.settings = settings

    @application.post("/api/procesar")
    async def process(request: Request, session=Depends(require_session), ai_client=Depends(get_ai_client)):
        try:
            selection = ProcessRequest.model_validate(await request.json())
        except (ValidationError, json.JSONDecodeError, UnicodeDecodeError):
            raise RequestValidationError([]) from None
        raw = await ai_client(selection)
        try:
            return validate_plan(raw, selection).model_dump()
        except (ValidationError, ValueError, TypeError, KeyError):
            raise AIError("RESPUESTA_INVALIDA", 502) from None

    @application.exception_handler(AIError)
    async def ai_error(request, exc):
        messages = {
            "IA_NO_DISPONIBLE": "No se ha podido consultar a la IA. Inténtalo más tarde.",
            "RESPUESTA_INVALIDA": "La IA ha devuelto una propuesta que no se puede utilizar.",
            "IA_TIMEOUT": "La IA ha tardado demasiado. Puedes volver a intentarlo.",
        }
        return JSONResponse(status_code=exc.status, content={
            "error": {"codigo": exc.code, "mensaje": messages[exc.code]}
        })

    @application.exception_handler(HTTPException)
    async def http_error(request, exc):
        if exc.status_code == 401:
            return JSONResponse(status_code=401, headers={"WWW-Authenticate": "Bearer"}, content={
                "error": {"codigo": "NO_AUTORIZADO", "mensaje": "Vuelve a iniciar sesión para realizar la consulta."}
            })
        return JSONResponse(status_code=exc.status_code, content={
            "error": {"codigo": "PETICION_NO_DISPONIBLE", "mensaje": "No se puede atender esta petición."}
        })

    @application.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(status_code=422, content={
            "error": {"codigo": "VALIDACION", "mensaje": "Revisa el objeto, los encantamientos y sus niveles."}
        })

    application.add_middleware(
        CORSMiddleware, allow_origins=origins,
        allow_methods=["POST"], allow_headers=["Authorization", "Content-Type"],
    )
    return application


app = create_app()
