#!/usr/bin/env python3
"""Verify issue ## Lane paths exist under repo root (read-only)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ISSUES = ROOT / "docs" / "board" / "issues"
LANE_HEADING = re.compile(r"^##\s+Lane\s*$", re.MULTILINE)
BACKTICK_PATH = re.compile(r"`([^`]+)`")


def parse_lane_paths(issue_text: str) -> list[str]:
    """Return glob-ish paths from ## Lane section bullet list."""
    match = LANE_HEADING.search(issue_text)
    if not match:
        return []
    rest = issue_text[match.end() :]
    next_h2 = re.search(r"\n##\s+", rest)
    section = rest[: next_h2.start()] if next_h2 else rest
    paths: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        for raw in BACKTICK_PATH.findall(line):
            p = raw.strip()
            if p and not p.startswith("http"):
                paths.append(p)
    return paths


def verify_lane_path(pattern: str) -> tuple[bool, str]:
    """Check one lane entry (file or glob with **)."""
    clean = pattern.replace("\\", "/").lstrip("/")
    if "**" in clean:
        prefix = clean.split("**", 1)[0].rstrip("/")
        base = ROOT / prefix
        if not base.exists():
            return False, f"missing directory: {prefix}"
        if base.is_file():
            return True, f"ok file: {prefix}"
        any_file = any(base.rglob("*"))
        if not any_file:
            return False, f"no files under: {prefix}"
        return True, f"ok under: {prefix}"
    path = ROOT / clean
    if path.exists():
        return True, f"ok: {clean}"
    return False, f"missing: {clean}"


def verify_issue(issue_id: str) -> tuple[int, list[str]]:
    path = ISSUES / f"{issue_id}.md"
    if not path.exists():
        return 1, [f"issue file not found: {path}"]
    text = path.read_text(encoding="utf-8")
    lanes = parse_lane_paths(text)
    if not lanes:
        return 1, ["no ## Lane paths found (add `- \\`path\\`` bullets)"]
    lines: list[str] = []
    fails = 0
    for pattern in lanes:
        ok, msg = verify_lane_path(pattern)
        lines.append(("OK " if ok else "FAIL ") + msg)
        if not ok:
            fails += 1
    return fails, lines
