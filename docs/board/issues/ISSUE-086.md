---
id: ISSUE-086
title: Board Copilot suggests next issue and lane
status: done
priority: P2
phase: D1
labels: [tooling, starter, helpers, board]
owner: coder-003
claimed_at: 2026-08-08T16:58:07Z
blocked_by: []
acceptance:
  - scripts/helpers/board_copilot.py --owner ID prints slots, suggest issue, lane prefer/avoid
  - Read-only — never claim or mutate board files
  - Uses NOW/NEXT/issues frontmatter; respects starter queue for --tier mini
---

## Context

Wave 1 internal helper. Keeps new workers from guessing when NOW is full or lanes collide.

## Lane

- `scripts/helpers/board_copilot.py` (new)
- May import from `scripts/devloop.py` / `board_context.py` / `agent_registry.py` carefully (no circular mess — prefer reading board markdown + issue frontmatter)
- `docs/dev/INTERNAL_HELPERS.md` usage line only

## Notes

- [2026-08-08T16:59:33Z] Marked done


- [2026-08-08T16:59:27Z] Added read-only board copilot CLI at scripts/helpers/board_copilot.py; it reads NOW/NEXT/issues frontmatter and prints slot count, suggested issue, lane, and avoid hints without mutating the board.


- Claimed by coder-003 at 2026-08-08T16:58:07Z


Spec: [INTERNAL_HELPERS.md](../dev/INTERNAL_HELPERS.md). Safe parallel with ISSUE-085 (different helper file).
