---
id: ISSUE-050
title: STT and TTS on one client
status: done
priority: P0
phase: 4
labels: [voice]
owner: minimax
claimed_at: 2026-08-08T10:32:51Z
blocked_by: [ISSUE-011]
acceptance:
  - Speak a turn; get spoken reply on Windows or Android
  - Text transcript still synced
---

## Context

Voice presence.

## Notes

- [2026-08-08T10:38:54Z] Marked done


- [2026-08-08T10:38:54Z] Windows client voice (ISSUE-050). Added clients/windows/voice.py (STT via speech_recognition + TTS via pyttsx3, graceful fallback). Wired --voice into client.py: no --once captures mic transcript, then speaks reply; --voice --once speaks the reply. Transcript still rides normal /chat SSE so sync preserved. requirements.txt += optional pyttsx3, speech_recognition. README voice section. Verified: AST parse, --help shows --voice, TTS/STT fallback paths no-crash. Live mic TTS/STT needs device w/ deps.


- Claimed by minimax at 2026-08-08T10:32:51Z


- Released by antigravity at 2026-08-08T10:01:39Z (was antigravity)


- Claimed by antigravity at 2026-08-08T09:54:09Z
