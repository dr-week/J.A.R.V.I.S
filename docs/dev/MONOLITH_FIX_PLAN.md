# Monolith Code Fix & Architecture Modernization Plan

This document establishes the systematic roadmap, architectural nomenclature standards, and refactoring guidelines to eliminate monolithic files across the Jarvis codebase and enforce small-context AI readability.

---

## 1. Core Principles & Coding Standards

To ensure every module can be parsed, understood, and safely modified by compact local models (e.g. 3B GGUF on 4GB VRAM):

1. **Max File Size Gate**: No file shall exceed **200 lines**. Target average is **80–120 lines**.
2. **Single Responsibility Principle (SRP)**: Each submodule must handle exactly one domain concern (e.g., pure network I/O, schema registration, or data transformation).
3. **Flat Control Flow & Early Returns**: Avoid nesting deeper than 2 levels. Guard clauses must exit early.
4. **Nomenclature Uniqueness & Conventions**:
   - `client.py`: Handles external HTTP/WebSocket network calls and protocol normalization.
   - `tools.py` / `schemas.py`: Houses `@tool` decorated functions and JSON schema definitions.
   - `engine.py`: Encapsulates local execution logic (subprocess, OS handles, or model inference).
   - `models.py`: Defines typed dataclasses or Pydantic data schemas.
   - `__init__.py`: Serves exclusively as a clean facade, re-exporting public symbols and running lazy registration.

---

## 2. Monolith Audit & Refactoring Roadmap

### Current Status Matrix

| Module / Path | Original Lines | Target Modules | Status |
|---|---|---|---|
| [`backend/app/hands/builtin_tools.py`](../../backend/app/hands/builtin_tools.py) | 171L | `core_tools.py`, `client_tools.py`, `builtin_tools.py` (facade) | ✅ **Completed** (19L) |
| [`backend/app/mind/openai_loop.py`](../../backend/app/mind/openai_loop.py) | 193L | `llm_client.py`, `message_builder.py`, `openai_loop.py` | ✅ **Completed** (126L) |
| [`backend/app/hands/tools/workspace_tools.py`](../../backend/app/hands/tools/workspace_tools.py) | 289L | `workspace_tree.py`, `workspace_ast.py`, `workspace_editor.py`, `workspace_tools.py` | ✅ **Completed** (28L) |
| [`backend/plugins/anything_llm/`](../../backend/plugins/anything_llm/) | 321L | `client.py`, `tools.py`, `__init__.py` | ✅ **Completed** (35L) |
| [`backend/plugins/piper_tts/`](../../backend/plugins/piper_tts/) | 300L | `engine.py`, `models.py`, `tools.py`, `__init__.py` | ⏳ **In Progress** |
| [`backend/plugins/homeassistant/`](../../backend/plugins/homeassistant/) | 256L | `client.py`, `entities.py`, `tools.py`, `__init__.py` | ⏳ **Scheduled** |
| [`scripts/board_context.py`](../../scripts/board_context.py) | 389L | `core/board_git.py`, `core/board_formatter.py`, `core/board_issues.py` | ⏳ **Scheduled** |

---

## 3. Standard Refactoring Pattern

When decomposing a monolithic plugin:

```
backend/plugins/example_plugin/
├── __init__.py      # Thin facade re-exporting symbols and triggering register()
├── client.py        # Async HTTP client and response normalization
├── engine.py        # (Optional) Subprocess / binary execution wrapper
├── models.py        # (Optional) Request / response dataclasses
└── tools.py         # Tool registrations and handler functions
```

### Nomenclature & Tool Naming Rules
- **Tool Names**: Must use `snake_case` with a domain prefix (e.g., `anythingllm_query`, `piper_tts_speak`, `workspace_map_tree`).
- **Error Envelopes**: All tool failures must return structured JSON envelopes with `status: "error"`, an uppercase `error_code` (e.g. `SEARCH_NOT_FOUND`), and an actionable `suggestion` string.
- **Token Budgeting**: Every tool output must respect the 1,400-char / 40-line limit before returning to the mind loop.
