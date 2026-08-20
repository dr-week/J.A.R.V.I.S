"""Workspace directory tree scanning with safety boundaries."""
from __future__ import annotations

from pathlib import Path
from typing import Any

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


def resolve_safe_path(rel_or_abs_path: str) -> Path:
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
        base = resolve_safe_path(subpath) if subpath else ROOT_DIR
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
