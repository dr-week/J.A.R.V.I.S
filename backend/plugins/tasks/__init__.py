"""Task management tools (Phase 3 life tools).

The plugin keeps its small, durable task store in the central brain
database. It self-registers when ``discover_plugins`` scans this package.
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
    connection = sqlite3.connect(str(DB_PATH))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            completed_at TEXT DEFAULT NULL
        )"""
    )
    return connection


def _task_add(title: str, description: str = "") -> dict[str, str]:
    """Create a durable task."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("title cannot be empty.")
    
    task = {
        "id": uuid.uuid4().hex[:12],
        "title": clean_title,
        "description": description.strip(),
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    with closing(_connection()) as connection:
        with connection:
            connection.execute(
                "INSERT INTO tasks(id, title, description, created_at) VALUES(:id, :title, :description, :created_at)",
                task,
            )
    return task


def _task_list(include_completed: bool = False) -> dict[str, Any]:
    query = "SELECT id, title, description, created_at, completed_at FROM tasks"
    if not include_completed:
        query += " WHERE completed_at IS NULL"
    query += " ORDER BY created_at ASC"
    
    with closing(_connection()) as connection:
        tasks = [dict(row) for row in connection.execute(query).fetchall()]
    return {"count": len(tasks), "tasks": tasks}


def _task_complete(task_id: str) -> dict[str, Any]:
    with closing(_connection()) as connection:
        with connection:
            row = connection.execute(
                "SELECT id, title, completed_at FROM tasks WHERE id=?", (task_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"No task found with id '{task_id}'.")
            if row["completed_at"]:
                return {"id": row["id"], "title": row["title"], "completed": True, "already_completed": True}
            
            connection.execute(
                "UPDATE tasks SET completed_at=? WHERE id=?",
                (datetime.now(UTC).isoformat().replace("+00:00", "Z"), task_id),
            )
    return {"id": row["id"], "title": row["title"], "completed": True, "already_completed": False}


registry.register(
    {
        "name": "task_add",
        "description": "Add a new task to the task list.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
        }, "required": ["title"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}}},
        "scopes": ["tasks:write"], "tags": ["productivity", "tasks"],
    }, _task_add,
)

registry.register(
    {
        "name": "task_list", "description": "List all tasks.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"include_completed": {"type": "boolean"}}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "tasks": {"type": "array"}}},
        "scopes": ["tasks:read"], "tags": ["productivity", "tasks"],
    }, _task_list,
)

registry.register(
    {
        "name": "task_complete", "description": "Mark a task as completed by its id.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "completed": {"type": "boolean"}}},
        "scopes": ["tasks:write"], "tags": ["productivity", "tasks"],
    }, _task_complete,
)
