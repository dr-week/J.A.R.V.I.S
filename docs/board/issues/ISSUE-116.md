---
id: ISSUE-116
title: Mypy strict typing — API layer
status: done
priority: P1
phase: 0
labels: [dev, starter, scripts]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - tool.mypy in pyproject.toml scoped to backend/app/api
  - uv run mypy backend/app/api reports zero errors
  - No behavior changes to routes
---

## Context

Strict types on API routers only — small surface for mini agents.

## Lane

- `pyproject.toml`
- `backend/app/api/**`

## Work

- [ ] Add `[tool.mypy]` config (strict or strict-ish for api/)
- [ ] Fix annotations in router modules under `backend/app/api/`

## Notes

- [2026-08-11T17:09:44Z] Marked done


- Released by unknown at 2026-08-11T17:06:52Z (was —)


- Released by unknown at 2026-08-11T17:06:51Z (was AI Engineer)


- Claimed by AI Engineer at 2026-08-11T17:06:40Z


Created by devloop. Run after or parallel to **115** (different paths).
