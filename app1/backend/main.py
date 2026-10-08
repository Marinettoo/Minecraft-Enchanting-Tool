"""Backend App 1: validar, consultar una IA y devolver el contrato público."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai_client import AIError, generate_plan
from config import Settings, load_settings
from schemas import ErrorResponse, ProcessRequest, ProcessResponse, validate_plan

MESSAGES = {
    "VALIDACION": "Revisa el objeto, los encantamientos, sus niveles y compatibilidad (entre 1 y 8, sin repetir).",
    "IA_NO_DISPONIBLE": "No se ha podido completar la petición. Inténtalo más tarde.",
    "RESPUESTA_INVALIDA": "La IA ha devuelto una respuesta que no se puede utilizar. Inténtalo de nuevo.",
    "IA_TIMEOUT": "La IA no ha respondido dentro del tiempo límite. Inténtalo más tarde.",
}


def error_response(code: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"codigo": code, "mensaje": MESSAGES[code]}})


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    application = FastAPI(title="MeT — Minecraft Enchanting Tool", version="1.0.0")
    application.add_middleware(CORSMiddleware, allow_origins=list(settings.origins),
                               allow_methods=["POST"], allow_headers=["Content-Type"])

    @application.exception_handler(RequestValidationError)
    async def invalid_request(_request: Request, _exc: RequestValidationError):
        return error_response("VALIDACION", 422)

    @application.exception_handler(AIError)
    async def provider_error(_request: Request, exc: AIError):
        return error_response(exc.code, exc.status)

    @application.post("/api/procesar", response_model=ProcessResponse, responses={
        code: {"model": ErrorResponse} for code in (422, 502, 504)
    })
    async def process(data: ProcessRequest):
        plan = await generate_plan(data, settings)
        try:
            return validate_plan(plan, data)
        except (ValueError, TypeError) as exc:
            raise AIError("RESPUESTA_INVALIDA", 502) from exc

    return application


app = create_app()
