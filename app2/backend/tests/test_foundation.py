from pathlib import Path

import pytest
from fastapi import Depends
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from app.auth import require_session
from app.config import load_settings
from app.main import create_app
from app.schemas import ProcessRequest


def test_config_environment_overrides_file(tmp_path, monkeypatch, settings):
    path = tmp_path / ".env"
    path.write_text(
        f'CLERK_JWT_KEY="{settings.clerk_jwt_key}"\nCLERK_ISSUER=https://archivo.example\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("CLERK_ISSUER", settings.clerk_issuer)
    assert load_settings(path).clerk_issuer == settings.clerk_issuer


@pytest.mark.parametrize("name,value", [
    ("AI_TIMEOUT_SECONDS", "20"), ("AI_TIMEOUT_SECONDS", "nan"),
    ("ALLOWED_ORIGINS", "*"), ("CLERK_AUTHORIZED_PARTIES", ""),
    ("CLERK_ISSUER", "http://clerk.example"), ("CLERK_JWT_KEY", "incorrecta"),
    ("OPENROUTER_MODEL", "otro-modelo"),
])
def test_invalid_configuration(tmp_path, monkeypatch, settings, name, value):
    monkeypatch.setenv("CLERK_JWT_KEY", settings.clerk_jwt_key)
    monkeypatch.setenv("CLERK_ISSUER", settings.clerk_issuer)
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError):
        load_settings(tmp_path / "no-existe")


def test_catalogue_matches_ers():
    from app.rules import OBJECTS, ENCHANTMENTS, INCOMPATIBLE
    import re
    ers = (Path(__file__).resolve().parents[3] / "docs/ERS-APP2.md").read_text(encoding="utf-8-sig")
    rows = re.findall(r"^\| [^|]+ \| ([a-z_]+) \| (\d+) \| ([^|]+) \|$", ers, re.M)
    assert len(OBJECTS) == 58
    assert len(ENCHANTMENTS) == 39
    assert {name: rule[0] for name, rule in ENCHANTMENTS.items()} == {name: int(level) for name, level, _ in rows}
    assert "diamond_sword" in OBJECTS and "leather_boots" in OBJECTS
    assert len(INCOMPATIBLE) == 8
    kinds = {
        "Espada": {"sword"}, "Espada y hacha": {"sword", "axe"},
        "Hacha, pico, pala y azada": {"axe", "pickaxe", "shovel", "hoe"},
        "Armadura": {"helmet", "chestplate", "leggings", "boots"},
        "Casco": {"helmet"}, "Botas": {"boots"}, "Grebas": {"leggings"},
        "Arco": {"bow"}, "Ballesta": {"crossbow"}, "Tridente": {"trident"},
        "Caña de pescar": {"fishing_rod"}, "Todos": set(OBJECTS.values()),
    }
    for name, _, allowed in rows:
        assert ENCHANTMENTS[name][1] == kinds[allowed.strip()]


def test_selection_types(selection):
    assert ProcessRequest.model_validate(selection).objeto == "diamond_sword"


@pytest.mark.parametrize("level", [True, "5", 1.5, 0, -1, 6])
def test_strict_levels(selection, level):
    from pydantic import ValidationError
    selection["encantamientos"][0]["nivel"] = level
    with pytest.raises(ValidationError):
        ProcessRequest.model_validate(selection)


@pytest.mark.parametrize("change", [
    {"objeto": "inexistente"}, {"extra": "no permitido"},
    {"encantamientos": []},
    {"encantamientos": [{"nombre": "mending", "nivel": 1}] * 9},
    {"encantamientos": [{"nombre": "sharpness", "nivel": 5}] * 2},
    {"encantamientos": [{"nombre": "feather_falling", "nivel": 4}]},
    {"encantamientos": [{"nombre": "sharpness", "nivel": 5}, {"nombre": "smite", "nivel": 5}]},
    {"encantamientos": [{"nombre": "mending", "nivel": 2}]},
    {"encantamientos": [{"nombre": "inexistente", "nivel": 1}]},
    {"encantamientos": [{"nombre": "mending", "nivel": 1, "extra": True}]},
])
def test_invalid_selections(selection, change):
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ProcessRequest.model_validate(selection | change)


def test_eight_books():
    names = [
        ("protection", 4), ("thorns", 3), ("feather_falling", 4), ("depth_strider", 3),
        ("soul_speed", 3), ("unbreaking", 3), ("mending", 1), ("vanishing_curse", 1),
    ]
    request = ProcessRequest.model_validate({
        "objeto": "diamond_boots",
        "encantamientos": [{"nombre": name, "nivel": level} for name, level in names],
    })
    assert len(request.encantamientos) == 8


def test_cors_and_generic_errors(settings):
    app = create_app(settings)

    @app.post("/probe")
    def probe(session=Depends(require_session)):
        return {}

    @app.get("/validation-probe")
    def validation_probe():
        raise RequestValidationError([{"input": "dato privado"}])

    with TestClient(app) as client:
        response = client.options("/probe", headers={
            "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        })
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
        denied = client.options("/probe", headers={
            "Origin": "https://ajeno.example", "Access-Control-Request-Method": "POST",
        })
        assert denied.status_code == 400
        response = client.post("/probe", headers={"Origin": "http://localhost:5173"})
        assert response.status_code == 401
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
        response = client.get("/validation-probe")
        assert response.status_code == 422
        assert "dato privado" not in response.text


def test_configuration_loads_at_startup(monkeypatch, settings):
    from dataclasses import replace
    from unittest.mock import Mock
    configured = replace(settings, allowed_origins=("https://frontend.example",))
    loader = Mock(return_value=configured)
    monkeypatch.setattr("app.main.load_settings", loader)
    app = create_app()
    loader.assert_not_called()
    with TestClient(app) as client:
        loader.assert_called_once_with()
        response = client.options("/probe", headers={
            "Origin": "https://frontend.example", "Access-Control-Request-Method": "POST",
        })
        assert response.headers["access-control-allow-origin"] == "https://frontend.example"
