import argparse
from pathlib import Path

from board_context import LIVE_BRIEF, LIVE_PLAN, render_brief, render_live_plan
from core.board_io import parse_frontmatter, utc_now
from core.board_snapshot import (
    pick_for_owner,
    rebuild_board,
    refresh_code_map,
    write_live_plan_file,
)
from core.feedback_log import feedback_for_owner, render_feedback_md

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "docs" / "board"
ISSUES = BOARD / "issues"

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

def cmd_watch(args: argparse.Namespace) -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
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
