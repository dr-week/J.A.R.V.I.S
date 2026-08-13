"""Workflow Automation plugin — Zero-code tool chaining engine.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import sqlite3
import json
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
        """CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            steps_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    return conn


def _workflow_create(name: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a multi-tool execution workflow."""
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    wf = {"id": uuid.uuid4().hex[:12], "name": name.strip(), "steps_json": json.dumps(steps), "created_at": now}
    with closing(_connection()) as conn:
        with conn:
            conn.execute("INSERT INTO workflows (id, name, steps_json, created_at) VALUES (:id, :name, :steps_json, :created_at)", wf)
    return {"id": wf["id"], "name": name, "step_count": len(steps)}


async def _workflow_run(workflow_id: str) -> dict[str, Any]:
    """Execute all tool steps in a saved workflow sequentially."""
    with closing(_connection()) as conn:
        row = conn.execute("SELECT * FROM workflows WHERE id=?", (workflow_id,)).fetchone()
        if not row:
            raise ValueError(f"No workflow found with id '{workflow_id}'.")
        steps = json.loads(row["steps_json"])
    
    results = []
    for step in steps:
        tool_name = step.get("tool")
        params = step.get("params", {})
        res = await registry.execute(tool_name, params)
        results.append({"tool": tool_name, "output": res})
        
    return {"workflow_id": workflow_id, "name": row["name"], "executed_steps": len(results), "results": results}


registry.register(
    {
        "name": "workflow_create",
        "description": "Create a sequential multi-tool automation workflow.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_once",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "steps": {"type": "array"},
            },
            "required": ["name", "steps"],
        },
        "returns": {"type": "object", "properties": {"id": {"type": "string"}}},
        "scopes": ["workflows:write"],
        "tags": ["workflows", "automation"],
    },
    _workflow_create,
)

registry.register(
    {
        "name": "workflow_run",
        "description": "Execute a saved multi-tool automation workflow by id.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_always",
        "executor": "brain",
        "parameters": {"type": "object", "properties": {"workflow_id": {"type": "string"}}, "required": ["workflow_id"]},
        "returns": {"type": "object", "properties": {"executed_steps": {"type": "integer"}}},
        "scopes": ["workflows:execute"],
        "tags": ["workflows", "automation"],
    },
    _workflow_run,
)
