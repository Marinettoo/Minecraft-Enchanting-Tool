"""Una llamada a OpenRouter, sin historial, reintentos ni proveedores alternativos."""

import asyncio
import json
import logging
import re

import httpx

from config import Settings
from schemas import ProcessRequest

log = logging.getLogger("uvicorn.error")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
SYSTEM_PROMPT = """Propón el orden de combinaciones de yunque de menor coste para
Minecraft Java. Supón objeto nuevo sin encantamientos ni trabajos previos y un
libro nuevo por cada encantamiento al nivel solicitado. No renombres ni repares.
Solo combina objeto+libro o libro+libro. Considera penalizaciones por trabajos
previos y el límite de 40 niveles de supervivencia. No añadas encantamientos.
Cómo calcular el coste de CADA combinación en el yunque (Minecraft Java):
coste = penalización_izquierda + penalización_derecha + coste_encantamientos.
- Cada objeto o libro tiene un contador n de veces que ha pasado por el yunque
  (objeto y libros nuevos: n=0). Su penalización es 2^n - 1 (n=0 -> 0, n=1 -> 1,
  n=2 -> 3, n=3 -> 7, n=4 -> 15, n=5 -> 31).
- Al combinar, el resultado tiene n = max(n_izquierda, n_derecha) + 1.
- coste_encantamientos = suma de (nivel x multiplicador) de TODOS los
  encantamientos que lleva el elemento de la derecha (si es un libro o un libro
  ya combinado, se usa el multiplicador de libro). Los encantamientos que ya
  tiene el elemento de la izquierda no se cobran.
- Multiplicadores de libro: protección 1, caída de pluma 1, espinas 4, filo 1,
  castigo 1, perdición de los artrópodos 1, empuje 1, aspecto ígneo 2, botín 2,
  filo barredor 2, eficiencia 1, toque de seda 4, irrompibilidad 1, fortuna 2,
  poder 1, infinidad 4, reparación 2.
- Si una combinación cuesta 40 niveles o más, en supervivencia sale "Demasiado
  caro": evítala y, si es inevitable, avísalo en advertencias.
Estrategia: cada paso con el objeto aumenta su n y encarece todo lo posterior, así
que combina primero los libros entre sí formando un árbol equilibrado (libro+libro)
y aplica al objeto pocos libros ya combinados. Los encantamientos caros (nivel x
multiplicador alto) conviene incorporarlos en los últimos pasos, porque se
vuelven a cobrar cada vez que el libro que los contiene se combina de nuevo.
Ejemplo resuelto. Objeto: arco. libro_1 = Infinidad 1 (1x4 = 4), libro_2 =
Irrompibilidad 3 (3x1 = 3), libro_3 = Poder 1 (1x1 = 1).
Paso 1: objeto + libro_1 = 0 + 0 + 4 = 4 (el objeto pasa a n=1).
Paso 2: libro_2 + libro_3 = 0 + 0 + 1 = 1 (el libro combinado tiene n=1).
Paso 3: paso_1 + paso_2 = (2^1-1) + (2^1-1) + (3+1) = 1 + 1 + 4 = 6.
Total = 4 + 1 + 6 = 11. Aplicar los libros uno a uno al objeto saldría peor
(en este caso 12). Compara siempre varias formas de agrupar antes de elegir.
Calcula cada paso con estas fórmulas y comprueba que coste_total_niveles es la
suma exacta de los costes.
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
                    "reasoning": {"effort": "low"},
                    "provider": {"allow_fallbacks": False},
                })
                response.raise_for_status()
    except (TimeoutError, httpx.TimeoutException) as from_error:
        raise AIError("IA_TIMEOUT", 504) from from_error
    except httpx.HTTPError as exc:
        resp = getattr(exc, "response", None)
        log.warning("IA: fallo de OpenRouter (%s): %.400s", resp.status_code if resp is not None else type(exc).__name__,
                    resp.text if resp is not None else exc)
        raise AIError("IA_NO_DISPONIBLE", 502) from exc
    try:
        choice = response.json()["choices"][0]
        content = choice["message"].get("content") or ""
        if choice.get("finish_reason") != "stop":
            log.warning("IA: respuesta incompleta (finish_reason=%s): %.300s", choice.get("finish_reason"), content)
            raise ValueError("Respuesta incompleta")
        # Algunos modelos envuelven el JSON en un bloque ```json ... ```
        content = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", content)
        return json.loads(content)
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        log.warning("IA: respuesta no utilizable (%s): %.500s", exc, response.text)
        raise AIError("RESPUESTA_INVALIDA", 502) from exc
