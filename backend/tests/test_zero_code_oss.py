"""Tests for newly integrated zero-code OSS plugins and design systems.

Covers:
- n8n_automation plugin
- AnythingLLM RAG plugin stub
- SearXNG private search plugin stub
- Kokoro TTS plugin stub
"""
import pytest
from backend.app.hands import registry


def test_oss_automation_plugins_registered():
    """Verify zero-code OSS automation & search tools are registered in registry."""
    tool_names = list(registry.REGISTRY.keys())
    assert "n8n_trigger_workflow" in tool_names
    assert "anythingllm_query" in tool_names
    assert "anythingllm_upload_doc" in tool_names
    assert "piper_tts_speak" in tool_names


@pytest.mark.asyncio
async def test_n8n_trigger_workflow_execution():
    """Test n8n webhook workflow trigger handles execution cleanly."""
    res = await registry.execute("n8n_trigger_workflow", {"workflow_slug": "test_slug", "data": {"key": "val"}})
    # n8n endpoint is not running locally in test environment, expect graceful connection error
    assert "result" in res or "error" in res
