---
id: ISSUE-118
title: Devloop Refactor - Command Extraction
status: done
priority: P2
phase: 0
labels: [dev, scripts]
owner: 
claimed_at: 
blocked_by: [ISSUE-117]
acceptance:
  - Create `scripts/commands/` package (see [MODULARITY_PLAN.md](../../dev/MODULARITY_PLAN.md) § M1)
  - Move all `cmd_*` handlers into command modules; devloop.py is argparse entry only
  - devloop commands must still work exactly as before.
---

## Context

Extract CLI command handlers from the main devloop script to reduce file size.

## Work

- [ ] Create `scripts/commands/` per MODULARITY_PLAN § M1
- [ ] Move `cmd_*` functions
- [ ] Thin `devloop.py` entry

## Lane

- `scripts/commands/**`
- `scripts/devloop.py`

## Notes

- [2026-08-11T17:09:52Z] Marked done


- Released by unknown at 2026-08-11T17:07:04Z (was AI_Agent)


- Claimed by AI_Agent at 2026-08-11T17:06:52Z


Created by devloop
