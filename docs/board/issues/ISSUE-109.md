---
id: ISSUE-109
title: smoke_web.py — brain health and sessions smoke
status: done
priority: P3
phase: D1
labels: [devloop, starter, scripts]
owner: cursor
claimed_at: 2026-08-09T19:05:00Z
blocked_by: []
acceptance:
  - scripts/smoke_web.py GET /health and GET /sessions from repo root
  - Documented in docs/dev/DEV_ENV.md script map
  - Exits non-zero when brain is down with clear message
---

## Context

[DEV_ENV.md](../../dev/DEV_ENV.md) · [MINIMAX_QUEUE.md](../../dev/MINIMAX_QUEUE.md) wave U.

## Lane

- `scripts/smoke_web.py`
- `docs/dev/DEV_ENV.md`

## Work

- [x] Implement smoke script (stdlib HTTP)
- [x] Verified with brain on :8787

## Notes

Optional: `--pair` when `JARVIS_PAIR_SECRET` is set.
