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
