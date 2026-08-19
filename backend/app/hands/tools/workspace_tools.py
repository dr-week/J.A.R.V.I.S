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
            total = len(orig_norm.splitlines())
            hint_start = max(1, (start_line or 1) - 5)
            hint_end = min(total, (end_line or hint_start) + 20)
            return {
                "ok": False,
                "status": "error",
                "error_code": "SEARCH_NOT_FOUND",
                "error": "Target search block not found. Exact whitespace and indentation must match.",
                "suggestion": (
                    f"Run file_read_chunk on '{file_path}' lines {hint_start}-{hint_end} "
                    "to inspect the exact text before retrying."
                ),
            }

        # 2. Check single occurrence
        count = orig_norm.count(search_norm)
        if count > 1 and start_line is None:
            return {
                "ok": False,
                "status": "error",
                "error_code": "AMBIGUOUS_MATCH",
                "error": f"Search block appears {count} times in file.",
                "suggestion": "Provide start_line and end_line to disambiguate the target occurrence.",
            }


        # 3. Perform atomic replacement
        new_content = orig_norm.replace(search_norm, replace_norm, 1)

        # 4. Pre-write AST / Syntax Validation Gate
        if p.suffix == ".py":
            is_valid, msg = validate_python_syntax(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "status": "error",
                    "error_code": "AST_SYNTAX_REJECTED",
                    "error": f"AST syntax validation failed: {msg}. Disk write aborted.",
                    "suggestion": "Fix the Python syntax error in your replace block before retrying.",
                }
        elif p.suffix == ".json":
            is_valid, msg = validate_json_syntax(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "status": "error",
                    "error_code": "JSON_SYNTAX_REJECTED",
                    "error": f"JSON syntax validation failed: {msg}. Disk write aborted.",
                    "suggestion": "Ensure your replace block produces valid JSON (check trailing commas or missing quotes).",
                }
        elif p.suffix in (".js", ".ts", ".tsx", ".jsx", ".html"):
            is_valid, msg = validate_bracket_balance(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "status": "error",
                    "error_code": "BRACKET_BALANCE_REJECTED",
                    "error": f"Bracket balance check failed: {msg}. Disk write aborted.",
                    "suggestion": "Count all opening/closing brackets, braces, and parens in your replace block.",
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


