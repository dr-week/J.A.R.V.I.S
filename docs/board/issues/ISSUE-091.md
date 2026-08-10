---
id: ISSUE-091
title: Flet footer hint when LLM key missing
status: done
priority: P2
phase: 0
labels: [windows, starter, ui]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - When /health returns llm_ready false, status or footer shows one-line hint to set GEMINI_API_KEY in backend .env
  - When llm_ready true, hint hidden
  - Reconnect refreshes hint correctly
---

## Context

Users see generic chat without knowing why replies are stubbed. MiniMax one-file slice.

## Lane

- `clients/windows/ui_gui.py` only

## Work

- [ ] Use existing health JSON in `refresh_connection`
- [ ] `py_compile` + `test_ui_smoke.py`

## Notes

- [2026-08-08T20:34:31Z] Marked done


Playbook: [docs/dev/MINIMAX_UI.md](../../dev/MINIMAX_UI.md)
