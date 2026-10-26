from dataclasses import replace
from time import time

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, Request
from fastapi.testclient import TestClient

from app.auth import require_session
from app.main import create_app


@pytest.fixture
def client(settings, ai_mock):
    app = create_app(settings)

    # Esta ruta solo existe en pruebas; no forma parte de la aplicación.
    @app.post("/probe")
    async def probe(request: Request, session=Depends(require_session)):
        await request.json()
        await ai_mock()
        return {"authorized": True}

    with TestClient(app) as test_client:
        yield test_client


def test_valid_session(client, token_factory, ai_mock):
    response = client.post("/probe", json={}, headers={"Authorization": f"Bearer {token_factory()}"})
    assert response.status_code == 200
    ai_mock.assert_awaited_once()


@pytest.mark.parametrize("header", [None, "", "Bearer", "Basic abc", "Bearer no-es-un-token", "Bearer uno dos", "Bearer ak_ficticia"])
def test_missing_or_malformed_token(client, ai_mock, header):
    headers = {"Authorization": header} if header is not None else {}
    response = client.post("/probe", content="JSON incorrecto", headers=headers)
    assert response.status_code == 401
    assert response.json()["error"]["codigo"] == "NO_AUTORIZADO"
    ai_mock.assert_not_awaited()


@pytest.mark.parametrize("changes", [
    {"exp": 1}, {"exp": None}, {"iss": "https://otra-instancia.example"},
    {"azp": "https://otro-origen.example"}, {"azp": None},
    {"nbf": int(time()) + 3600}, {"sub": None}, {"sid": None},
])
def test_rejected_claims(client, token_factory, ai_mock, changes):
    response = client.post("/probe", json={}, headers={"Authorization": f"Bearer {token_factory(changes)}"})
    assert response.status_code == 401
    ai_mock.assert_not_awaited()


def test_wrong_signature(client, token_factory, ai_mock):
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = token_factory(key=other_key)
    response = client.post("/probe", json={}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert token not in response.text
    ai_mock.assert_not_awaited()


def test_cookie_does_not_replace_bearer(client, token_factory, ai_mock):
    response = client.post("/probe", json={}, headers={"Cookie": f"__session={token_factory()}"})
    assert response.status_code == 401
    ai_mock.assert_not_awaited()


@pytest.mark.parametrize("audience,expected", [("met", 200), ("otra", 401), (None, 401)])
def test_audience(client, settings, token_factory, ai_mock, audience, expected):
    client.app.state.settings = replace(settings, clerk_audience="met")
    response = client.post("/probe", json={}, headers={"Authorization": f"Bearer {token_factory({'aud': audience})}"})
    assert response.status_code == expected
    assert ai_mock.await_count == (1 if expected == 200 else 0)


def test_verification_failure_is_closed(client, token_factory, ai_mock, monkeypatch):
    def unavailable(*args, **kwargs):
        raise RuntimeError("detalle privado que no se debe mostrar")
    monkeypatch.setattr("app.auth.authenticate_request", unavailable)
    response = client.post("/probe", json={}, headers={"Authorization": f"Bearer {token_factory()}"})
    assert response.status_code == 401
    assert "detalle privado" not in response.text
    ai_mock.assert_not_awaited()


def test_missing_key_does_not_use_remote_verification(client, settings, token_factory, ai_mock):
    client.app.state.settings = replace(settings, clerk_jwt_key="")
    response = client.post("/probe", json={}, headers={"Authorization": f"Bearer {token_factory()}"})
    assert response.status_code == 401
    ai_mock.assert_not_awaited()


def test_bearer_scheme_is_case_insensitive(client, token_factory):
    response = client.post("/probe", json={}, headers={"Authorization": f"bearer {token_factory()}"})
    assert response.status_code == 200
