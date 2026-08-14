"""SearXNG Private Search Plugin (search_web tool fallback).

Enables private web search via a self-hosted SearXNG Docker sidecar or REST endpoint
per docs/OSS.md (Pattern 3: Docker Sidecar + REST call).
"""
from __future__ import annotations

import os
from typing import Any
import httpx

from backend.app.hands import registry

SEARXNG_DEFAULT_URL = "http://localhost:8080"


async def _search_web(
    query: str,
    limit: int = 5,
    categories: str = "general",
    language: str = "auto",
    url: str = "",
) -> dict[str, Any]:
    """Execute a private web search query against a SearXNG instance."""
    clean_query = (query or "").strip()
    if not clean_query:
        return {"error": "Search query cannot be empty."}

    base_url = (
        url
        or os.environ.get("SEARXNG_URL")
        or os.environ.get("JARVIS_SEARXNG_URL")
        or SEARXNG_DEFAULT_URL
    ).strip()
    endpoint = f"{base_url.rstrip('/')}/search"

    params: dict[str, Any] = {
        "q": clean_query,
        "format": "json",
        "categories": categories,
    }
    if language and language != "auto":
        params["language"] = language

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()

        raw_results = data.get("results", [])
        formatted_results: list[dict[str, Any]] = []

        for item in raw_results[:limit]:
            formatted_results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "engine": item.get("engine", ""),
                }
            )

        return {
            "query": clean_query,
            "count": len(formatted_results),
            "results": formatted_results,
        }
    except Exception as exc:
        return {
            "query": clean_query,
            "results": [],
            "error": f"SearXNG search request failed: {exc}. Ensure SearXNG sidecar is running at {base_url}.",
        }


# Register search_web as the primary web search tool definition
if "search_web" not in registry.REGISTRY:
    registry.register(
        {
            "name": "search_web",
            "description": (
                "Search the web privately using self-hosted SearXNG sidecar. "
                "Returns titles, URLs, snippets, and engines for query."
            ),
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query keywords or question.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of search results to return (default 5).",
                    },
                    "categories": {
                        "type": "string",
                        "description": "SearXNG search categories: 'general', 'news', 'science', 'it'.",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (e.g. 'en', 'auto').",
                    },
                    "url": {
                        "type": "string",
                        "description": "Optional custom SearXNG base URL override.",
                    },
                },
                "required": ["query"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "count": {"type": "integer"},
                    "results": {"type": "array"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["web:search", "web:read"],
            "tags": ["search", "web", "searxng", "research"],
        },
        _search_web,
    )

if "searxng_search" not in registry.REGISTRY:
    registry.register(
        {
            "name": "searxng_search",
            "description": (
                "Search the web privately via SearXNG private metasearch engine sidecar."
            ),
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query keywords or question.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of search results to return (default 5).",
                    },
                    "categories": {
                        "type": "string",
                        "description": "SearXNG search categories: 'general', 'news', 'science', 'it'.",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (e.g. 'en', 'auto').",
                    },
                    "url": {
                        "type": "string",
                        "description": "Optional custom SearXNG base URL override.",
                    },
                },
                "required": ["query"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "count": {"type": "integer"},
                    "results": {"type": "array"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["web:search", "web:read"],
            "tags": ["search", "web", "searxng", "research"],
        },
        _search_web,
    )
