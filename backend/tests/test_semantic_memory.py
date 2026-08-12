"""Tests for semantic_memory plugin and RAG search."""
from __future__ import annotations

import pytest

from backend.app.hands.registry import REGISTRY
from backend.app.soul.memory import delete_memory, search_semantic_memories, upsert_memory
from backend.plugins.semantic_memory import _memory_search


def test_memory_search_tool_registered():
    """Verify tool registration in REGISTRY."""
    assert "memory_search" in REGISTRY


def test_semantic_memory_search_ranking():
    """Test TF-IDF keyword search ranking over stored memories."""
    # Seed memories
    upsert_memory("pet_dog", "Golden Retriever named Max", source="test")
    upsert_memory("favorite_food", "Italian pizza and pasta", source="test")
    upsert_memory("work_city", "Bangalore India software engineer", source="test")

    try:
        # Search for dog
        results = search_semantic_memories("what is the name of my pet dog?")
        assert len(results) >= 1
        assert results[0]["key"] == "pet_dog"
        assert "Max" in results[0]["value"]

        # Search for food via plugin tool function
        res_tool = _memory_search("favorite Italian food", limit=2)
        assert res_tool["count"] >= 1
        assert res_tool["memories"][0]["key"] == "favorite_food"
    finally:
        delete_memory("pet_dog")
        delete_memory("favorite_food")
        delete_memory("work_city")
