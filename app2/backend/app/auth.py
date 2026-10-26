"""Verificación local de sesiones mediante el SDK oficial de Clerk."""

import logging
import math

import httpx
from clerk_backend_api import AuthenticateRequestOptions, authenticate_request
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


def require_session(request: Request) -> dict:
    parts = request.headers.get("Authorization", "").split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401)
    settings = request.app.state.settings
    if settings is None or not settings.clerk_jwt_key:
        raise HTTPException(status_code=401)
    try:
        # Normaliza el esquema Bearer y evita que el SDK use una cookie como alternativa.
        auth_request = httpx.Request(
            request.method, str(request.url), headers={"Authorization": f"Bearer {parts[1]}"}
        )
        state = authenticate_request(auth_request, AuthenticateRequestOptions(
            jwt_key=settings.clerk_jwt_key,
            authorized_parties=list(settings.clerk_authorized_parties),
            audience=[settings.clerk_audience] if settings.clerk_audience else None,
            accepts_token=["session_token"],
            clock_skew_in_ms=0,
        ))
        payload = state.payload or {}
        expiry = payload.get("exp")
        valid = (
            state.is_signed_in and payload.get("iss") == settings.clerk_issuer
            and isinstance(expiry, (int, float)) and not isinstance(expiry, bool)
            and math.isfinite(expiry)
            and isinstance(payload.get("sub"), str) and bool(payload["sub"])
            and isinstance(payload.get("sid"), str) and bool(payload["sid"])
        )
    except Exception:
        # Un fallo del verificador tampoco autoriza, y nunca se registra el token.
        logger.warning("Autorización: NO_AUTORIZADO")
        raise HTTPException(status_code=401) from None
    if not valid:
        raise HTTPException(status_code=401)
    return {"sub": payload["sub"], "sid": payload["sid"]}
