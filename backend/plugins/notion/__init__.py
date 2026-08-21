"""Notion Workspace Connector Plugin (Phase 3+).

Provides clean, non-monolithic Notion API integration for CoreBrain.
Supports searching workspace, querying databases, creating pages, and appending content blocks.

Architecture & Security Rationale:
- Token is read brain-locally from `JARVIS_NOTION_API_KEY` or `NOTION_API_KEY`.
- Never exposes secrets in LLM tool parameters or action logs.
- Uses flat logic and explicit validation to ensure reliability in multi-agent environments.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from backend.app.hands import registry

_NOTION_API = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"


def _token() -> str:
    """Retrieve Notion API token from environment variables."""
    return (os.environ.get("JARVIS_NOTION_API_KEY") or os.environ.get("NOTION_API_KEY") or "").strip()


def _get_headers() -> dict[str, str]:
    """Construct Notion standard REST API request headers."""
    token = _token()
    if not token:
        raise RuntimeError("Notion is not configured. Set JARVIS_NOTION_API_KEY or NOTION_API_KEY.")
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Notion-Version": _NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _notion_search(query: str = "", filter_type: str = "") -> dict[str, Any]:
    """Search pages and databases across the accessible Notion workspace."""
    payload: dict[str, Any] = {"query": query.strip()}
    if filter_type in {"page", "database"}:
        payload["filter"] = {"value": filter_type, "property": "object"}

    response = httpx.post(
        f"{_NOTION_API}/search",
        headers=_get_headers(),
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    raw_results = response.json().get("results", [])
    
    results = []
    for item in raw_results:
        obj_type = item.get("object")
        item_id = item.get("id")
        url = item.get("url", "")
        title = "Untitled"
        
        if obj_type == "page":
            props = item.get("properties", {})
            for p in props.values():
                if p.get("type") == "title":
                    title_list = p.get("title", [])
                    if title_list:
                        title = title_list[0].get("plain_text", "Untitled")
                    break
        elif obj_type == "database":
            title_list = item.get("title", [])
            if title_list:
                title = title_list[0].get("plain_text", "Untitled")

        results.append({
            "id": item_id,
            "object": obj_type,
            "title": title,
            "url": url,
            "last_edited_time": item.get("last_edited_time"),
        })

    return {"query": query, "count": len(results), "results": results}


def _notion_query_database(database_id: str = "", page_size: int = 20) -> dict[str, Any]:
    """Query items from a specific Notion database."""
    if not database_id.strip():
        raise ValueError("database_id cannot be empty.")
    if not 1 <= page_size <= 100:
        raise ValueError("page_size must be between 1 and 100.")

    clean_db_id = database_id.strip().replace("-", "")
    response = httpx.post(
        f"{_NOTION_API}/databases/{clean_db_id}/query",
        headers=_get_headers(),
        json={"page_size": page_size},
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()
    items = []
    for row in data.get("results", []):
        row_id = row.get("id")
        url = row.get("url", "")
        title = "Untitled"
        for p in row.get("properties", {}).values():
            if p.get("type") == "title":
                t_list = p.get("title", [])
                if t_list:
                    title = t_list[0].get("plain_text", "Untitled")
                break
        items.append({"id": row_id, "title": title, "url": url})

    return {"database_id": database_id, "count": len(items), "items": items}


def _notion_create_page(
    parent_id: str = "",
    title: str = "",
    content: str = "",
    is_database_parent: bool = True,
) -> dict[str, Any]:
    """Create a new page in a database or under another parent page."""
    if not parent_id.strip():
        raise ValueError("parent_id cannot be empty.")
    if not title.strip():
        raise ValueError("title cannot be empty.")

    clean_parent_id = parent_id.strip()
    parent = {"database_id": clean_parent_id} if is_database_parent else {"page_id": clean_parent_id}
    
    properties: dict[str, Any] = {
        "title": {
            "title": [{"text": {"content": title.strip()}}]
        }
    } if is_database_parent else {
        "title": [{"text": {"content": title.strip()}}]
    }

    children: list[dict[str, Any]] = []
    if content.strip():
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": content.strip()}}]
            }
        })

    payload: dict[str, Any] = {
        "parent": parent,
        "properties": properties,
        "children": children,
    }

    response = httpx.post(
        f"{_NOTION_API}/pages",
        headers=_get_headers(),
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    res = response.json()
    return {
        "status": "created",
        "page_id": res.get("id"),
        "url": res.get("url"),
        "title": title,
    }


def _notion_append_block(page_id: str = "", text: str = "", block_type: str = "paragraph") -> dict[str, Any]:
    """Append a content block (paragraph, to_do, heading_2) to a page."""
    if not page_id.strip():
        raise ValueError("page_id cannot be empty.")
    if not text.strip():
        raise ValueError("text cannot be empty.")
    if block_type not in {"paragraph", "to_do", "heading_2", "bulleted_list_item"}:
        raise ValueError("block_type must be paragraph, to_do, heading_2, or bulleted_list_item.")

    clean_page_id = page_id.strip().replace("-", "")
    block_payload = {
        "rich_text": [{"type": "text", "text": {"content": text.strip()}}]
    }

    payload = {
        "children": [
            {
                "object": "block",
                "type": block_type,
                block_type: block_payload,
            }
        ]
    }

    response = httpx.patch(
        f"{_NOTION_API}/blocks/{clean_page_id}/children",
        headers=_get_headers(),
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    return {"status": "appended", "page_id": page_id, "block_type": block_type}


# Register all Notion tools in Hands registry
if "notion_search" not in registry.REGISTRY:
    registry.register(
        {
            "name": "notion_search",
            "description": "Search pages and databases in the Notion workspace.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term."},
                    "filter_type": {"type": "string", "enum": ["page", "database", ""], "default": ""},
                },
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "count": {"type": "integer"},
                    "results": {"type": "array"},
                },
            },
            "scopes": ["notion:read"],
            "tags": ["notion", "connector", "notes"],
        },
        _notion_search,
    )

if "notion_query_database" not in registry.REGISTRY:
    registry.register(
        {
            "name": "notion_query_database",
            "description": "Query records and items from a Notion database.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "database_id": {"type": "string", "description": "Notion database ID."},
                    "page_size": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                },
                "required": ["database_id"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "database_id": {"type": "string"},
                    "count": {"type": "integer"},
                    "items": {"type": "array"},
                },
            },
            "scopes": ["notion:read"],
            "tags": ["notion", "connector", "database"],
        },
        _notion_query_database,
    )

if "notion_create_page" not in registry.REGISTRY:
    registry.register(
        {
            "name": "notion_create_page",
            "description": "Create a new page in a database or parent page in Notion.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "parent_id": {"type": "string", "description": "Database ID or Page ID."},
                    "title": {"type": "string", "description": "Title of the page."},
                    "content": {"type": "string", "description": "Initial text content."},
                    "is_database_parent": {"type": "boolean", "default": True},
                },
                "required": ["parent_id", "title"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "page_id": {"type": "string"},
                    "url": {"type": "string"},
                },
            },
            "scopes": ["notion:write"],
            "tags": ["notion", "connector", "notes"],
        },
        _notion_create_page,
    )

if "notion_append_block" not in registry.REGISTRY:
    registry.register(
        {
            "name": "notion_append_block",
            "description": "Append a content block (paragraph, to_do, heading) to an existing Notion page.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Target page ID."},
                    "text": {"type": "string", "description": "Block text content."},
                    "block_type": {
                        "type": "string",
                        "enum": ["paragraph", "to_do", "heading_2", "bulleted_list_item"],
                        "default": "paragraph",
                    },
                },
                "required": ["page_id", "text"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "page_id": {"type": "string"},
                    "block_type": {"type": "string"},
                },
            },
            "scopes": ["notion:write"],
            "tags": ["notion", "connector", "notes"],
        },
        _notion_append_block,
    )
