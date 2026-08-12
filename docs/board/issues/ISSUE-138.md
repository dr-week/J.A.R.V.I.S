---
id: ISSUE-138
title: The Auditory Cortex (Wake word & STT)
status: done
priority: P1
phase: 7
labels: [backend, sensory]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - Integrate openWakeWord to detect "Jarvis" or "Friday" locally.
  - Integrate faster-whisper to transcribe voice commands into text.
  - Forward the transcribed text to the LangGraph CEO loop.
---

## Context

FRIDAY Architecture: The AI needs to listen to the room without streaming constant audio to the cloud.

## Work

- [ ] Create backend/app/sensory/hearing.py
- [ ] Connect openWakeWord stream
- [ ] Connect faster-whisper transcription

## Notes

- [2026-08-11T11:14:21Z] Marked done


- Released by unknown at 2026-08-11T11:12:49Z (was auditory_cortex_agent)


- Claimed by auditory_cortex_agent at 2026-08-11T11:12:19Z


Created for Minimax queue (FRIDAY Protocol)
