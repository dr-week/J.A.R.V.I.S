"""Semantic Memory Plugin (Phase 3 — Local RAG & Fast Semantic Recall).

Exposes semantic memory search over stored user preferences and context,
saving LLM context tokens by returning only top-k relevant memory items.
"""
from __future__ import annotations

from typing import Any

from backend.app.hands import registry
from backend.app.soul.memory import search_semantic_memories


def _memory_search(query: str, limit: int = 3) -> dict[str, Any]:
    """Search stored memories using keyword relevance scoring."""
    clean_query = (query or "").strip()
    if not clean_query:
        return {"count": 0, "memories": []}

    results = search_semantic_memories(clean_query, limit=limit)
    return {"count": len(results), "query": clean_query, "memories": results}


registry.register(
    {
        "name": "memory_search",
        "description": (
            "Perform semantic recall search over stored user memories. "
            "Returns top relevant memory entries matching query terms."
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
                    "description": "Keywords or question to search memories for (e.g. 'favorite food')",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of top memory results to return (default 3)",
                },
            },
            "required": ["query"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "memories": {"type": "array"},
            },
        },
        "scopes": ["soul:read"],
        "tags": ["soul", "memory", "rag"],
    },
    _memory_search,
)
