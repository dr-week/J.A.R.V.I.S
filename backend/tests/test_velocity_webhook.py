"""Webhook / Velocity IPC tests (no live Velocity required)."""
from fastapi.testclient import TestClient

from backend.app.main import app


def test_velocity_webhook_accepts_payload():
    client = TestClient(app)
    resp = client.post(
        "/internal/webhook/velocity",
        json={
            "app_id": "demo-app",
            "status": "building",
            "message": "scaffolding",
            "step": 1,
            "progress": 0.2,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["processed"] is True


def test_velocity_webhook_rejects_bad_json():
    client = TestClient(app)
    resp = client.post(
        "/internal/webhook/velocity",
        content=b"not-json",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
