---
id: ISSUE-030
title: Tool protocol and registry
status: done
priority: P0
phase: 2
labels: [hands, tools]
owner: 
claimed_at: 
blocked_by: [ISSUE-010]
acceptance:
  - Tools register with name, JSON schema, risk level
  - Agent can list and call a hello-world tool
---

## Context

Hands foundation.

## Notes

- [2026-08-07T19:41:30Z] Marked done


- [2026-08-07T19:41:17Z] Implemented Tool Registry and Tool execution loop. Agents can now register JSON schemas and execute tool calls in stream_chat using Gemini's native tool calling.
