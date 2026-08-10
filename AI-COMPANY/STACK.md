# The Open Source Venture Stack

Venture lane only — **not** the default Jarvis product brain (SQLite + Python Mind). Full map: [docs/dev/OSS_ARSENAL.md](../docs/dev/OSS_ARSENAL.md).

This document defines the strict technology stack used for the AI Venture Studio (The Enterprise Protocol).
Do not reinvent the wheel. Use these industry-standard frameworks.

## Phase 1 (Core) & Phase 2 (Capabilities)

| Layer | Framework | Purpose |
|-------|-----------|---------|
| **Brain** | `ollama` | Local LLM execution. |
| **Orchestrator** | `langgraph` | Explicit state and workflow control for the AI CEO. Do not use raw loops. |
| **Tool Protocol** | `mcp` | Model Context Protocol. Standardized tool exposure (Velocity, GitHub). |
| **Database** | `psycopg2-binary` (PostgreSQL) | Structured business state (Revenue, Projects, Budgets). |
| **Vector DB** | `qdrant-client` | Semantic search over market research and customer feedback. |
| **Web Research** | `firecrawl-py` | Deep web scraping for the Market Scout to extract pricing/features. |

## Phase 3 (Production - Planned)

- **Observability:** `langfuse` (Track agents/tokens/errors)
- **Evaluation:** `ragas` / `deepeval` (Test AI quality)
- **Persistent Memory:** `letta` / `mem0`
