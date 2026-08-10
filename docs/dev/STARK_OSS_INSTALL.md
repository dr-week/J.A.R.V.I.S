# Stark OSS install manifest

**What Tony would `pip install` / `npm install` — and when.** Not everything on day one.

Doctrine: [LAB_STACK.md](LAB_STACK.md) · locked product choices: [OSS.md](../OSS.md) · board slices: [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md)

```bash
# Brain (repo root)
pip install -e ".[dev]"          # or: uv pip install -e ".[dev]"
cd clients/web && npm install
```

---

## Already in the reactor (do not rip out)

### Python (`pyproject.toml` runtime)

| Package | Stark reason |
|---------|----------------|
| **fastapi** + **uvicorn** | API + ASGI — the arc reactor bus |
| **pydantic** | Typed contracts — no magic dict soup |
| **aiosqlite** | Local memory — your data stays home |
| **httpx** | Test + outbound HTTP without bespoke clients |
| **python-jose** + **passlib** | Tokens — suit pairing |
| **google-genai** | Mind fuel (swap model via config, not rewrite) |
| **python-dotenv** | `.env` until **pydantic-settings** (**122**) |
| **watchdog** | Hot paths / file awareness |

### Python dev (`[project.optional-dependencies] dev`)

| Package | Stark reason |
|---------|----------------|
| **ruff** | Fast lint — workshop hygiene |
| **pre-commit** | Stop broken docs entering the lab |
| **mypy** | Catch API lies before runtime |
| **pytest** + **pytest-asyncio** | Reactor regression tests |

### Web (`clients/web`)

| Package | Stark reason |
|---------|----------------|
| **vite** + **react** + **typescript** | One HUD — chat/product UI |
| **oxlint** | Fast JS lint |
| **lucide-react** | Icons without design thrash |

### Flutter / Windows / Android

| Stack | Role |
|-------|------|
| **Flutter** + **url_launcher** | Field Body — execute, link to web |
| **Flet** + **httpx** (windows client) | Tray/voice lab |
| **Kotlin Compose** (android) | Device bridge |

---

## Install next (Phase 2 tail — “instrument the suit”)

Stark installs these **before** wake word or message queues.

| `pip install` | Issue | Why |
|---------------|-------|-----|
| **pydantic-settings** | **130** → **122** | Fail fast on bad `.env` — reactor config is typed |
| **loguru** | **131** → **124** | Structured logs — flight recorder |
| **psutil** | **125** | CPU/RAM/disk — suit vitals tool |

```bash
pip install pydantic-settings loguru psutil
# Prefer issues 130/131/125 — don’t hand-edit only
```

**Optional workshop accelerator (not in pyproject yet):**

| Tool | Install | When |
|------|---------|------|
| **uv** | `pip install uv` or installer | Faster `uv run pytest` — document in README |
| **httpie** | `pip install httpie` | Human API poke — never required in CI |

---

## Install when Phase 3 opens (L4 — life robots)

| `pip install` | Purpose | Note |
|---------------|---------|------|
| **sqlite-vec** | Embeddings in SQLite | Default semantic memory per OSS.md |
| **chromadb** | Vector fallback | Only if sqlite-vec limits hit — ADR |
| **alembic** | Migrations | **123** — before schema churn hurts |
| **apscheduler** | Cron in-process | Prefer over Celery for first robots |
| **icalendar** | Calendar parse | Plugin slice |
| **caldav** | Calendar sync | Plugin slice |
| **feedparser** | RSS / feeds | Plugin slice |

```bash
# Example — only after Phase 3 issue claims
pip install sqlite-vec apscheduler alembic
```

---

## Install when Phase 4 opens (voice — “Friday, status”)

| Library | Purpose | Note |
|---------|---------|------|
| **faster-whisper** or **whisper.cpp** bindings | Local STT | No cloud-only ears |
| **piper-tts** / Piper binaries | Local TTS | OSS.md primary |
| **openwakeword** | Wake prototype | **126** — lab script only until Phase 4 exit |
| **webrtcvad** | Voice activity | Optional — trim audio cost |
| **sounddevice** / **pyaudio** | Mic capture (Windows lab) | With wake prototype |

Stark would **not** `pip install openwakeword` into production tray until **104** confirm + **107** WS auth are done.

---

## Install when Phase 5 opens (house)

| Integration | Install |
|-------------|---------|
| **Home Assistant** | Already REST — no pip; long-lived token |
| **paho-mqtt** | Room satellites / MQTT tools later |

---

## Phase 6 — polyglot plugins (after ISSUE-128 design)

| Install | When | Issue |
|---------|------|-------|
| **lupa** (`pip install lupa`) | Embedded Lua tools | **129** |
| **Go** (`go install` / build binary) | Subprocess plugins | **132** |
| **R** (system `Rscript`) | Stats / data tools | **133** |

Detail: [POLYGLOT_TOOLS.md](POLYGLOT_TOOLS.md). **Do not** install lupa until **128** schema + sandbox rules exist.

---

| Library | Gate |
|---------|------|
| **celery** + **redis** | **127** — prove need vs APScheduler |
| **opentelemetry-api** + exporters | Multi-host brain |
| **sentry-sdk** | Optional crash telemetry |

---

## What Stark would **not** install (yet)

| Temptation | Why wait |
|------------|----------|
| **langchain** / **llama-index** | Jarvis owns Mind orchestration — don’t stack frameworks on frameworks |
| **electron** | Web PWA + Flet lanes exist |
| **docker** as default dev | `run_brain.py` + one process first |
| **kubernetes** | One PC reactor is the product early |
| **torch** full GPU stack | Until voice phase + hardware plan |
| Second vector DB **and** sqlite-vec | One primary per OSS.md |

---

## One-command cheat sheet (by role)

```bash
# New human dev
pip install -e ".[dev]"
pre-commit install
python scripts/check_dev_env.py

# MiniMax issue 115
pytest backend/tests

# MiniMax issue 116
mypy backend/app/api

# After 128/129 land in pyproject
pip install -e ".[dev]"   # picks up new deps
```

---

## Sync with the board

When a package moves from this doc into `pyproject.toml`, update [OSS.md](../OSS.md) and close the matching issue (**115–129**).

Related: [STARK_TIMELINE.md](STARK_TIMELINE.md) · [OSS_DEV_PLAN.md](OSS_DEV_PLAN.md)
