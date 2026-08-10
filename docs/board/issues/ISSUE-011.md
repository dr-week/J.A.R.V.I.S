---
id: ISSUE-011
title: Windows client stub chat against brain
status: done
priority: P0
phase: 0
labels: [windows, client]
owner: cursor
claimed_at: 2026-08-07T14:08:56Z
blocked_by: [ISSUE-010]
acceptance:
  - Windows client sends a message to brain
  - Receives a reply (streamed or full)
  - Uses pairing/token stub if present
---

## Context

Desktop presence body #1.

## Notes

- [2026-08-07T14:10:27Z] Marked done


- [2026-08-07T14:10:27Z] Windows client: SSE chat --once + TUI; pairing via POST /pair stub; token file + Authorization header. Verified pair+chat against local brain.


- Claimed by cursor at 2026-08-07T14:08:56Z
