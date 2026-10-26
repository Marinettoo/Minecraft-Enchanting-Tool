"""Configuración del backend, sin mostrar claves en errores ni registros."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from dotenv import dotenv_values

MODEL = "poolside/laguna-s-2.1:free"
LOCAL_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


@dataclass(frozen=True)
class Settings:
    clerk_jwt_key: str = field(repr=False)
    clerk_issuer: str
    clerk_authorized_parties: tuple[str, ...] = LOCAL_ORIGINS
    allowed_origins: tuple[str, ...] = LOCAL_ORIGINS
    clerk_audience: str | None = None
    openrouter_api_key: str = field(default="", repr=False)
    openrouter_model: str = MODEL
    ai_timeout_seconds: float = 60


def _origin(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return bool(
            parsed.hostname and parsed.port != 0 and not parsed.username and not parsed.password
            and not parsed.path and not parsed.query and not parsed.fragment
            and (parsed.scheme == "https" or (
                parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
            ))
        )
    except ValueError:
        return False


def load_settings(env_file: Path | None = None) -> Settings:
    path = env_file if env_file is not None else Path(__file__).resolve().parents[1] / ".env"
    values = {**dotenv_values(path), **os.environ}

    def origins(name: str) -> tuple[str, ...]:
        entries = tuple(part.strip() for part in values.get(name, ",".join(LOCAL_ORIGINS)).split(","))
        if not entries or not all(_origin(entry) for entry in entries):
            raise ValueError(f"Configura orígenes explícitos y válidos en {name}")
        return entries

    public_key = values.get("CLERK_JWT_KEY", "") or ""
    try:
        key = load_pem_public_key(public_key.encode())
        if not isinstance(key, RSAPublicKey):
            raise ValueError("Tipo de clave incorrecto")
    except (ValueError, TypeError) as exc:
        raise ValueError("Configura una clave pública RSA válida en CLERK_JWT_KEY") from exc
    issuer = (values.get("CLERK_ISSUER", "") or "").rstrip("/")
    if not _origin(issuer) or not issuer.startswith("https://"):
        raise ValueError("Configura CLERK_ISSUER con el emisor HTTPS de tu instancia")
    if values.get("OPENROUTER_MODEL", MODEL) != MODEL:
        raise ValueError("OPENROUTER_MODEL debe coincidir con el modelo acordado")
    try:
        timeout = float(values.get("AI_TIMEOUT_SECONDS", "60"))
    except (ValueError, TypeError) as exc:
        raise ValueError("AI_TIMEOUT_SECONDS debe ser 60") from exc
    if timeout != 60:
        raise ValueError("AI_TIMEOUT_SECONDS debe ser 60")
    return Settings(
        clerk_jwt_key=public_key, clerk_issuer=issuer,
        clerk_authorized_parties=origins("CLERK_AUTHORIZED_PARTIES"),
        allowed_origins=origins("ALLOWED_ORIGINS"),
        clerk_audience=values.get("CLERK_AUDIENCE") or None,
        openrouter_api_key=values.get("OPENROUTER_API_KEY", "") or "",
        ai_timeout_seconds=timeout,
    )
