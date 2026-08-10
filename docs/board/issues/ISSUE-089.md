---
id: ISSUE-089
title: Flet footer shows Bridge connected after WS register
status: done
priority: P2
phase: 2
labels: [windows, starter, ui]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - With --bridge, footer bridge_text shows Bridge connecting then Bridge connected after register ack
  - On disconnect or bridge error, shows Bridge disconnected or retry hint
  - Does not change chat SSE behavior
---

## Context

ISSUE-081 added bridge hints; UI still stays on "starting" until disconnect. Mini slice for MiniMax.

## Lane

- `clients/windows/client.py` — **only** `bridge_loop` and the small `run_bridge` thread wrapper that calls `set_bridge_status`
- Do **not** edit `ui_gui.py` unless footer label text must change (prefer status strings from client)

## Work

- [ ] After WS register ack in `bridge_loop`, invoke bridge status callback if provided
- [ ] `py_compile` client.py
- [ ] Manual: brain + `python clients/windows/client.py --bridge --pair` — footer shows connected

## Notes

- [2026-08-08T20:34:30Z] Marked done


Playbook: [docs/dev/MINIMAX_UI.md](../../dev/MINIMAX_UI.md)
