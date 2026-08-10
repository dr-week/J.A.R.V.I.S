---
id: ISSUE-116
title: Mypy strict typing — API layer
status: backlog
priority: P1
phase: "0"
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

Created by devloop. Run after or parallel to **115** (different paths).
