"""Internal and external webhooks for CoreBrain.

Supported Webhook Endpoints:
- `/internal/webhook/velocity`: Velocity build engine IPC → WebSocket clients.
- `/webhook/telegram`: Telegram Bot incoming updates → brain bridge.
- `/webhook/github`: GitHub Webhook receiver with HMAC-SHA256 signature verification & SyncManager broadcast.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Header, Request

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhooks"])


def _verify_github_signature(secret: str, signature_header: str | None, payload_bytes: bytes) -> bool:
    """Verify HMAC SHA256 signature from GitHub webhook header.
    
    Security Rationale:
    - Protects the brain host against unauthenticated forged webhook payloads.
    - If secret is configured, rejection occurs before parsing JSON or broadcasting.
    """
    if not secret:
        # If no secret is configured on brain host, skip signature verification
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected_hash = signature_header.split("sha256=", 1)[1]
    mac = hmac.new(secret.encode("utf-8"), msg=payload_bytes, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), expected_hash)


@router.post("/internal/webhook/velocity")
async def velocity_webhook(request: Request) -> dict[str, Any]:
    """Velocity → Jarvis IPC.

    JSON body (flexible):
      app_id, status, message, step?, progress?, device_id?
    Broadcasts `velocity_update` on the sync WebSocket bus so the web UI
    can show build progress without polling.
    """
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON object required")

    app_id = payload.get("app_id")
    status = payload.get("status")
    message = payload.get("message")
    device_id = str(payload.get("device_id") or "")
    event = {
        "type": "velocity_update",
        "data": {
            "app_id": app_id,
            "status": status,
            "message": message,
            "step": payload.get("step"),
            "progress": payload.get("progress"),
        },
    }
    logger.info(
        "[Velocity IPC] app=%s status=%s step=%s",
        app_id,
        status,
        payload.get("step"),
    )

    from ..sync.manager import manager

    delivered = 0
    if device_id:
        ok = await manager.send_to_device(device_id, event)
        delivered = 1 if ok else 0
    if not device_id or delivered == 0:
        await manager.broadcast(event)
        delivered = len(manager.active_device_ids())

    return {"success": True, "processed": True, "delivered_hint": delivered}


@router.post("/webhook/telegram")
async def telegram_webhook(request: Request) -> dict[str, Any]:
    """Telegram Bot Webhook → Jarvis Brain bridge.
    
    Accepts incoming message updates from Telegram and dispatches them
    to the Jarvis brain turn loop.
    """
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    message_data = payload.get("message") or payload.get("edited_message")
    if not message_data:
        return {"ok": True, "skipped": True}

    chat_id = str(message_data.get("chat", {}).get("id") or "")
    text = message_data.get("text", "").strip()

    if not chat_id or not text:
        return {"ok": True, "skipped": True}

    from backend.plugins.telegram_bot import _telegram_send
    
    # Simple reply acknowledgment for bridge
    _telegram_send(f"Jarvis Received: {text}", chat_id=chat_id)
    return {"ok": True, "chat_id": chat_id, "text": text}


@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(default="ping", alias="X-GitHub-Event"),
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> dict[str, Any]:
    """GitHub Webhook Receiver.
    
    Validates HMAC signature and broadcasts parsed GitHub events across
    all connected OmniPresence devices via SyncManager.
    """
    body_bytes = await request.body()
    secret = os.environ.get("JARVIS_GITHUB_WEBHOOK_SECRET", "").strip()
    
    if not _verify_github_signature(secret, x_hub_signature_256, body_bytes):
        logger.warning("[GitHub Webhook] Invalid signature rejected")
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    try:
        payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    repo_name = payload.get("repository", {}).get("full_name", "unknown")
    logger.info("[GitHub Webhook] Received event '%s' for repository '%s'", x_github_event, repo_name)

    from ..sync.manager import manager

    sync_event = {
        "type": "github_event",
        "event": x_github_event,
        "repository": repo_name,
        "action": payload.get("action", ""),
        "sender": payload.get("sender", {}).get("login", ""),
        "data": payload,
    }
    await manager.broadcast(sync_event)

    return {
        "status": "ok",
        "event": x_github_event,
        "repository": repo_name,
        "broadcast_devices": len(manager.active_device_ids()),
    }
