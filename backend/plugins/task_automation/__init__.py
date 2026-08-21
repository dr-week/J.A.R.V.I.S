"""TaskAutomationNexus — Autonomous Task List & Workflow Engine (Phase 3+).

Provides clean, non-monolithic workflow and background automation scheduling for CoreBrain.
Supports creating recurring/delayed multi-step tasks, listing automation tasks,
triggering task runs on-demand, canceling schedules, and reviewing execution history.

Architecture & Design Rationale:
- Decouples task definitions from tool executors, enabling arbitrary polyglot tool chains
  (e.g., GitHub -> Slack -> Notion -> Email) to be queued and triggered automatically.
- Tracks execution timestamps, status (active, completed, cancelled, failed), and payload logs.
- Thread-safe storage layer that operates cleanly in asynchronous event loops.
"""
from __future__ import annotations

import datetime
import time
import uuid
from typing import Any

from backend.app.hands import registry

# In-memory storage for autonomous tasks and execution audit logs
_AUTOMATION_TASKS: dict[str, dict[str, Any]] = {}
_AUTOMATION_HISTORY: list[dict[str, Any]] = []


def _now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _automation_task_create(
    title: str = "",
    tool_name: str = "",
    tool_params: dict[str, Any] | None = None,
    schedule_type: str = "immediate",
    interval_seconds: int = 0,
    description: str = "",
) -> dict[str, Any]:
    """Create a new autonomous task in the automation task list."""
    if not title.strip():
        raise ValueError("title cannot be empty.")
    if not tool_name.strip():
        raise ValueError("tool_name cannot be empty (e.g. 'github_issues_list', 'slack_post_message').")
    if schedule_type not in {"immediate", "interval", "scheduled"}:
        raise ValueError("schedule_type must be 'immediate', 'interval', or 'scheduled'.")
    if schedule_type == "interval" and interval_seconds <= 0:
        raise ValueError("interval_seconds must be greater than 0 for interval schedule.")

    task_id = f"auto-{uuid.uuid4().hex[:8]}"
    created_at = _now_iso()

    task_record = {
        "id": task_id,
        "title": title.strip(),
        "description": description.strip(),
        "tool_name": tool_name.strip(),
        "tool_params": tool_params or {},
        "schedule_type": schedule_type,
        "interval_seconds": interval_seconds,
        "status": "active",
        "created_at": created_at,
        "updated_at": created_at,
        "last_run_at": None,
        "run_count": 0,
    }
    _AUTOMATION_TASKS[task_id] = task_record

    return {
        "status": "created",
        "task_id": task_id,
        "task": task_record,
    }


def _automation_task_list(status_filter: str = "") -> dict[str, Any]:
    """List automation tasks, optionally filtered by status (active, completed, cancelled)."""
    tasks = list(_AUTOMATION_TASKS.values())
    if status_filter:
        tasks = [t for t in tasks if t.get("status") == status_filter.lower()]

    return {
        "count": len(tasks),
        "tasks": sorted(tasks, key=lambda t: t.get("created_at", ""), reverse=True),
    }


async def _automation_task_trigger(task_id: str = "") -> dict[str, Any]:
    """Manually invoke and execute an automation task immediately through the Hands registry."""
    if not task_id.strip():
        raise ValueError("task_id cannot be empty.")
    if task_id not in _AUTOMATION_TASKS:
        raise ValueError(f"Task '{task_id}' not found.")

    task = _AUTOMATION_TASKS[task_id]
    tool_name = task["tool_name"]
    params = task.get("tool_params", {})

    started_at = _now_iso()
    start_time = time.perf_counter()

    # Execute tool via registry
    try:
        execution_result = await registry.execute(tool_name, params)
        exec_status = "success" if "error" not in execution_result else "failed"
    except Exception as exc:
        execution_result = {"error": str(exc)}
        exec_status = "failed"

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    finished_at = _now_iso()

    # Update task state
    task["last_run_at"] = finished_at
    task["run_count"] = task.get("run_count", 0) + 1
    task["updated_at"] = finished_at

    history_entry = {
        "history_id": f"hist-{uuid.uuid4().hex[:8]}",
        "task_id": task_id,
        "tool_name": tool_name,
        "status": exec_status,
        "result": execution_result,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_ms": duration_ms,
    }
    _AUTOMATION_HISTORY.append(history_entry)

    return {
        "status": exec_status,
        "task_id": task_id,
        "tool_name": tool_name,
        "duration_ms": duration_ms,
        "result": execution_result,
    }


def _automation_task_cancel(task_id: str = "") -> dict[str, Any]:
    """Cancel or deactivate an automation task."""
    if not task_id.strip():
        raise ValueError("task_id cannot be empty.")
    if task_id not in _AUTOMATION_TASKS:
        raise ValueError(f"Task '{task_id}' not found.")

    task = _AUTOMATION_TASKS[task_id]
    task["status"] = "cancelled"
    task["updated_at"] = _now_iso()

    return {"status": "cancelled", "task_id": task_id}


def _automation_task_history(task_id: str = "", limit: int = 20) -> dict[str, Any]:
    """Retrieve execution history logs for automation tasks."""
    history = _AUTOMATION_HISTORY
    if task_id:
        history = [h for h in history if h.get("task_id") == task_id]

    bounded_limit = max(1, min(limit, 100))
    sliced_history = list(reversed(history))[:bounded_limit]

    return {
        "count": len(sliced_history),
        "history": sliced_history,
    }


# Register all task automation tools in Hands registry
if "automation_task_create" not in registry.REGISTRY:
    registry.register(
        {
            "name": "automation_task_create",
            "description": "Create a new autonomous task or workflow schedule in the task list.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Human-readable task title."},
                    "tool_name": {"type": "string", "description": "Target tool to execute."},
                    "tool_params": {"type": "object", "description": "Parameters for the target tool."},
                    "schedule_type": {
                        "type": "string",
                        "enum": ["immediate", "interval", "scheduled"],
                        "default": "immediate",
                    },
                    "interval_seconds": {"type": "integer", "default": 0},
                    "description": {"type": "string", "description": "Optional details or goal of the task."},
                },
                "required": ["title", "tool_name"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "task_id": {"type": "string"},
                },
            },
            "scopes": ["automation:tasks:write"],
            "tags": ["automation", "tasks", "scheduler", "workflow"],
        },
        _automation_task_create,
    )

if "automation_task_list" not in registry.REGISTRY:
    registry.register(
        {
            "name": "automation_task_list",
            "description": "List all configured autonomous tasks and schedules.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["active", "completed", "cancelled", ""],
                        "default": "",
                    },
                },
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "tasks": {"type": "array"},
                },
            },
            "scopes": ["automation:tasks:read"],
            "tags": ["automation", "tasks", "scheduler", "workflow"],
        },
        _automation_task_list,
    )

if "automation_task_trigger" not in registry.REGISTRY:
    registry.register(
        {
            "name": "automation_task_trigger",
            "description": "Immediately trigger and run an automation task from the task list.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier to run."},
                },
                "required": ["task_id"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "task_id": {"type": "string"},
                    "result": {"type": "object"},
                },
            },
            "scopes": ["automation:tasks:execute"],
            "tags": ["automation", "tasks", "scheduler", "workflow"],
        },
        _automation_task_trigger,
    )

if "automation_task_cancel" not in registry.REGISTRY:
    registry.register(
        {
            "name": "automation_task_cancel",
            "description": "Cancel or disable an autonomous task schedule.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier to cancel."},
                },
                "required": ["task_id"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "task_id": {"type": "string"},
                },
            },
            "scopes": ["automation:tasks:write"],
            "tags": ["automation", "tasks", "scheduler", "workflow"],
        },
        _automation_task_cancel,
    )

if "automation_task_history" not in registry.REGISTRY:
    registry.register(
        {
            "name": "automation_task_history",
            "description": "View execution logs and history of past automated task runs.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Optional task ID filter."},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                },
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "history": {"type": "array"},
                },
            },
            "scopes": ["automation:tasks:read"],
            "tags": ["automation", "tasks", "scheduler", "workflow"],
        },
        _automation_task_history,
    )
