"""Tests for TaskAutomationNexus Plugin.

Validates:
- Tool registration in Hands registry (create, list, trigger, cancel, history)
- Input validation (missing title, invalid schedule type)
- Task creation and retrieval
- Task filtering by status
- Manual execution trigger dispatching via Hands registry
- Task cancellation
- Execution history logging
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.task_automation import (
    _automation_task_cancel,
    _automation_task_create,
    _automation_task_history,
    _automation_task_list,
    _automation_task_trigger,
)

# Ensure plugins are discovered
registry.discover_plugins()


def test_task_automation_tools_registered():
    """Verify all automation tools are in registry."""
    registry.discover_plugins()
    assert "automation_task_create" in registry.REGISTRY
    assert "automation_task_list" in registry.REGISTRY
    assert "automation_task_trigger" in registry.REGISTRY
    assert "automation_task_cancel" in registry.REGISTRY
    assert "automation_task_history" in registry.REGISTRY


def test_automation_task_create_validation():
    """Verify validation for empty title/tool or invalid schedule."""
    with pytest.raises(ValueError, match="title cannot be empty"):
        _automation_task_create(title="", tool_name="hello_world")

    with pytest.raises(ValueError, match="tool_name cannot be empty"):
        _automation_task_create(title="My task", tool_name="")

    with pytest.raises(ValueError, match="schedule_type must be"):
        _automation_task_create(title="My task", tool_name="hello_world", schedule_type="invalid")


def test_automation_task_lifecycle_create_and_list():
    """Verify task creation and listing."""
    res = _automation_task_create(
        title="Sync Daily GitHub Issues",
        tool_name="github_issues_list",
        tool_params={"repo": "owner/repo"},
        schedule_type="interval",
        interval_seconds=3600,
        description="Sync daily issues from GitHub",
    )
    assert res["status"] == "created"
    task_id = res["task_id"]
    assert task_id.startswith("auto-")
    assert res["task"]["title"] == "Sync Daily GitHub Issues"

    # List tasks
    list_res = _automation_task_list(status_filter="active")
    assert list_res["count"] >= 1
    found = any(t["id"] == task_id for t in list_res["tasks"])
    assert found is True


@pytest.mark.asyncio
async def test_automation_task_trigger_and_history():
    """Verify executing an automation task records execution history."""
    c_res = _automation_task_create(
        title="Trigger Test Task",
        tool_name="get_current_time",
    )
    task_id = c_res["task_id"]

    with patch("backend.app.hands.registry.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"time": "2026-08-21T08:00:00Z"}
        
        exec_res = await _automation_task_trigger(task_id=task_id)
        assert exec_res["status"] == "success"
        assert exec_res["task_id"] == task_id
        assert exec_res["result"] == {"time": "2026-08-21T08:00:00Z"}
        mock_exec.assert_called_once_with("get_current_time", {})

    # Check history
    hist_res = _automation_task_history(task_id=task_id)
    assert hist_res["count"] >= 1
    assert hist_res["history"][0]["task_id"] == task_id
    assert hist_res["history"][0]["status"] == "success"


def test_automation_task_cancel():
    """Verify cancelling an automation task."""
    c_res = _automation_task_create(
        title="Cancel Target Task",
        tool_name="hello_world",
    )
    task_id = c_res["task_id"]

    cancel_res = _automation_task_cancel(task_id=task_id)
    assert cancel_res["status"] == "cancelled"

    list_res = _automation_task_list(status_filter="cancelled")
    assert any(t["id"] == task_id for t in list_res["tasks"])
