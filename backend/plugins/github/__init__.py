"""GitHub connector plugin (Phase 3).

Authentication is intentionally brain-local: the token is read from the
brain process environment and is never exposed in tool arguments or results.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from backend.app.hands import registry

_GITHUB_API = "https://api.github.com"


def _token() -> str:
    return os.environ.get("JARVIS_GITHUB_TOKEN", "").strip()


def _default_repository() -> str:
    return os.environ.get("JARVIS_GITHUB_REPOSITORY", "").strip()


def _github_issues_list(repo: str = "", state: str = "open", limit: int = 20) -> dict[str, Any]:
    """Return a concise list of issues from one GitHub repository."""
    token = _token()
    repository = (repo or _default_repository()).strip()
    if not token:
        raise RuntimeError("GitHub is not configured. Set JARVIS_GITHUB_TOKEN on the brain host.")
    if not repository or "/" not in repository:
        raise ValueError("repo must be an owner/repository value, or set JARVIS_GITHUB_REPOSITORY on the brain host.")
    if state not in {"open", "closed", "all"}:
        raise ValueError("state must be 'open', 'closed', or 'all'.")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")

    response = httpx.get(
        f"{_GITHUB_API}/repos/{repository}/issues",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        params={"state": state, "per_page": limit},
        timeout=10.0,
    )
    response.raise_for_status()
    issues = [
        {
            "number": issue["number"], "title": issue["title"], "state": issue["state"],
            "url": issue["html_url"], "updated_at": issue["updated_at"],
        }
        for issue in response.json()
        if "pull_request" not in issue
    ]
    return {"repository": repository, "count": len(issues), "issues": issues}


registry.register(
    {
        "name": "github_issues_list",
        "description": "List GitHub issues in a repository using the brain-local GitHub token.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "repo": {"type": "string", "description": "GitHub repository as owner/repository."},
            "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
        }, "required": []},
        "returns": {"type": "object", "properties": {
            "repository": {"type": "string"}, "count": {"type": "integer"}, "issues": {"type": "array"},
        }},
        "scopes": ["github:issues:read"], "tags": ["github", "connector", "productivity"],
    },
    _github_issues_list,
)
