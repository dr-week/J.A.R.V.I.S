"""API -- /pair device pairing stub (ISSUE-011/013).

Clients exchange JARVIS_PAIRING_SECRET for a device token.
Full auth hardening belongs to ISSUE-013; this is the stub clients can use now.
"""
from __future__ import annotations

import secrets
import time
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from .. import config
from ..soul.memory import get_device_by_token, save_device_token

router = APIRouter(prefix="/pair", tags=["pair"])


class PairRequest(BaseModel):
    pairing_secret: str
    device_id: str = Field(min_length=1)
    device_name: str = "windows"


class PairResponse(BaseModel):
    token: str
    device_id: str
    device_name: str
    expires_at: float


def issue_token(device_id: str, device_name: str) -> PairResponse:
    token = secrets.token_urlsafe(32)
    expires_at = time.time() + config.JWT_EXPIRE_DAYS * 86400
    save_device_token(token, device_id, device_name, expires_at)
    return PairResponse(
        token=token,
        device_id=device_id,
        device_name=device_name,
        expires_at=expires_at,
    )


def validate_token(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None
    raw = token.removeprefix("Bearer ").strip()
    
    # Optional cleanup on each validation
    # delete_expired_tokens()
    
    info = get_device_by_token(raw)
    if not info:
        return None
    if info["expires_at"] < time.time():
        # Token is in DB but expired; it will be deleted later by a cron or explicitly
        return None
    return info


@router.post("", response_model=PairResponse)
async def pair_device(body: PairRequest) -> PairResponse:
    if body.pairing_secret != config.PAIRING_SECRET:
        raise HTTPException(status_code=401, detail="Invalid pairing secret")
    return issue_token(body.device_id, body.device_name)


@router.get("/me")
async def pair_me(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    info = validate_token(authorization)
    if not info:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return {"ok": True, **info}
