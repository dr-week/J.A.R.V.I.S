"""Tests for LiteLLM unified model gateway plugin.

Covers:
- Tool registration in Hands registry
- Input validation (empty prompt/messages)
- Successful primary model completion (Gemini)
- Multi-provider fallback routing (Gemini -> OpenAI -> Ollama)
- Full fallback exhaustion and graceful error reporting
- Tool execution via Hands registry
- Provider credentials and endpoint resolution
- Custom fallback model hierarchies
- Uninitialized package handling
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.litellm_gateway import (
    DEFAULT_FALLBACK_MODELS,
    _resolve_provider_credentials,
    litellm_completion,
)

# Ensure plugins are discovered
registry.discover_plugins()


def _build_mock_response(content: str, model: str, prompt_tokens: int = 10, completion_tokens: int = 20):
    resp = MagicMock()
    choice = MagicMock()
    choice.message = MagicMock()
    choice.message.content = content
    resp.choices = [choice]
    resp.model = model
    usage = MagicMock()
    usage.prompt_tokens = prompt_tokens
    usage.completion_tokens = completion_tokens
    usage.total_tokens = prompt_tokens + completion_tokens
    resp.usage = usage
    return resp


def test_litellm_plugin_registered():
    """Verify litellm_completion is registered in the Hands tool registry."""
    registry.discover_plugins()
    assert "litellm_completion" in registry.REGISTRY
    tool_def = registry.REGISTRY["litellm_completion"]
    assert tool_def["name"] == "litellm_completion"
    assert tool_def["phase"] == 3
    assert "llm:complete" in tool_def.get("scopes", [])
    assert "gateway" in tool_def.get("tags", [])


def test_litellm_completion_empty_inputs():
    """Verify completion rejects empty prompt and empty messages."""
    res = litellm_completion(prompt="", messages=None)
    assert "error" in res
    assert "requires non-empty" in res["error"]


def test_litellm_completion_successful_primary():
    """Verify successful completion with primary Gemini model."""
    mock_resp = _build_mock_response("Hello, I am Jarvis via Gemini.", "gemini/gemini-2.0-flash")

    with patch("litellm.completion", return_value=mock_resp) as mock_complete:
        res = litellm_completion(prompt="Hello Jarvis", model="gemini/gemini-2.0-flash")

        assert res["status"] == "success"
        assert res["content"] == "Hello, I am Jarvis via Gemini."
        assert res["model"] == "gemini/gemini-2.0-flash"
        assert res["provider"] == "gemini"
        assert res["usage"]["total_tokens"] == 30
        assert res["fallbacks_attempted"] == ["gemini/gemini-2.0-flash"]
        mock_complete.assert_called_once()


def test_litellm_completion_fallback_routing():
    """Verify fallback routing to OpenAI when primary Gemini model fails."""
    mock_openai_resp = _build_mock_response("Hello from OpenAI fallback.", "openai/gpt-4o-mini")

    def side_effect(**kwargs):
        model = kwargs.get("model", "")
        if "gemini" in model:
            raise RuntimeError("Gemini API quota exceeded or connection timeout")
        return mock_openai_resp

    with patch("litellm.completion", side_effect=side_effect) as mock_complete:
        res = litellm_completion(
            prompt="Compute system summary",
            model="gemini/gemini-2.0-flash",
            fallback_models=["openai/gpt-4o-mini", "ollama/llama3"],
        )

        assert res["status"] == "success"
        assert res["content"] == "Hello from OpenAI fallback."
        assert res["model"] == "openai/gpt-4o-mini"
        assert res["provider"] == "openai"
        assert res["fallbacks_attempted"] == ["gemini/gemini-2.0-flash", "openai/gpt-4o-mini"]
        assert mock_complete.call_count == 2


def test_litellm_completion_all_fallbacks_fail():
    """Verify error reporting when all candidate models fail."""
    with patch("litellm.completion", side_effect=RuntimeError("Connection refused")) as mock_complete:
        res = litellm_completion(
            prompt="Ping",
            fallback_models=["gemini/gemini-2.0-flash", "openai/gpt-4o-mini", "ollama/llama3"],
        )

        assert res["status"] == "error"
        assert "LiteLLM completion failed for all candidate models" in res["error"]
        assert len(res["fallbacks_attempted"]) >= 3
        assert mock_complete.call_count >= 3


@pytest.mark.asyncio
async def test_litellm_completion_via_registry():
    """Verify tool execution through Hands registry dispatch."""
    registry.discover_plugins()
    mock_resp = _build_mock_response("Registry execution verified.", "gemini/gemini-2.0-flash")

    with patch("litellm.completion", return_value=mock_resp):
        res = await registry.execute("litellm_completion", {"prompt": "Run diagnosis"})
        assert "result" in res
        result = res["result"]
        assert result["status"] == "success"
        assert result["content"] == "Registry execution verified."


def test_resolve_provider_credentials():
    """Verify provider identification and credential resolution."""
    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "gemini-secret",
            "OPENAI_API_KEY": "openai-secret",
            "OLLAMA_API_BASE": "http://127.0.0.1:11434",
        },
    ):
        p1, k1, b1 = _resolve_provider_credentials("gemini/gemini-2.0-flash")
        assert p1 == "gemini"
        assert k1 == "gemini-secret"

        p2, k2, b2 = _resolve_provider_credentials("openai/gpt-4o-mini")
        assert p2 == "openai"
        assert k2 == "openai-secret"

        p3, k3, b3 = _resolve_provider_credentials("ollama/llama3")
        assert p3 == "ollama"
        assert b3 == "http://127.0.0.1:11434"


def test_litellm_custom_messages_input():
    """Verify messages list parameter is properly passed."""
    mock_resp = _build_mock_response("Response to multi-turn.", "ollama/llama3")
    messages = [
        {"role": "system", "content": "You are Jarvis."},
        {"role": "user", "content": "What is status?"},
    ]

    with patch("litellm.completion", return_value=mock_resp) as mock_complete:
        res = litellm_completion(messages=messages, model="ollama/llama3")
        assert res["status"] == "success"
        assert res["model"] == "ollama/llama3"
        call_kwargs = mock_complete.call_args[1]
        assert call_kwargs["messages"] == messages


def test_litellm_uninitialized_fallback():
    """Verify uninitialized status when litellm is not available."""
    with patch("backend.plugins.litellm_gateway._HAS_LITELLM", False), patch(
        "backend.plugins.litellm_gateway.litellm", None
    ):
        res = litellm_completion(prompt="Hello")
        assert res["status"] == "uninitialized"
        assert "not installed" in res["error"]
