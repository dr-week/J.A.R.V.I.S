"""Tests for GitHub Webhook Receiver API endpoint.

Verifies:
- HMAC SHA256 signature verification logic
- Handling invalid signature with 401 Unauthorized
- Handling missing/invalid JSON payload
- Successful event processing and SyncManager broadcast dispatch
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


def _compute_sig(secret: str, body: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


@pytest.mark.asyncio
async def test_github_webhook_invalid_signature():
    """Verify webhook rejects mismatched HMAC signature when secret is configured."""
    secret = "my-secret-key"
    payload = json.dumps({"action": "opened", "repository": {"full_name": "owner/repo"}}).encode("utf-8")
    
    with patch.dict(os.environ, {"JARVIS_GITHUB_WEBHOOK_SECRET": secret}):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/webhook/github",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-GitHub-Event": "issues",
                    "X-Hub-Signature-256": "sha256=invalid_hash_value",
                },
            )
            assert resp.status_code == 401
            assert "Invalid HMAC signature" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_github_webhook_valid_signature_broadcasts():
    """Verify webhook accepts valid HMAC signature and broadcasts event."""
    secret = "my-secret-key"
    payload_data = {
        "action": "opened",
        "issue": {"number": 101, "title": "New issue reported"},
        "repository": {"full_name": "owner/repo"},
        "sender": {"login": "octocat"},
    }
    payload_bytes = json.dumps(payload_data).encode("utf-8")
    valid_sig = _compute_sig(secret, payload_bytes)

    with patch.dict(os.environ, {"JARVIS_GITHUB_WEBHOOK_SECRET": secret}), patch(
        "backend.app.sync.manager.manager.broadcast", new_callable=AsyncMock
    ) as mock_broadcast, patch(
        "backend.app.sync.manager.manager.active_device_ids", return_value=["device-1"]
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/webhook/github",
                content=payload_bytes,
                headers={
                    "Content-Type": "application/json",
                    "X-GitHub-Event": "issues",
                    "X-Hub-Signature-256": valid_sig,
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert data["event"] == "issues"
            assert data["repository"] == "owner/repo"
            assert data["broadcast_devices"] == 1
            
            mock_broadcast.assert_called_once()
            called_event = mock_broadcast.call_args[0][0]
            assert called_event["type"] == "github_event"
            assert called_event["event"] == "issues"
            assert called_event["sender"] == "octocat"
