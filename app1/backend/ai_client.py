"""Una llamada a OpenRouter, sin historial, reintentos ni proveedores alternativos."""

import asyncio
import json

import httpx

from config import Settings
from schemas import ProcessRequest

API_URL = "https://openrouter.ai/api/v1/chat/completions"
SYSTEM_PROMPT = """Propón el orden de combinaciones de yunque de menor coste para
Minecraft Java. Supón objeto nuevo sin encantamientos ni trabajos previos y un
libro nuevo por cada encantamiento al nivel solicitado. No renombres ni repares.
Solo combina objeto+libro o libro+libro. Considera penalizaciones por trabajos
previos y el límite de 40 niveles de supervivencia. No añadas encantamientos.
Devuelve exclusivamente JSON, sin Markdown, con esta forma:
{"resultado":{"pasos":[{"orden":1,"izquierda":"objeto","derecha":"libro_1",
"coste_niveles":2}],"coste_total_niveles":2,"advertencias":[]}}.
Referencias: objeto es el objeto inicial; libro_1, libro_2, etc. corresponden al
orden de encantamientos de la entrada; paso_1, paso_2, etc. son resultados de
pasos anteriores. Cada recurso se consume una sola vez. El objeto o el resultado
que lo contiene siempre va a la izquierda. Incluye exactamente tantos pasos
como libros; el resultado final debe contener el objeto y todos los libros.
Orden consecutivo desde 1, costes enteros no negativos, total igual a su suma.
Advertencias breves en español. No uses herramientas ni solicites más datos."""


class AIError(Exception):
    def __init__(self, code: str, status: int):
        self.code, self.status = code, status
        super().__init__(code)


def mock_plan(request: ProcessRequest) -> dict:
    """Datos ficticios para integrar la interfaz, no un optimizador."""
    return {"resultado": {
        "pasos": [{"orden": i, "izquierda": "objeto" if i == 1 else f"paso_{i - 1}",
                   "derecha": f"libro_{i}", "coste_niveles": 1}
                  for i in range(1, len(request.encantamientos) + 1)],
        "coste_total_niveles": len(request.encantamientos),
        "advertencias": ["MODO SIMULADO: costes ficticios; no se ha consultado ninguna IA."],
    }}


async def generate_plan(request: ProcessRequest, settings: Settings) -> object:
    if settings.mode == "mock":
        return mock_plan(request)
    if (not settings.api_key or settings.api_key == "pon_aqui_tu_clave"
            or not settings.model or settings.model == "nombre-del-modelo-gratuito"):
        raise AIError("IA_NO_DISPONIBLE", 502)
    try:
        # El deadline limita la operación completa, además del timeout de HTTPX.
        async with asyncio.timeout(settings.timeout):
            async with httpx.AsyncClient(timeout=settings.timeout, follow_redirects=False) as client:
                response = await client.post(API_URL, headers={"Authorization": f"Bearer {settings.api_key}"}, json={
                    "model": settings.model,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                 {"role": "user", "content": request.model_dump_json()}],
                    "stream": False,
                    "max_tokens": 2500,
                    "provider": {"allow_fallbacks": False},
                })
                response.raise_for_status()
    except (TimeoutError, httpx.TimeoutException) as from_error:
        raise AIError("IA_TIMEOUT", 504) from from_error
    except httpx.HTTPError as exc:
        raise AIError("IA_NO_DISPONIBLE", 502) from exc
    try:
        choice = response.json()["choices"][0]
        if choice.get("finish_reason") != "stop":
            raise ValueError("Respuesta incompleta")
        return json.loads(choice["message"]["content"])
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise AIError("RESPUESTA_INVALIDA", 502) from exc
