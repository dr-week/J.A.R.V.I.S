"""Tests for Linear Connector Plugin.

Validates:
- Tool registration in Hands registry (list issues, create issue, update status, list teams)
- Missing token detection
- Parameter validation
- Mocked GraphQL execution for get issues
- Mocked GraphQL execution for issue creation
- Mocked GraphQL execution for issue status update
- Mocked GraphQL execution for get teams
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.linear import (
    _linear_create_issue,
    _linear_list_issues,
    _linear_list_teams,
    _linear_update_issue_status,
)

# Ensure plugins are discovered
registry.discover_plugins()


def test_linear_tools_registered():
    """Verify all Linear tools are in registry."""
    registry.discover_plugins()
    assert "linear_list_issues" in registry.REGISTRY
    assert "linear_create_issue" in registry.REGISTRY
    assert "linear_update_issue_status" in registry.REGISTRY
    assert "linear_list_teams" in registry.REGISTRY


def test_linear_missing_token_raises():
    """Verify missing API key raises error."""
    with patch.dict(os.environ, {"JARVIS_LINEAR_API_KEY": "", "LINEAR_API_KEY": ""}, clear=True):
        with pytest.raises(RuntimeError, match="Linear is not configured"):
            _linear_list_issues()


def test_linear_list_issues_success():
    """Verify GraphQL issues parsing and team key filtering."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "issues": {
                "nodes": [
                    {
                        "id": "iss-1",
                        "identifier": "ENG-101",
                        "title": "Fix memory leak",
                        "priority": 1,
                        "state": {"name": "In Progress"},
                        "assignee": {"name": "Alex"},
                        "url": "https://linear.app/team/issue/ENG-101",
                    },
                    {
                        "id": "iss-2",
                        "identifier": "DES-55",
                        "title": "New logo",
                        "priority": 2,
                        "state": {"name": "Backlog"},
                        "assignee": None,
                        "url": "https://linear.app/team/issue/DES-55",
                    },
                ]
            }
        }
    }

    with patch.dict(os.environ, {"LINEAR_API_KEY": "lin_api_test"}), patch("httpx.post", return_value=mock_resp):
        res = _linear_list_issues(team_key="ENG")
        assert res["count"] == 1
        assert res["issues"][0]["identifier"] == "ENG-101"
        assert res["issues"][0]["assignee"] == "Alex"


def test_linear_create_issue_success():
    """Verify issue creation GraphQL mutation."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "issueCreate": {
                "success": True,
                "issue": {
                    "id": "iss-new",
                    "identifier": "ENG-102",
                    "title": "Add voice STT",
                    "url": "https://linear.app/team/issue/ENG-102",
                },
            }
        }
    }

    with patch.dict(os.environ, {"LINEAR_API_KEY": "lin_api_test"}), patch("httpx.post", return_value=mock_resp) as mock_post:
        res = _linear_create_issue(team_id="team-eng", title="Add voice STT", description="Integrate Whisper")
        assert res["status"] == "created"
        assert res["identifier"] == "ENG-102"
        mock_post.assert_called_once()


def test_linear_update_issue_status_success():
    """Verify issue status update GraphQL mutation."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "issueUpdate": {
                "success": True,
                "issue": {
                    "id": "iss-101",
                    "identifier": "ENG-101",
                    "state": {"name": "Done"},
                },
            }
        }
    }

    with patch.dict(os.environ, {"LINEAR_API_KEY": "lin_api_test"}), patch("httpx.post", return_value=mock_resp) as mock_post:
        res = _linear_update_issue_status(issue_id="iss-101", state_id="state-done")
        assert res["status"] == "updated"
        assert res["state"] == "Done"
        mock_post.assert_called_once()


def test_linear_list_teams_success():
    """Verify get teams query."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "teams": {
                "nodes": [
                    {"id": "t-1", "name": "Engineering", "key": "ENG"},
                    {"id": "t-2", "name": "Design", "key": "DES"},
                ]
            }
        }
    }

    with patch.dict(os.environ, {"LINEAR_API_KEY": "lin_api_test"}), patch("httpx.post", return_value=mock_resp):
        res = _linear_list_teams()
        assert res["count"] == 2
        assert res["teams"][0]["key"] == "ENG"
