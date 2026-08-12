import argparse

from agent_registry import (
    load_registry,
    next_blackbox_id,
    next_coder_id,
    register_agent,
    suggest_issue_for_tier,
)
from core.board_io import is_unblocked, list_issues, open_issues
from core.board_snapshot import rebuild_board, write_live_plan_file

MAX_PARALLEL = 2

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
