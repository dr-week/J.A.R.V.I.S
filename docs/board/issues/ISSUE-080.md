---
id: ISSUE-080
title: GET action_log recent entries read-only API
status: done
priority: P1
phase: 2
labels: [hands, backend, starter]
owner: cursor
claimed_at: 2026-08-09T05:23:32Z
blocked_by: [ISSUE-031]
acceptance:
  - GET endpoint returns last N action_log rows newest first default N=20
  - No delete or mutate; secrets redacted per existing gate rules
  - Brief note in TOOL_SCHEMA or hands router docstring
---

## Context

Small API slice for debugging Hands (mini+ backend).

## Lane

- `backend/app/api/hands.py`, `backend/app/soul/memory.py` or action_log helper only
- Do not change confirmation gate behavior

## Notes

- [2026-08-09T05:26:11Z] Marked done


- [2026-08-09T05:26:10Z] verified: default N=20 newest-first; secrets redacted via gate redact_parameters (top-level + nested); limit capped at 200; read-only confirmed


- Claimed by cursor at 2026-08-09T05:23:32Z


Part **E** in SMALL_AI_PARTS.md. ISSUE-031 is done — unblocked.
