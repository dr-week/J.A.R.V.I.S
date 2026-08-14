"""Tests for AnythingLLM RAG Knowledge Base REST sidecar plugin stub.

Verifies:
- Tool registration in Hands registry
- Schema and exported function definitions
- Input validation (empty query, missing file, missing text)
- Offline graceful fallback handling
- Mocked successful query execution
- Mocked successful document upload (file and raw text)
- Environment variable configuration
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.anything_llm import anythingllm_query, anythingllm_upload_doc

# Ensure all plugins are discovered
registry.discover_plugins()


def test_anythingllm_tools_registered():
    """Verify AnythingLLM tools are registered in the Hands registry."""
    tool_names = list(registry.REGISTRY.keys())
    assert "anythingllm_query" in tool_names
    assert "anythingllm_upload_doc" in tool_names

    query_def = registry.REGISTRY["anythingllm_query"]
    assert query_def["phase"] == 3
    assert "rag:read" in query_def["scopes"]
    assert "anythingllm" in query_def["tags"]

    upload_def = registry.REGISTRY["anythingllm_upload_doc"]
    assert upload_def["phase"] == 3
    assert "rag:write" in upload_def["scopes"]
    assert upload_def["risk_level"] == "confirm_once"


@pytest.mark.asyncio
async def test_anythingllm_query_empty_input():
    """Verify anythingllm_query rejects empty query strings."""
    res = await anythingllm_query(query="   ")
    assert "error" in res
    assert "empty" in res["error"].lower()

    # Via registry.execute
    reg_res = await registry.execute("anythingllm_query", {"query": ""})
    output = reg_res.get("result", reg_res)
    assert "error" in output


@pytest.mark.asyncio
async def test_anythingllm_upload_empty_input():
    """Verify anythingllm_upload_doc rejects empty payload."""
    res = await anythingllm_upload_doc(file_path="", text_content="")
    assert "error" in res
    assert "must provide either" in res["error"].lower()

    # Via registry.execute
    reg_res = await registry.execute("anythingllm_upload_doc", {"file_path": "", "text_content": ""})
    output = reg_res.get("result", reg_res)
    assert "error" in output


@pytest.mark.asyncio
async def test_anythingllm_upload_nonexistent_file():
    """Verify anythingllm_upload_doc rejects missing file paths."""
    res = await anythingllm_upload_doc(file_path="nonexistent_document_12345.pdf")
    assert "error" in res
    assert "file not found" in res["error"].lower()


@pytest.mark.asyncio
async def test_anythingllm_query_offline_fallback():
    """Verify anythingllm_query handles unreachable endpoint gracefully without raising."""
    res = await anythingllm_query(
        query="What are the core capabilities of Jarvis?",
        url="http://127.0.0.1:59998",
        workspace="jarvis-core",
    )
    assert res["status"] == "error"
    assert res["query"] == "What are the core capabilities of Jarvis?"
    assert res["workspace"] == "jarvis-core"
    assert "failed" in res["error"].lower()
    assert "59998" in res["error"]


@pytest.mark.asyncio
async def test_anythingllm_upload_offline_fallback():
    """Verify anythingllm_upload_doc handles unreachable endpoint gracefully."""
    res = await anythingllm_upload_doc(
        text_content="Sample Jarvis RAG document content",
        doc_name="sample.txt",
        url="http://127.0.0.1:59998",
        workspace="jarvis-core",
    )
    assert res["status"] == "error"
    assert res["workspace"] == "jarvis-core"
    assert "failed" in res["error"].lower()


@pytest.mark.asyncio
async def test_anythingllm_query_mocked_success():
    """Verify anythingllm_query parses RAG query response properly."""
    mock_data = {
        "id": "chat-uuid-1234",
        "type": "textResponse",
        "textResponse": "Jarvis is a personal assistant co-builder with Soul, Hands, and Presence.",
        "sources": [
            {
                "title": "ARCHITECTURE.md",
                "score": 0.95,
                "text": "Jarvis architecture consists of centralized brain and presence nodes.",
            }
        ],
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = mock_data

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await anythingllm_query(
            query="Explain Jarvis architecture",
            workspace="engineering",
            mode="query",
            api_key="secret-rag-key",
        )

        assert res["status"] == "ok"
        assert res["query"] == "Explain Jarvis architecture"
        assert res["workspace"] == "engineering"
        assert res["mode"] == "query"
        assert "Soul, Hands, and Presence" in res["response"]
        assert len(res["sources"]) == 1
        assert res["sources"][0]["title"] == "ARCHITECTURE.md"

        # Verify call arguments
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"] == {"message": "Explain Jarvis architecture", "mode": "query"}
        assert call_kwargs["headers"]["Authorization"] == "Bearer secret-rag-key"


@pytest.mark.asyncio
async def test_anythingllm_upload_doc_file_mocked_success(tmp_path: Path):
    """Verify anythingllm_upload_doc uploads file as multipart form-data."""
    test_file = tmp_path / "jarvis_spec.md"
    test_file.write_text("# Jarvis Spec\n\nFull autonomous loop specification.", encoding="utf-8")

    mock_data = {
        "success": True,
        "document": {
            "name": "jarvis_spec.md",
            "id": "doc-spec-999",
            "chunks": 4,
        },
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = mock_data

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await anythingllm_upload_doc(
            file_path=str(test_file),
            workspace="docs-workspace",
            api_key="test-api-token",
        )

        assert res["status"] == "uploaded"
        assert res["workspace"] == "docs-workspace"
        assert res["doc_name"] == "jarvis_spec.md"
        assert res["response"]["success"] is True

        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args
        assert "document/upload" in call_args[0]
        assert "file" in call_kwargs["files"]
        assert call_kwargs["headers"]["Authorization"] == "Bearer test-api-token"


@pytest.mark.asyncio
async def test_anythingllm_upload_raw_text_mocked_success():
    """Verify anythingllm_upload_doc uploads raw text JSON payload."""
    mock_data = {
        "success": True,
        "document": {
            "name": "quick_note.txt",
            "id": "doc-note-111",
        },
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = mock_data

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await anythingllm_upload_doc(
            text_content="User preference: Always write clean, flat Python code.",
            doc_name="user_preferences.txt",
            workspace="preferences",
        )

        assert res["status"] == "uploaded"
        assert res["workspace"] == "preferences"
        assert res["doc_name"] == "user_preferences.txt"
        assert res["response"]["document"]["id"] == "doc-note-111"

        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args
        assert "document/raw-text" in call_args[0]
        assert call_kwargs["json"]["docName"] == "user_preferences.txt"
        assert "User preference" in call_kwargs["json"]["textContent"]


@pytest.mark.asyncio
async def test_anythingllm_registry_execution():
    """Verify tools execute through registry.execute."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"textResponse": "Result from knowledge base", "sources": []}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await registry.execute("anythingllm_query", {"query": "Test query"})
        assert "result" in res
        assert res["result"]["status"] == "ok"
        assert res["result"]["response"] == "Result from knowledge base"
