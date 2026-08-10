---
id: ISSUE-022
title: Cross-device profile and memory sync
status: done
priority: P0
phase: 1
labels: [soul, sync]
owner: minimax
claimed_at: 2026-08-08T10:43:16Z
blocked_by: [ISSUE-021, ISSUE-013]
acceptance:
  - Memory written from one client visible on another after sync
  - Conflict policy documented (LWW v1)
---

## Context

Everywhere = same self.

## Notes

- [2026-08-08T10:49:17Z] Marked done


- [2026-08-08T10:48:58Z] Implemented. LWW v1 enforced in upsert_memory (stale write returns applied:false; tested). API PUT /soul/memories/{key} now accepts updated_at and returns applied. Fixed /sync/status active_connections bug -> active_device_ids. Windows client: new sync_cache.py + push_memory handling in bridge loop (mirror at ~/.jarvis/windows_sync_cache.json). ADR-0017 + SYNC_PROTOCOL + README updated. py_compile + functional LWW/sync tests pass.


- Claimed by minimax at 2026-08-08T10:43:16Z
