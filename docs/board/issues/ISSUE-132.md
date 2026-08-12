---
id: ISSUE-132
title: Velocity IPC (Inter-Process Communication)
status: done
priority: P2
phase: 3
labels: [backend, infrastructure]
owner: cursor
claimed_at: 
blocked_by: []
acceptance:
  - Allow Velocity to stream build progress back to the Jarvis WebSocket.
  - When Velocity finishes a step, it hits a Jarvis /internal/webhook.
---

## Context

Velocity Integration: Send realtime updates to the user while Velocity runs in the background celery queue.

## Lane

- `backend/app/api/webhooks.py`
- `backend/app/main.py`
- `backend/app/sync/manager.py`
- `docs/dev/LOCAL_LLM.md`
- `backend/tests/test_velocity_webhook.py`

## Work

- [x] Create /internal/webhook endpoint in Jarvis
- [x] Connect webhook to SSE/WebSocket broadcast
- [x] Optional device_id unicast + progress/step fields
- [x] Pytest for webhook

## Notes

- [2026-08-11T17:58:46Z] Marked done


- [2026-08-11] Implemented by cursor — see LOCAL_LLM.md Velocity IPC section.

Created for Cursor queue (Velocity Integration)
