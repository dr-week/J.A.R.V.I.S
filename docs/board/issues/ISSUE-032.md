---
id: ISSUE-032
title: Windows device bridge open app URL file
status: done
priority: P0
phase: 2
labels: [hands, windows]
owner: minimax
claimed_at: 2026-08-08T08:15:15Z
blocked_by: [ISSUE-030, ISSUE-011]
acceptance:
  - Brain can request Windows client to open app/URL/file
  - Result returned and logged
---

## Context

PC Hands.

## Notes

- [2026-08-08T08:28:40Z] Marked done


- [2026-08-08T08:28:11Z] Implemented Windows device bridge (ISSUE-032): windows_open client-executor tool registered; sync manager upgraded with per-device routing + request/response correlation; /ws supports register/tool_execute/tool_result; new clients/windows/device_bridge.py opens app/URL/file; client --bridge WS loop added. Verified: result returned and logged to action_log.


- Claimed by minimax at 2026-08-08T08:15:15Z
