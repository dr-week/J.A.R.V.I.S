---
id: ISSUE-140
title: The Visual Cortex (OpenCV + Tesseract)
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
  - Implement a background loop that takes screenshots.
  - Process screenshots with OpenCV and Tesseract to extract readable text/UI state.
  - Expose "Read Screen" as an MCP tool for LangGraph.
---
## Context

FRIDAY Architecture: The AI needs "Eyes" to see what is on the user's screen without relying entirely on API integrations.

## Work

- [ ] Create backend/app/sensory/vision.py
- [ ] Connect OpenCV and Tesseract
- [ ] Connect to MCP

## Notes

Created for Minimax queue (FRIDAY Protocol)
