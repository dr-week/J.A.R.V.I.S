"""Unit tests for Batch 1 and Batch 2 plugins.

Tests registration and execution of calendar, contacts, email, notes, news,
clipboard, screenshot_ocr, and media_control tools.
"""
from __future__ import annotations

import pytest
from backend.app.hands import registry


from backend.app.hands import registry

# Ensure all plugins in backend/plugins are discovered and registered
registry.discover_plugins()


from backend.app.hands import registry

# Ensure all plugins in backend/plugins are discovered and registered
registry.discover_plugins()


def test_batch1_plugins_registered():
    """Verify Batch 1 P0 plugins registered their tools."""
    tool_names = list(registry.REGISTRY.keys())
    
    # Calendar tools
    assert "calendar_add" in tool_names
    assert "calendar_list" in tool_names
    assert "calendar_today" in tool_names
    assert "calendar_delete" in tool_names

    # Contacts tools
    assert "contact_add" in tool_names
    assert "contact_search" in tool_names
    assert "contact_list" in tool_names
    assert "contact_edit" in tool_names
    assert "contact_delete" in tool_names

    # Email tools
    assert "email_inbox" in tool_names
    assert "email_search" in tool_names
    assert "email_read" in tool_names
    assert "email_send" in tool_names

    # Notes tools
    assert "note_create" in tool_names
    assert "note_search" in tool_names
    assert "note_list" in tool_names
    assert "note_edit" in tool_names
    assert "note_delete" in tool_names


def test_batch2_plugins_registered():
    """Verify Batch 2 P1 utility plugins registered their tools."""
    tool_names = list(registry.REGISTRY.keys())

    # News tools
    assert "news_headlines" in tool_names
    assert "news_search" in tool_names
    assert "news_add_feed" in tool_names

    # Clipboard tools
    assert "clipboard_get" in tool_names
    assert "clipboard_set" in tool_names
    assert "clipboard_history" in tool_names

    # Screenshot OCR tools
    assert "screenshot_take" in tool_names
    assert "screenshot_ocr" in tool_names

    # Media control tools
    assert "media_volume_get" in tool_names
    assert "media_volume_set" in tool_names
    assert "media_mute_toggle" in tool_names


@pytest.mark.asyncio
async def test_notes_plugin_crud():
    """Test notes create and list execution via registry."""
    assert "note_create" in registry.REGISTRY

    exec_res = await registry.execute("note_create", {"title": "Test Note", "content": "Important info", "tags": "test"})
    assert "result" in exec_res
    res = exec_res["result"]
    assert res.get("id") is not None
    assert res.get("title") == "Test Note"

    assert "note_list" in registry.REGISTRY
    exec_list_res = await registry.execute("note_list", {"limit": 5})
    assert "result" in exec_list_res
    list_res = exec_list_res["result"]
    assert list_res.get("count") >= 1


def test_batch3_and_4_plugins_registered():
    """Verify Batch 3, 4, and Telegram plugins registered their tools."""
    tool_names = list(registry.REGISTRY.keys())
    
    assert "notify_send" in tool_names
    assert "focus_start" in tool_names
    assert "focus_status" in tool_names
    assert "pdf_create_report" in tool_names
    assert "translate_text" in tool_names
    assert "habit_create" in tool_names
    assert "habit_check_in" in tool_names
    assert "habit_list" in tool_names
    assert "secret_store" in tool_names
    assert "secret_get" in tool_names
    assert "telegram_send" in tool_names


def test_batch5_plugins_registered():
    """Verify Batch 5 advanced plugins registered their tools."""
    tool_names = list(registry.REGISTRY.keys())
    
    assert "stt_transcribe" in tool_names
    assert "video_summarize" in tool_names
    assert "location_geocode" in tool_names
    assert "workflow_create" in tool_names
    assert "workflow_run" in tool_names
    assert "n8n_trigger_workflow" in tool_names


@pytest.mark.asyncio
async def test_workflow_engine_chaining():
    """Test creating and running a workflow tool chain via registry."""
    wf_res = await registry.execute(
        "workflow_create",
        {
            "name": "Test Workflow",
            "steps": [
                {"tool": "habit_list", "params": {}},
            ],
        },
    )
    assert "result" in wf_res
    wf_id = wf_res["result"]["id"]

    run_res = await registry.execute("workflow_run", {"workflow_id": wf_id})
    assert "result" in run_res
    assert run_res["result"]["executed_steps"] == 1
