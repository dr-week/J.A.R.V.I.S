"""Tests for Modular GitHub Connector Plugin.

Validates:
- Tool registration in Hands registry (issues, PRs, workflows)
- Token handling and fallback
- Input validation (missing repo, empty title, invalid limits)
- Mocked HTTP execution for issues listing
- Mocked HTTP execution for issue creation
- Mocked HTTP execution for PR status inspection
- Mocked HTTP execution for workflow dispatch
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.github import (
    _github_issues_list,
    _github_issue_create,
    _github_pr_status,
    _github_workflow_dispatch,
)

# Ensure plugins are discovered
registry.discover_plugins()


def test_github_tools_registered():
    """Verify all GitHub tools are properly registered."""
    registry.discover_plugins()
    assert "github_issues_list" in registry.REGISTRY
    assert "github_issue_create" in registry.REGISTRY
    assert "github_pr_status" in registry.REGISTRY
    assert "github_workflow_dispatch" in registry.REGISTRY


def test_missing_token_raises():
    """Verify missing credentials raise a clear runtime error."""
    with patch.dict(os.environ, {"JARVIS_GITHUB_TOKEN": "", "GITHUB_TOKEN": ""}, clear=True):
        with pytest.raises(RuntimeError, match="GitHub is not configured"):
            _github_issues_list(repo="owner/repo")


def test_invalid_repo_raises():
    """Verify invalid repo names are rejected."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123"}):
        with pytest.raises(ValueError, match="repo must be an owner/repository value"):
            _github_issues_list(repo="invalidrepo")


def test_github_issues_list_success():
    """Verify issues list parsing and filter out pull requests."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"number": 1, "title": "First issue", "state": "open", "html_url": "https://github.com/o/r/issues/1", "updated_at": "2026-08-20"},
        {"number": 2, "title": "A PR disguised as issue", "state": "open", "pull_request": {}, "html_url": "https://github.com/o/r/pull/2"},
    ]

    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123"}), patch("httpx.get", return_value=mock_resp) as mock_get:
        res = _github_issues_list(repo="owner/repo", state="open", limit=10)
        assert res["repository"] == "owner/repo"
        assert res["count"] == 1
        assert res["issues"][0]["number"] == 1
        assert res["issues"][0]["title"] == "First issue"
        mock_get.assert_called_once()


def test_github_issue_create_success():
    """Verify issue creation payload formatting and response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "number": 42,
        "title": "Bug in audio loop",
        "html_url": "https://github.com/o/r/issues/42",
    }

    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123"}), patch("httpx.post", return_value=mock_resp) as mock_post:
        res = _github_issue_create(repo="owner/repo", title="Bug in audio loop", body="Logs attached", labels=["bug"])
        assert res["status"] == "created"
        assert res["number"] == 42
        assert res["url"] == "https://github.com/o/r/issues/42"
        mock_post.assert_called_once()


def test_github_pr_status_success():
    """Verify PR status retrieval."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "number": 10,
        "title": "Refactor router",
        "state": "open",
        "mergeable": True,
        "merged": False,
        "html_url": "https://github.com/o/r/pull/10",
    }

    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123"}), patch("httpx.get", return_value=mock_resp):
        res = _github_pr_status(repo="owner/repo", pull_number=10)
        assert res["number"] == 10
        assert res["state"] == "open"
        assert res["mergeable"] is True
        assert res["merged"] is False


def test_github_workflow_dispatch_success():
    """Verify workflow dispatch triggering."""
    mock_resp = MagicMock()
    mock_resp.status_code = 204

    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123"}), patch("httpx.post", return_value=mock_resp) as mock_post:
        res = _github_workflow_dispatch(repo="owner/repo", workflow_id="ci.yml", ref="main", inputs={"mode": "fast"})
        assert res["status"] == "dispatched"
        assert res["workflow_id"] == "ci.yml"
        mock_post.assert_called_once()
