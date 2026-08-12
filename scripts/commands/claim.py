import argparse
import re
from pathlib import Path

from core.board_io import (
    append_note,
    issue_path,
    list_issues,
    load_issue,
    owner_norm,
    save_issue,
    unchecked_task_lines,
    utc_now,
)
from core.board_snapshot import rebuild_board, write_live_plan_file
from core.feedback_log import post_feedback

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "docs" / "board"
MAX_PARALLEL = 2

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
    from core.board_io import open_issues
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
