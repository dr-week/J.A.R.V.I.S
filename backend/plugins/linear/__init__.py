"""Linear Project & Issue Management Connector Plugin (Phase 3+).

Provides clean, non-monolithic Linear GraphQL API integration for CoreBrain.
Supports querying team issues, creating issues, updating issue states, and listing teams.

Architecture & Security Rationale:
- Token is read brain-locally from `JARVIS_LINEAR_API_KEY` or `LINEAR_API_KEY`.
- Queries the official Linear GraphQL endpoint (`https://api.linear.app/graphql`).
- Never exposes API keys in tool parameters or execution audit logs.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from backend.app.hands import registry

_LINEAR_GRAPHQL_API = "https://api.linear.app/graphql"


def _token() -> str:
    """Retrieve Linear API key from environment variables."""
    return (os.environ.get("JARVIS_LINEAR_API_KEY") or os.environ.get("LINEAR_API_KEY") or "").strip()


def _get_headers() -> dict[str, str]:
    """Construct standard Linear GraphQL request headers."""
    token = _token()
    if not token:
        raise RuntimeError("Linear is not configured. Set JARVIS_LINEAR_API_KEY or LINEAR_API_KEY.")
    return {
        "Content-Type": "application/json",
        "Authorization": token,
    }


def _execute_query(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute a GraphQL query or mutation against Linear API."""
    payload: dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    response = httpx.post(
        _LINEAR_GRAPHQL_API,
        headers=_get_headers(),
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data and data["errors"]:
        error_msg = data["errors"][0].get("message", "Linear GraphQL Error")
        raise RuntimeError(f"Linear API error: {error_msg}")
    return data.get("data", {})


def _linear_list_issues(team_key: str = "", limit: int = 20) -> dict[str, Any]:
    """List issues from Linear, optionally filtered by team key."""
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")

    query = """
    query GetIssues($first: Int) {
      issues(first: $first) {
        nodes {
          id
          identifier
          title
          priority
          state {
            name
            type
          }
          assignee {
            name
          }
          url
        }
      }
    }
    """
    data = _execute_query(query, {"first": limit})
    raw_nodes = data.get("issues", {}).get("nodes", [])

    issues = []
    for node in raw_nodes:
        ident = node.get("identifier", "")
        if team_key and not ident.startswith(team_key.upper()):
            continue
        issues.append({
            "id": node.get("id"),
            "identifier": ident,
            "title": node.get("title"),
            "state": node.get("state", {}).get("name", "Unknown"),
            "priority": node.get("priority", 0),
            "assignee": node.get("assignee", {}).get("name") if node.get("assignee") else None,
            "url": node.get("url"),
        })

    return {"count": len(issues), "issues": issues}


def _linear_create_issue(
    team_id: str = "",
    title: str = "",
    description: str = "",
    priority: int = 0,
) -> dict[str, Any]:
    """Create a new issue in Linear."""
    if not team_id.strip():
        raise ValueError("team_id cannot be empty.")
    if not title.strip():
        raise ValueError("title cannot be empty.")

    mutation = """
    mutation CreateIssue($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
          url
        }
      }
    }
    """
    variables = {
        "input": {
            "teamId": team_id.strip(),
            "title": title.strip(),
            "description": description.strip(),
            "priority": priority,
        }
    }
    data = _execute_query(mutation, variables)
    create_result = data.get("issueCreate", {})
    if not create_result.get("success"):
        raise RuntimeError("Failed to create Linear issue.")

    issue = create_result.get("issue", {})
    return {
        "status": "created",
        "id": issue.get("id"),
        "identifier": issue.get("identifier"),
        "title": issue.get("title"),
        "url": issue.get("url"),
    }


def _linear_update_issue_status(issue_id: str = "", state_id: str = "") -> dict[str, Any]:
    """Update the workflow state/status of an existing Linear issue."""
    if not issue_id.strip():
        raise ValueError("issue_id cannot be empty.")
    if not state_id.strip():
        raise ValueError("state_id cannot be empty.")

    mutation = """
    mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue {
          id
          identifier
          state {
            name
          }
        }
      }
    }
    """
    variables = {
        "id": issue_id.strip(),
        "input": {"stateId": state_id.strip()},
    }
    data = _execute_query(mutation, variables)
    update_result = data.get("issueUpdate", {})
    if not update_result.get("success"):
        raise RuntimeError("Failed to update Linear issue state.")

    issue = update_result.get("issue", {})
    return {
        "status": "updated",
        "id": issue.get("id"),
        "identifier": issue.get("identifier"),
        "state": issue.get("state", {}).get("name"),
    }


def _linear_list_teams() -> dict[str, Any]:
    """List teams in the Linear organization."""
    query = """
    query GetTeams {
      teams {
        nodes {
          id
          name
          key
        }
      }
    }
    """
    data = _execute_query(query)
    teams = [
        {
            "id": node.get("id"),
            "name": node.get("name"),
            "key": node.get("key"),
        }
        for node in data.get("teams", {}).get("nodes", [])
    ]
    return {"count": len(teams), "teams": teams}


# Register Linear tools in Hands registry
if "linear_list_issues" not in registry.REGISTRY:
    registry.register(
        {
            "name": "linear_list_issues",
            "description": "List issues from Linear project management workspace.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_key": {"type": "string", "description": "Optional team prefix (e.g. 'ENG')."},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                },
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "issues": {"type": "array"},
                },
            },
            "scopes": ["linear:issues:read"],
            "tags": ["linear", "connector", "agile", "productivity"],
        },
        _linear_list_issues,
    )

if "linear_create_issue" not in registry.REGISTRY:
    registry.register(
        {
            "name": "linear_create_issue",
            "description": "Create a new issue on Linear with title, description, and team.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string", "description": "Team ID where the issue belongs."},
                    "title": {"type": "string", "description": "Issue title."},
                    "description": {"type": "string", "description": "Issue description / body."},
                    "priority": {"type": "integer", "enum": [0, 1, 2, 3, 4], "default": 0},
                },
                "required": ["team_id", "title"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "id": {"type": "string"},
                    "identifier": {"type": "string"},
                    "url": {"type": "string"},
                },
            },
            "scopes": ["linear:issues:write"],
            "tags": ["linear", "connector", "agile", "productivity"],
        },
        _linear_create_issue,
    )

if "linear_update_issue_status" not in registry.REGISTRY:
    registry.register(
        {
            "name": "linear_update_issue_status",
            "description": "Update the workflow state or status of a Linear issue.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string", "description": "Linear issue ID."},
                    "state_id": {"type": "string", "description": "Target workflow state ID."},
                },
                "required": ["issue_id", "state_id"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "id": {"type": "string"},
                    "identifier": {"type": "string"},
                    "state": {"type": "string"},
                },
            },
            "scopes": ["linear:issues:write"],
            "tags": ["linear", "connector", "agile", "productivity"],
        },
        _linear_update_issue_status,
    )

if "linear_list_teams" not in registry.REGISTRY:
    registry.register(
        {
            "name": "linear_list_teams",
            "description": "List teams in the Linear organization.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "teams": {"type": "array"},
                },
            },
            "scopes": ["linear:teams:read"],
            "tags": ["linear", "connector", "agile", "productivity"],
        },
        _linear_list_teams,
    )
