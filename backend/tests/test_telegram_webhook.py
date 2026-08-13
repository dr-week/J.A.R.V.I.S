"""Unit tests for Telegram Webhook bridge endpoint."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_telegram_webhook_invalid_json():
    response = client.post("/webhook/telegram", data="invalid json")
    assert response.status_code == 400


def test_telegram_webhook_no_message():
    response = client.post("/webhook/telegram", json={"update_id": 12345})
    assert response.status_code == 200
    assert response.json().get("skipped") is True


def test_telegram_webhook_valid_message():
    payload = {
        "update_id": 12345,
        "message": {
            "message_id": 1,
            "chat": {"id": 999888},
            "text": "Hello Jarvis",
        },
    }
    response = client.post("/webhook/telegram", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True
    assert data.get("chat_id") == "999888"
    assert data.get("text") == "Hello Jarvis"
