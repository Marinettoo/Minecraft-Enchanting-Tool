from time import time
from unittest.mock import AsyncMock

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.config import Settings


@pytest.fixture(scope="session")
def signing_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def settings(signing_key):
    public_key = signing_key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return Settings(
        clerk_jwt_key=public_key,
        clerk_issuer="https://clerk.example",
        clerk_authorized_parties=("http://localhost:5173",),
        allowed_origins=("http://localhost:5173",),
    )


@pytest.fixture
def token_factory(signing_key):
    def make_token(changes=None, key=None):
        now = int(time())
        payload = {
            "iss": "https://clerk.example", "sub": "user_ficticio",
            "sid": "sess_ficticia", "azp": "http://localhost:5173",
            "iat": now, "nbf": now - 1, "exp": now + 120,
        }
        payload.update(changes or {})
        payload = {name: value for name, value in payload.items() if value is not None}
        return jwt.encode(payload, key or signing_key, algorithm="RS256")
    return make_token


@pytest.fixture
def selection():
    return {"objeto": "diamond_sword", "encantamientos": [{"nombre": "sharpness", "nivel": 5}]}


@pytest.fixture
def ai_response():
    return {"resultado": {
        "pasos": [{"orden": 1, "izquierda": "objeto", "derecha": "libro_1", "coste_niveles": 5}],
        "coste_total_niveles": 5, "advertencias": [],
    }}


@pytest.fixture
def ai_mock(ai_response):
    return AsyncMock(return_value=ai_response)


@pytest.fixture
def session_mock():
    return {"sub": "user_ficticio", "sid": "sess_ficticia"}


@pytest.fixture
def api_client(settings, ai_mock):
    from fastapi.testclient import TestClient
    from app.ai_client import get_ai_client
    from app.main import create_app
    app = create_app(settings)
    app.dependency_overrides[get_ai_client] = lambda: ai_mock
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def no_external_http(monkeypatch):
    original_send = httpx.Client.send

    def send(client, request, *args, **kwargs):
        if request.url.host != "testserver":
            raise AssertionError("Las pruebas no deben consultar servicios externos")
        return original_send(client, request, *args, **kwargs)

    async def async_send(*args, **kwargs):
        raise AssertionError("Usa el proveedor simulado en las pruebas")

    monkeypatch.setattr(httpx.Client, "send", send)
    monkeypatch.setattr(httpx.AsyncClient, "send", async_send)
