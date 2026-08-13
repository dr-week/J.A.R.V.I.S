"""Habit Tracker plugin — tracking daily habit streaks in SQLite.

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


def _connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS user_habits (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            last_completed TEXT,
            created_at TEXT NOT NULL
        )"""
    )
    return conn


def _habit_create(name: str) -> dict[str, Any]:
    """Create a new habit to track."""
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    habit = {"id": uuid.uuid4().hex[:12], "name": name.strip(), "streak": 0, "last_completed": None, "created_at": now}
    with closing(_connection()) as conn:
        with conn:
            conn.execute("INSERT INTO user_habits (id, name, streak, last_completed, created_at) VALUES (:id, :name, :streak, :last_completed, :created_at)", habit)
    return habit


def _habit_check_in(habit_id: str) -> dict[str, Any]:
    """Check in a completed habit for today."""
    today = datetime.now(UTC).date().isoformat()
    with closing(_connection()) as conn:
        with conn:
            row = conn.execute("SELECT * FROM user_habits WHERE id=?", (habit_id,)).fetchone()
            if not row:
                raise ValueError(f"No habit found with id '{habit_id}'.")
            if row["last_completed"] == today:
                return {"id": habit_id, "already_completed_today": True, "streak": row["streak"]}
            new_streak = row["streak"] + 1
            conn.execute("UPDATE user_habits SET streak=?, last_completed=? WHERE id=?", (new_streak, today, habit_id))
    return {"id": habit_id, "checked_in": True, "streak": new_streak}


def _habit_list() -> dict[str, Any]:
    """List all tracked habits and current streaks."""
    with closing(_connection()) as conn:
        rows = conn.execute("SELECT * FROM user_habits ORDER BY streak DESC").fetchall()
    habits = [dict(r) for r in rows]
    return {"count": len(habits), "habits": habits}


registry.register(
    {
        "name": "habit_create",
        "description": "Create a new daily habit to track.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_once",
        "executor": "brain",
        "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}}},
        "scopes": ["habits:write"],
        "tags": ["productivity", "habits"],
    },
    _habit_create,
)

registry.register(
    {
        "name": "habit_check_in",
        "description": "Check in a habit completed today to increment its streak.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {"type": "object", "properties": {"habit_id": {"type": "string"}}, "required": ["habit_id"]},
        "returns": {"type": "object", "properties": {"streak": {"type": "integer"}}},
        "scopes": ["habits:write"],
        "tags": ["productivity", "habits"],
    },
    _habit_check_in,
)

registry.register(
    {
        "name": "habit_list",
        "description": "List tracked habits and their current streaks.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "habits": {"type": "array"}}},
        "scopes": ["habits:read"],
        "tags": ["productivity", "habits"],
    },
    _habit_list,
)
