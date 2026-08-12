"""velocity_build — bridge Jarvis Hands → Velocity app builder.

Posts a JSON build request to the Velocity HTTP endpoint.
Requires user confirmation (confirm_always).
"""
from __future__ import annotations

import json
import uuid
from typing import Any

import httpx

from ... import config


def _velocity_base() -> str:
    return (getattr(config, "VELOCITY_URL", None) or "").rstrip("/") or "http://127.0.0.1:5174"


async def velocity_build(app_description: str, app_id: str = "") -> dict[str, Any]:
    """Send a build request to Velocity. Returns status payload."""
    app_id = (app_id or "").strip() or f"app-{uuid.uuid4().hex[:10]}"
    payload = {
        "app_id": app_id,
        "app_description": app_description,
        "source": "jarvis",
        "callback_url": f"http://127.0.0.1:{config.PORT}/internal/webhook/velocity",
    }
    url = f"{_velocity_base()}/api/build"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code >= 400:
                return {
                    "ok": False,
                    "app_id": app_id,
                    "error": f"Velocity HTTP {resp.status_code}: {resp.text[:400]}",
                    "payload": payload,
                }
            body: Any
            try:
                body = resp.json()
            except json.JSONDecodeError:
                body = {"raw": resp.text[:500]}
            return {"ok": True, "app_id": app_id, "velocity": body, "sent": payload}
    except httpx.ConnectError:
        return {
            "ok": False,
            "app_id": app_id,
            "error": (
                f"Velocity not reachable at {url}. "
                "Start Velocity or set JARVIS_VELOCITY_URL in .env."
            ),
            "payload": payload,
        }
    except Exception as exc:
        return {"ok": False, "app_id": app_id, "error": str(exc), "payload": payload}


def register_velocity_build() -> None:
    """Register the velocity_build tool on the Hands registry."""
    from ..registry import register

    register(
        {
            "name": "velocity_build",
            "description": (
                "Start a Velocity AI app build from a natural-language app description. "
                "Use when the user wants a new generated app scaffolded in Velocity."
            ),
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_description": {
                        "type": "string",
                        "description": "What app to build (features, platform, style).",
                    },
                    "app_id": {
                        "type": "string",
                        "description": "Optional stable app id; auto-generated if omitted.",
                    },
                },
                "required": ["app_description"],
            },
            "returns": {"type": "object"},
            "scopes": [],
            "tags": ["velocity", "builder"],
        },
        velocity_build,
    )
