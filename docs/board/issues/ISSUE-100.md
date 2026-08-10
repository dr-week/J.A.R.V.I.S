---
id: ISSUE-100
status: done
phase: 2
owner: antigravity
claimed_at: 2026-08-09T15:41:38Z
---

# Mind: Unblock Phase 2 Tools & Core Memory

## Context
Currently, `agent.py` hardcodes the tool registry check to ignore anything above Phase 0. This blocks critical Phase 2 features like the device bridges and third-party plugins. Furthermore, Jarvis lacks the ability to explicitly save or retrieve memories, violating FR-S1.

## Acceptance Criteria
- [ ] Remove the Phase 0 check from `_build_gemini_tools` in `agent.py`.
- [ ] Create `save_memory`, `list_memories`, and `forget_memory` tools in `backend/app/soul/tools.py`.
- [ ] Register the memory tools on startup in `main.py`.

## Notes

- [2026-08-09T15:43:19Z] Marked done


- Claimed by antigravity at 2026-08-09T15:41:38Z
