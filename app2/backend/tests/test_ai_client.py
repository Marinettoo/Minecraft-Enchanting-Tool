import asyncio
from dataclasses import replace
import json
from unittest.mock import AsyncMock

import httpx
import pytest

from app.ai_client import AIError, generate_plan
from app.schemas import ProcessRequest


@pytest.mark.parametrize("envelope", [
    None, [], {}, {"choices": []}, {"choices": [None]},
    {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]},
    {"choices": [{"finish_reason": "stop", "message": {"content": None}}]},
    {"choices": [{"finish_reason": "stop", "message": {"content": "texto sin JSON"}}]},
    {"choices": [{"finish_reason": "stop", "message": {"content": "Aquí tienes: {}"}}]},
    {"choices": [{"finish_reason": "stop", "message": {"content": "```json\n{}"}}]},
])
def test_unusable_provider_response(settings, selection, monkeypatch, envelope):
    response = httpx.Response(200, request=httpx.Request("POST", "https://openrouter.ai"), json=envelope)
    post = AsyncMock(return_value=response)
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(AIError) as caught:
        asyncio.run(generate_plan(ProcessRequest.model_validate(selection), replace(settings, openrouter_api_key="ficticia")))
    assert caught.value.code == "RESPUESTA_INVALIDA"
    post.assert_awaited_once()


def test_complete_markdown_block(settings, selection, monkeypatch, ai_response):
    content = '```json\n' + json.dumps(ai_response) + '\n```'
    response = httpx.Response(200, request=httpx.Request("POST", "https://openrouter.ai"), json={
        "choices": [{"finish_reason": "stop", "message": {"content": content}}]
    })
    post = AsyncMock(return_value=response)
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    assert asyncio.run(generate_plan(ProcessRequest.model_validate(selection), replace(settings, openrouter_api_key="ficticia"))) == ai_response


@pytest.mark.parametrize("kind,code,status", [("http", "IA_NO_DISPONIBLE", 502), ("network", "IA_NO_DISPONIBLE", 502), ("timeout", "IA_TIMEOUT", 504)])
def test_provider_failure_is_controlled(api_client, settings, selection, token_factory, monkeypatch, kind, code, status):
    from app.ai_client import get_ai_client
    from functools import partial
    api_client.app.dependency_overrides[get_ai_client] = lambda: partial(generate_plan, settings=replace(settings, openrouter_api_key="ficticia"))
    request = httpx.Request("POST", "https://openrouter.ai")
    failure = {
        "http": httpx.HTTPStatusError("dato privado", request=request, response=httpx.Response(429, request=request)),
        "network": httpx.ConnectError("dato privado"), "timeout": httpx.ReadTimeout("dato privado"),
    }[kind]
    post = AsyncMock(side_effect=failure)
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    response = api_client.post("/api/procesar", json=selection, headers={"Authorization": f"Bearer {token_factory()}"})
    assert response.status_code == status
    assert response.json()["error"]["codigo"] == code
    assert "dato privado" not in response.text
    post.assert_awaited_once()


def test_total_deadline(settings, selection, monkeypatch):
    real_timeout = asyncio.timeout
    def immediate_timeout(seconds):
        assert seconds == 60
        return real_timeout(0)
    async def delayed(*args, **kwargs):
        await asyncio.sleep(0)
    post = AsyncMock(side_effect=delayed)
    monkeypatch.setattr(asyncio, "timeout", immediate_timeout)
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(AIError) as caught:
        asyncio.run(generate_plan(ProcessRequest.model_validate(selection), replace(settings, openrouter_api_key="ficticia")))
    assert caught.value.code == "IA_TIMEOUT"
    post.assert_awaited_once()
