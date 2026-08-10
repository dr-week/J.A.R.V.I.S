"""Smoke tests that do not require a running uvicorn process."""

from backend.app.main import app
from fastapi.testclient import TestClient


def test_health_returns_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "assistant_name" in body
    assert "version" in body
