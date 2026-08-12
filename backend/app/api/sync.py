from __future__ import annotations

import typing

"""API — /sync endpoints."""
from fastapi import APIRouter

from ..sync.manager import manager

router = APIRouter(prefix="/sync")

@router.get("/status")
async def sync_status() -> typing.Any:
    return {
        "status": "ok",
        "connected_clients": len(manager.active_device_ids()),
        "active_devices": manager.active_device_ids(),
    }
