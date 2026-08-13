"""Telegram Bot presence plugin — python-telegram-bot wrapper.

Provides tools to push notifications to user via Telegram.
Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import os
from typing import Any
from backend.app.hands import registry

try:
    import urllib.request
    import json
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False


def _telegram_send(message: str, chat_id: str = "") -> dict[str, Any]:
    """Send a message to a user/chat via Telegram Bot API."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    target_chat = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
    
    if not token or not target_chat:
        return {"error": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured in .env"}
        
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({"chat_id": target_chat, "text": message}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"sent": data.get("ok", False), "chat_id": target_chat}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "telegram_send",
        "description": "Send a push message to the user's phone via Telegram Bot API.",
        "version": "1.0.0",
        "phase": 4,
        "risk_level": "confirm_once",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "chat_id": {"type": "string"},
            },
            "required": ["message"],
        },
        "returns": {"type": "object", "properties": {"sent": {"type": "boolean"}}},
        "scopes": ["telegram:write"],
        "tags": ["presence", "telegram", "messaging"],
    },
    _telegram_send,
)
