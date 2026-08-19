"""Workspace tool schema registrations.

Single responsibility: connect workspace executor functions (from workspace_tools.py)
to the tool registry with their JSON schemas. No executor logic lives here.
"""
from __future__ import annotations


def register_workspace_tools() -> None:
    """Register all 4 workspace tool schemas against their executors."""
    from ..registry import register
    from .workspace_tools import (
        workspace_map_tree,
        file_ast_outline,
        file_read_chunk,
        file_edit_strict,
    )

    register(
        {
            "name": "workspace_map_tree",
            "description": "Get a lightweight directory tree of files in the workspace (ignores git/cache/node_modules).",
            "version": "1.0.0",
            "phase": 2,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "subpath": {"type": "string", "description": "Optional subdirectory relative to workspace root."},
                    "max_depth": {"type": "integer", "description": "Max depth to traverse (default: 3)."},
                },
                "required": [],
            },
            "scopes": ["workspace:read"],
            "tags": ["workspace", "code"],
        },
        workspace_map_tree,
    )

    register(
        {
            "name": "file_ast_outline",
            "description": "Extract class and function outlines with line numbers from a Python or source file in <5ms.",
            "version": "1.0.0",
            "phase": 2,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Relative or absolute path to source file."},
                },
                "required": ["file_path"],
            },
            "scopes": ["workspace:read"],
            "tags": ["workspace", "code", "ast"],
        },
        file_ast_outline,
    )

    register(
        {
            "name": "file_read_chunk",
            "description": "Read a precise line range from a workspace file (prevents context window overflow).",
            "version": "1.0.0",
            "phase": 2,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to file."},
                    "start_line": {"type": "integer", "description": "1-based starting line number."},
                    "end_line": {"type": "integer", "description": "1-based ending line number."},
                },
                "required": ["file_path"],
            },
            "scopes": ["workspace:read"],
            "tags": ["workspace", "code"],
        },
        file_read_chunk,
    )

    register(
        {
            "name": "file_edit_strict",
            "description": "Atomically apply exact search-and-replace edit to a file with pre-write AST syntax validation.",
            "version": "1.0.0",
            "phase": 2,
            "risk_level": "confirm_once",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to file."},
                    "search": {"type": "string", "description": "Exact text block to replace."},
                    "replace": {"type": "string", "description": "New replacement text block."},
                    "start_line": {"type": "integer", "description": "Optional starting line hint."},
                    "end_line": {"type": "integer", "description": "Optional ending line hint."},
                },
                "required": ["file_path", "search", "replace"],
            },
            "scopes": ["workspace:write"],
            "tags": ["workspace", "code", "edit"],
        },
        file_edit_strict,
    )
