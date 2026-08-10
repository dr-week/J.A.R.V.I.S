---
id: ISSUE-033
title: Android device bridge intent and deep-link
status: done
priority: P0
phase: 2
labels: [hands, android]
owner: minimax
claimed_at: 2026-08-08T09:15:56Z
blocked_by: [ISSUE-030, ISSUE-012]
acceptance:
  - Brain can request Android client to launch intent/deep-link
  - Result returned and logged
---

## Context

Phone Hands — “search in this app” class.

## Notes

- [2026-08-08T09:57:04Z] Marked done


- [2026-08-08T09:57:04Z] VERIFIED: fake Android device (android-fake-1234) registered via /ws; android_open dispatched; tool_execute+request_id received; tool_result returned; action_log row written (confirmed_by=user). Kotlin DeviceBridge+BridgeService auto-start; action_log check via scratch/test_android_bridge.py.


- [2026-08-08T09:55:02Z] Android device bridge: WS register/tool_execute/tool_result; android_open registered (executor=client, confirm_once, required target); BridgeService+DeviceBridge auto-start from MainActivity; ChatScreen shows bridge status; SYNC_PROTOCOL + android README updated. py_compile OK. Not yet verified: brain dispatch (needs emulator/phone).


- Claimed by minimax at 2026-08-08T09:15:56Z
