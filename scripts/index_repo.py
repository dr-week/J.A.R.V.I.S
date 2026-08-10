#!/usr/bin/env python3
"""Lightweight repo index and generated code map for Jarvis.

This is a small developer helper, not a second source of truth.
It scans the workspace, stores a tiny SQLite index, and can emit a
Markdown map of the most relevant files for fast navigation.
"""
from __future__ import annotations

import argparse
import ast
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "repo_index.db"
DEFAULT_MAP = ROOT / "docs" / "CODE_MAP.md"

IGNORE_DIRS = {
    ".git",
    ".gradle",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "build",
    "dist",
    "node_modules",
}

TARGET_DIRS = ("backend", "clients", "docs", "scripts", "tools")
TEXT_EXTS = {".py", ".md", ".kts", ".kt", ".json", ".yml", ".yaml", ".txt", ".toml"}


@dataclass
class Entry:
    path: str
    kind: str
    summary: str
    symbols: str
    mtime: float


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS repo_files (
            path TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            summary TEXT NOT NULL,
            symbols TEXT NOT NULL,
            mtime REAL NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_repo_files_kind ON repo_files(kind)")
    return conn


def should_skip(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return "docs"
    if suffix in {".py", ".kts", ".kt"}:
        return "code"
    if suffix in {".json", ".yml", ".yaml", ".toml"}:
        return "config"
    return "text" if suffix in TEXT_EXTS else "file"


def summarize_python(text: str) -> tuple[str, list[str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return first_line_summary(text), []
    doc = ast.get_docstring(tree) or ""
    symbols: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.append(node.name)
    summary = doc.splitlines()[0].strip() if doc else first_line_summary(text)
    return summary, symbols[:20]


def first_line_summary(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:180]
    return ""


def summarize_markdown(text: str) -> tuple[str, list[str]]:
    title = ""
    symbols: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not title and stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            continue
        if stripped.startswith("## "):
            symbols.append(stripped[3:].strip())
        if title and len(symbols) >= 8:
            break
    summary = title or first_line_summary(text)
    return summary, symbols


def summarize_text(path: Path, text: str) -> tuple[str, list[str]]:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return summarize_python(text)
    if suffix == ".md":
        return summarize_markdown(text)
    return first_line_summary(text), []


def collect_entries() -> list[Entry]:
    entries: list[Entry] = []
    for base in TARGET_DIRS:
        root = ROOT / base
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or should_skip(path):
                continue
            if path.suffix.lower() not in TEXT_EXTS and path.name not in {"README", "LICENSE"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            summary, symbols = summarize_text(path, text)
            rel = path.relative_to(ROOT).as_posix()
            entries.append(
                Entry(
                    path=rel,
                    kind=classify(path),
                    summary=summary[:180],
                    symbols=", ".join(symbols),
                    mtime=path.stat().st_mtime,
                )
            )
    return sorted(entries, key=lambda e: e.path)


def write_index(db_path: Path) -> list[Entry]:
    entries = collect_entries()
    with connect(db_path) as conn:
        conn.execute("DELETE FROM repo_files")
        conn.executemany(
            "INSERT OR REPLACE INTO repo_files(path, kind, summary, symbols, mtime) VALUES (?, ?, ?, ?, ?)",
            [(e.path, e.kind, e.summary, e.symbols, e.mtime) for e in entries],
        )
        conn.commit()
    return entries


def query_index(db_path: Path, term: str, limit: int = 12) -> list[Entry]:
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT path, kind, summary, symbols, mtime
            FROM repo_files
            WHERE path LIKE ? OR summary LIKE ? OR symbols LIKE ?
            ORDER BY mtime DESC, path ASC
            LIMIT ?
            """,
            (f"%{term}%", f"%{term}%", f"%{term}%", limit),
        ).fetchall()
    return [Entry(*row) for row in rows]


def render_map(entries: list[Entry], limit: int = 80) -> str:
    lines = [
        "# Code Map",
        "",
        "Generated by `python scripts/index_repo.py map`.",
        "",
        "| Path | Kind | Summary | Symbols |",
        "|------|------|---------|---------|",
    ]
    for entry in entries[:limit]:
        symbols = entry.symbols or "—"
        summary = entry.summary or "—"
        lines.append(f"| `{entry.path}` | {entry.kind} | {summary} | {symbols} |")
    lines.append("")
    lines.append(f"_Generated {utc_now()} from {len(entries)} indexed files._")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a lightweight Jarvis repo index")
    parser.add_argument("command", choices=["index", "map", "query"])
    parser.add_argument("term", nargs="?", default="")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--out", default=str(DEFAULT_MAP))
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    db_path = Path(args.db)

    if args.command == "index":
        entries = write_index(db_path)
        print(f"Indexed {len(entries)} files into {db_path}")
        return

    if args.command == "query":
        if not args.term:
            raise SystemExit("query requires a search term")
        if not db_path.exists():
            write_index(db_path)
        rows = query_index(db_path, args.term, limit=args.limit)
        print(json.dumps([e.__dict__ for e in rows], indent=2))
        return

    entries = write_index(db_path)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_map(entries, limit=max(args.limit, len(entries))), encoding="utf-8")
    print(f"Wrote {out_path} from {len(entries)} indexed files")


if __name__ == "__main__":
    main()
