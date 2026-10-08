"""Configuración privada; las variables del entorno prevalecen sobre .env."""

import math
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    mode: str = "openrouter"
    api_key: str = field(default="", repr=False)
    model: str = ""
    timeout: float = 20
    origins: tuple[str, ...] = ("http://localhost:5173",)


def load_settings() -> Settings:
    load_dotenv(Path(__file__).with_name(".env"))
    mode = os.getenv("AI_MODE", "openrouter")
    timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "20"))
    if mode not in {"mock", "openrouter"}:
        raise ValueError("AI_MODE debe ser mock u openrouter")
    if not math.isfinite(timeout) or not 0 < timeout <= 60:
        raise ValueError("AI_TIMEOUT_SECONDS debe estar entre 0 (excluido) y 60")
    origins = tuple(x.strip().rstrip("/") for x in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if x.strip())
    if not origins or "*" in origins:
        raise ValueError("Configura orígenes explícitos en ALLOWED_ORIGINS")
    return Settings(mode, os.getenv("OPENROUTER_API_KEY", ""), os.getenv("OPENROUTER_MODEL", ""), timeout, origins)
