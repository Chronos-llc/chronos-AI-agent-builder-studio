"""Core backend smoke tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert "message" in payload


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "healthy"


def test_protected_routes_require_auth():
    response = client.get("/api/v1/agents")
    assert response.status_code in {401, 403}

