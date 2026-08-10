---
id: ISSUE-128
title: Design Polyglot Tool Executor Interface
status: backlog
priority: P2
phase: "6"
labels:
  - architecture
  - backend
owner: ""
claimed_at: ""
blocked_by: []
acceptance:
  - POLYGLOT_TOOLS.md omni-glot tiers + TOOL_SCHEMA runtime fields (python, lua, subprocess)
  - ADR in DECISIONS.md: subprocess-first; gRPC/MATLAB/rpy2 deferred
  - ExternalExecutor interface in backend (design + stub dispatch; full Lua in 129)
---

## Lane

- `docs/dev/POLYGLOT_TOOLS.md`
- `docs/TOOL_SCHEMA.md`
- `docs/DECISIONS.md`
- `backend/app/hands/` (interface only)

## Work

- [ ] Schema + ADR
- [ ] ExternalExecutor stub (python path unchanged)
