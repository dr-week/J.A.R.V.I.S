#!/usr/bin/env python3
"""Read-only repo navigator for Jarvis agents.

Answers "where is X?" and "what touches Y?" in a compact format using the
lightweight repo index. It never opens full files or mutates the repo.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "repo_index.db"
CODE_MAP = ROOT / "docs" / "CODE_MAP.md"
DOC_HINTS = {
    "sync": "docs/SYNC_PROTOCOL.md",
    "board": "docs/board/NOW.md",
    "presence": "docs/ROADMAP.md",
    "windows": "clients/windows/README.md",
    "android": "clients/android/README.md",
    "tools": "docs/TOOL_SCHEMA.md",
    "helpers": "docs/dev/INTERNAL_HELPERS.md",
}


def connect(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def ensure_index() -> None:
    if DB_PATH.exists():
        return
    from scripts.index_repo import DEFAULT_DB, write_index

    write_index(DEFAULT_DB)
    if DEFAULT_DB != DB_PATH:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        DB_PATH.write_bytes(DEFAULT_DB.read_bytes())


def load_map_fallback() -> list[dict[str, str]]:
    if not CODE_MAP.exists():
        return []
    rows: list[dict[str, str]] = []
    for line in CODE_MAP.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 4:
            continue
        rows.append(
            {
                "path": parts[0].strip("`"),
                "kind": parts[1],
                "summary": parts[2],
                "symbols": parts[3],
            }
        )
    return rows


def query_db(term: str, limit: int = 8) -> list[dict[str, str]]:
    ensure_index()
    if not DB_PATH.exists():
        return []
    with connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT path, kind, summary, symbols
            FROM repo_files
            WHERE path LIKE ? OR summary LIKE ? OR symbols LIKE ?
            ORDER BY mtime DESC, path ASC
            LIMIT ?
            """,
            (f"%{term}%", f"%{term}%", f"%{term}%", limit),
        ).fetchall()
    return [
        {"path": path, "kind": kind, "summary": summary, "symbols": symbols}
        for path, kind, summary, symbols in rows
    ]


def short(rows: list[dict[str, str]], limit: int = 5) -> list[dict[str, str]]:
    return rows[:limit]


def show_rows(header: str, rows: list[dict[str, str]]) -> None:
    print(header)
    if not rows:
        print("  (none)")
        return
    for row in rows:
        summary = row.get("summary") or "—"
        print(f"  {row.get('path')} — {summary}")


def find(term: str) -> None:
    rows = query_db(term, limit=8)
    if not rows:
        rows = [r for r in load_map_fallback() if term.lower() in " ".join(r.values()).lower()][:8]
    docs = [r for r in rows if r["kind"] == "docs"]
    code = [r for r in rows if r["kind"] != "docs"]
    print(f"query: {term}")
    if docs:
        show_rows("docs first:", short(docs, 2))
    if code:
        show_rows("code:", short(code, 5))
    if not docs and not code:
        print("  (no matches)")


def symbol(term: str) -> None:
    rows = query_db(term, limit=8)
    code = [r for r in rows if r["kind"] != "docs"]
    print(f"symbol: {term}")
    show_rows("code:", short(code, 6))


def doc(term: str) -> None:
    key = term.strip().lower()
    hint = DOC_HINTS.get(key)
    rows = query_db(term, limit=8)
    docs = [r for r in rows if r["kind"] == "docs"]
    if hint:
        docs = [{"path": hint, "summary": "doc hint", "symbols": "", "kind": "docs"}] + docs
    print(f"doc: {term}")
    show_rows("docs first:", short(docs, 4))


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only repo navigator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_find = sub.add_parser("find", help="Search by topic or phrase")
    p_find.add_argument("term")

    p_symbol = sub.add_parser("symbol", help="Search by function/class/symbol")
    p_symbol.add_argument("term")

    p_doc = sub.add_parser("doc", help="Find the most relevant docs for a topic")
    p_doc.add_argument("term")

    p_rebuild = sub.add_parser("rebuild", help="Refresh the repo index and code map")

    args = parser.parse_args()

    if args.cmd == "rebuild":
        from scripts.index_repo import DEFAULT_DB, DEFAULT_MAP, render_map, write_index

        entries = write_index(DEFAULT_DB)
        DEFAULT_MAP.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_MAP.write_text(render_map(entries, limit=len(entries)), encoding="utf-8")
        print(f"rebuild: indexed {len(entries)} files -> {DEFAULT_DB}")
        print(f"rebuild: wrote {DEFAULT_MAP}")
        return

    if args.cmd == "find":
        find(args.term)
    elif args.cmd == "symbol":
        symbol(args.term)
    elif args.cmd == "doc":
        doc(args.term)


if __name__ == "__main__":
    main()
