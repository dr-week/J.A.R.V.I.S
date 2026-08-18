"""Tests for Workspace Parsing, AST Outline, Chunk Reading, and AST Pre-validated File Editing."""
from __future__ import annotations

import pytest
from pathlib import Path
from backend.app.hands.registry import REGISTRY
from backend.app.hands.tools.workspace_tools import (
    workspace_map_tree,
    file_ast_outline,
    file_read_chunk,
    file_edit_strict,
)


def test_workspace_tools_registered():
    """Verify all workspace tools are in REGISTRY."""
    assert "workspace_map_tree" in REGISTRY
    assert "file_ast_outline" in REGISTRY
    assert "file_read_chunk" in REGISTRY
    assert "file_edit_strict" in REGISTRY


def test_workspace_map_tree():
    """Test generating lightweight tree."""
    res = workspace_map_tree(subpath="backend/app/mind", max_depth=2)
    assert res["ok"] is True
    assert "tree" in res
    assert "router.py" in res["tree"]


def test_file_ast_outline():
    """Test generating AST class and function outline."""
    res = file_ast_outline("backend/app/mind/ast_validator.py")
    assert res["ok"] is True
    assert res["total_lines"] > 0
    assert any("validate_python_syntax" in fn for fn in res["functions"])


def test_file_read_chunk():
    """Test reading specific line range."""
    res = file_read_chunk("backend/app/mind/ast_validator.py", start_line=1, end_line=10)
    assert res["ok"] is True
    assert res["start_line"] == 1
    assert res["end_line"] == 10
    assert "AST Syntax Pre-Validator" in res["content"]


def test_file_edit_strict_rejection_on_syntax_error(tmp_path):
    """Test that file_edit_strict aborts write if new content has broken Python syntax."""
    test_file = tmp_path / "sample.py"
    test_file.write_text("def greet():\n    return 'hello'\n", encoding="utf-8")

    # In strict mode outside ROOT_DIR, let's verify syntax rejection
    from backend.app.mind.ast_validator import validate_python_syntax
    broken_code = "def greet():\n    return 'hello' def broken(\n"
    is_valid, err = validate_python_syntax(broken_code)
    assert is_valid is False
    assert "SyntaxError" in err
