from fastapi.testclient import TestClient

from app.web import create_web_app


def web_client(tmp_path, settings):
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "index.html").write_text("<h1>App2 de prueba</h1>", encoding="utf-8")
    (frontend / "app.js").write_text("console.log('prueba')", encoding="utf-8")
    (tmp_path / "privado.txt").write_text("no publicar", encoding="utf-8")
    return TestClient(create_web_app(frontend, settings))


def test_frontend_is_available_without_calling_api(tmp_path, settings):
    with web_client(tmp_path, settings) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "App2 de prueba" in response.text
        assert client.get("/app.js").status_code == 200


def test_static_mount_does_not_hide_protected_api(tmp_path, settings):
    with web_client(tmp_path, settings) as client:
        response = client.post("/api/procesar", json={})
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "NO_AUTORIZADO"


def test_files_outside_frontend_are_not_served(tmp_path, settings):
    with web_client(tmp_path, settings) as client:
        for path in ("/%2e%2e/privado.txt", "/.env", "/app/config.py"):
            response = client.get(path)
            assert response.status_code == 404
            assert "no publicar" not in response.text
