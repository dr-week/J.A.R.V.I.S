---
id: ISSUE-107
title: WebSocket /ws authenticate device token
status: done
priority: P3
phase: 2
labels: [backend, security]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - Browser and Field clients can authenticate WS (query token or first message) per SECURITY.md
  - Unauthenticated /ws rejected in production mode or documented LAN-only exception
  - SYNC_PROTOCOL.md and web syncSocket.ts aligned
---

## Context

[PLAN_AUDIT.md](../../dev/PLAN_AUDIT.md) §7 — web sends `?token=` but brain accepts all connections today.

## Lane

- `backend/app/api/chat.py`, `backend/app/sync/**`
- `docs/SYNC_PROTOCOL.md`, `docs/SECURITY.md`

## Notes

- [2026-08-11T17:55:12Z] Marked done
