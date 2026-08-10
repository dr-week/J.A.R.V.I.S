---
id: ISSUE-090
title: Flet New chat button resets session
status: done
priority: P2
phase: 0
labels: [windows, starter, ui]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - Header or footer has New chat control
  - Clears chat list (keeps welcome/system lines optional — at least clears user/assistant bubbles)
  - New UUID used for session_id on next send
  - Existing token and brain connection unchanged
---

## Context

Operators need a fresh thread without killing the app. MiniMax one-file UI slice.

## Lane

- `clients/windows/ui_gui.py` only
- May add `session_holder: dict` parameter from `launch_flet_desktop` / `client.py` **only if** issue owner adds one line in client to pass `{"session_id": args.session_id}` — coordinate in Notes before editing client

## Work

- [ ] New chat button + clear UI
- [ ] `py_compile ui_gui.py`
- [ ] `python clients/windows/test_ui_smoke.py`

## Notes

- [2026-08-08T20:34:31Z] Marked done


Playbook: [docs/dev/MINIMAX_UI.md](../../dev/MINIMAX_UI.md)
