import asyncio
import copy
import json
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

import ai_client
import main
from ai_client import AIError, mock_plan
from config import Settings
from schemas import ProcessRequest

VALID = {"objeto": "diamond_sword", "encantamientos": [
    {"nombre": "sharpness", "nivel": 5}, {"nombre": "mending", "nivel": 1},
]}


@pytest.fixture
def setup(monkeypatch):
    provider = AsyncMock(return_value=mock_plan(ProcessRequest.model_validate(VALID)))
    monkeypatch.setattr(main, "generate_plan", provider)
    with TestClient(main.create_app(Settings(mode="mock"))) as client:
        yield client, provider


def test_valid_request_calls_once_and_keeps_contract(setup):
    client, provider = setup
    response = client.post("/api/procesar", json=VALID)
    assert response.status_code == 200
    provider.assert_awaited_once()
    assert provider.call_args.args[0].model_dump() == VALID
    result = response.json()["resultado"]
    assert set(result) == {"pasos", "coste_total_niveles", "advertencias"}
    assert result["pasos"][0] == {"orden": 1, "izquierda": "diamond_sword", "derecha": "Libro de sharpness 5", "coste_niveles": 1}
    assert result["coste_total_niveles"] == 2


@pytest.mark.parametrize("payload", [
    {}, {"objeto": " "}, {**VALID, "objeto": "unknown"},
    {**VALID, "encantamientos": []}, {**VALID, "extra": "instrucciones"},
    {**VALID, "encantamientos": [{"nombre": "unknown", "nivel": 1}]},
    *[{**VALID, "encantamientos": [{"nombre": "sharpness", "nivel": level}]} for level in (0, 6, True, "5", 1.5)],
    {**VALID, "encantamientos": [{"nombre": "mending", "nivel": 2}]},
    {**VALID, "encantamientos": [{"nombre": "sharpness", "nivel": 1}] * 2},
    {**VALID, "encantamientos": [{"nombre": "sharpness", "nivel": 1}] * 9},
    {**VALID, "encantamientos": [{"nombre": "power", "nivel": 1}]},
    {**VALID, "encantamientos": [{"nombre": n, "nivel": 1} for n in ("sharpness", "smite")]},
    {"objeto": "diamond_pickaxe", "encantamientos": [{"nombre": n, "nivel": 1} for n in ("fortune", "silk_touch")]},
    {"objeto": "bow", "encantamientos": [{"nombre": n, "nivel": 1} for n in ("infinity", "mending")]},
])
def test_invalid_input_does_not_call_provider(setup, payload):
    client, provider = setup
    response = client.post("/api/procesar", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["codigo"] == "VALIDACION"
    provider.assert_not_awaited()


@pytest.mark.parametrize("body", ["", "{", "null", "[]"])
def test_invalid_json(setup, body):
    client, provider = setup
    response = client.post("/api/procesar", content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    provider.assert_not_awaited()


def test_limits_one_and_seven_enchantments(setup):
    # Con estas listas el máximo compatible real es 7 (espada), aunque el
    # contrato admite hasta 8. No inventamos un octavo para hacer pasar el test.
    client, provider = setup
    names = ["sharpness", "knockback", "fire_aspect", "looting", "sweeping_edge", "unbreaking", "mending"]
    for count in (1, 7):
        data = {"objeto": "diamond_sword", "encantamientos": [{"nombre": n, "nivel": 1} for n in names[:count]]}
        provider.return_value = mock_plan(ProcessRequest.model_validate(data))
        assert client.post("/api/procesar", json=data).status_code == 200


def test_eight_passes_length_but_fails_incompatibility(setup):
    client, provider = setup
    names = ["sharpness", "smite", "knockback", "fire_aspect", "looting", "sweeping_edge", "unbreaking", "mending"]
    data = {"objeto": "diamond_sword", "encantamientos": [{"nombre": n, "nivel": 1} for n in names]}
    assert client.post("/api/procesar", json=data).status_code == 422
    provider.assert_not_awaited()


@pytest.mark.parametrize("code,status", [("IA_NO_DISPONIBLE", 502), ("IA_TIMEOUT", 504)])
def test_controlled_provider_errors(setup, code, status):
    client, provider = setup
    provider.side_effect = AIError(code, status)
    response = client.post("/api/procesar", json=VALID)
    assert response.status_code == status
    assert set(response.json()) == {"error"}
    assert response.json()["error"]["codigo"] == code
    provider.assert_awaited_once()


@pytest.mark.parametrize("fault", ["empty", "sum", "reuse", "future", "order", "right_object", "missing", "bool_cost"])
def test_rejects_invalid_ai_plan(setup, fault):
    client, provider = setup
    plan = copy.deepcopy(provider.return_value)
    result = plan["resultado"]
    if fault == "empty":
        plan = {}
    elif fault == "sum":
        result["coste_total_niveles"] = 99
    elif fault == "reuse":
        result["pasos"][1]["derecha"] = "libro_1"
    elif fault == "future":
        result["pasos"][0]["izquierda"] = "paso_2"
    elif fault == "order":
        result["pasos"][0]["orden"] = 2
    elif fault == "right_object":
        result["pasos"][0].update(izquierda="libro_1", derecha="objeto")
    elif fault == "missing":
        result["pasos"].pop()
    elif fault == "bool_cost":
        result["pasos"][0]["coste_niveles"] = True
    provider.return_value = plan
    response = client.post("/api/procesar", json=VALID)
    assert response.status_code == 502
    assert response.json()["error"]["codigo"] == "RESPUESTA_INVALIDA"


def test_book_combinations_are_allowed(setup):
    client, provider = setup
    provider.return_value = {"resultado": {"pasos": [
        {"orden": 1, "izquierda": "libro_1", "derecha": "libro_2", "coste_niveles": 40},
        {"orden": 2, "izquierda": "objeto", "derecha": "paso_1", "coste_niveles": 4},
    ], "coste_total_niveles": 44, "advertencias": []}}
    response = client.post("/api/procesar", json=VALID)
    assert response.status_code == 200
    assert any("40" in warning for warning in response.json()["resultado"]["advertencias"])


def test_cors(setup):
    client, provider = setup
    for origin, expected in [("http://localhost:5173", 200), ("https://unknown.example", 400)]:
        response = client.options("/api/procesar", headers={"Origin": origin, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"})
        assert response.status_code == expected
        if expected == 200:
            assert response.headers["access-control-allow-origin"] == origin
    provider.assert_not_awaited()


@pytest.mark.parametrize("scenario,expected", [
    ("ok", None), ("status", "IA_NO_DISPONIBLE"), ("network", "IA_NO_DISPONIBLE"),
    ("timeout", "IA_TIMEOUT"), ("deadline", "IA_TIMEOUT"),
    ("bad_envelope", "RESPUESTA_INVALIDA"), ("bad_content", "RESPUESTA_INVALIDA"),
    ("truncated", "RESPUESTA_INVALIDA"),
])
def test_openrouter_transport_without_network(monkeypatch, scenario, expected):
    calls = []
    request_data = ProcessRequest.model_validate(VALID)
    plan = mock_plan(request_data)

    async def handler(request):
        calls.append(request)
        if scenario == "network":
            raise httpx.ConnectError("secret-provider-detail", request=request)
        if scenario == "timeout":
            raise httpx.ReadTimeout("secret-provider-detail", request=request)
        if scenario == "deadline":
            await asyncio.sleep(1)
        if scenario == "status":
            return httpx.Response(429, json={"secret": "hidden"})
        if scenario == "bad_envelope":
            return httpx.Response(200, json={})
        return httpx.Response(200, json={"choices": [{
            "finish_reason": "length" if scenario == "truncated" else "stop",
            "message": {"content": "not json" if scenario == "bad_content" else json.dumps(plan)},
        }]})

    original_client = httpx.AsyncClient
    monkeypatch.setattr(ai_client.httpx, "AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(handler), **kwargs))
    settings = Settings(api_key="test-key", model="test/model", timeout=0.05 if scenario == "deadline" else 20)
    if expected:
        with pytest.raises(AIError) as error:
            asyncio.run(ai_client.generate_plan(request_data, settings))
        assert error.value.code == expected
        assert "secret" not in str(error.value)
    else:
        assert asyncio.run(ai_client.generate_plan(request_data, settings)) == plan
    assert len(calls) == 1
    body = json.loads(calls[0].content)
    assert body["model"] == "test/model"
    assert len(body["messages"]) == 2
    assert calls[0].headers["Authorization"] == "Bearer test-key"


def test_mock_and_missing_credentials_never_connect(monkeypatch):
    def forbidden(**kwargs):
        pytest.fail("No debería crearse un cliente HTTP")
    monkeypatch.setattr(ai_client.httpx, "AsyncClient", forbidden)
    data = ProcessRequest.model_validate(VALID)
    plan = asyncio.run(ai_client.generate_plan(data, Settings(mode="mock")))
    assert "SIMULADO" in plan["resultado"]["advertencias"][0]
    with pytest.raises(AIError, match="IA_NO_DISPONIBLE"):
        asyncio.run(ai_client.generate_plan(data, Settings()))
