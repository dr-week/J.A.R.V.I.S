---
id: ISSUE-140
title: The Visual Cortex (OpenCV + Tesseract)
status: done
priority: P1
phase: 7
labels: [backend, sensory]
owner: visual_cortex_agent
claimed_at: 2026-08-11T17:05:09Z
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

- [2026-08-11T17:06:39Z] Marked done


- Claimed by visual_cortex_agent at 2026-08-11T17:05:09Z


Created for Minimax queue (FRIDAY Protocol)
