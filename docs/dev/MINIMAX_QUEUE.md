# MiniMax / mini-AI work queue

**Purpose:** One-file (or one-script) slices so **minimax** / **minimax2** can ship without reading the whole repo.

**Session start:** [MINIMAX.md](MINIMAX.md) · **env:** [DEV_ENV.md](DEV_ENV.md) · **split template:** [SMALL_AI_PARTS.md](SMALL_AI_PARTS.md)

```bash
python scripts/devloop.py sync --owner minimax2
python scripts/devloop.py who
python scripts/devloop.py next --owner minimax2 --tier mini
python scripts/devloop.py claim ISSUE-XXX --owner minimax2
python scripts/devloop.py verify ISSUE-XXX    # lane paths exist
python scripts/devloop.py brief --owner minimax2
```

---

## Wave U — scripts & dev velocity (no Flutter) ✅ shipped

| Issue | Status |
|-------|--------|
| **109** smoke_web | done |
| **110** ruff | done |
| **108** pre-commit | done |
| **111** devloop verify | done |

Next mini-friendly backlog: **Wave X** (Dev Environment) or Flet wave in [MINIMAX_UI.md](MINIMAX_UI.md).

**Pick issues:** use `devloop next --owner minimax2 --tier mini` (uses `MINI_ISSUE_QUEUE`).

---

## Wave V — Flutter Field (parent **101**) ✅ UI shipped

| Issue | Status |
|-------|--------|
| **112** FieldScreen | done (`field_screen.dart`) |
| **113** JarvisApp wire | done |
| **114** url_launcher | done |
| **103** strip legacy chat | todo (after **101** closes) |

**101** remains NOW until Windows `tool_execute` smoke + `devloop done ISSUE-101`.

---

## Wave U (archived table)

| Order | Issue | Files (stay in lane) | Done when |
|-------|-------|----------------------|-----------|
| 1 | **109** | `scripts/smoke_web.py` | done |
| 2 | **110** | `ruff.toml`, `backend/README.md` | done |
| 3 | **108** | `.pre-commit-config.yaml`, `DEV_ENV.md` | done |
| 4 | **111** | `scripts/helpers/issue_lane_verify.py` + `devloop verify` | done |

---

## Wave V (archived detail)

| Order | Issue | Files | Do not touch |
|-------|-------|-------|--------------|
| 1 | **112** | `clients/flutter/lib/ui/field/field_screen.dart` | `chat_screen.dart`, backend |
| 2 | **113** | `clients/flutter/lib/app/jarvis_app.dart` only | Android, `clients/web` |
| 3 | **114** | `pubspec.yaml` (`url_launcher`), button in `field_screen.dart` | WS protocol |
| 4 | **103** | Remove chat default / legacy thread UI | After **101** |

**Acceptance mapping (101):**

- Field home → **112** + **113**
- `tool_execute` → already in `FieldController` — verify on Windows in **101** note
- Web link-out → **114**
- No `android_open` in Flutter → keep in executor tests / code review

When **112 + 113 + 114** are `done`, close **101** with `--force` only if parent checkboxes were satisfied in children.

---

## Wave W — web / backend (standard tier)

| Issue | Lane | Notes |
|-------|------|-------|
| **104** | `backend/app/sync/**` | WS `confirm_request` — **done** (backend); Field = **142** |
| **106** | `clients/web` | PWA manifest |
| **107** | `backend` WS auth | Security |

Give **104** to **cursor** / standard agent; mini stays on Flet or Wave X.

---

## Wave X — Dev Environment & Script Modularity (MiniMax Ready)

| Issue | Lane | Notes | Assignee |
|-------|------|-------|----------|
| **119** | `pyproject.toml` | pytest deps | done |
| **115** | `backend/tests/**` | pytest tests | `minimax2` **← next** |
| **116** | `backend/app/api/**` | Mypy API only | `minimax2` |
| **120** | `.github/workflows/` | CI doc + env | `minimax2` |
| **117** | `scripts/core/` | devloop core extract | `minimax` |
| **118** | `scripts/commands/` | devloop cmds (after 117) | `minimax` |

---

## Wave Y — Config & observability (phased)

| Issue | Lane | Notes | Assignee |
|-------|------|-------|----------|
| ~~**119**~~ | `pyproject.toml` | pytest deps | done |
| **122** | `backend/app/config.py` | Settings (after **119**) | `minimax2` |
| **124** | `backend/app/logger.py` | loguru wire | `minimax2` |
| **123** | `alembic/` | migrations | `minimax` (Phase 3) |

**Not Wave Y:** **130–132** = Velocity ([Wave Alpha](#wave-alpha--velocity-app-builder-integration-phase-3) below). **128–129** = polyglot design/Lua (Phase 6).


## Wave Z — Suit sensors (gated)

| Issue | Lane | Notes | Assignee |
|-------|------|-------|----------|
| **125** | plugin + pyproject | psutil vitals | `minimax2` |
| **126** | `clients/windows/wake.py` | wake prototype | Phase **4** only |
| **127** | `DECISIONS.md` | Celery ADR — no code until approved | cursor / human |

Phased actions: [LAB_STACK.md](LAB_STACK.md).

## Wave Y (legacy devloop modularization)

| **117** | `scripts/core/` | devloop core | `minimax` |
| **118** | `scripts/commands/` | devloop cmds | `minimax` |

---

## Wave Omega — Polyglot (Phase 6)

| Issue | Lane | Notes | Assignee |
|-------|------|-------|----------|
| **128** | `docs/`, `hands/` | Polyglot executor design | `cursor` |
| **129** | `lupa`, plugin demo | Embedded Lua | `minimax` |
| **133** | `backend/plugins/r_demo/` | R subprocess template | `minimax2` |

**Note:** **132** is Velocity IPC (Phase 3), not polyglot — see Wave Alpha below.

---

## Wave Alpha — Velocity App Builder Integration (Phase 3)

| Issue | Lane | Notes | Assignee |
|-------|------|-------|----------|
| **130** | `plugins/`, `scripts/` | Establish Velocity Plugin Submodule | `minimax` (main) |
| **131** | `backend/app/hands/` | Create `velocity_build` Tool | `cursor` (architecture) |
| **132** | `backend/app/api/` | Velocity IPC / Webhook Streaming | `cursor` (architecture) |

---

## Wave E — The Enterprise Protocol (Phase 8)

| Issue | Lane | Notes | Assignee |
|-------|------|-------|----------|
| **136** | `scripts/` | Build the Corporate Orchestrator Loop (`ceo_loop.py`) | `cursor` |
| **137** | `scripts/` | The Market Scout Engine | `minimax` |

---

## Wave F — The FRIDAY Stack (Phase 7)

| Issue | Lane | Notes | Assignee |
|-------|------|-------|----------|
| **138** | `backend/app/sensory/` | The Auditory Cortex (Wake word & STT) | `minimax` |
| **139** | `backend/app/sensory/` | The Motor Cortex (PyAutoGUI) | `cursor` |
| **140** | `backend/app/sensory/` | The Visual Cortex (OpenCV + Tesseract) | `minimax` |

---

## Wave G — Horizon H (Phase 9+)

| Issue | Lane | Notes | Assignee |
|-------|------|-------|----------|
| **141** | `scripts/` | Research CAD Generation APIs | `minimax` |

---

## OSS integrations (use, don’t rebuild)

| Tool | Jarvis use | Issue / doc |
|------|------------|-------------|
| **Ruff** | Python lint | **110** |
| **pre-commit** | Doc + env gate | **108** |
| **uv** | Faster installs | optional note in `backend/README.md` |
| **Vite** | Chat UI | in use — `clients/web` |
| **Oxlint** | Web lint | `npm run lint` in web |

Full list: [DEV_ENV.md](DEV_ENV.md) · locked deps: [OSS.md](../OSS.md).

---

## After each slice

```bash
python scripts/verify_doc_links.py
python scripts/devloop.py update ISSUE-XXX --note "verified: …"
python scripts/devloop.py done ISSUE-XXX
python scripts/devloop.py sync --owner minimax2
```
