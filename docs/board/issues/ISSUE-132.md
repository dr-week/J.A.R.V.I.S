---
id: ISSUE-132
title: Velocity IPC (Inter-Process Communication)
status: backlog
priority: P2
phase: "3"
labels:
  - backend
  - infrastructure
owner: ""
claimed_at: ""
blocked_by: ["ISSUE-131"]
acceptance:
  - Allow Velocity to stream build progress back to the Jarvis WebSocket.
  - When Velocity finishes a step, it hits a Jarvis /internal/webhook.
---
## Context

Velocity Integration: Send realtime updates to the user while Velocity runs in the background celery queue.

## Work

- [ ] Create /internal/webhook endpoint in Jarvis
- [ ] Connect webhook to SSE/WebSocket broadcast

## Notes

Created for Cursor queue (Velocity Integration)
