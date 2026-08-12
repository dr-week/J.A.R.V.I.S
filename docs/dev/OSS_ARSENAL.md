# OSS arsenal — 20-tool evaluation

The canonical upstream repository list is [GITHUB_INTEGRATIONS.md](../GITHUB_INTEGRATIONS.md).
This file evaluates tools; it does not replace that inventory.

**Two lanes:**

| Lane | Path | Database | Orchestrator |
|------|------|----------|--------------|
| **Jarvis product** | `backend/`, clients | **SQLite** (v1) | Python Mind loop (FR-M2) |
| **Venture studio** | `AI-COMPANY/`, [BUSINESS_OPERATOR.md](../BUSINESS_OPERATOR.md) | **PostgreSQL + Qdrant** (when venture lane opens) | **LangGraph** CEO subgraph |

Do not merge lanes without ADR in [DECISIONS.md](../DECISIONS.md). Product phase gate: [ROADMAP.md](../ROADMAP.md).

---

## Verdict table (your list)

| # | Tool | Verdict | Phase | Lane | Notes |
|---|------|---------|-------|------|-------|
| 1 | **Ollama** | ✅ Integrate | 4–6 | Both | Local LLM option; [LLM.md](../LLM.md), ADR-0012 follow-up. Gemini remains default until configured. |
| 2 | **LangGraph** | ✅ Scoped | 8 / venture | **Venture** | [ISSUE-136](../board/issues/ISSUE-136.md), `AI-COMPANY/STACK.md`. **Not** default Jarvis chat loop — use for CEO workflow only. |
| 3 | **MCP** | ✅ Integrate | 3–6 | Both | Expose Jarvis tools to external agents; consume MCP servers (GitHub, etc.). ADR before core dependency. |
| 4 | **faster-whisper** | ✅ Integrate | 4 | Product | Preferred local STT over cloud-only; Windows + brain paths. |
| 5 | **Piper / Kokoro** | ✅ Piper first | 4 | Product | [OSS.md](../OSS.md) locks **Piper**; **Kokoro** = optional ADR if Piper insufficient. |
| 6 | **openWakeWord** | ✅ Prototype | 4 | Product | [ISSUE-126](../board/issues/ISSUE-126.md); lab script before tray integration. |
| 7 | **pywinauto** | ⚠️ Limited | 5+ | Product | Windows UI automation; `confirm_always`, brittle. Prefer **Playwright** for web. See ISSUE-139 (PyAutoGUI) — pick **one** desktop automation story. |
| 8 | **Playwright** | ✅ Integrate | 3–4 | Both | Web flows, testing, “boring money” SaaS; safer than desktop GUI for many tasks. |
| 9 | **OpenCV** | ⚠️ Optional | 5+ | Product | Pre/post for vision pipelines; not user-facing alone. |
| 10 | **YOLO** | ⚠️ Optional | 5+ | House | Room/device vision later; heavy; GPU. Pair with HA, not replace. |
| 11 | **PostgreSQL** | ✅ Venture / later | 3+ venture, 6 product? | Venture first | `AI-COMPANY` business state. Product stays SQLite until multi-user ADR ([DECISIONS.md](../DECISIONS.md)). |
| 12 | **Qdrant** | ✅ Venture / defer product | 3+ venture | Venture | Scout/research vectors in studio. Product memory: **sqlite-vec first** per OSS.md. |
| 13 | **OpenHands** | 🔶 Dev only | — | Meta | Separate coding agent for experiments; **do not** embed in brain. Use with `devloop` policy. |
| 14 | **n8n** | ⚠️ Optional | 3–4 | Venture | External workflow engine; integrate via webhooks/tools vs rebuilding cron in brain. ADR vs APScheduler. |
| 15 | **Home Assistant** | ✅ In use | 5 | Product | Plugin exists; locked house fabric. |
| 16 | **Langfuse** | ✅ Integrate | 3–4 | Both | LLM/agent tracing when LangGraph + multi-step ventures go live. |
| 17 | **Tauri** | ❌ Defer | 4+ ADR | Product | [OSS.md](../OSS.md): **Flet** Windows lane; no second desktop shell without ADR. Web PWA (**106**) before Tauri. |
| 18 | **LiteLLM** | ✅ Next | 3–4 | Both | Model gateway, provider fallback, and token accounting; integrate before adding more model providers. |
| 19 | **OpenTelemetry Collector** | ✅ Next | 3–4 | Both | Vendor-neutral traces, metrics, and logs for brain/tool/device reliability. |
| 20 | **SearXNG** | ✅ Next | 3 | Product | Private search backend for web research; keep current search provider as fallback. |

Legend: ✅ yes on roadmap · ⚠️ narrow use · 🔶 dev/meta only · ❌ conflicts with locked default until ADR

---

## Layered architecture (how they fit together)

```text
                    ┌─────────────────────────────────────┐
                    │  Jarvis Brain (FastAPI + SQLite)     │
                    │  Mind loop · Soul · Hands · gate     │
                    └──────────────┬──────────────────────┘
                                   │ MCP tools / HTTP
          ┌────────────────────────┼────────────────────────┐
          ↓                        ↓                        ↓
   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
   │ Ollama      │         │ LangGraph   │         │ Home        │
   │ (local LLM) │         │ CEO venture │         │ Assistant   │
   └─────────────┘         │ + Postgres  │         └─────────────┘
                           │ + Qdrant    │
                           │ + Langfuse  │
                           └─────────────┘
          ↓                        ↓
   faster-whisper            Playwright / n8n
   Piper / openWakeWord       (experiments & ops)
          ↓
   pywinauto (last resort) · OpenCV/YOLO (vision, later)
```

**OpenHands** sits **beside** the repo (like Cursor), not inside `backend/app/main.py`.

---

## Conflicts to resolve (pick one)

| Concern | Option A (Jarvis default) | Option B (Venture / ADR) |
|---------|---------------------------|---------------------------|
| Vector memory | sqlite-vec | Qdrant in `AI-COMPANY` only |
| SQL | SQLite | PostgreSQL for venture metrics |
| Desktop shell | Flet + web PWA | Tauri (needs ADR) |
| Windows GUI automation | Playwright for web | pywinauto for legacy Win32 |
| Orchestration | Python agent loop | LangGraph for `company/ceo.py` only |
| Workflows | APScheduler in brain | n8n external |

---

## Suggested install order (Stark)

1. **LiteLLM** — model routing and token accounting
2. **OpenTelemetry Collector** — brain/tool/device traces and metrics
3. **SearXNG** — private web-search backend
4. **Playwright** — tests + web automation tools
5. **MCP** — tool surface for scout/builder agents
6. **faster-whisper + Piper** — Phase 4 voice
7. **Ollama** — optional local mind
8. **LangGraph + Postgres + Qdrant** — only when `AI-COMPANY` venture lane is active (**136+**)
9. **openWakeWord** — after voice path stable
10. **n8n** — if cron/webhook volume warrants ADR
11. **OpenCV/YOLO** — house/vision epic only
12. **pywinauto** — only with explicit acceptance + confirm gate
13. **Tauri** — only after PWA + ADR rejects Flet path

---

## Board / docs cross-links

| Tool cluster | Issues / docs |
|--------------|----------------|
| LangGraph CEO | **136**, `AI-COMPANY/STACK.md` |
| Voice | **126**, **138** (if exists), OSS STT/TTS |
| MCP + desktop | **139**, **140** |
| HA | plugin `homeassistant`, ADR-0019 |
| Venture loop | [BUSINESS_OPERATOR.md](../BUSINESS_OPERATOR.md) |

---

## Related

[OSS.md](../OSS.md) · [LAB_STACK.md](LAB_STACK.md) · [STARK_OSS_INSTALL.md](STARK_OSS_INSTALL.md) · [AI-COMPANY/STACK.md](../../AI-COMPANY/STACK.md)
