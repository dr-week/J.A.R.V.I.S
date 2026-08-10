#!/usr/bin/env python3
"""Read-only board copilot for Jarvis agents.

Prints a short suggestion for the safest next issue and lane for an owner.
This helper only reads board markdown and issue frontmatter.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "docs" / "board"
ISSUES = BOARD / "issues"

MAX_PARALLEL = 2


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, raw = line.split(":", 1)
        meta[key.strip()] = raw.strip().strip('"')
    return meta


def load_issue(issue_id: str) -> dict[str, str]:
    path = ISSUES / f"{issue_id}.md"
    if not path.exists():
        return {}
    meta = parse_frontmatter(path.read_text(encoding="utf-8"))
    meta["__path"] = str(path)
    return meta


def load_issues() -> list[dict[str, str]]:
    if not ISSUES.exists():
        return []
    out: list[dict[str, str]] = []
    for path in sorted(ISSUES.glob("ISSUE-*.md")):
        meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta:
            meta["__path"] = str(path)
            out.append(meta)
    return out


def normalize_owner(value: str) -> str:
    return (value or "").strip().lower()


def split_csvish(value: str) -> list[str]:
    raw = value.strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [part.strip().strip('"').strip("'") for part in raw.split(",") if part.strip()]


def is_starter(meta: dict[str, str]) -> bool:
    labels = split_csvish(meta.get("labels", ""))
    return "starter" in {label.lower() for label in labels}


def is_unblocked(meta: dict[str, str]) -> bool:
    blocked = split_csvish(meta.get("blocked_by", ""))
    if not blocked:
        return True
    done_ids = {m.get("id", "") for m in load_issues() if m.get("status") == "done"}
    return all(item in done_ids for item in blocked)


def load_now() -> list[dict[str, str]]:
    return [m for m in load_issues() if m.get("status") == "now"]


def load_next() -> list[dict[str, str]]:
    issues = load_issues()
    order = {"now": 0, "backlog": 1, "todo": 1, "blocked": 2, "done": 3}
    priority = {"P0": 0, "P1": 1, "P2": 2}
    issues = [m for m in issues if m.get("status") != "done"]
    issues.sort(key=lambda m: (order.get(m.get("status", "backlog"), 9), priority.get(m.get("priority", "P2"), 9), m.get("id", "")))
    return issues


def starter_queue() -> set[str]:
    return {m.get("id", "") for m in load_issues() if m.get("status") != "done" and is_starter(m) and is_unblocked(m)}


def lane_for_issue(meta: dict[str, str]) -> str:
    issue_id = meta.get("id", "")
    if issue_id == "ISSUE-085":
        return "scripts/helpers/repo_nav.py"
    if issue_id == "ISSUE-086":
        return "scripts/helpers/board_copilot.py"
    labels = meta.get("labels", "")
    if "windows" in labels:
        return "clients/windows/"
    if "android" in labels:
        return "clients/android/"
    if "docs" in labels:
        return "docs/"
    return "scripts/"


def issue_summary(meta: dict[str, str]) -> str:
    return f"{meta.get('id')} — {meta.get('title')}"


def pick_issue(owner: str, tier: str) -> tuple[str, dict[str, str], str]:
    now = load_now()
    if any(normalize_owner(m.get("owner", "")) == normalize_owner(owner) for m in now):
        mine = next(m for m in now if normalize_owner(m.get("owner", "")) == normalize_owner(owner))
        return "your NOW", mine, lane_for_issue(mine)

    queue = load_next()
    starter_ids = starter_queue() if tier == "mini" else set()
    for meta in queue:
        if meta.get("status") == "now" and normalize_owner(meta.get("owner", "")) not in {"", normalize_owner(owner)}:
            continue
        if tier == "mini" and meta.get("id") not in starter_ids:
            continue
        return "suggest", meta, lane_for_issue(meta)
    return "none", {}, ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only board copilot")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--tier", default="standard", choices=["mini", "standard", "lead"])
    args = parser.parse_args()

    now = load_now()
    free = max(0, MAX_PARALLEL - len(now))
    if now:
        mine = [m for m in now if normalize_owner(m.get("owner", "")) == normalize_owner(args.owner)]
        if mine:
            print(f"slots: {free}/{MAX_PARALLEL} free")
            print(f"your NOW: {mine[0].get('id')} — {mine[0].get('title')}")
            print(f"lane: {lane_for_issue(mine[0])}")
            print("why: you already own an active issue")
            return

    kind, meta, lane = pick_issue(args.owner, args.tier)
    print(f"slots: {free}/{MAX_PARALLEL} free")
    print("your NOW: (none)")
    if not meta:
        print("suggest: none")
        print("lane: —")
        print("why: no open issue available")
        return
    avoid = []
    for issue in now:
        owner = issue.get("owner") or "—"
        if normalize_owner(owner) and normalize_owner(owner) != normalize_owner(args.owner):
            avoid.append(f"{issue.get('id')}={owner}")
    print(f"suggest: {issue_summary(meta)}")
    print(f"lane: {lane}")
    if avoid:
        print(f"avoid: {', '.join(avoid)}")
    if args.tier == "mini":
        print("why: starter + unblocked + mini-safe")
    else:
        print("why: unblocked and lowest-friction next issue")


if __name__ == "__main__":
    main()
