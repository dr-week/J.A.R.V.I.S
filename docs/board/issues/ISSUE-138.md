---
id: ISSUE-138
title: The Auditory Cortex (Wake word & STT)
status: backlog
priority: P1
phase: "7"
labels:
  - backend
  - sensory
owner: ""
claimed_at: ""
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

Created for Minimax queue (FRIDAY Protocol)
