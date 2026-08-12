import argparse
import sys
from pathlib import Path

from board_context import KNOWN_OWNERS, LIVE_BRIEF, LIVE_PLAN, render_brief, render_live_plan
from core.board_io import list_issues, owner_norm, parse_frontmatter
from core.board_snapshot import (
    make_snapshot,
    pick_for_owner,
    rebuild_board,
    refresh_code_map,
    write_live_plan_file,
)
from core.feedback_log import feedback_for_owner, load_feedback, post_feedback, render_feedback_md

ROOT = Path(__file__).resolve().parents[2]
MAX_PARALLEL = 2

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
