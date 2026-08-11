---
id: ISSUE-117
title: Devloop Refactor - Core Extraction
status: now
priority: P2
phase: 0
labels: [dev, scripts]
owner: antigravity
claimed_at: 2026-08-11T04:19:49Z
blocked_by: []
acceptance:
  - Create `scripts/core/` package (see [MODULARITY_PLAN.md](../../dev/MODULARITY_PLAN.md) § M1)
  - Move board domain logic (list_issues, rebuild_board, LIVE_PLAN writers) out of devloop.py
  - Update devloop.py to import these functions. Keep all CLI parser logic untouched in this slice.
  - devloop commands must still work exactly as before.
---

## Context

The scripts/devloop.py file is ~1000 lines long, which makes it hard for small-context models. We need to split it.

## Work

- [ ] Create `scripts/core/` per [MODULARITY_PLAN.md](../../dev/MODULARITY_PLAN.md) § M1
- [ ] Move core logic (list_issues, rebuild_board, LIVE_PLAN, snapshot)
- [ ] Update devloop.py imports; CLI parser stays in devloop.py

## Lane

- `scripts/core/**`
- `scripts/devloop.py`
- `docs/dev/MODULARITY_PLAN.md` (if tree changes)

## Notes

- Claimed by antigravity at 2026-08-11T04:19:49Z


Created by devloop
