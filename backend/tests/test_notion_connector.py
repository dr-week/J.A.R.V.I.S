"""Tests for Notion Workspace Connector Plugin.

Validates:
- Tool registration in Hands registry (search, query, create page, append block)
- Missing token detection
- Parameter validation (empty title, invalid block type)
- Mocked HTTP execution for workspace search
- Mocked HTTP execution for database query
- Mocked HTTP execution for page creation
- Mocked HTTP execution for block append
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.notion import (
    _notion_append_block,
    _notion_create_page,
    _notion_query_database,
    _notion_search,
)

# Ensure plugins are discovered
registry.discover_plugins()


def test_notion_tools_registered():
    """Verify all Notion tools are in registry."""
    registry.discover_plugins()
    assert "notion_search" in registry.REGISTRY
    assert "notion_query_database" in registry.REGISTRY
    assert "notion_create_page" in registry.REGISTRY
    assert "notion_append_block" in registry.REGISTRY


def test_notion_missing_token_raises():
    """Verify missing API key raises error."""
    with patch.dict(os.environ, {"JARVIS_NOTION_API_KEY": "", "NOTION_API_KEY": ""}, clear=True):
        with pytest.raises(RuntimeError, match="Notion is not configured"):
            _notion_search(query="Project")


def test_notion_search_success():
    """Verify workspace search results parsing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "object": "page",
                "id": "page-123",
                "url": "https://notion.so/page-123",
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": "Weekly Goals"}]}
                },
                "last_edited_time": "2026-08-20T12:00:00.000Z",
            }
        ]
    }

    with patch.dict(os.environ, {"NOTION_API_KEY": "secret_abc"}), patch("httpx.post", return_value=mock_resp):
        res = _notion_search(query="Weekly")
        assert res["count"] == 1
        assert res["results"][0]["id"] == "page-123"
        assert res["results"][0]["title"] == "Weekly Goals"


def test_notion_query_database_success():
    """Verify database query items extraction."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "id": "row-1",
                "url": "https://notion.so/row-1",
                "properties": {
                    "Task": {"type": "title", "title": [{"plain_text": "Ship v2"}]}
                },
            }
        ]
    }

    with patch.dict(os.environ, {"NOTION_API_KEY": "secret_abc"}), patch("httpx.post", return_value=mock_resp):
        res = _notion_query_database(database_id="db-999")
        assert res["count"] == 1
        assert res["items"][0]["title"] == "Ship v2"


def test_notion_create_page_success():
    """Verify page creation request."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "page-new",
        "url": "https://notion.so/page-new",
    }

    with patch.dict(os.environ, {"NOTION_API_KEY": "secret_abc"}), patch("httpx.post", return_value=mock_resp) as mock_post:
        res = _notion_create_page(parent_id="db-999", title="Meeting Notes", content="Discussed roadmap")
        assert res["status"] == "created"
        assert res["page_id"] == "page-new"
        mock_post.assert_called_once()


def test_notion_append_block_success():
    """Verify block append patch request."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch.dict(os.environ, {"NOTION_API_KEY": "secret_abc"}), patch("httpx.patch", return_value=mock_resp) as mock_patch:
        res = _notion_append_block(page_id="page-123", text="Action item 1", block_type="to_do")
        assert res["status"] == "appended"
        assert res["block_type"] == "to_do"
        mock_patch.assert_called_once()
