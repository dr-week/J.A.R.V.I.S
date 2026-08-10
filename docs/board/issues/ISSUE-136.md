---
id: ISSUE-136
title: Build the Corporate Orchestrator Loop (LangGraph)
status: backlog
priority: P1
phase: "8"
labels:
  - backend
  - agents
owner: ""
claimed_at: ""
blocked_by: []
acceptance:
  - Create the backend/app/company/ceo.py LangGraph orchestrator.
  - Script uses LangGraph StateGraph to model the CEO workflow (Research -> Analyze -> Decide -> Execute).
  - Generates constrained Task Packets in tasks/pending/ based on highest ROI priority.
---
## Context

AI Venture Studio: The AI CEO is the core loop that reads state, analyzes opportunities, and outputs tasks to other agents.
Must use LangGraph for explicit state control as defined in AI-COMPANY/STACK.md.

## Work

- [ ] Create ceo.py using LangGraph
- [ ] Connect to AI-COMPANY/ state files

## Notes

Created for Cursor queue (Enterprise Protocol)
