# Open-source leverage

**Rule:** Prefer mature open-source building blocks over custom reinvention. Jarvis owns Soul/Mind/Hands *integration*, not commodity engines.

**Zero-Code Principle:** Every remaining capability should be a **3-line wrapper**, **CLI subprocess**, **Docker sidecar**, or **MCP server** — never a from-scratch implementation.

## Locked defaults (by area)

| Area | Phase | Choose | Stars | Avoid reinventing |
|------|-------|--------|-------|-------------------|
| Brain API | 0+ | FastAPI + Uvicorn | 80k+ | Custom HTTP stack |
| Data | 0-2 | SQLite | built-in | Custom file DB |
| Semantic memory | 3+ | `sqlite-vec` first; ChromaDB if needed | 20k+ | Homegrown vector search |
| **Web presence (primary)** | 0+ | **Vite + React + TypeScript** - `clients/web/` | 60k+ | Treating Flutter as the default web UI |
| **Mobile/desktop presence (Field Body)** | 0+ | **Flutter + Dart** - `clients/flutter/` | 170k+ | Duplicating `clients/web` chat in Flutter |
| **Windows legacy lane** | 0+ | **Flet + Python** - `clients/windows/` (tray, voice, bridge) | 12k+ | New Electron/Tauri without ADR |
| Android bridge stub | 0+ | Kotlin Compose stub in `clients/android/` | - | Full duplicate of Flutter + web |
| LLM Gateway | 3-4 | **LiteLLM** - one endpoint for Gemini/OpenAI/Ollama | 20k+ | Per-provider SDK lock-in |
| STT | 4 | **faster-whisper** (local); cloud optional | 13k+ | Cloud-only STT lock-in |
| TTS | 4 | **Piper** (primary); **Kokoro** optional via ADR | 4k+ | Paid TTS as default |
| Wake word | 4 | **openWakeWord** (dscripka) | 4k+ | Custom ML keyword detection |
| Web search | 3+ | **SearXNG** self-hosted sidecar | 15k+ | Google/Bing API bills |
| Browser automation | 3+ | **CloakBrowser** / **nodriver** stealth | 29k+ | Brittle Playwright without stealth |
| Workflow automation | 4+ | **n8n** self-hosted sidecar via webhook tool | 55k+ | Custom multi-app Python glue |
| House | 5 | **Home Assistant** as device fabric | 75k+ | Per-brand IoT drivers |
| RAG / Knowledge Base | 3+ | **AnythingLLM** or **privateGPT** Docker sidecar | 35k+ | Custom vector store + chunking pipeline |
| Finance tracking | 4+ | **Actual Budget** self-hosted REST API | 16k+ | Custom ledger math |
| Image generation | 5+ | **ComfyUI** local REST API endpoint | 65k+ | Custom diffusers pipeline |
| Agent orchestration | 6+ | **CrewAI** or **AutoGen** framework | 30k+ | Custom multi-agent loop |
| Tool/runtime | 6 | Python plugins + **optional** Lua/Go/R via POLYGLOT_TOOLS.md | - | Monolithic new frameworks |

**Roles (human decision):** [dev/PRESENCE_STACKS.md](dev/PRESENCE_STACKS.md).

## Zero-Code Integration Patterns

### Pattern 1: 3-Line PyPI Wrapper (fastest)
```python
# Example: STT via faster-whisper
from faster_whisper import WhisperModel
model = WhisperModel("base")
segments, _ = model.transcribe(audio_path)
```

### Pattern 2: CLI Subprocess (no Python library needed)
```python
# Example: yt-dlp video summarizer
import subprocess
result = subprocess.run(["yt-dlp", "--get-description", url], capture_output=True, text=True)
```

### Pattern 3: Docker Sidecar + REST call (microservice, zero Python logic)
```python
# Example: SearXNG private search
import httpx
results = httpx.get("http://localhost:8080/search?q=query&format=json").json()
```

### Pattern 4: MCP Server (npx one-liner, auto tool discovery)
```json
{ "mcpServers": { "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"] } } }
```

## Principles

1. Brain stays the orchestration layer — OSS is *plugged in*, not forked randomly
2. Prefer **local/offline-capable** for voice and house control
3. One primary choice per concern; second option is fallback, not dual-support forever
4. Record swaps in [DECISIONS.md](DECISIONS.md)
5. **New Rule:** Every new integration MUST use one of the 4 patterns above. No custom logic.

## What Jarvis still owns

- Persona, memory policy, confirmations, sync identity
- Tool protocol and device bridges
- Multi-surface presence + house conversation continuity
- Devloop / agent-buildable process

## Currently Integrated OSS Plugins (87+ tools)

| Plugin | OSS Library | Stars | Pattern |
|--------|------------|-------|---------|
| `calendar` | icalendar | 2k | PyPI wrapper |
| `email` | imapclient + smtplib | built-in | PyPI wrapper |
| `contacts` | SQLite CRUD | built-in | Pure Python |
| `notes` | SQLite FTS5 | built-in | Pure Python |
| `news` | feedparser | 2k | PyPI wrapper |
| `clipboard` | pyperclip | 4k | PyPI wrapper |
| `screenshot_ocr` | mss + pytesseract | 8k | PyPI wrapper |
| `media_control` | pycaw | 1k | PyPI wrapper |
| `notifications` | notify-py | 1k | PyPI wrapper |
| `focus_timer` | asyncio | built-in | Pure Python |
| `pdf_gen` | fpdf2 | 3k | PyPI wrapper |
| `translator` | argostranslate | 4k | PyPI wrapper |
| `habits` | SQLite | built-in | Pure Python |
| `secrets` | keyring | 2k | PyPI wrapper |
| `telegram_bot` | python-telegram-bot | 29k | PyPI wrapper |
| `stt` | faster-whisper | 13k | PyPI wrapper |
| `video_summary` | yt-dlp | 80k | CLI subprocess |
| `location` | geopy | 5k | PyPI wrapper |
| `workflows` | custom chain engine | - | Pure Python |
| `n8n_automation` | n8n webhook | 55k | REST/Docker sidecar |
| `browser_use` | CloakBrowser + Playwright | 29k | PyPI wrapper |
| `homeassistant` | Home Assistant REST | 75k | REST sidecar |
| `mcp_installer` | MCP SDK | - | MCP server |
| `anything_llm` | AnythingLLM | 64k | REST sidecar |
| `litellm_gateway` | LiteLLM | 20k | PyPI wrapper |
| `piper_tts` | Piper | 4k | CLI subprocess |

## Dev tooling (integrate, don't fork)

| Tool | Status |
|------|--------|
| Ruff, pre-commit | ✅ |
| pytest (deps), mypy, uv | pytest ✅ **59 tests passing** |
| loguru | ✅ ISSUE-124 done |
| psutil | ✅ ISSUE-125 done |

Install manifest (what to pip/npm when): [dev/STARK_OSS_INSTALL.md](dev/STARK_OSS_INSTALL.md).

Plan: [dev/OSS_DEV_PLAN.md](dev/OSS_DEV_PLAN.md) → [dev/OSS_ARSENAL.md](dev/OSS_ARSENAL.md) (20-tool map) → [dev/LAB_STACK.md](dev/LAB_STACK.md) → [dev/STARK_TIMELINE.md](dev/STARK_TIMELINE.md).

Repository inventory: [GITHUB_INTEGRATIONS.md](GITHUB_INTEGRATIONS.md). Keep
repository names, status, and phase boundaries synchronized there before
changing this OSS policy.

**Next integration wave:** AnythingLLM RAG → SearXNG → Piper TTS → ComfyUI image gen.
Each uses the same 3-slice flow: contract → wiring → acceptance proof.
