"""Reminder and day-planning tools (Phase 3 life tools).

The plugin keeps its small, durable reminder store in the central brain
database.  It self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime, timezone
from typing import Any

from backend.app.config import DB_PATH
from backend.app.hands import registry
from backend.app.soul.memory import list_memories


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(str(DB_PATH))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """CREATE TABLE IF NOT EXISTS reminders (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            due_at TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            cancelled_at TEXT DEFAULT NULL
        )"""
    )
    return connection


def _parse_due_at(value: str) -> datetime:
    """Validate ISO-8601 input and normalise it to an aware UTC instant."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("due_at must be an ISO-8601 date/time, e.g. 2026-08-08T09:00:00Z.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _set_reminder(title: str, due_at: str, notes: str = "") -> dict[str, str]:
    """Create a durable reminder due at the supplied ISO-8601 time."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("title cannot be empty.")
    due = _parse_due_at(due_at).isoformat().replace("+00:00", "Z")
    reminder = {
        "id": uuid.uuid4().hex[:12],
        "title": clean_title,
        "due_at": due,
        "notes": notes.strip(),
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    with closing(_connection()) as connection:
        with connection:
            connection.execute(
                "INSERT INTO reminders(id, title, due_at, notes, created_at) VALUES(:id, :title, :due_at, :notes, :created_at)",
                reminder,
            )
    return reminder


def _list_reminders(include_cancelled: bool = False) -> dict[str, Any]:
    query = "SELECT id, title, due_at, notes, created_at, cancelled_at FROM reminders"
    if not include_cancelled:
        query += " WHERE cancelled_at IS NULL"
    query += " ORDER BY due_at ASC, created_at ASC"
    with closing(_connection()) as connection:
        reminders = [dict(row) for row in connection.execute(query).fetchall()]
    return {"count": len(reminders), "reminders": reminders}


def _cancel_reminder(reminder_id: str) -> dict[str, Any]:
    with closing(_connection()) as connection:
        with connection:
            row = connection.execute(
                "SELECT id, title, cancelled_at FROM reminders WHERE id=?", (reminder_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"No reminder found with id '{reminder_id}'.")
            if row["cancelled_at"]:
                return {"id": row["id"], "title": row["title"], "cancelled": True, "already_cancelled": True}
            connection.execute(
                "UPDATE reminders SET cancelled_at=? WHERE id=?",
                (datetime.now(UTC).isoformat().replace("+00:00", "Z"), reminder_id),
            )
    return {"id": row["id"], "title": row["title"], "cancelled": True, "already_cancelled": False}


def _plan_today(date: str = "") -> dict[str, Any]:
    """Produce an ordered, local-brain plan from active reminders and memories."""
    target_date = datetime.fromisoformat(date).date() if date else datetime.now(UTC).date()
    now = datetime.now(UTC)
    active = _list_reminders()["reminders"]
    items: list[dict[str, str]] = []
    for reminder in active:
        due = _parse_due_at(reminder["due_at"])
        if due.date() == target_date or (target_date == now.date() and due < now):
            items.append(
                {
                    "time": due.strftime("%H:%M UTC"),
                    "title": reminder["title"],
                    "source": "reminder",
                    "reminder_id": reminder["id"],
                    "notes": reminder["notes"],
                }
            )

    context = [
        {"key": memory["key"], "value": memory["value"]}
        for memory in list_memories()
        if any(word in memory["key"].lower() for word in ("calendar", "schedule", "plan", "priority", "work"))
    ]
    return {
        "date": target_date.isoformat(),
        "ordered_plan": items,
        "count": len(items),
        "context": context,
        "message": "No reminders are due for this day." if not items else "Plan ordered by reminder due time.",
    }


registry.register(
    {
        "name": "reminder_set",
        "description": "Create a durable reminder for an ISO-8601 date and time.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"}, "due_at": {"type": "string", "format": "date-time"},
            "notes": {"type": "string"},
        }, "required": ["title", "due_at"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "due_at": {"type": "string"}}},
        "scopes": ["reminders:write"], "tags": ["productivity", "reminders"],
    }, _set_reminder,
)

registry.register(
    {
        "name": "reminder_list", "description": "List reminders ordered by due time.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"include_cancelled": {"type": "boolean"}}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "reminders": {"type": "array"}}},
        "scopes": ["reminders:read"], "tags": ["productivity", "reminders"],
    }, _list_reminders,
)

registry.register(
    {
        "name": "reminder_cancel", "description": "Cancel a reminder by its id.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_always", "executor": "brain",
        "parameters": {"type": "object", "properties": {"reminder_id": {"type": "string"}}, "required": ["reminder_id"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "cancelled": {"type": "boolean"}}},
        "scopes": ["reminders:write"], "tags": ["productivity", "reminders"],
    }, _cancel_reminder,
)

registry.register(
    {
        "name": "plan_today", "description": "Create an ordered daily plan from reminders and available brain context.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"date": {"type": "string", "format": "date"}}, "required": []},
        "returns": {"type": "object", "properties": {"date": {"type": "string"}, "ordered_plan": {"type": "array"}}},
        "scopes": ["reminders:read", "memory:read"], "tags": ["productivity", "planning"],
    }, _plan_today,
)
