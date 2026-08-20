"""Workspace tools facade — re-exports all workspace functions from focused submodules.

Modular architecture:
  - workspace_tree.py   : workspace_map_tree, resolve_safe_path
  - workspace_ast.py    : file_ast_outline, file_read_chunk
  - workspace_editor.py : file_edit_strict
"""
from __future__ import annotations

from .workspace_tree import ROOT_DIR, IGNORE_DIRS, resolve_safe_path, workspace_map_tree
from .workspace_ast import file_ast_outline, file_read_chunk
from .workspace_editor import file_edit_strict

# Backward compatibility alias
_resolve_safe_path = resolve_safe_path

__all__ = [
    "ROOT_DIR",
    "IGNORE_DIRS",
    "resolve_safe_path",
    "_resolve_safe_path",
    "workspace_map_tree",
    "file_ast_outline",
    "file_read_chunk",
    "file_edit_strict",
]
