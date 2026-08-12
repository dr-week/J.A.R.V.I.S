#!/usr/bin/env python3
"""Jarvis internal AI app-dev feedback loop.

Manages docs/board issues: status, next, claim, release, issue, update, done,
refresh, sync, plan, brief, prompt (alias of brief), loop, bootstrap, verify.
"""
from __future__ import annotations

import argparse

from commands.claim import cmd_claim, cmd_done, cmd_issue, cmd_release, cmd_update
from commands.comms import cmd_brief, cmd_inbox, cmd_loop, cmd_prompt, cmd_say
from commands.info import cmd_agents, cmd_bootstrap, cmd_next, cmd_status, cmd_who
from commands.onboard import cmd_onboard, cmd_register
from commands.sync import cmd_plan, cmd_refresh, cmd_sync, cmd_watch


def cmd_verify(args: argparse.Namespace) -> None:
    from commands.verify_cmd import verify
    diff_val = getattr(args, "diff", False)
    try:
        verify(issue_id=args.id, diff=diff_val)
    except SystemExit as e:
        raise e
    except Exception as e:
        if e.__class__.__name__ == "Exit":
            raise SystemExit(e.exit_code)
        raise e


VALID_KINDS = ("claim", "done", "note", "ask", "block", "handoff")

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
