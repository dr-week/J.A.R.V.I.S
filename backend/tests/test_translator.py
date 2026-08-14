"""Tests for offline neural translation plugin (argostranslate wrapper).

Verifies tool registration in Hands registry, parameter schema validation,
offline uninitialized fallback behavior, and mocked argostranslate execution per docs/OSS.md (Pattern 1).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.translator import _translate_text

# Ensure all plugins are discovered
registry.discover_plugins()


def test_translate_tool_registered():
    """Verify translate_text tool is properly registered in registry."""
    assert "translate_text" in registry.REGISTRY
    tool_def = registry.REGISTRY["translate_text"]
    assert tool_def["name"] == "translate_text"
    assert tool_def["phase"] == 6
    assert "text" in tool_def["parameters"]["properties"]
    assert "from_code" in tool_def["parameters"]["properties"]
    assert "to_code" in tool_def["parameters"]["properties"]
    assert tool_def["parameters"]["required"] == ["text"]


@pytest.mark.asyncio
async def test_translate_empty_text():
    """Verify translate_text rejects empty text input."""
    res = await registry.execute("translate_text", {"text": "  "})
    assert "result" in res or "error" in res
    output = res.get("result", res)
    assert "error" in output
    assert "cannot be empty" in output["error"]


@pytest.mark.asyncio
async def test_translate_uninitialized_fallback():
    """Verify translate_text returns clean guidance when argostranslate is not installed."""
    with patch("backend.plugins.translator._HAS_ARGOS", False):
        res = await registry.execute(
            "translate_text",
            {"text": "Hello world", "from_code": "en", "to_code": "es"},
        )
        assert "result" in res
        result = res["result"]
        assert result.get("status") == "uninitialized"
        assert "error" in result
        assert "argostranslate is not installed" in result["error"]
        assert result["original"] == "Hello world"
        assert result["from_code"] == "en"
        assert result["to_code"] == "es"


@pytest.mark.asyncio
async def test_translate_mocked_success():
    """Verify translate_text translates text using argostranslate (Pattern 1 wrapper)."""
    mock_argos = MagicMock()
    mock_argos.translate.translate.return_value = "Hola Mundo"

    with patch("backend.plugins.translator._HAS_ARGOS", True), \
         patch("backend.plugins.translator.argostranslate", mock_argos):

        res = await registry.execute(
            "translate_text",
            {"text": "Hello World", "from_code": "en", "to_code": "es"},
        )

        assert "result" in res
        result = res["result"]
        assert result["status"] == "translated"
        assert result["original"] == "Hello World"
        assert result["translated"] == "Hola Mundo"
        assert result["from_code"] == "en"
        assert result["to_code"] == "es"
        mock_argos.translate.translate.assert_called_once_with("Hello World", "en", "es")


@pytest.mark.asyncio
async def test_translate_mocked_exception_handling():
    """Verify translate_text catches and formats translation errors gracefully."""
    mock_argos = MagicMock()
    mock_argos.translate.translate.side_effect = RuntimeError("Language model pair en->fr not installed")

    with patch("backend.plugins.translator._HAS_ARGOS", True), \
         patch("backend.plugins.translator.argostranslate", mock_argos):

        res = await registry.execute(
            "translate_text",
            {"text": "Good morning", "from_code": "en", "to_code": "fr"},
        )

        assert "result" in res
        result = res["result"]
        assert "error" in result
        assert "ArgosTranslate translation failed" in result["error"]


def test_direct_function_call():
    """Verify _translate_text direct invocation."""
    empty_res = _translate_text("")
    assert "error" in empty_res

    with patch("backend.plugins.translator._HAS_ARGOS", False):
        uninit_res = _translate_text("Test", "en", "de")
        assert uninit_res["status"] == "uninitialized"
        assert uninit_res["from_code"] == "en"
        assert uninit_res["to_code"] == "de"

    mock_argos = MagicMock()
    mock_argos.translate.translate.return_value = "Bonjour"
    with patch("backend.plugins.translator._HAS_ARGOS", True), \
         patch("backend.plugins.translator.argostranslate", mock_argos):
        res = _translate_text("Hello", "en", "fr")
        assert res["status"] == "translated"
        assert res["translated"] == "Bonjour"
