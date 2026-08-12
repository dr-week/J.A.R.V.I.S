"""Calendar plugin — local iCalendar-based event management.

Stores events in the central brain SQLite database.
Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime, timedelta
from typing import Any

from backend.app.config import DB_PATH
from backend.app.hands import registry


def _connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS calendar_events (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            start_at TEXT NOT NULL,
            end_at TEXT,
            location TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            all_day INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )"""
    )
    return conn


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _calendar_add(
    title: str,
    start_at: str,
    end_at: str = "",
    location: str = "",
    description: str = "",
    all_day: bool = False,
) -> dict[str, Any]:
    """Create a calendar event."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("title cannot be empty.")
    event = {
        "id": uuid.uuid4().hex[:12],
        "title": clean_title,
        "start_at": start_at,
        "end_at": end_at or start_at,
        "location": location.strip(),
        "description": description.strip(),
        "all_day": 1 if all_day else 0,
        "created_at": _now_iso(),
    }
    with closing(_connection()) as conn:
        with conn:
            conn.execute(
                """INSERT INTO calendar_events
                   (id, title, start_at, end_at, location, description, all_day, created_at)
                   VALUES(:id, :title, :start_at, :end_at, :location, :description, :all_day, :created_at)""",
                event,
            )
    event["all_day"] = bool(event["all_day"])
    return event


def _calendar_list(start_date: str = "", end_date: str = "", limit: int = 50) -> dict[str, Any]:
    """List events in a date range (defaults to next 7 days)."""
    if not start_date:
        start_date = datetime.now(UTC).date().isoformat()
    if not end_date:
        end_date = (datetime.now(UTC).date() + timedelta(days=7)).isoformat()
    with closing(_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM calendar_events WHERE start_at >= ? AND start_at <= ? ORDER BY start_at ASC LIMIT ?",
            (start_date, end_date + "T23:59:59Z", limit),
        ).fetchall()
    events = [dict(r) for r in rows]
    for e in events:
        e["all_day"] = bool(e["all_day"])
    return {"count": len(events), "events": events}


def _calendar_today() -> dict[str, Any]:
    """List today's events."""
    today = datetime.now(UTC).date().isoformat()
    return _calendar_list(start_date=today, end_date=today)


def _calendar_delete(event_id: str) -> dict[str, Any]:
    """Delete a calendar event by id."""
    with closing(_connection()) as conn:
        with conn:
            row = conn.execute("SELECT id, title FROM calendar_events WHERE id=?", (event_id,)).fetchone()
            if not row:
                raise ValueError(f"No event found with id '{event_id}'.")
            conn.execute("DELETE FROM calendar_events WHERE id=?", (event_id,))
    return {"id": row["id"], "title": row["title"], "deleted": True}


# ── Register tools ──────────────────────────────────────────────

registry.register(
    {
        "name": "calendar_add", "description": "Create a calendar event with title, start/end time, and optional location.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"}, "start_at": {"type": "string", "format": "date-time"},
            "end_at": {"type": "string", "format": "date-time"}, "location": {"type": "string"},
            "description": {"type": "string"}, "all_day": {"type": "boolean"},
        }, "required": ["title", "start_at"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "title": {"type": "string"}}},
        "scopes": ["calendar:write"], "tags": ["productivity", "calendar"],
    }, _calendar_add,
)

registry.register(
    {
        "name": "calendar_list", "description": "List calendar events in a date range (default: next 7 days).",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "start_date": {"type": "string", "format": "date"}, "end_date": {"type": "string", "format": "date"},
            "limit": {"type": "integer"},
        }, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "events": {"type": "array"}}},
        "scopes": ["calendar:read"], "tags": ["productivity", "calendar"],
    }, _calendar_list,
)

registry.register(
    {
        "name": "calendar_today", "description": "List today's calendar events.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "events": {"type": "array"}}},
        "scopes": ["calendar:read"], "tags": ["productivity", "calendar"],
    }, _calendar_today,
)

registry.register(
    {
        "name": "calendar_delete", "description": "Delete a calendar event by its id.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_always", "executor": "brain",
        "parameters": {"type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "deleted": {"type": "boolean"}}},
        "scopes": ["calendar:write"], "tags": ["productivity", "calendar"],
    }, _calendar_delete,
)
