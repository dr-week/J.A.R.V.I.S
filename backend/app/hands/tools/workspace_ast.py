"""Workspace AST and surgical chunk readers with in-memory caching."""
from __future__ import annotations

import ast
from typing import Any

from .workspace_tree import resolve_safe_path

# LRU / In-memory AST cache for sub-millisecond repeated queries
_AST_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}


def file_ast_outline(file_path: str) -> dict[str, Any]:
    """Generate a compact AST outline (classes & functions with line numbers) in <5ms."""
    try:
        p = resolve_safe_path(file_path)
        if not p.exists() or not p.is_file():
            return {"ok": False, "error": f"File '{file_path}' not found."}

        mtime = p.stat().st_mtime
        if file_path in _AST_CACHE:
            cached_mtime, cached_res = _AST_CACHE[file_path]
            if cached_mtime == mtime:
                return cached_res

        content = p.read_text(encoding="utf-8", errors="replace")
        total_lines = len(content.splitlines())

        if p.suffix == ".py":
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                res = {
                    "ok": True,
                    "file": file_path,
                    "total_lines": total_lines,
                    "syntax_error": f"Line {e.lineno}: {e.msg}",
                    "classes": [],
                    "functions": [],
                }
                return res

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

            res = {
                "ok": True,
                "file": file_path,
                "total_lines": total_lines,
                "classes": classes,
                "functions": functions,
            }
            _AST_CACHE[file_path] = (mtime, res)
            return res
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
        p = resolve_safe_path(file_path)
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
