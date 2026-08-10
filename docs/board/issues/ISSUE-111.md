---
id: ISSUE-111
title: devloop verify — issue lane paths exist
status: done
priority: P3
phase: D1
labels: [devloop, starter, scripts]
owner: cursor
claimed_at: 2026-08-09T19:05:00Z
blocked_by: []
acceptance:
  - python scripts/devloop.py verify ISSUE-XXX checks ## Lane backtick paths
  - helpers/issue_lane_verify.py stays small and read-only
  - Documented in DEV_ENV.md and MINIMAX_QUEUE.md
---

## Context

Reduces wrong-folder edits for mini agents.

## Lane

- `scripts/helpers/issue_lane_verify.py`
- `scripts/devloop.py`
- `docs/dev/DEV_ENV.md`

## Work

- [x] verify subcommand + helper
- [x] Documented in DEV_ENV / MINIMAX_QUEUE
