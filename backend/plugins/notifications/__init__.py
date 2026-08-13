"""Notifications plugin — cross-platform desktop notifications via notify-py.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

from typing import Any
from backend.app.hands import registry

try:
    from notifypy import Notify
    _HAS_NOTIFY = True
except ImportError:
    _HAS_NOTIFY = False


def _notify_send(title: str, message: str) -> dict[str, Any]:
    """Send a desktop notification."""
    if not _HAS_NOTIFY:
        return {"error": "notify-py is not installed. Run: pip install notify-py"}
    try:
        notification = Notify()
        notification.title = title
        notification.message = message
        notification.send()
        return {"status": "sent", "title": title, "message": message}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "notify_send",
        "description": "Send a desktop notification to the user.",
        "version": "1.0.0",
        "phase": 4,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["title", "message"],
        },
        "returns": {"type": "object", "properties": {"status": {"type": "string"}}},
        "scopes": ["system:write"],
        "tags": ["notifications", "presence"],
    },
    _notify_send,
)
