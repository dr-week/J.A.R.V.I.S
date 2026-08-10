---
id: ISSUE-010
title: Backend FastAPI health and monorepo layout
status: done
priority: P0
phase: 0
labels: [backend, skeleton]
owner: cursor
claimed_at: 2026-08-06T19:57:07Z
blocked_by: [ISSUE-002]
acceptance:
  - backend/ FastAPI app starts locally
  - GET /health returns ok
  - .env.example documents required vars
  - Folder layout matches AGENTS.md repo map
---

## Context

Phase 0 gate: brain process exists.

## Work

- [ ] Create backend package
- [ ] Health route
- [ ] README snippet for run instructions

## Notes

- [2026-08-06T20:01:42Z] Marked done


- [2026-08-06T20:01:37Z] Backend complete: FastAPI health + chat SSE + WebSocket + soul CRUD + learning engine + tool registry. 6/6 acceptance tests passing. Brain runs on port 8787.


- Claimed by cursor at 2026-08-06T19:57:07Z


- Claimed by cursor at 2026-08-06T19:35:33Z
