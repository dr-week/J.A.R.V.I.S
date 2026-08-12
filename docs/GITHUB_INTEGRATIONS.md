# GitHub integration inventory

Canonical list of open-source GitHub repositories that Jarvis uses, plans to
use, or has explicitly deferred. This file is an inventory, not permission to
add a dependency: each runtime integration still needs an issue, tests, and a
security review.

## Status meanings

- **In use** — present in the dependency set or runtime code and covered by the current architecture.
- **Planned** — approved by the roadmap/OSS plan, but not fully wired into the product yet.
- **Optional** — useful only for a narrow future capability; add after an acceptance test and ADR when needed.
- **Deferred** — do not add without an explicit architecture decision.

## Product repositories

| Repository | Purpose in Jarvis | Status | Phase / evidence |
|---|---|---|---|
| [fastapi/fastapi](https://github.com/fastapi/fastapi) | Brain HTTP API | In use | Phase 0; `backend/app/` |
| [encode/uvicorn](https://github.com/encode/uvicorn) | Brain process server | In use | Phase 0; `scripts/run_brain.py` |
| [googleapis/python-genai](https://github.com/googleapis/python-genai) | Gemini provider | In use | Brain LLM adapter |
| [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | MCP tool protocol/client | In use | Hands registry and MCP client |
| [microsoft/playwright-python](https://github.com/microsoft/playwright-python) | Web navigation and browser automation | In use / narrow | Phase 3–4; browser tool |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Local speech-to-text | Planned | Phase 4 voice |
| [rhasspy/piper](https://github.com/rhasspy/piper) | Local text-to-speech | Planned | Phase 4 voice; Piper is the default |
| [Home Assistant/core](https://github.com/home-assistant/core) | House device fabric | In use / bridge | Phase 5; `backend/plugins/homeassistant/` |
| [dscripka/openWakeWord](https://github.com/dscripka/openWakeWord) | Optional wake-word detection | Optional | Phase 4 prototype |
| [opencv/opencv](https://github.com/opencv/opencv) | Vision preprocessing | Optional | Phase 5+ house vision |
| [ultralytics/ultralytics](https://github.com/ultralytics/ultralytics) | Object detection for room/device vision | Optional | Phase 5+; GPU-dependent |

## Recommended next integrations

These are the next three integrations because they improve reliability and
operating cost before adding more product surface area.

| Priority | Repository | Jarvis role | Status | Planned phase |
|---|---|---|---|---|
| 1 | [BerriAI/litellm](https://github.com/BerriAI/litellm) | One model gateway for Gemini, OpenAI-compatible endpoints, and Ollama; record model/token usage | Planned | Phase 3–4 |
| 2 | [open-telemetry/opentelemetry-collector](https://github.com/open-telemetry/opentelemetry-collector) | Collect traces, metrics, and logs for brain turns, tool calls, and device bridges | Planned | Phase 3–4 |
| 3 | [searxng/searxng](https://github.com/searxng/searxng) | Private self-hosted search backend for the web-research plugin | Planned | Phase 3 |

### Small-chunk integration plan

Each integration should move through the same three slices so the work stays
small and easy to verify:

1. Discover and draft the contract.
2. Wire the smallest runtime path.
3. Add the acceptance proof and docs update.

#### 1. LiteLLM — model and token control

- Slice A: define the provider contract and `.env` shape for gateway routing.
- Slice B: wire one OpenAI-compatible path while keeping Gemini as the default.
- Slice C: record token/model/latency metadata and verify one Gemini turn plus
  one local/OpenAI-compatible turn without exposing secrets to the client.

#### 2. OpenTelemetry Collector — operational visibility

- Slice A: choose the first trace/span fields for brain requests and tool calls.
- Slice B: wire local export for the brain, agent loop, and bridge round trip.
- Slice C: prove a trace can be followed end to end while telemetry-off mode
  still passes the normal smoke tests.

#### 3. SearXNG — private search

- Slice A: define the optional `web_research` backend contract and fallback
  behavior.
- Slice B: wire search timeout, result-size, domain, and robots/safety controls.
- Slice C: verify a mocked/local SearXNG response turns into a concise research
  result without leaking secrets or user memory.

### Dependency guardrails

- Integrate one repository at a time: LiteLLM → OpenTelemetry → SearXNG.
- Keep each repository in three small slices: contract, wiring, acceptance.
- Each integration needs a focused test, `.env.example` documentation, and a
  rollback path before its status changes from **Planned** to **In use**.
- Do not add a second database, desktop shell, or orchestration framework as
  part of this plan.

## Venture and future repositories

These belong to the venture/operator lane or later phases. They must not be
treated as core Jarvis runtime dependencies without an ADR.

| Repository | Purpose | Status | Boundary |
|---|---|---|---|
| [ollama/ollama](https://github.com/ollama/ollama) | Local LLM serving | Planned | Optional local provider |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | CEO/workflow orchestration | Planned | `AI-COMPANY/` only initially |
| [postgres/postgres](https://github.com/postgres/postgres) | Venture/business state | Planned | Venture lane; product remains SQLite v1 |
| [qdrant/qdrant](https://github.com/qdrant/qdrant) | Venture research vectors | Planned | Venture lane; not product memory default |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | LLM/agent tracing | Planned | Cross-lane observability |
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | External workflow automation | Optional | Webhooks/tools after an ADR |
| [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) | External coding agent | Optional | Sits beside Jarvis, not inside the brain |

## Explicitly deferred

| Repository | Reason |
|---|---|
| [tauri-apps/tauri](https://github.com/tauri-apps/tauri) | Flet + web PWA are the locked Windows/web defaults; Tauri needs an ADR. |

## Integration rules

1. Prefer the upstream repository; do not fork or vendor commodity engines.
2. Add secrets only through `.env`; never pass tokens in tool arguments.
3. Record architecture-changing swaps in [`DECISIONS.md`](DECISIONS.md).
4. Update this inventory, [`OSS.md`](OSS.md), and the relevant phase plan together.
5. Add a focused test or smoke proof before marking a repository **In use**.

Related: [`DOCS_MAP.md`](DOCS_MAP.md) · [`OSS.md`](OSS.md) · [`dev/OSS_ARSENAL.md`](dev/OSS_ARSENAL.md) · [`dev/OSS_DEV_PLAN.md`](dev/OSS_DEV_PLAN.md)
