#!/usr/bin/env python3
"""Jarvis internal AI app-dev feedback loop.

Manages docs/board issues: status, next, claim, release, issue, update, done,
refresh, sync, plan, brief, prompt (alias of brief), loop, bootstrap, verify.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_registry import (
    load_registry,
    next_blackbox_id,
    next_coder_id,
    register_agent,
    suggest_issue_for_tier,
)
from board_context import (
    KNOWN_OWNERS,
    LIVE_BRIEF,
    LIVE_PLAN,
    build_snapshot,
    render_brief,
    render_live_plan,
    snapshot_fingerprint,
)
from helpers.issue_lane_verify import verify_issue

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "docs" / "board"
ISSUES = BOARD / "issues"
FEEDBACK_JSONL = BOARD / "feedback.jsonl"
FEEDBACK_MD = BOARD / "FEEDBACK.md"
CODE_MAP = ROOT / "docs" / "CODE_MAP.md"

STATUS_ORDER = {"now": 0, "backlog": 1, "todo": 1, "blocked": 2, "done": 3}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
MAX_PARALLEL = 2  # designed for 2 people / 2 AIs at once
VALID_KINDS = ("claim", "done", "note", "ask", "block", "handoff")


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, Any] = {}
    body = parts[2].lstrip("\n")
    lines = parts[1].strip("\n").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw == "" and i + 1 < len(lines) and lines[i + 1].startswith("  -"):
            items: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith("-"):
                items.append(lines[i].strip()[1:].strip().strip('"'))
                i += 1
            meta[key] = items
            continue
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            meta[key] = (
                [x.strip().strip('"') for x in inner.split(",") if x.strip()] if inner else []
            )
        else:
            meta[key] = raw.strip('"')
        i += 1
    return meta, body


def dump_frontmatter(meta: dict[str, Any]) -> str:
    order = [
        "id",
        "title",
        "status",
        "priority",
        "phase",
        "labels",
        "owner",
        "claimed_at",
        "blocked_by",
        "acceptance",
    ]
    lines = ["---"]
    keys = [k for k in order if k in meta] + [k for k in meta if k not in order]
    for key in keys:
        val = meta[key]
        if isinstance(val, list):
            if key in {"acceptance"} or (val and not all(len(str(x)) < 40 for x in val)):
                lines.append(f"{key}:")
                for item in val:
                    lines.append(f"  - {item}")
            else:
                inner = ", ".join(str(x) for x in val)
                lines.append(f"{key}: [{inner}]")
        else:
            lines.append(f"{key}: {val}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def issue_path(issue_id: str) -> Path:
    return ISSUES / f"{issue_id.upper()}.md"


def load_issue(issue_id: str) -> tuple[dict[str, Any], str, Path]:
    path = issue_path(issue_id)
    if not path.exists():
        raise SystemExit(f"Issue not found: {path}")
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return meta, body, path


def save_issue(meta: dict[str, Any], body: str, path: Path) -> None:
    path.write_text(dump_frontmatter(meta) + "\n" + body.lstrip("\n"), encoding="utf-8")


def list_issues() -> list[tuple[dict[str, Any], Path]]:
    if not ISSUES.exists():
        return []
    out: list[tuple[dict[str, Any], Path]] = []
    for path in sorted(ISSUES.glob("ISSUE-*.md")):
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta:
            out.append((meta, path))
    return out


def sort_key(meta: dict[str, Any]) -> tuple:
    return (
        STATUS_ORDER.get(str(meta.get("status", "backlog")), 9),
        PRIORITY_ORDER.get(str(meta.get("priority", "P2")), 9),
        str(meta.get("id", "")),
    )


def sort_pair(item: tuple[dict[str, Any], Path]) -> tuple:
    return sort_key(item[0])


def is_unblocked(meta: dict[str, Any], done_ids: set[str]) -> bool:
    blocked = meta.get("blocked_by") or []
    if isinstance(blocked, str):
        blocked = [blocked] if blocked else []
    return all(str(b) in done_ids or str(b) == "" for b in blocked)


def open_issues(include_blocked: bool = False) -> list[tuple[dict[str, Any], Path]]:
    done_ids = {str(m.get("id")) for m, _ in list_issues() if m.get("status") == "done"}
    items = []
    for m, p in list_issues():
        if str(m.get("status")) == "done":
            continue
        if str(m.get("status")) == "blocked" and not include_blocked:
            continue
        if not include_blocked and not is_unblocked(m, done_ids):
            continue
        items.append((m, p))
    return sorted(items, key=sort_pair)


def owner_norm(value: Any) -> str:
    return str(value or "").strip().lower()


def append_note(body: str, note: str) -> str:
    if "## Notes" in body:
        return body.replace("## Notes", "## Notes\n" + note, 1)
    return body + "\n## Notes\n" + note


def unchecked_task_lines(body: str) -> list[str]:
    """Markdown `- [ ]` lines in the issue body (Work / Acceptance sections)."""
    return [
        line.strip()
        for line in body.splitlines()
        if re.match(r"^-\s*\[\s\]", line.strip())
    ]


def load_feedback(limit: int | None = None) -> list[dict[str, Any]]:
    if not FEEDBACK_JSONL.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in FEEDBACK_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if limit is not None:
        return rows[-limit:]
    return rows


def post_feedback(
    *,
    from_owner: str,
    to_owner: str,
    kind: str,
    body: str,
    issue: str = "",
) -> dict[str, Any]:
    kind = kind.lower().strip()
    if kind not in VALID_KINDS:
        raise SystemExit(f"Invalid kind '{kind}'. Use one of: {', '.join(VALID_KINDS)}")
    event = {
        "ts": utc_now(),
        "from": owner_norm(from_owner) or "unknown",
        "to": owner_norm(to_owner) or "*",
        "kind": kind,
        "issue": (issue or "").upper(),
        "body": body.strip(),
    }
    FEEDBACK_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with FEEDBACK_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    render_feedback_md()
    return event


def feedback_for_owner(owner: str, limit: int = 15) -> list[dict[str, Any]]:
    me = owner_norm(owner)
    out: list[dict[str, Any]] = []
    for ev in reversed(load_feedback()):
        to = owner_norm(ev.get("to"))
        frm = owner_norm(ev.get("from"))
        if frm == me:
            continue
        if to in {me, "*", "all", "broadcast", ""}:
            out.append(ev)
        if len(out) >= limit:
            break
    return list(reversed(out))


def render_feedback_md() -> None:
    events = load_feedback(limit=40)
    lines = [
        "# Cross-agent feedback loop",
        "",
        "Shared channel between **Cursor** (`cursor`) and **Google Antigravity** (`antigravity`).",
        "",
        "Machine log: [`feedback.jsonl`](feedback.jsonl) (append-only).",
        "",
        "## Ritual",
        "",
        "```bash",
        "python scripts/devloop.py loop",
        "python scripts/devloop.py inbox --owner cursor",
        "python scripts/devloop.py inbox --owner antigravity",
        "python scripts/devloop.py say --from cursor --to antigravity --kind note -- \"message\"",
        "```",
        "",
        "Full protocol: [docs/dev/FEEDBACK_LOOP.md](../dev/FEEDBACK_LOOP.md)",
        "",
        "## Latest messages",
        "",
    ]
    if not events:
        lines.append("_No messages yet. Use `devloop say` or claim/done to post._")
        lines.append("")
    else:
        for ev in reversed(events):
            issue = ev.get("issue") or "-"
            lines.append(
                f"### {ev.get('ts')} | {ev.get('from')} → {ev.get('to')} | "
                f"`{ev.get('kind')}` | {issue}"
            )
            lines.append("")
            lines.append(ev.get("body") or "")
            lines.append("")
    FEEDBACK_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def pick_for_owner(owner: str | None) -> tuple[dict[str, Any], Path] | None:
    """Pick issue for a worker: their NOW first, else first unclaimed backlog."""
    opens = open_issues()
    if not opens:
        return None
    if not owner:
        now = [x for x in opens if x[0].get("status") == "now"]
        return (now or opens)[0]

    mine = [
        x
        for x in opens
        if x[0].get("status") == "now" and owner_norm(x[0].get("owner")) == owner_norm(owner)
    ]
    if mine:
        return mine[0]

    for m, p in opens:
        if m.get("status") == "now":
            # Skip other workers' active claims
            if owner_norm(m.get("owner")) and owner_norm(m.get("owner")) != owner_norm(owner):
                continue
        if m.get("status") in {"backlog", "todo"}:
            return m, p
        if m.get("status") == "now" and owner_norm(m.get("owner")) in {"", owner_norm(owner)}:
            return m, p
    return None


def rebuild_board() -> None:
    items = list_issues()
    now = [(m, p) for m, p in items if m.get("status") == "now"]
    done = [(m, p) for m, p in items if m.get("status") == "done"]
    open_ = open_issues(include_blocked=True)
    open_ = [(m, p) for m, p in open_ if m.get("status") != "done"]

    now_lines = [
        "# NOW",
        "",
        f"Active focus — **max {MAX_PARALLEL} parallel workers** (people or AIs).",
        "See [docs/dev/PARALLEL.md](../dev/PARALLEL.md).",
        "",
        "| ID | Title | Phase | Priority | Owner |",
        "|----|-------|-------|----------|-------|",
    ]
    if not now:
        now_lines.append("| — | _(none claimed)_ | — | — | — |")
    else:
        for m, _ in sorted(now, key=sort_pair):
            now_lines.append(
                f"| [{m.get('id')}](issues/{m.get('id')}.md) | {m.get('title')} | "
                f"{m.get('phase')} | {m.get('priority')} | {m.get('owner') or '—'} |"
            )
    now_lines.append("")
    now_lines.append("Generated plan: [LIVE_PLAN.md](LIVE_PLAN.md) (`devloop sync`).")
    now_lines.append("")
    (BOARD / "NOW.md").write_text("\n".join(now_lines) + "\n", encoding="utf-8")

    actionable = open_issues()
    next_candidates = [m for m, _ in actionable if m.get("status") in {"now", "backlog", "todo"}][:12]
    next_lines = [
        "# NEXT",
        "",
        "Refreshed by `python scripts/devloop.py refresh`.",
        "Two workers: use `next --owner YOU` so you skip the other's claim.",
        "",
    ]
    for i, m in enumerate(next_candidates, 1):
        own = m.get("owner") or "—"
        next_lines.append(
            f"{i}. **{m.get('id')}** (phase {m.get('phase')}, {m.get('priority')}, "
            f"owner={own}) — {m.get('title')}"
        )
    next_lines.append("")
    (BOARD / "NEXT.md").write_text("\n".join(next_lines) + "\n", encoding="utf-8")

    backlog_lines = [
        "# BACKLOG",
        "",
        "Open work ranked by status then priority. Source: issue frontmatter.",
        "",
        "| ID | Title | Phase | Priority | Status | Owner |",
        "|----|-------|-------|----------|--------|-------|",
    ]
    for m, _ in sorted(
        [(m, p) for m, p in items if m.get("status") != "done"],
        key=sort_pair,
    ):
        backlog_lines.append(
            f"| {m.get('id')} | {m.get('title')} | {m.get('phase')} | "
            f"{m.get('priority')} | {m.get('status')} | {m.get('owner') or '—'} |"
        )
    backlog_lines.append("")
    (BOARD / "BACKLOG.md").write_text("\n".join(backlog_lines) + "\n", encoding="utf-8")

    done_lines = ["# DONE", "", "Completed issues (newest first).", ""]
    if not done:
        done_lines.append("_None yet._")
    else:
        for m, _ in sorted(done, key=lambda x: str(x[0].get("id")), reverse=True):
            done_lines.append(f"- [{m.get('id')}](issues/{m.get('id')}.md) — {m.get('title')}")
    done_lines.append("")
    (BOARD / "DONE.md").write_text("\n".join(done_lines) + "\n", encoding="utf-8")


def cmd_who(_: argparse.Namespace) -> None:
    rebuild_board()
    snap = make_snapshot()
    snap["fingerprint"] = snapshot_fingerprint(snap)
    print("=== WHO IS WORKING ON WHAT ===")
    print(f"Updated: {snap['generated_at']} | fp {snap['fingerprint']}")
    print()
    now = snap["now"]
    if not now:
        print("NOW: (empty) — 2 slots free")
    else:
        print(f"NOW: {len(now)}/2 slots")
        for item in now:
            print(
                f"  {item.get('owner') or '?':12} -> {item['id']} "
                f"[phase {item.get('phase')} {item.get('priority')}] {item['title']}"
            )
        free = max(0, MAX_PARALLEL - len(now))
        if free:
            print(f"  (+ {free} slot(s) free for cursor / antigravity / minimax / claude)")
    print()
    print("Files: docs/board/NOW.md | docs/board/LIVE_PLAN.md | docs/board/FEEDBACK.md")
    print("Refresh: python scripts/devloop.py sync")


def cmd_status(_: argparse.Namespace) -> None:
    rebuild_board()
    now = [m for m, _ in list_issues() if m.get("status") == "now"]
    blocked = [m for m, _ in list_issues() if m.get("status") == "blocked"]
    print("=== JARVIS DEVLOOP STATUS ===")
    print(f"Parallel slots: {len(now)}/{MAX_PARALLEL} (2 people or 2 AIs)")
    print(f"NOW ({len(now)}):")
    for m in now:
        print(
            f"  - {m.get('id')}: {m.get('title')} "
            f"[{m.get('priority')} phase {m.get('phase')}] owner={m.get('owner') or '—'}"
        )
    if not now:
        print("  (empty — two workers can claim)")
    tip = open_issues()
    print(f"NEXT tip: {tip[0][0].get('id') if tip else 'none'}")
    if blocked:
        print("BLOCKED:")
        for m in blocked:
            print(f"  - {m.get('id')}: {m.get('title')} blocked_by={m.get('blocked_by')}")
    print(f"Actionable open issues: {len(open_issues())} (unblocked only)")
    print("Who: python scripts/devloop.py who")
    print("Parallel guide: docs/dev/PARALLEL.md")


def cmd_next(args: argparse.Namespace) -> None:
    rebuild_board()
    tier = getattr(args, "tier", None)
    picked: tuple[dict[str, Any], Path] | None = None
    if tier == "mini":
        done_ids = {str(m.get("id")) for m, _ in list_issues() if m.get("status") == "done"}
        result = suggest_issue_for_tier(
            "mini",
            list_issues_fn=list_issues,
            open_issues_fn=open_issues,
            is_unblocked_fn=lambda m, d=done_ids: is_unblocked(m, d),
        )
        if result:
            picked = result
    if picked is None:
        picked = pick_for_owner(getattr(args, "owner", None))
    if not picked:
        print("No open issue available for this owner (slot full or all claimed).")
        if tier == "mini":
            print("Tip: claim from docs/dev/MINIMAX_QUEUE.md or add `starter` label.")
        return
    meta = picked[0]
    print(f"{meta.get('id')}: {meta.get('title')}")
    print(
        f"phase={meta.get('phase')} priority={meta.get('priority')} "
        f"status={meta.get('status')} owner={meta.get('owner') or '—'}"
    )
    acc = meta.get("acceptance") or []
    if acc:
        print("acceptance:")
        for a in acc:
            print(f"  - {a}")


def cmd_claim(args: argparse.Namespace) -> None:
    meta, body, path = load_issue(args.id)
    owner = args.owner or "agent"
    existing = owner_norm(meta.get("owner"))
    if (
        meta.get("status") == "now"
        and existing
        and existing != owner_norm(owner)
        and not args.steal
    ):
        raise SystemExit(
            f"{meta.get('id')} is owned by '{meta.get('owner')}'. "
            f"Pick another issue or pass --steal if that worker is gone."
        )

    now_items = [m for m, _ in list_issues() if m.get("status") == "now"]
    already_mine = meta.get("status") == "now" and existing == owner_norm(owner)
    if not already_mine and len(now_items) >= MAX_PARALLEL:
        owners = ", ".join(f"{m.get('id')}={m.get('owner') or '—'}" for m in now_items)
        raise SystemExit(
            f"NOW full ({MAX_PARALLEL} parallel workers). In progress: {owners}. "
            f"Finish or release one first."
        )

    if not already_mine:
        for m, _ in list_issues():
            if (
                m.get("status") == "now"
                and owner_norm(m.get("owner")) == owner_norm(owner)
                and m.get("id") != meta.get("id")
            ):
                raise SystemExit(
                    f"Owner '{owner}' already has {m.get('id')} in NOW. "
                    f"Done/release it before claiming another."
                )

    meta["status"] = "now"
    meta["owner"] = owner
    meta["claimed_at"] = utc_now()
    body = append_note(body, f"\n- Claimed by {meta['owner']} at {meta['claimed_at']}\n")
    save_issue(meta, body, path)
    rebuild_board()
    write_live_plan_file()
    filled = sum(1 for m, _ in list_issues() if m.get("status") == "now")
    print(f"Claimed {meta['id']} as {owner} (parallel {filled}/{MAX_PARALLEL})")
    other = "antigravity" if owner_norm(owner) == "cursor" else "cursor"
    if owner_norm(owner) not in {"cursor", "antigravity"}:
        other = "*"
    post_feedback(
        from_owner=owner,
        to_owner=other,
        kind="claim",
        issue=str(meta.get("id")),
        body=f"Claimed {meta.get('id')}: {meta.get('title')}. Please avoid overlapping paths.",
    )


def cmd_release(args: argparse.Namespace) -> None:
    meta, body, path = load_issue(args.id)
    owner = args.owner or ""
    if (
        owner
        and owner_norm(meta.get("owner")) not in {"", owner_norm(owner)}
        and not args.steal
    ):
        raise SystemExit(f"Cannot release {meta.get('id')}: owned by {meta.get('owner')}")
    prev = meta.get("owner") or "—"
    meta["status"] = "backlog"
    meta["owner"] = ""
    meta["claimed_at"] = ""
    body = append_note(body, f"\n- Released by {owner or 'unknown'} at {utc_now()} (was {prev})\n")
    save_issue(meta, body, path)
    rebuild_board()
    print(f"Released {meta.get('id')} back to backlog")


def cmd_update(args: argparse.Namespace) -> None:
    meta, body, path = load_issue(args.id)
    stamp = utc_now()
    body = append_note(body, f"\n- [{stamp}] {args.note}\n")
    save_issue(meta, body, path)
    print(f"Updated {meta['id']}")


def cmd_done(args: argparse.Namespace) -> None:
    meta, body, path = load_issue(args.id)
    pending = unchecked_task_lines(body)
    if pending and not getattr(args, "force", False):
        print(f"Cannot mark {meta.get('id')} done — {len(pending)} unchecked task(s):")
        for line in pending[:8]:
            print(f"  {line}")
        if len(pending) > 8:
            print(f"  ... and {len(pending) - 8} more")
        print("Tick [ ] → [x] in the issue, or pass --force after manual verify.")
        raise SystemExit(1)
    meta["status"] = "done"
    stamp = utc_now()
    body = append_note(body, f"\n- [{stamp}] Marked done\n")
    save_issue(meta, body, path)

    changelog = BOARD / "CHANGELOG.md"
    entry = f"- {stamp[:10]}: DONE {meta.get('id')} — {meta.get('title')}\n"
    if changelog.exists():
        text = changelog.read_text(encoding="utf-8")
        lines = text.splitlines()
        insert_at = 1
        for i, line in enumerate(lines):
            if line.startswith("## "):
                insert_at = i + 1
                break
        lines.insert(insert_at, entry.rstrip())
        changelog.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        changelog.write_text("# Changelog\n\n" + entry, encoding="utf-8")

    rebuild_board()
    write_live_plan_file()
    owner = str(meta.get("owner") or "unknown")
    other = "antigravity" if owner_norm(owner) == "cursor" else "cursor"
    if owner_norm(owner) not in {"cursor", "antigravity"}:
        other = "*"
    tip = open_issues()
    tip_id = tip[0][0].get("id") if tip else "none"
    post_feedback(
        from_owner=owner,
        to_owner=other,
        kind="done",
        issue=str(meta.get("id")),
        body=(
            f"Done {meta.get('id')}: {meta.get('title')}. "
            f"Slot free. Suggested next tip: {tip_id}. "
            f"Run: python scripts/devloop.py loop"
        ),
    )
    print(f"Done {meta['id']}")


def next_issue_id() -> str:
    nums = []
    for m, _ in list_issues():
        mid = str(m.get("id", ""))
        mo = re.match(r"ISSUE-(\d+)", mid)
        if mo:
            nums.append(int(mo.group(1)))
    n = max(nums) + 1 if nums else 1
    return f"ISSUE-{n:03d}"


def cmd_issue(args: argparse.Namespace) -> None:
    issue_id = next_issue_id()
    meta = {
        "id": issue_id,
        "title": args.title,
        "status": "backlog",
        "priority": args.priority,
        "phase": args.phase,
        "labels": [x.strip() for x in args.labels.split(",") if x.strip()] if args.labels else [],
        "owner": "",
        "claimed_at": "",
        "blocked_by": [],
        "acceptance": [args.acceptance] if args.acceptance else ["Define acceptance criteria"],
    }
    body = (
        f"## Context\n\n{args.title}\n\n## Work\n\n- [ ] Implement\n\n"
        f"## Notes\n\nCreated by devloop at {utc_now()}\n"
    )
    path = issue_path(issue_id)
    save_issue(meta, body, path)
    rebuild_board()
    print(f"Created {issue_id} -> {path}")


def make_snapshot() -> dict[str, Any]:
    issues = list_issues()
    now_items = [m for m, _ in issues if m.get("status") == "now"]
    return build_snapshot(
        issues=issues,
        open_issues=open_issues(),
        now_items=now_items,
        pick_for_owner_fn=pick_for_owner,
    )


def write_live_plan_file() -> dict[str, Any]:
    snap = make_snapshot()
    snap["fingerprint"] = snapshot_fingerprint(snap)
    LIVE_PLAN.parent.mkdir(parents=True, exist_ok=True)
    LIVE_PLAN.write_text(render_live_plan(snap), encoding="utf-8")
    return snap


def refresh_code_map() -> None:
    """Regenerate the lightweight repo index and code map if available."""
    try:
        from index_repo import DEFAULT_DB, render_map, write_index
    except Exception:
        return

    entries = write_index(DEFAULT_DB)
    CODE_MAP.parent.mkdir(parents=True, exist_ok=True)
    CODE_MAP.write_text(render_map(entries, limit=len(entries)), encoding="utf-8")


def cmd_refresh(_: argparse.Namespace) -> None:
    rebuild_board()
    render_feedback_md()
    refresh_code_map()
    snap = write_live_plan_file()
    print("Board refreshed: NOW.md NEXT.md BACKLOG.md DONE.md FEEDBACK.md")
    print(f"Live plan: {LIVE_PLAN.relative_to(ROOT)} (fingerprint tail in file)")
    _ = snap


def cmd_sync(args: argparse.Namespace) -> None:
    """Refresh board + feedback + LIVE_PLAN; optional LIVE_BRIEF for --owner."""
    rebuild_board()
    render_feedback_md()
    refresh_code_map()
    snap = write_live_plan_file()
    owner = getattr(args, "owner", None)
    if owner:
        picked = pick_for_owner(owner)
        if picked:
            meta, path = picked
            _, body = parse_frontmatter(path.read_text(encoding="utf-8"))
            inbox = feedback_for_owner(owner, limit=8)
            text = render_brief(
                snap=snap,
                owner=owner,
                meta=meta,
                body=body,
                path=path,
                inbox=inbox,
            )
            LIVE_BRIEF.write_text(text, encoding="utf-8")
            print(f"Wrote {LIVE_BRIEF.relative_to(ROOT)}")
        else:
            print(f"No issue pick for owner={owner}; LIVE_BRIEF not updated.")
    print(f"Sync OK @ {snap['generated_at']} | open={snap['open_count']} | focus phase {snap['focus_phase']}")
    print(f"Plan: {LIVE_PLAN.relative_to(ROOT)}")


def cmd_plan(_: argparse.Namespace) -> None:
    refresh_code_map()
    snap = write_live_plan_file()
    print(render_live_plan(snap))


def cmd_brief(args: argparse.Namespace) -> None:
    rebuild_board()
    refresh_code_map()
    snap = make_snapshot()
    owner = args.owner or "agent"
    if not args.owner:
        print("Note: using owner=agent; pass --owner for lane-specific rules.")
    picked = pick_for_owner(owner)
    if not picked:
        print("No open issue available for this owner.")
        return
    meta, path = picked
    _, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    inbox = feedback_for_owner(owner, limit=8)
    text = render_brief(
        snap=snap,
        owner=owner,
        meta=meta,
        body=body,
        path=path,
        inbox=inbox,
    )
    LIVE_BRIEF.write_text(text, encoding="utf-8")
    LIVE_PLAN.write_text(render_live_plan(snap), encoding="utf-8")
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))
    print()
    print(f"--- also wrote {LIVE_BRIEF.relative_to(ROOT)} and refreshed {LIVE_PLAN.name} ---")


def cmd_prompt(args: argparse.Namespace) -> None:
    """Dynamic work package. Writes LIVE_BRIEF + LIVE_PLAN."""
    if not getattr(args, "owner", None):
        args.owner = "agent"
        print("Tip: pass --owner cursor|minimax|antigravity|claude for owner-specific rules.")
    cmd_brief(args)


def cmd_say(args: argparse.Namespace) -> None:
    msg = " ".join(args.message).strip()
    if not msg:
        raise SystemExit("Message body required after --")
    ev = post_feedback(
        from_owner=args.from_owner,
        to_owner=args.to,
        kind=args.kind,
        issue=args.issue or "",
        body=msg,
    )
    print(
        f"Posted {ev['kind']}: {ev['from']} -> {ev['to']} "
        f"({ev.get('issue') or '-'})"
    )


def cmd_inbox(args: argparse.Namespace) -> None:
    render_feedback_md()
    owner = args.owner
    rows = feedback_for_owner(owner, limit=args.limit)
    print(f"=== INBOX for {owner} ({len(rows)}) ===")
    if not rows:
        print("(empty)")
        return
    for ev in rows:
        print(
            f"[{ev.get('ts')}] {ev.get('from')} -> {ev.get('to')} "
            f"| {ev.get('kind')} | {ev.get('issue') or '-'}"
        )
        print(f"  {ev.get('body')}")


def cmd_loop(_: argparse.Namespace) -> None:
    rebuild_board()
    render_feedback_md()
    refresh_code_map()
    snap = write_live_plan_file()
    now = [m for m, _ in list_issues() if m.get("status") == "now"]
    print("=== CROSS-AGENT LOOP ===")
    print(f"Generated: {snap['generated_at']} · focus phase {snap['focus_phase']} · fp `{snap.get('fingerprint', '')}`")
    print("Live plan: docs/board/LIVE_PLAN.md")
    print(f"Slots: {len(now)}/{MAX_PARALLEL}")
    if not now:
        print("NOW: (empty)")
    for m in now:
        print(
            f"  - {m.get('owner') or '—'}: {m.get('id')} — {m.get('title')} "
            f"[phase {m.get('phase')} {m.get('priority')}]"
        )
    print()
    for oid in KNOWN_OWNERS:
        if oid in ("alice", "bob"):
            continue
        tip = pick_for_owner(oid)
        if tip:
            m = tip[0]
            mine = m.get("status") == "now" and owner_norm(m.get("owner")) == oid
            suffix = " [YOUR NOW]" if mine else ""
            print(f"NEXT for {oid}: {m.get('id')} — {m.get('title')}{suffix}")
        else:
            print(f"NEXT for {oid}: (none available)")
    print()
    print("Personal brief: python scripts/devloop.py brief --owner YOUR_ID")
    print("Who is working: python scripts/devloop.py who")
    print("Full sync:       python scripts/devloop.py sync --owner YOUR_ID")
    print("--- Recent feedback ---")
    recent = load_feedback(limit=8)
    if not recent:
        print("(no messages yet)")
    for ev in recent:
        print(
            f"[{ev.get('ts')}] {ev.get('from')}->{ev.get('to')} "
            f"{ev.get('kind')} {ev.get('issue') or ''}: {ev.get('body')}"
        )
    print()
    print("Commands: inbox --owner ME | say --from ME --to THEM --kind note -- \"...\"")


def cmd_watch(args: argparse.Namespace) -> None:
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        raise SystemExit("watchdog not installed. Run: uv pip install watchdog")

    import time
    
    class BoardHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith(".md"):
                # Avoid infinite loops when we write NOW.md etc.
                name = Path(event.src_path).name
                if name in ("NOW.md", "NEXT.md", "BACKLOG.md", "DONE.md", "FEEDBACK.md", "LIVE_PLAN.md"):
                    return
                print(f"[{utc_now()}] Detected change in {name}, syncing...")
                cmd_sync(argparse.Namespace(owner=None))
                
    observer = Observer()
    observer.schedule(BoardHandler(), str(ISSUES), recursive=False)
    observer.schedule(BoardHandler(), str(BOARD), recursive=False)
    observer.start()
    
    print(f"Watching for changes in {BOARD}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def cmd_agents(_: argparse.Namespace) -> None:
    rebuild_board()
    data = load_registry()
    now_by_owner: dict[str, dict[str, Any]] = {}
    for m, _ in list_issues():
        if m.get("status") == "now" and m.get("owner"):
            now_by_owner[owner_norm(m.get("owner"))] = m

    print("=== AGENT REGISTRY + NOW ===")
    print(f"File: {ROOT / 'docs/board/agents.json'}")
    print()
    for a in data.get("agents", []):
        aid = str(a.get("id", ""))
        tier = a.get("tier", "?")
        plat = a.get("platform", "?")
        name = a.get("display_name", aid)
        active = a.get("active", True)
        issue = now_by_owner.get(owner_norm(aid))
        if issue:
            work = f"NOW -> {issue.get('id')}"
        else:
            work = "idle"
        flag = "" if active else " (inactive)"
        print(f"  {aid:14} | {tier:8} | {plat:10} | {name}{flag} | {work}")
    print()
    print("Onboard new: python scripts/devloop.py onboard --tier mini --platform blackbox")


def cmd_register(args: argparse.Namespace) -> None:
    entry = register_agent(
        agent_id=args.id,
        display_name=args.display_name or args.id,
        tier=args.tier,
        platform=args.platform,
        note=args.note or "",
    )
    print(f"Registered {entry['id']} tier={entry['tier']} platform={entry['platform']}")


def cmd_onboard(args: argparse.Namespace) -> None:
    rebuild_board()
    write_live_plan_file()
    data = load_registry()

    if args.id:
        agent_id = args.id.strip().lower()
    elif args.platform == "blackbox":
        agent_id = next_blackbox_id(data)
    else:
        agent_id = next_coder_id(data)

    display = args.display_name or f"AI Coder ({agent_id})"
    try:
        entry = register_agent(
            agent_id=agent_id,
            display_name=display,
            tier=args.tier,
            platform=args.platform,
            note=args.note or "onboarded via devloop",
        )
    except ValueError as e:
        if not args.id:
            raise SystemExit(str(e)) from e
        entry = {"id": agent_id, "tier": args.tier, "platform": args.platform}
        print(f"Note: {e} (using existing id)")

    now_count = sum(1 for m, _ in list_issues() if m.get("status") == "now")
    slots_free = max(0, MAX_PARALLEL - now_count)

    picked = suggest_issue_for_tier(
        args.tier,
        list_issues_fn=list_issues,
        open_issues_fn=open_issues,
        is_unblocked_fn=is_unblocked,
    )

    print("=== ONBOARD NEW AI CODER ===")
    print()
    print(f"Your owner id:     {entry['id']}")
    print(f"Display name:      {display}")
    print(f"Tier:              {args.tier}")
    print(f"Platform:          {args.platform}")
    print(f"Parallel slots:    {now_count}/{MAX_PARALLEL} used ({slots_free} free)")
    print()
    print("Paste into the AI project instructions:")
    print("-" * 50)
    print(f"Owner id: {entry['id']}. EXECUTE MODE — no plan re-approval.")
    print("Read .blackbox/EXECUTE.md and docs/dev/MINIMAX.md (mini tier) or AGENTS.md.")
    print(f"Every command uses --owner {entry['id']}")
    print("-" * 50)
    print()
    if slots_free == 0:
        print("NOW is full. Wait, then run:")
        print(f"  python scripts/devloop.py claim ISSUE-XXX --owner {entry['id']}")
    elif picked:
        meta, path = picked
        iid = meta.get("id")
        print(f"Suggested issue:   {iid} — {meta.get('title')}")
        print()
        print("```bash")
        print(f"python scripts/devloop.py sync --owner {entry['id']}")
        print(f"python scripts/devloop.py claim {iid} --owner {entry['id']}")
        print(f"python scripts/devloop.py brief --owner {entry['id']}")
        print("```")
    else:
        print("No starter issue in queue — run: python scripts/devloop.py next --owner " + entry["id"])
    print()
    print("Manager check: python scripts/devloop.py agents")
    print("Who is working: python scripts/devloop.py who")


def cmd_verify(args: argparse.Namespace) -> None:
    # Route to the new modular Typer app
    from commands.verify_cmd import verify
    diff_val = getattr(args, "diff", False)
    
    try:
        verify(issue_id=args.id, diff=diff_val)
    except SystemExit as e:
        raise e
    except Exception as e:
        # Catch typer.Exit safely
        if e.__class__.__name__ == "Exit":
            raise SystemExit(e.exit_code)
        raise e


def cmd_bootstrap(_: argparse.Namespace) -> None:
    ISSUES.mkdir(parents=True, exist_ok=True)
    FEEDBACK_JSONL.touch(exist_ok=True)
    rebuild_board()
    render_feedback_md()
    print(f"Bootstrap OK. Root={ROOT}")
    print(f"Issues on board: {len(list_issues())}")
    print(f"Parallel workers supported: {MAX_PARALLEL}")
    print("Run: python scripts/devloop.py loop")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Jarvis internal AI app-dev feedback loop (2 parallel workers)"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("who", help="Show active owners and issues (shared visibility)").set_defaults(func=cmd_who)
    sub.add_parser("refresh").set_defaults(func=cmd_refresh)
    sub.add_parser("bootstrap").set_defaults(func=cmd_bootstrap)
    sub.add_parser("loop").set_defaults(func=cmd_loop)
    sub.add_parser("plan", help="Print regenerated LIVE_PLAN to stdout").set_defaults(func=cmd_plan)
    sub.add_parser("watch", help="Watch board and auto-sync changes").set_defaults(func=cmd_watch)

    sy = sub.add_parser("sync", help="Refresh board + LIVE_PLAN; optional LIVE_BRIEF")
    sy.add_argument("--owner", default=None, help="Also write LIVE_BRIEF for this owner")
    sy.set_defaults(func=cmd_sync)

    bf = sub.add_parser("brief", help="Dynamic agent instructions (stdout + LIVE_BRIEF)")
    bf.add_argument("--owner", default="agent", help="Worker id")
    bf.set_defaults(func=cmd_brief)

    n = sub.add_parser("next")
    n.add_argument(
        "--owner",
        default=None,
        help="Your worker id (cursor, antigravity, claude, ...)",
    )
    n.add_argument(
        "--tier",
        default=None,
        choices=["mini", "standard"],
        help="mini: MINI_ISSUE_QUEUE + starter backlog (for minimax2)",
    )
    n.set_defaults(func=cmd_next)

    pr = sub.add_parser("prompt")
    pr.add_argument("--owner", default=None, help="Your worker id for a personal brief")
    pr.set_defaults(func=cmd_prompt)

    c = sub.add_parser("claim")
    c.add_argument("id")
    c.add_argument("--owner", default="agent")
    c.add_argument(
        "--steal",
        action="store_true",
        help="Take over another worker's claim (only if they abandoned it)",
    )
    c.set_defaults(func=cmd_claim)

    r = sub.add_parser("release")
    r.add_argument("id")
    r.add_argument("--owner", default="")
    r.add_argument("--steal", action="store_true")
    r.set_defaults(func=cmd_release)

    u = sub.add_parser("update")
    u.add_argument("id")
    u.add_argument("--note", required=True)
    u.set_defaults(func=cmd_update)

    d = sub.add_parser("done")
    d.add_argument("id")
    d.add_argument(
        "--force",
        action="store_true",
        help="Mark done even if issue body has unchecked - [ ] tasks",
    )
    d.set_defaults(func=cmd_done)

    i = sub.add_parser("issue")
    i.add_argument("--title", required=True)
    i.add_argument("--phase", default="0")
    i.add_argument("--priority", default="P1", choices=["P0", "P1", "P2"])
    i.add_argument("--labels", default="")
    i.add_argument("--acceptance", default="")
    i.set_defaults(func=cmd_issue)

    s = sub.add_parser("say", help="Post a message on the cross-agent bus")
    s.add_argument("--from", dest="from_owner", required=True)
    s.add_argument("--to", required=True, help="Other owner id, or * for broadcast")
    s.add_argument("--kind", default="note", choices=list(VALID_KINDS))
    s.add_argument("--issue", default="")
    s.add_argument("message", nargs=argparse.REMAINDER, help="Message after --")
    s.set_defaults(func=cmd_say)

    ib = sub.add_parser("inbox", help="Read messages for an owner")
    ib.add_argument("--owner", required=True)
    ib.add_argument("--limit", type=int, default=15)
    ib.set_defaults(func=cmd_inbox)

    sub.add_parser("agents", help="List registered agents and NOW work").set_defaults(func=cmd_agents)

    reg = sub.add_parser("register", help="Register an agent id in agents.json")
    reg.add_argument("--id", required=True)
    reg.add_argument("--display-name", default="")
    reg.add_argument("--tier", default="standard", choices=["mini", "standard", "lead"])
    reg.add_argument("--platform", default="unknown")
    reg.add_argument("--note", default="")
    reg.set_defaults(func=cmd_register)

    ob = sub.add_parser("onboard", help="Name a new AI coder and suggest an issue")
    ob.add_argument("--tier", default="mini", choices=["mini", "standard", "lead"])
    ob.add_argument("--platform", default="blackbox", choices=["blackbox", "cursor", "antigravity", "claude", "other"])
    ob.add_argument("--display-name", default="")
    ob.add_argument("--id", default="", help="Optional fixed id; else auto minimax3 / coder-NNN")
    ob.add_argument("--note", default="")
    ob.set_defaults(func=cmd_onboard)

    vf = sub.add_parser("verify", help="Check issue ## Lane paths exist on disk")
    vf.add_argument("id", help="ISSUE-XXX or XXX")
    vf.add_argument("--diff", action="store_true", help="Fail if git diff contains files outside the Lane")
    vf.set_defaults(func=cmd_verify)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    # Allow: say ... -- message words
    if getattr(args, "message", None) is not None and args.message[:1] == ["--"]:
        args.message = args.message[1:]
    args.func(args)


if __name__ == "__main__":
    main()
