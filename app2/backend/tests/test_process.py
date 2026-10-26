from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.ai_client import get_ai_client
from app.main import create_app


@pytest.fixture
def client(settings, ai_mock):
    application = create_app(settings)
    application.dependency_overrides[get_ai_client] = lambda: ai_mock
    with TestClient(application) as test_client:
        yield test_client


def authorization(token_factory):
    return {"Authorization": f"Bearer {token_factory()}"}


def test_one_book(client, selection, token_factory, ai_mock):
    response = client.post("/api/procesar", json=selection, headers=authorization(token_factory))
    assert response.status_code == 200
    result = response.json()["resultado"]
    assert result["pasos"][0]["izquierda"] == "Espada de diamante"
    assert result["pasos"][0]["derecha"] == "Libro de Filo V"
    assert result["coste_total_niveles"] == 5
    assert result["advertencias"] == []
    ai_mock.assert_awaited_once()


def test_eight_books(client, token_factory, ai_mock):
    names = [("protection", 4), ("thorns", 3), ("feather_falling", 4), ("depth_strider", 3),
             ("soul_speed", 3), ("unbreaking", 3), ("mending", 1), ("vanishing_curse", 1)]
    selection = {"objeto": "diamond_boots", "encantamientos": [
        {"nombre": name, "nivel": level} for name, level in names
    ]}
    steps = [{"orden": i, "izquierda": "objeto" if i == 1 else f"paso_{i-1}",
              "derecha": f"libro_{i}", "coste_niveles": 1} for i in range(1, 9)]
    ai_mock.return_value = {"resultado": {"pasos": steps, "coste_total_niveles": 8, "advertencias": []}}
    response = client.post("/api/procesar", json=selection, headers=authorization(token_factory))
    assert response.status_code == 200
    assert len(response.json()["resultado"]["pasos"]) == 8
    assert response.json()["resultado"]["coste_total_niveles"] == 8
    ai_mock.assert_awaited_once()


def test_books_can_be_combined_first(client, token_factory, ai_mock):
    selection = {"objeto": "diamond_sword", "encantamientos": [
        {"nombre": "sharpness", "nivel": 5}, {"nombre": "mending", "nivel": 1}
    ]}
    ai_mock.return_value = {"resultado": {"pasos": [
        {"orden": 1, "izquierda": "libro_1", "derecha": "libro_2", "coste_niveles": 2},
        {"orden": 2, "izquierda": "objeto", "derecha": "paso_1", "coste_niveles": 8},
    ], "coste_total_niveles": 10, "advertencias": []}}
    response = client.post("/api/procesar", json=selection, headers=authorization(token_factory))
    assert response.status_code == 200
    assert response.json()["resultado"]["pasos"][1]["derecha"] == "Resultado del paso 1"


@pytest.mark.parametrize("cost,warn", [(39, False), (40, True)])
def test_survival_warning(client, selection, token_factory, ai_mock, ai_response, cost, warn):
    plan = deepcopy(ai_response)
    plan["resultado"]["pasos"][0]["coste_niveles"] = cost
    plan["resultado"]["coste_total_niveles"] = cost
    ai_mock.return_value = plan
    response = client.post("/api/procesar", json=selection, headers=authorization(token_factory))
    assert response.status_code == 200
    assert any("40 niveles" in text for text in response.json()["resultado"]["advertencias"]) == warn


def test_no_access_precedes_body_validation(client, ai_mock):
    response = client.post("/api/procesar", content="no es JSON")
    assert response.status_code == 401
    ai_mock.assert_not_awaited()


def test_invalid_selection_does_not_call_ai(client, token_factory, ai_mock):
    response = client.post("/api/procesar", json={"objeto": "inexistente", "encantamientos": []},
                           headers=authorization(token_factory))
    assert response.status_code == 422
    ai_mock.assert_not_awaited()


def test_invalid_result_has_no_partial_response(client, selection, token_factory, ai_mock, ai_response):
    ai_response["resultado"]["coste_total_niveles"] = 999
    response = client.post("/api/procesar", json=selection, headers=authorization(token_factory))
    assert response.status_code == 502
    assert response.json()["error"]["codigo"] == "RESPUESTA_INVALIDA"
    assert "resultado" not in response.json()
    ai_mock.assert_awaited_once()


def test_provider_receives_only_selection(settings, selection, ai_response, monkeypatch):
    import asyncio
    import json
    import httpx
    from dataclasses import replace
    from unittest.mock import AsyncMock
    from app.ai_client import generate_plan
    from app.schemas import ProcessRequest

    response = httpx.Response(200, request=httpx.Request("POST", "https://openrouter.ai"), json={
        "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(ai_response)}}]
    })
    post = AsyncMock(return_value=response)
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    configured = replace(settings, openrouter_api_key="clave_ficticia")
    raw = asyncio.run(generate_plan(ProcessRequest.model_validate(selection), configured))
    assert raw == ai_response
    post.assert_awaited_once()
    payload = post.call_args.kwargs["json"]
    assert payload["model"] == settings.openrouter_model
    assert json.loads(payload["messages"][1]["content"]) == selection
    assert "clave_ficticia" not in json.dumps(payload)
    assert payload["provider"]["allow_fallbacks"] is False
    assert payload["stream"] is False


def test_provider_timeout_does_not_retry(settings, selection, monkeypatch):
    import asyncio
    import httpx
    from dataclasses import replace
    from unittest.mock import AsyncMock
    from app.ai_client import AIError, generate_plan
    from app.schemas import ProcessRequest

    post = AsyncMock(side_effect=httpx.ReadTimeout("tiempo agotado"))
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(AIError) as caught:
        asyncio.run(generate_plan(ProcessRequest.model_validate(selection), replace(settings, openrouter_api_key="ficticia")))
    assert caught.value.code == "IA_TIMEOUT"
    assert caught.value.status == 504
    post.assert_awaited_once()
