"""GitHub Modular Connector Plugin (Phase 3+).

Provides clean, non-monolithic GitHub integration tools for CoreBrain.
Supports issue listing/creation, pull request status inspection, and workflow dispatch.

Authentication & Security Rationale:
- Token is read brain-locally from `JARVIS_GITHUB_TOKEN` or `GITHUB_TOKEN`.
- The token is never leaked or passed through tool call arguments.
- Safe parameters and strict validation prevent command injection.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from backend.app.hands import registry

_GITHUB_API = "https://api.github.com"


def _token() -> str:
    """Retrieve GitHub token from environment variables (safe fallback)."""
    return (os.environ.get("JARVIS_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()


def _default_repository() -> str:
    """Retrieve default target repository if configured."""
    return os.environ.get("JARVIS_GITHUB_REPOSITORY", "").strip()


def _get_headers() -> dict[str, str]:
    """Construct standard GitHub REST API request headers."""
    token = _token()
    if not token:
        raise RuntimeError("GitHub is not configured. Set JARVIS_GITHUB_TOKEN or GITHUB_TOKEN.")
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _github_issues_list(repo: str = "", state: str = "open", limit: int = 20) -> dict[str, Any]:
    """Return a concise list of issues from one GitHub repository."""
    repository = (repo or _default_repository()).strip()
    if not repository or "/" not in repository:
        raise ValueError("repo must be an owner/repository value, or set JARVIS_GITHUB_REPOSITORY.")
    if state not in {"open", "closed", "all"}:
        raise ValueError("state must be 'open', 'closed', or 'all'.")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")

    response = httpx.get(
        f"{_GITHUB_API}/repos/{repository}/issues",
        headers=_get_headers(),
        params={"state": state, "per_page": limit},
        timeout=10.0,
    )
    response.raise_for_status()
    issues = [
        {
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"],
            "url": issue.get("html_url", ""),
            "updated_at": issue.get("updated_at", ""),
        }
        for issue in response.json()
        if "pull_request" not in issue
    ]
    return {"repository": repository, "count": len(issues), "issues": issues}


def _github_issue_create(
    repo: str = "",
    title: str = "",
    body: str = "",
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new issue on a GitHub repository."""
    repository = (repo or _default_repository()).strip()
    if not repository or "/" not in repository:
        raise ValueError("repo must be an owner/repository value, or set JARVIS_GITHUB_REPOSITORY.")
    if not title.strip():
        raise ValueError("title cannot be empty.")

    payload: dict[str, Any] = {"title": title.strip(), "body": body.strip()}
    if labels:
        payload["labels"] = labels

    response = httpx.post(
        f"{_GITHUB_API}/repos/{repository}/issues",
        headers=_get_headers(),
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "status": "created",
        "repository": repository,
        "number": data.get("number"),
        "title": data.get("title"),
        "url": data.get("html_url"),
    }


def _github_pr_status(repo: str = "", pull_number: int = 1) -> dict[str, Any]:
    """Retrieve status, mergeability, and state of a Pull Request."""
    repository = (repo or _default_repository()).strip()
    if not repository or "/" not in repository:
        raise ValueError("repo must be an owner/repository value, or set JARVIS_GITHUB_REPOSITORY.")
    if pull_number < 1:
        raise ValueError("pull_number must be a positive integer.")

    response = httpx.get(
        f"{_GITHUB_API}/repos/{repository}/pulls/{pull_number}",
        headers=_get_headers(),
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "repository": repository,
        "number": data.get("number"),
        "title": data.get("title"),
        "state": data.get("state"),
        "mergeable": data.get("mergeable"),
        "merged": data.get("merged", False),
        "url": data.get("html_url"),
    }


def _github_workflow_dispatch(
    repo: str = "",
    workflow_id: str = "",
    ref: str = "main",
    inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Trigger a GitHub Actions workflow dispatch event."""
    repository = (repo or _default_repository()).strip()
    if not repository or "/" not in repository:
        raise ValueError("repo must be an owner/repository value, or set JARVIS_GITHUB_REPOSITORY.")
    if not workflow_id.strip():
        raise ValueError("workflow_id cannot be empty (e.g. 'ci.yml').")

    payload: dict[str, Any] = {"ref": ref}
    if inputs:
        payload["inputs"] = inputs

    response = httpx.post(
        f"{_GITHUB_API}/repos/{repository}/actions/workflows/{workflow_id.strip()}/dispatches",
        headers=_get_headers(),
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    return {
        "status": "dispatched",
        "repository": repository,
        "workflow_id": workflow_id,
        "ref": ref,
    }


# Register all GitHub tools to Hands Registry
if "github_issues_list" not in registry.REGISTRY:
    registry.register(
        {
            "name": "github_issues_list",
            "description": "List GitHub issues in a repository using the brain-local GitHub token.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "GitHub repository as owner/repository."},
                    "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                },
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "repository": {"type": "string"},
                    "count": {"type": "integer"},
                    "issues": {"type": "array"},
                },
            },
            "scopes": ["github:issues:read"],
            "tags": ["github", "connector", "productivity"],
        },
        _github_issues_list,
    )

if "github_issue_create" not in registry.REGISTRY:
    registry.register(
        {
            "name": "github_issue_create",
            "description": "Create a new issue on a GitHub repository.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Target repository as owner/repository."},
                    "title": {"type": "string", "description": "Issue title."},
                    "body": {"type": "string", "description": "Issue description/body."},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Issue labels."},
                },
                "required": ["title"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "number": {"type": "integer"},
                    "url": {"type": "string"},
                },
            },
            "scopes": ["github:issues:write"],
            "tags": ["github", "connector", "productivity"],
        },
        _github_issue_create,
    )

if "github_pr_status" not in registry.REGISTRY:
    registry.register(
        {
            "name": "github_pr_status",
            "description": "Check status and mergeability of a Pull Request.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Target repository as owner/repository."},
                    "pull_number": {"type": "integer", "description": "Pull request number."},
                },
                "required": ["pull_number"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "repository": {"type": "string"},
                    "number": {"type": "integer"},
                    "state": {"type": "string"},
                    "mergeable": {"type": "boolean"},
                },
            },
            "scopes": ["github:pulls:read"],
            "tags": ["github", "connector", "productivity"],
        },
        _github_pr_status,
    )

if "github_workflow_dispatch" not in registry.REGISTRY:
    registry.register(
        {
            "name": "github_workflow_dispatch",
            "description": "Trigger a GitHub Actions workflow dispatch event.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Target repository as owner/repository."},
                    "workflow_id": {"type": "string", "description": "Workflow ID or file (e.g. 'ci.yml')."},
                    "ref": {"type": "string", "description": "Git branch or ref to run on.", "default": "main"},
                    "inputs": {"type": "object", "description": "Optional workflow input parameters."},
                },
                "required": ["workflow_id"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "workflow_id": {"type": "string"},
                },
            },
            "scopes": ["github:actions:write"],
            "tags": ["github", "connector", "ci"],
        },
        _github_workflow_dispatch,
    )
