---
id: ISSUE-081
title: Flet status bar shows device id and bridge alive
status: done
priority: P2
phase: 2
labels: [windows, starter]
owner: coder-003
claimed_at: 2026-08-08T16:43:09Z
blocked_by: []
acceptance:
  - When --bridge is used with GUI status area shows device_id
  - User can see bridge connected or disconnected hint in UI
---

## Context

Small Windows UI polish (mini+). One file.

## Lane

- `clients/windows/client.py` only — coordinate if another NOW issue touches same file

## Notes

- [2026-08-08T16:43:58Z] Marked done


- [2026-08-08T16:43:52Z] Added device_id and bridge status hints to the Windows Flet UI; the status area now shows the device id and a bridge connected/disconnected line when --bridge is active.


- Claimed by coder-003 at 2026-08-08T16:43:09Z


Part **F** in SMALL_AI_PARTS.md.
