"""Focus Timer plugin — minimal timer using stdlib asyncio.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import asyncio
from typing import Any
from backend.app.hands import registry

_ACTIVE_TIMERS: dict[str, asyncio.Task] = {}


def _focus_start(minutes: int = 25, label: str = "Focus Session") -> dict[str, Any]:
    """Start a focus timer."""
    if minutes <= 0:
        raise ValueError("minutes must be greater than 0.")
    
    async def _timer():
        await asyncio.sleep(minutes * 60)
        from backend.plugins.notifications import _notify_send
        _notify_send("Focus Timer Complete!", f"{label} ({minutes}m) has ended.")

    task = asyncio.create_task(_timer())
    _ACTIVE_TIMERS[label] = task
    return {"status": "started", "label": label, "minutes": minutes}


def _focus_status() -> dict[str, Any]:
    """Check active focus timers."""
    active = [label for label, task in _ACTIVE_TIMERS.items() if not task.done()]
    return {"active_count": len(active), "timers": active}


registry.register(
    {
        "name": "focus_start",
        "description": "Start a Pomodoro focus timer (default 25 minutes).",
        "version": "1.0.0",
        "phase": 4,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "minutes": {"type": "integer"},
                "label": {"type": "string"},
            },
            "required": [],
        },
        "returns": {"type": "object", "properties": {"status": {"type": "string"}}},
        "scopes": ["timer:write"],
        "tags": ["productivity", "timer"],
    },
    _focus_start,
)

registry.register(
    {
        "name": "focus_status",
        "description": "Check active focus timers.",
        "version": "1.0.0",
        "phase": 4,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"active_count": {"type": "integer"}}},
        "scopes": ["timer:read"],
        "tags": ["productivity", "timer"],
    },
    _focus_status,
)
