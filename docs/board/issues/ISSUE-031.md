---
id: ISSUE-031
title: Confirmation gate and action_log
status: done
priority: P0
phase: 2
labels: [hands, security]
owner: cursor
claimed_at: 2026-08-08T06:58:34Z
blocked_by: [ISSUE-030]
acceptance:
  - High-risk tools require confirm before execute
  - Executions append to action_log with redaction rules
---

## Context

Trust + audit.

## Notes

- [2026-08-08T06:59:35Z] Marked done


- [2026-08-08T06:59:35Z] Added hands/gate.py: confirm_always/confirm_once, pending session confirm, allowlist. run_tool logs redacted params to action_log. dangerous_demo test tool. GET /hands/actions. Chat confirm_pending_tool + 'confirm' phrase.


- Claimed by cursor at 2026-08-08T06:58:34Z
