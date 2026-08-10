# Feedback loop between AI developers

**Doc map:** [DOCS_MAP.md](../DOCS_MAP.md)

## Goal

Cursor, Antigravity, Claude, and MiniMax stay in sync **without relying on the human to re-paste status**. The board is the shared bus.

```text
Worker A                    Board                         Worker B
   |                          |                              |
   |-- claim/done/say ------->|                              |
   |                          |<------ loop / inbox ---------|
   |                          |------ FEEDBACK.md ---------->|
```

## Commands

| Command | Purpose |
|---------|---------|
| `devloop loop` | Dual status + last handoffs + next tip per owner |
| `devloop inbox --owner ME` | Messages addressed to you (or broadcast) |
| `devloop say --from ME --to THEM --kind note -- "…"` | Send a handoff / ask / block |
| `devloop claim` / `done` | Auto-posts to the feedback log |

Optional:

```bash
python scripts/devloop.py say --from cursor --to antigravity --kind handoff --issue ISSUE-021 \
  -- "020 done. Please take 021 memory CRUD. I can take 013 pairing."
```

## Files

| Path | Role |
|------|------|
| `docs/board/feedback.jsonl` | Append-only event log |
| `docs/board/FEEDBACK.md` | Human/AI readable view |
| `docs/board/NOW.md` | Who holds which slot |

## Session checklist for each AI

1. `python scripts/devloop.py who` or `sync` — see **who holds NOW**
2. `python scripts/devloop.py loop`
2. `python scripts/devloop.py inbox --owner YOUR_ID`
3. `python scripts/devloop.py prompt --owner YOUR_ID` (includes inbox snippet)
4. Work only your claimed paths
5. `say` if you need the other AI to wait/avoid a directory
6. `done` → other AI sees auto handoff on next `loop`

## Human relay (when IDEs do not share a terminal)

1. Run `python scripts/devloop.py loop` in one IDE
2. Paste the output into the other AI chat
3. Or both AIs just read `docs/board/FEEDBACK.md` from the repo
