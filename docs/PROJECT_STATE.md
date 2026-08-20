# Jarvis Live Project State

Living document of current system health, active lanes, known technical debt, and next immediate implementation tasks.

---

## 1. System Health & Environment Status

* **Brain Engine**: FastAPI + SQLite (`backend/app/main.py`) — `GET /health` operational.
* **Codebase Health**: **17,877 total lines** across 198 files.
  * 🟢 **Modular (<150 lines)**: 159 files (80.3% files, 56.1% lines)
  * 🟡 **Moderate (151-250 lines)**: 34 files (17.2% files, 35.3% lines)
  * 🔴 **Monolithic (>250 lines)**: 5 files (2.5% files, 8.5% lines)
* **Web Presence**: React 19 + Tailwind v4 + shadcn/ui (`clients/web/`) — Production build verified.
* **Fast Smoke Verification**: `pytest -m fast` — **10/10 passed (0.09s)**.
* **Full Test Suite**: **147 / 147 passed**.

---

## 2. Active Worker Lanes (Max 2 Parallel)

| Worker ID | Assigned Lane | Focus | Current Task |
|---|---|---|---|
| **`antigravity`** (Current) | Core Engine & Optimization | `backend/**`, `scripts/**`, `docs/**` | Monolith decomposition & token optimization |
| **`cursor`** | Presence & Clients | `clients/**` | Flutter bridge & presence loops |

---

## 3. Known Technical Debt & Risk Registry

| ID | Component | Description & Risk | Resolution Strategy |
|---|---|---|---|
| **TD-01** | `scripts/board_context.py` (389L) | Monolithic board reader/formatter | Decompose into `board_git.py`, `board_formatter.py`, `board_issues.py` |
| **TD-02** | `anything_llm` / `piper_tts` (>300L) | Plugins mix HTTP I/O, subprocess, and tool schemas | Split into dedicated `client.py`, `engine.py`, `tools.py` modules |
| **TD-03** | `workspace_tools.py` (261L) | AST parse, tree scan, chunk read, and strict edit in one file | Decompose into `workspace_tree.py`, `workspace_ast.py`, `workspace_editor.py` |
| **TD-04** | VRAM / Context Limits | 4GB VRAM ceiling during long chat runs | Enforce `MAX_CONTEXT_TURNS=6`, output truncation, and dynamic `num_ctx` |

---

## 4. Next Immediate Implementation Tasks

1. [x] **Core Monolith Split**: Split `builtin_tools.py` and `openai_loop.py`.
2. [x] **Token Budget & Error Envelopes**: Truncate oversized tool output; add actionable suggestion dicts.
3. [x] **Fast Smoke Suite**: `pytest -m fast` with 10 instant checks.
4. [ ] **Batch 1 Monolith Refactor**: Decompose `workspace_tools.py` and `board_context.py`.
5. [ ] **Batch 2 Plugin Refactor**: Decompose `anything_llm` and `piper_tts`.

