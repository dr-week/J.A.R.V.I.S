---
id: ISSUE-102
title: Web — session list and resume (FR-P3)
status: done
priority: P1
phase: 0
labels: [web, sync]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - Fetches GET /sessions and displays recent sessions in nav or sidebar
  - Selecting a session uses GET /sessions/{session_id} and continues with that session_id in /chat
  - New session still supported; brain remains SoT
  - WEB_UI.md updated; no Flutter session UI
---

## Context

FR-P3 continuous session sync — **web-only** chat product ([PRESENCE_STACKS.md](../../dev/PRESENCE_STACKS.md)).

## Lane

- `clients/web/**`
- `docs/dev/WEB_UI.md`

## API

- `GET /sessions?limit=`
- `GET /sessions/{session_id}?limit=`

## Notes

- [2026-08-09T16:14:59Z] Marked done


- [SYNC_PLAN.md](../../dev/SYNC_PLAN.md) · [PLAN_AUDIT.md](../../dev/PLAN_AUDIT.md)
