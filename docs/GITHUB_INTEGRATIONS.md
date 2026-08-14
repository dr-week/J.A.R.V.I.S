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

---

## ✅ Currently In Use (Zero-Code Integrations — 87+ tools)

| Repository | Stars | Purpose in Jarvis | Pattern | Phase |
|---|---|---|---|---|
| [fastapi/fastapi](https://github.com/fastapi/fastapi) | 80k | Brain HTTP API | PyPI | Phase 0 |
| [encode/uvicorn](https://github.com/encode/uvicorn) | 8k | Brain process server | PyPI | Phase 0 |
| [googleapis/python-genai](https://github.com/googleapis/python-genai) | 1k | Gemini LLM provider | PyPI | Brain |
| [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | 4k | MCP tool protocol/client | PyPI + MCP | Hands |
| [microsoft/playwright-python](https://github.com/microsoft/playwright-python) | 12k | Web browser automation | PyPI | Phase 3-4 |
| [nickvdyck/CloakBrowser](https://github.com/Kaliiiiiiiiii-Vinyzu/CloakBrowser) | 29k | Stealth anti-bot bypass | PyPI | Phase 3-4 |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 13k | Local speech-to-text | PyPI wrapper | Phase 4 |
| [home-assistant/core](https://github.com/home-assistant/core) | 75k | House device fabric | REST sidecar | Phase 5 |
| [icalendar/icalendar](https://github.com/collective/icalendar) | 2k | Calendar events (.ics) | PyPI wrapper | Phase 3 |
| [imbo/imapClient](https://github.com/martinrusev/imapClient) | 1k | IMAP email reader | PyPI wrapper | Phase 3 |
| [mark-d-/feedparser](https://github.com/kurtmckee/feedparser) | 2k | RSS/Atom news feeds | PyPI wrapper | Phase 3 |
| [asweigart/pyperclip](https://github.com/asweigart/pyperclip) | 4k | Clipboard read/write | PyPI wrapper | Phase 3 |
| [BoboTiG/python-mss](https://github.com/BoboTiG/python-mss) | 1k | Screenshot capture | PyPI wrapper | Phase 3 |
| [madmaze/pytesseract](https://github.com/madmaze/pytesseract) | 6k | OCR on screenshots | PyPI wrapper | Phase 3 |
| [AndreMiras/pycaw](https://github.com/AndreMiras/pycaw) | 1k | Windows audio/volume | PyPI wrapper | Phase 3 |
| [argosopentech/argos-translate](https://github.com/argosopentech/argos-translate) | 4k | Offline neural translation | PyPI wrapper | Phase 4 |
| [py-notify/notify-py](https://github.com/ms7m/notify-py) | 1k | Desktop notifications | PyPI wrapper | Phase 3 |
| [jaraco/keyring](https://github.com/jaraco/keyring) | 2k | OS secret keychain | PyPI wrapper | Phase 3 |
| [python-telegram-bot/python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) | 29k | Telegram mobile presence | PyPI wrapper | Phase 4 |
| [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | 80k | Video info/transcript | CLI subprocess | Phase 4 |
| [geopy/geopy](https://github.com/geopy/geopy) | 5k | Location geocoding | PyPI wrapper | Phase 4 |
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | 55k | Multi-app workflow automation | REST webhook | Phase 4 |
| [codingo/fpdf2](https://github.com/py-pdf/fpdf2) | 1k | PDF report generation | PyPI wrapper | Phase 3 |
| [Delgan/loguru](https://github.com/Delgan/loguru) | 20k | Structured logging | PyPI | All phases |
| [giampaolo/psutil](https://github.com/giampaolo/psutil) | 10k | System vitals / CPU/RAM | PyPI wrapper | Phase 3 |
| [Mintplex-Labs/anything-llm](https://github.com/Mintplex-Labs/anything-llm) | 64k | Full RAG knowledge base sidecar | REST sidecar | Phase 3+ |
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 20k | Unified model gateway across Gemini/OpenAI/Ollama | PyPI wrapper | Phase 3-4 |
| [rhasspy/piper](https://github.com/rhasspy/piper) | 4k | Lightweight local neural TTS fallback | CLI subprocess | Phase 4 |
| [dscripka/openWakeWord](https://github.com/dscripka/openWakeWord) | 4k | Local AI wake-word detection | PyPI wrapper | Phase 4 |

---

## 🔜 Next Integration Wave (Planned — Zero Code Required)

These are prioritized by impact vs. coding effort ratio. Each uses one of the 4 zero-code patterns.

| Priority | Repository | Stars | Jarvis Role | Pattern | Phase |
|---|---|---|---|---|---|
| ⭐ 2 | [Mintplex-Labs/anything-llm](https://github.com/Mintplex-Labs/anything-llm) | **64k** | Full RAG: document ingestion, chunking, vector search, multi-tenant chat | Docker sidecar + REST | Phase 3+ |
| ⭐ 3 | [searxng/searxng](https://github.com/searxng/searxng) | **35k** | Private self-hosted search — replaces Google/Bing API costs | Docker sidecar + REST | Phase 3 |
| ⭐ 4 | [hexgrad/kokoro](https://github.com/hexgrad/kokoro) | **8k** | Local neural TTS — replaces ElevenLabs/OpenAI voice | 3-line PyPI wrapper | Phase 4 |
| ⭐ 5 | [rhasspy/piper](https://github.com/rhasspy/piper) | 4k | Lightweight local TTS fallback | CLI subprocess | Phase 4 |
| ⭐ 6 | [dscripka/openWakeWord](https://github.com/dscripka/openWakeWord) | 2.5k | Wake-word detection ("jarvis") | 3-line PyPI wrapper | Phase 4 |
| ⭐ 7 | [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) | **125k** | Local AI image generation (Stable Diffusion/FLUX) | Docker sidecar + REST | Phase 5+ |
| ⭐ 8 | [actualbudget/actual](https://github.com/actualbudget/actual) | **28k** | Self-hosted finance tracker — replaces Mint/YNAB | Docker sidecar + REST | Phase 4+ |
| ⭐ 9 | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | **57k** | Multi-agent task orchestration (Swarm CEO layer) | 3-line PyPI wrapper | Phase 6 |
| ⭐ 10 | [ultrafunkamsterdam/nodriver](https://github.com/ultrafunkamsterdam/nodriver) | 4.6k | Stealth browser upgrade — zero detection, async-native | 3-line PyPI wrapper | Phase 3-4 |
| 11 | [go-vikunja/vikunja](https://github.com/go-vikunja/vikunja) | 5k | Self-hosted task/project board with CalDAV REST | Docker sidecar + REST | Phase 4+ |
| 12 | [radicale-org/Radicale](https://github.com/radicale-org/Radicale) | 4.9k | Self-hosted CalDAV/CardDAV server | CLI/Docker sidecar | Phase 4+ |
| 13 | [open-telemetry/opentelemetry-collector](https://github.com/open-telemetry/opentelemetry-collector) | 5k | Distributed traces for brain/tool/bridge turns | Docker sidecar | Phase 3-4 |

---

## 🌙 Venture & Future Repositories

These belong to the venture/operator lane or Phase 7+ endgame. Must not be treated as core runtime without an ADR.

| Repository | Stars | Purpose | Status | Boundary |
|---|---|---|---|---|
| [ollama/ollama](https://github.com/ollama/ollama) | 100k | Local LLM serving | Planned | Optional local provider via LiteLLM |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 15k | CEO/workflow orchestration | Planned | `AI-COMPANY/` only initially |
| [postgres/postgres](https://github.com/postgres/postgres) | 17k | Venture/business state | Planned | Venture lane; product remains SQLite v1 |
| [qdrant/qdrant](https://github.com/qdrant/qdrant) | 21k | Venture research vectors | Planned | Venture lane; not product memory default |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 7k | LLM/agent tracing | Planned | Cross-lane observability |
| [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) | 50k | External coding agent | Optional | Sits beside Jarvis, not inside the brain |
| [microsoft/autogen](https://github.com/microsoft/autogen) | 40k | Multi-agent conversation | Optional | Phase 7+ Swarm |
| [opencv/opencv](https://github.com/opencv/opencv) | 80k | Vision preprocessing | Optional | Phase 5+ house vision |
| [ultralytics/ultralytics](https://github.com/ultralytics/ultralytics) | 40k | Object detection for room/device vision | Optional | Phase 5+; GPU-dependent |
| [ros-planning/ros2](https://github.com/ros2/ros2) | 2k | Physical robot actuation | Optional | Phase 7 Endgame only |

---

## 🚫 Explicitly Deferred

| Repository | Reason |
|---|---|
| [tauri-apps/tauri](https://github.com/tauri-apps/tauri) | Flet + web PWA are the locked Windows/web defaults; Tauri needs an ADR. |
| [electron/electron](https://github.com/electron/electron) | Same reason as Tauri. |
| [huggingface/transformers](https://github.com/huggingface/transformers) | Use faster-whisper/Kokoro for audio; ComfyUI for images. Don't load raw HF models in the brain. |

---

## Integration Rules

1. Prefer the upstream repository; do not fork or vendor commodity engines.
2. Add secrets only through `.env`; never pass tokens in tool arguments.
3. Record architecture-changing swaps in [`DECISIONS.md`](DECISIONS.md).
4. Update this inventory, [`OSS.md`](OSS.md), and the relevant phase plan together.
5. Add a focused test or smoke proof before marking a repository **In use**.
6. **New Rule:** Every new integration MUST use one of the 4 zero-code patterns: PyPI wrapper | CLI subprocess | Docker sidecar | MCP server.

Related: [`DOCS_MAP.md`](DOCS_MAP.md) → [`OSS.md`](OSS.md) → [`dev/OSS_ARSENAL.md`](dev/OSS_ARSENAL.md) → [`dev/OSS_DEV_PLAN.md`](dev/OSS_DEV_PLAN.md)
