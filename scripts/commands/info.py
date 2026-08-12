import argparse
from pathlib import Path

from agent_registry import load_registry, suggest_issue_for_tier
from board_context import snapshot_fingerprint
from core.board_io import is_unblocked, list_issues, open_issues, owner_norm
from core.board_snapshot import make_snapshot, pick_for_owner, rebuild_board
from core.feedback_log import render_feedback_md

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "docs" / "board"
ISSUES = BOARD / "issues"
FEEDBACK_JSONL = BOARD / "feedback.jsonl"
MAX_PARALLEL = 2

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
    picked = None
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

def cmd_agents(_: argparse.Namespace) -> None:
    rebuild_board()
    data = load_registry()
    now_by_owner = {}
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

def cmd_bootstrap(_: argparse.Namespace) -> None:
    ISSUES.mkdir(parents=True, exist_ok=True)
    FEEDBACK_JSONL.touch(exist_ok=True)
    rebuild_board()
    render_feedback_md()
    print(f"Bootstrap OK. Root={ROOT}")
    print(f"Issues on board: {len(list_issues())}")
    print(f"Parallel workers supported: {MAX_PARALLEL}")
    print("Run: python scripts/devloop.py loop")
