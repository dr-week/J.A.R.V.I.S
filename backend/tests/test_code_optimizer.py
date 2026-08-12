"""Tests for code_optimizer plugin."""
from __future__ import annotations

from pathlib import Path
import pytest

from backend.app.hands.registry import REGISTRY
from backend.plugins.code_optimizer import _dev_optimize_code


def test_dev_optimize_code_tool_registered():
    """Verify tool registration in REGISTRY."""
    assert "dev_optimize_code" in REGISTRY


@pytest.mark.asyncio
async def test_dev_optimize_code_execution(tmp_path: Path):
    """Test running dev_optimize_code on an unformatted python file."""
    unformatted_file = tmp_path / "sample.py"
    unformatted_file.write_text("import os, sys\ndef foo( a,b ):\n  return a+b\n", encoding="utf-8")

    res = await _dev_optimize_code(target_path=str(unformatted_file))

    assert res["ok"] is True
    assert "sample.py" in res["target"]
    assert len(res["summary"]) >= 1

    # Verify code was formatted by ruff
    formatted_content = unformatted_file.read_text(encoding="utf-8")
    assert "def foo(a, b):" in formatted_content or "def foo(" in formatted_content
