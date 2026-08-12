"""Clipboard plugin — cross-platform clipboard with history via pyperclip.

Stores clipboard history in the central brain SQLite database.
Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime
from typing import Any

from backend.app.config import DB_PATH
from backend.app.hands import registry

try:
    import pyperclip
    _HAS_PYPERCLIP = True
except ImportError:
    _HAS_PYPERCLIP = False


def _connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS clipboard_history (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            copied_at TEXT NOT NULL
        )"""
    )
    return conn


def _clipboard_get() -> dict[str, Any]:
    """Get current clipboard content and save to history."""
    if not _HAS_PYPERCLIP:
        return {"error": "pyperclip not installed. Run: pip install pyperclip"}
    try:
        content = pyperclip.paste()
        # Save to history
        now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        with closing(_connection()) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO clipboard_history (id, content, copied_at) VALUES (?, ?, ?)",
                    (uuid.uuid4().hex[:12], content[:2000], now),
                )
        return {"content": content}
    except Exception as exc:
        return {"error": str(exc)}


def _clipboard_set(content: str) -> dict[str, Any]:
    """Set clipboard content."""
    if not _HAS_PYPERCLIP:
        return {"error": "pyperclip not installed. Run: pip install pyperclip"}
    try:
        pyperclip.copy(content)
        now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        with closing(_connection()) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO clipboard_history (id, content, copied_at) VALUES (?, ?, ?)",
                    (uuid.uuid4().hex[:12], content[:2000], now),
                )
        return {"copied": True, "length": len(content)}
    except Exception as exc:
        return {"error": str(exc)}


def _clipboard_history(limit: int = 10) -> dict[str, Any]:
    """Show recent clipboard history."""
    with closing(_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM clipboard_history ORDER BY copied_at DESC LIMIT ?", (limit,)
        ).fetchall()
    items = [dict(r) for r in rows]
    return {"count": len(items), "history": items}


# ── Register ────────────────────────────────────────────────────

registry.register(
    {
        "name": "clipboard_get", "description": "Get the current system clipboard content.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"content": {"type": "string"}}},
        "scopes": ["clipboard:read"], "tags": ["utility", "clipboard"],
    }, _clipboard_get,
)

registry.register(
    {
        "name": "clipboard_set", "description": "Copy text to the system clipboard.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]},
        "returns": {"type": "object", "properties": {"copied": {"type": "boolean"}}},
        "scopes": ["clipboard:write"], "tags": ["utility", "clipboard"],
    }, _clipboard_set,
)

registry.register(
    {
        "name": "clipboard_history", "description": "Show recent clipboard history entries.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "history": {"type": "array"}}},
        "scopes": ["clipboard:read"], "tags": ["utility", "clipboard"],
    }, _clipboard_history,
)
