"""Tests for ppt_generator plugin."""
from __future__ import annotations

from pathlib import Path
import pytest
from pptx import Presentation

from backend.app.hands.registry import REGISTRY
from backend.plugins.ppt_generator import _ppt_create_deck


def test_ppt_generator_tool_registered():
    """Verify tool registration in REGISTRY."""
    assert "ppt_create_deck" in REGISTRY


def test_ppt_create_deck_generation(tmp_path: Path):
    """Test generating a 3-slide PowerPoint presentation."""
    out_file = tmp_path / "test_deck.pptx"

    slides_data = [
        {"title": "Introduction", "bullets": ["Overview of Jarvis", "Autonomous agent architecture"]},
        {"title": "Key Features", "bullets": ["MCP integration", "Local RAG memory", "Native PPT generation"]},
    ]

    res = _ppt_create_deck(
        title="Jarvis Executive Summary",
        subtitle="Autonomous AI Assistant Platform",
        slides=slides_data,
        output_path=str(out_file),
    )

    assert res["ok"] is True
    assert res["total_slides"] == 3
    assert out_file.exists()

    # Load file with pptx to verify validity
    prs = Presentation(str(out_file))
    assert len(prs.slides) == 3
