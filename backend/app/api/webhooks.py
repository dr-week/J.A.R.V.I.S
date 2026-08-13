"""Internal webhooks — Velocity build progress → WebSocket clients."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhooks"])


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

