---
id: ISSUE-082
title: Flet reconnect brain button on health failure
status: done
priority: P2
phase: 2
labels: [windows, starter]
owner: cursor
claimed_at: ""
blocked_by: []
acceptance:
  - If /health fails show a Reconnect control that retries health and updates status
  - Does not break SSE chat when brain is up
---

## Context

Small UX slice (mini+). **Claim after ISSUE-081** or different owner with coordination.

## Lane

- `clients/windows/ui_gui.py` (UI moved out of monolithic `client.py`)

## Notes

- [2026-08-09] Done: Reconnect in header + `refresh_connection` in `ui_gui.py`. Verified with smoke test.
- Part **G** in SMALL_AI_PARTS.md.
