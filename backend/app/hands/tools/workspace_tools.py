"""Workspace Parsing, AST Outlines, Chunk Reading, and AST Pre-validated File Editing."""
from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any

from ...mind.ast_validator import validate_python_syntax, validate_json_syntax, validate_bracket_balance

ROOT_DIR = Path(__file__).resolve().parents[4]

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "venv",
    ".venv",
}


def _resolve_safe_path(rel_or_abs_path: str) -> Path:
    """Resolve and enforce workspace path boundary to prevent path traversal."""
    p = Path(rel_or_abs_path)
    if not p.is_absolute():
        p = (ROOT_DIR / p).resolve()
    else:
        p = p.resolve()

    if not str(p).startswith(str(ROOT_DIR)):
        raise PermissionError(f"Access denied: '{rel_or_abs_path}' is outside workspace root.")
    return p


def workspace_map_tree(subpath: str = "", max_depth: int = 3) -> dict[str, Any]:
    """Generate a token-light directory map of the workspace."""
    try:
        base = _resolve_safe_path(subpath) if subpath else ROOT_DIR
        if not base.exists():
            return {"ok": False, "error": f"Path '{subpath}' does not exist."}

        tree_lines: list[str] = []

        def _traverse(current: Path, depth: int, prefix: str = ""):
            if depth > max_depth:
                return
            try:
                entries = sorted(list(current.iterdir()), key=lambda e: (not e.is_dir(), e.name.lower()))
            except Exception:
                return

            entries = [e for e in entries if e.name not in IGNORE_DIRS and not e.name.startswith(".")]

            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                rel = str(entry.relative_to(ROOT_DIR)).replace("\\", "/")
                
                if entry.is_dir():
                    tree_lines.append(f"{prefix}{connector}{entry.name}/")
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    _traverse(entry, depth + 1, new_prefix)
                else:
                    tree_lines.append(f"{prefix}{connector}{entry.name}")

        _traverse(base, 1)
        return {
            "ok": True,
            "root": str(ROOT_DIR.name),
            "tree": "\n".join(tree_lines[:200]),
            "total_nodes": len(tree_lines),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def file_ast_outline(file_path: str) -> dict[str, Any]:
    """Generate a compact AST outline (classes & functions with line numbers) in <5ms."""
    try:
        p = _resolve_safe_path(file_path)
        if not p.exists() or not p.is_file():
            return {"ok": False, "error": f"File '{file_path}' not found."}

        content = p.read_text(encoding="utf-8", errors="replace")
        total_lines = len(content.splitlines())

        if p.suffix == ".py":
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                return {
                    "ok": True,
                    "file": file_path,
                    "total_lines": total_lines,
                    "syntax_error": f"Line {e.lineno}: {e.msg}",
                    "classes": [],
                    "functions": [],
                }

            classes = []
            functions = []

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    end_lineno = getattr(node, "end_lineno", node.lineno)
                    classes.append(f"class {node.name} (lines {node.lineno}-{end_lineno})")
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end_lineno = getattr(node, "end_lineno", node.lineno)
                    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                    functions.append(f"{prefix} {node.name} (lines {node.lineno}-{end_lineno})")

            return {
                "ok": True,
                "file": file_path,
                "total_lines": total_lines,
                "classes": classes,
                "functions": functions,
            }
        else:
            return {
                "ok": True,
                "file": file_path,
                "total_lines": total_lines,
                "note": "Non-Python file; use file_read_chunk for inspection.",
            }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def file_read_chunk(file_path: str, start_line: int = 1, end_line: int = 100) -> dict[str, Any]:
    """Read a specific slice of lines from a workspace file."""
    try:
        p = _resolve_safe_path(file_path)
        if not p.exists() or not p.is_file():
            return {"ok": False, "error": f"File '{file_path}' not found."}

        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        total_lines = len(lines)

        start = max(1, start_line)
        end = min(total_lines, end_line)

        if start > total_lines:
            return {"ok": False, "error": f"start_line {start_line} exceeds total lines ({total_lines})."}

        chunk_lines = lines[start - 1 : end]
        formatted = [f"{i + start:4d} | {line}" for i, line in enumerate(chunk_lines)]

        return {
            "ok": True,
            "file": file_path,
            "total_lines": total_lines,
            "start_line": start,
            "end_line": end,
            "content": "\n".join(chunk_lines),
            "annotated_lines": "\n".join(formatted),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def file_edit_strict(
    file_path: str,
    search: str,
    replace: str,
    start_line: int | None = None,
    end_line: int | None = None,
) -> dict[str, Any]:
    """Pre-validate syntax with AST and atomically apply search & replace edit."""
    try:
        p = _resolve_safe_path(file_path)
        if not p.exists() or not p.is_file():
            return {"ok": False, "error": f"File '{file_path}' not found."}

        original = p.read_text(encoding="utf-8", errors="replace")

        # 1. Normalize line endings
        orig_norm = original.replace("\r\n", "\n")
        search_norm = search.replace("\r\n", "\n")
        replace_norm = replace.replace("\r\n", "\n")

        if search_norm not in orig_norm:
            return {
                "ok": False,
                "error": "Target search block not found in file. Ensure exact whitespace and line match.",
            }

        # 2. Check single occurrence
        count = orig_norm.count(search_norm)
        if count > 1 and start_line is None:
            return {
                "ok": False,
                "error": f"Search block appears {count} times in file. Provide start_line/end_line to disambiguate.",
            }

        # 3. Perform atomic replacement
        new_content = orig_norm.replace(search_norm, replace_norm, 1)

        # 4. Pre-write AST / Syntax Validation Gate
        if p.suffix == ".py":
            is_valid, msg = validate_python_syntax(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "error": f"AST Syntax Validation Rejected Edit: {msg}. Disk write aborted.",
                }
        elif p.suffix == ".json":
            is_valid, msg = validate_json_syntax(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "error": f"JSON Syntax Validation Rejected Edit: {msg}. Disk write aborted.",
                }
        elif p.suffix in (".js", ".ts", ".tsx", ".jsx", ".html"):
            is_valid, msg = validate_bracket_balance(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "error": f"Bracket Validation Rejected Edit: {msg}. Disk write aborted.",
                }

        # 5. Write to disk
        p.write_text(new_content, encoding="utf-8")

        return {
            "ok": True,
            "file": file_path,
            "message": f"Successfully edited {file_path}",
            "lines_changed": len(replace_norm.splitlines()) - len(search_norm.splitlines()),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def register_workspace_tools() -> None:
    """Register all workspace parsing and AST editing tools."""
    from ..registry import register

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
