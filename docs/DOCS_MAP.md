# Documentation map — keep markdown in sync

Single index for **which doc is canonical**, **which files mirror each other**, and **what to update together**.

---

## Clusters

### Vision & future (product north star)

| Canonical | Purpose | Sync when you change… |
|-----------|---------|------------------------|
| [VISION.md](VISION.md) | One sentence, principles, feel | FUTURE level ladder summary, README tagline |
| [DEMO.md](DEMO.md) | Live demo script, checklist | README demo section, demo_up scripts |
| [FUTURE.md](FUTURE.md) | Horizons, robots, level ladder | VISION progression line, PARTNERSHIP level ladder link |
| [PARTNERSHIP.md](PARTNERSHIP.md) | Human + agent co-labor, earn together | FUTURE, BUSINESS_OPERATOR, AGENTS.md mission |
| [BUSINESS_OPERATOR.md](BUSINESS_OPERATOR.md) | Profit loop, 5 roles, objective function | PARTNERSHIP Layer 3, SCOPE later |
| [ROADMAP.md](ROADMAP.md) | Phase exit criteria | FUTURE horizons, STRATEGY cheat sheet |
| [MASTER_PLAN.md](MASTER_PLAN.md) | Canonical master plan & OSS ecosystem | ROADMAP, GITHUB_INTEGRATIONS, PROJECT_STATE |
| [PROJECT_STATE.md](PROJECT_STATE.md) | Living project health, technical debt & tasks | MASTER_PLAN, board/NOW |
| [STRATEGY.md](STRATEGY.md) | How we win, agent routing, board truth | STRATEGY ↔ SYNC_PLAN ↔ LIVE_PLAN; ROADMAP phases |

### Agent & build OS

| Canonical | Purpose | Sync when you change… |
|-----------|---------|------------------------|
| [AGENTS.md](../AGENTS.md) | Contract for all coding agents | MINIMAX rules pointer, skills list, PROCESS |
| [dev/MINIMAX.md](dev/MINIMAX.md) | Blackbox MiniMax rules | `.blackbox/RULES.md`, `.blackbox/skills/jarvis-dev/SKILL.md` |
| [dev/MINISTRAL.md](dev/MINISTRAL.md) | Ministral mini-coder boot card | MINISTRAL_QUEUE, PARALLEL |
| [dev/LOCAL_LLM.md](dev/LOCAL_LLM.md) | LM Studio / Ollama + Velocity env | LLM.md, ISSUE-131 |
| [dev/MINISTRAL_QUEUE.md](dev/MINISTRAL_QUEUE.md) | Safe issues for `ministral` | MINISTRAL.md, board issues |
| [dev/MINIMAX_UI.md](dev/MINIMAX_UI.md) | Flet UI mini-issue queue | MINIMAX.md, SMALL_AI_PARTS.md, agent_registry queue |
| [dev/MAJOR_WORK_PLAN.md](dev/MAJOR_WORK_PLAN.md) | Post-swarm major tracks M1–M5 + M-Android | ROADMAP, LIVE_PLAN, STRATEGY_FORWARD |
| [dev/STRATEGY_FORWARD.md](dev/STRATEGY_FORWARD.md) | Horizons, script waves, mini routing | STRATEGY, FUTURE, MINIMAX_QUEUE, LIVE_PLAN |
| [dev/STARK_TIMELINE.md](dev/STARK_TIMELINE.md) | Forward strategy + checkpoints | FUTURE, LAB_STACK, STRATEGY_FORWARD |
| [dev/STARK_OSS_INSTALL.md](dev/STARK_OSS_INSTALL.md) | pip/npm manifest by phase | OSS.md, LAB_STACK |
| [dev/LAB_STACK.md](dev/LAB_STACK.md) | Stark doctrine + OSS phases | STARK_OSS_INSTALL, MINIMAX_QUEUE |
| [dev/OSS_ARSENAL.md](dev/OSS_ARSENAL.md) | 20-tool verdict table (product vs venture) | OSS.md, AI-COMPANY/STACK |
| [dev/OSS_DEV_PLAN.md](dev/OSS_DEV_PLAN.md) | OSS ↔ scripts ↔ issues table | LAB_STACK, DEV_ENV |
| [dev/MINIMAX_QUEUE.md](dev/MINIMAX_QUEUE.md) | Mini waves U–Z, claim order | OSS_DEV_PLAN, agent_registry |
| [dev/MODULARITY_PLAN.md](dev/MODULARITY_PLAN.md) | Phased modularization; 117–118 tree | AI_CODE_STRUCTURE, ISSUE-117/118 |
| [dev/PR_SPLIT.md](dev/PR_SPLIT.md) | Uncommitted work → independent PR slices | pr-slices/*, MODULARITY_PLAN |
| [dev/pr-slices/](dev/pr-slices/) | Per-PR scope pages (01–04) | PR_SPLIT.md |
| [dev/AI_CODE_STRUCTURE.md](dev/AI_CODE_STRUCTURE.md) | Repo layout for agents; layer rules | backend/app/README, MODULARITY_PLAN |
| [dev/AI_CODER_AUTOMATION.md](dev/AI_CODER_AUTOMATION.md) | 40-gap map + test gate + coder≠reviewer | DEFINITION_OF_DONE, jarvis-dev skill |
| [dev/FEEDBACK_LOOP.md](dev/FEEDBACK_LOOP.md) | `loop` / `inbox` / `say` | AGENTS cross-agent bus, MINIMAX handoff |
| [dev/PROCESS.md](dev/PROCESS.md) | Work loop | AGENTS work loop |
| [dev/DEFINITION_OF_DONE.md](dev/DEFINITION_OF_DONE.md) | Done checklist | MINIMAX verify section |

### Skills (portable ↔ Blackbox)

| Portable (source of truth for generic steps) | Blackbox mirror |
|-----------------------------------------------|-----------------|
| [skills/jarvis-dev/SKILL.md](../skills/jarvis-dev/SKILL.md) | [.blackbox/skills/jarvis-dev/SKILL.md](../.blackbox/skills/jarvis-dev/SKILL.md) |
| [skills/jarvis-product/SKILL.md](../skills/jarvis-product/SKILL.md) | [.blackbox/skills/jarvis-product/SKILL.md](../.blackbox/skills/jarvis-product/SKILL.md) |

**Rule:** `jarvis-dev` portable = all agents. Blackbox `jarvis-dev` = portable + **MINIMAX.md** extras.  
**Rule:** `jarvis-product` — keep **Do / Don't / North star** identical; Blackbox file may add doc links only.

| Blackbox entry | Points to |
|----------------|-----------|
| [.blackbox/RULES.md](../.blackbox/RULES.md) | Short index → MINIMAX.md + skills |
| [.blackbox/EXECUTE.md](../.blackbox/EXECUTE.md) | No plan re-approval |

### Agents roster

| Path | Role |
|------|------|
| [board/agents.json](board/agents.json) | Registered coder ids + tier |
| Path | Role |
|------|------|
| [dev/INTERNAL_HELPERS.md](dev/INTERNAL_HELPERS.md) | Wave 1: Repo Navigator + Board Copilot (script helpers) |
| [dev/SMALL_AI_PARTS.md](dev/SMALL_AI_PARTS.md) | **Work divided for mini AI** — parts A–H, parallel combos |
| [dev/AGENT_ONBOARDING.md](dev/AGENT_ONBOARDING.md) | `devloop onboard` manager workflow |

### Product spec & runtime

| Doc | Sync with |
|-----|-----------|
| [DESIGN.md](DESIGN.md) | WEB_UI, FLUTTER_UI, MINIMAX_UI; UI issues; `.cursor/rules/jarvis-design.mdc` — **not** OSS unless stack changes |
| [dev/DEV_ENV.md](dev/DEV_ENV.md) | Scripts, OSS dev tools, `check_dev_env`, daily workflow |
| [dev/AI_CODE_STRUCTURE.md](dev/AI_CODE_STRUCTURE.md) | Repo layers; agent edit map | AI_CODER_AUTOMATION |
| [dev/SYNC_PLAN.md](dev/SYNC_PLAN.md) | Doc + board + presence sync; backlog 101–107 |
| [dev/PLAN_AUDIT.md](dev/PLAN_AUDIT.md) | Requirements ↔ plan cross-check |
| [dev/PRESENCE_STACKS.md](dev/PRESENCE_STACKS.md) | Web vs Flutter Field vs Kotlin Android vs Flet; update when priority changes |
| [OSS.md](OSS.md) | Locked OSS defaults per surface; update when choosing/swapping UI framework |
| [GITHUB_INTEGRATIONS.md](GITHUB_INTEGRATIONS.md) | Canonical GitHub repository inventory and integration status | OSS.md, OSS_ARSENAL, OSS_DEV_PLAN |
| [dev/WEB_UI.md](dev/WEB_UI.md) | `clients/web/**`, DESIGN tokens |
| [dev/ANIMATIONS.md](dev/ANIMATIONS.md) | Animation presets, fluid physics, micro-interactions | DESIGN.md, WEB_UI, FLUTTER_UI |
| [dev/FLUTTER_FIELD.md](dev/FLUTTER_FIELD.md) | `clients/flutter/**` — Field Body (bridge/tools/confirm), **not** chat |
| [dev/FLUTTER_UI.md](dev/FLUTTER_UI.md) | Breakpoints only if thin UI remains |
| [dev/MINIMAX_UI.md](dev/MINIMAX_UI.md) | `clients/windows/ui_gui.py`, DESIGN tokens |
| [REQUIREMENTS.md](REQUIREMENTS.md) | SCOPE, ACCEPTANCE, jarvis-product skill |
| [SCOPE.md](SCOPE.md) | REQUIREMENTS out-of-scope |
| [HOME_HUB.md](HOME_HUB.md) | ROADMAP Phase 5 (house body), run modes/reboot-survival notes |
| [SYNC_PROTOCOL.md](SYNC_PROTOCOL.md) | Device bridge issues, MINIMAX pattern, ARCHITECTURE |
| [TOOL_SCHEMA.md](TOOL_SCHEMA.md) | `hands/registry.py`, MINIMAX client tools |
| [LEARNING.md](LEARNING.md) | FUTURE adaptive mutation, REQUIREMENTS FR-S* | SELF_IMPROVEMENT_LOOP |
| [dev/SELF_IMPROVEMENT_LOOP.md](dev/SELF_IMPROVEMENT_LOOP.md) | FRIDAY-style git + eval; autonomy tiers | FUTURE, LEARNING, eval/README |
| [dev/SELF_STATE.md](dev/SELF_STATE.md) | Living strengths/weaknesses + experiment | After eval runs |
| [PERSONA.md](PERSONA.md) | Soul/persona issues, MINIMAX §8 |
| [DECISIONS.md](DECISIONS.md) | Any ADR; link new ADRs from ARCHITECTURE when major |
| [CODE_MAP.md](CODE_MAP.md) | `scripts/index_repo.py`, file discovery, quick navigation |

### UI Design System & Money Maker Hub (`docs/ui/`)

| Doc | Purpose | Sync with |
|---|---|---|
| [ui/UI_RULES.md](ui/UI_RULES.md) | Simplification rules, anti-bloat, 3-sec cognitive load | DESIGN.md, WEB_UI |
| [ui/UI_SPECIFICATION.md](ui/UI_SPECIFICATION.md) | HUD layouts, Opportunity Radar, responsive cards | DESIGN.md, FLUTTER_FIELD |
| [ui/UI_DEPENDENCY_PLAN.md](ui/UI_DEPENDENCY_PLAN.md) | Minimalist package matrix, zero-overhead bundle plan | OSS.md, package.json |
| [ui/UI_DESIGN_SYSTEM.md](ui/UI_DESIGN_SYSTEM.md) | Unified token matrix, glassmorphism math, elevation | DESIGN.md, tailwind.config |
| [ui/UI_TEMPLATES_CATALOG.md](ui/UI_TEMPLATES_CATALOG.md) | Big-brand monetization blueprints (SaaS, D2C, B2B) | BUSINESS_OPERATOR.md |
| [ui/UI_INDIA_MARKET_PATTERNS.md](ui/UI_INDIA_MARKET_PATTERNS.md) | 1-tap UPI intent, vernacular & trust badges | STRATEGY.md, BUSINESS_OPERATOR |
| [ui/UI_CHAIN_REACTION_PLAN.md](ui/UI_CHAIN_REACTION_PLAN.md) | Autonomous 0-token parallel generation pipeline | AI_CODER_AUTOMATION.md |

### Board (runtime truth — not duplicated in vision docs)

| Path | Role |
|------|------|
| [board/NOW.md](board/NOW.md) | Who owns slots — **overrides** stale “current assignment” in MINIMAX/skills |
| [board/NEXT.md](board/NEXT.md) | Tip issue id |
| [board/LIVE_PLAN.md](board/LIVE_PLAN.md) | **Generated** plan (fingerprint, per-owner next) — run `devloop sync` |
| [board/LIVE_BRIEF.md](board/LIVE_BRIEF.md) | **Generated** agent brief — run `devloop brief --owner ID` |
| [board/issues/](board/issues/) | Acceptance per task |

When board phase advances, update **STRATEGY “Where we are now”** and run **`devloop sync`** (LIVE_PLAN auto-updates).

---

## Owner ids (same everywhere)

`cursor` · `antigravity` · `claude` · `minimax` · `minimax2` · `minimax-mini` · `alice` · `bob`

Documented in: PARALLEL.md, MINIMAX.md, AGENTS.md, STRATEGY.md, FEEDBACK_LOOP.md.

---

## Edit checklist (copy when touching docs)

- [ ] Cross-links still resolve (relative paths from each file)
- [ ] Portable skill ↔ Blackbox mirror (if you changed shared rules)
- [ ] MINIMAX.md ↔ `.blackbox/RULES.md` (if MiniMax rules changed)
- [ ] SYNC_PROTOCOL.md (if WS / client tool messages changed)
- [ ] PLAN_AUDIT.md refreshed when closing plan-related issues
- [ ] STRATEGY ↔ LIVE_PLAN (run `devloop sync`, do not hand-edit stale issue lists)
- [ ] DESIGN.md + surface UI doc (if `clients/**` chrome changed)
- [ ] README Status blurb (if major milestone)
- [ ] ADR in DECISIONS.md (if architecture decision)
- [ ] CODE_MAP.md (if you changed the repo index or discovery layout)

---

## Quick links by role

| You are | Read first |
|---------|------------|
| Human | VISION → STRATEGY → board/NOW |
| Cursor / Antigravity / Claude | AGENTS → PARALLEL → issue file → jarvis-dev skill |
| MiniMax / Blackbox | `.blackbox/RULES.md` → MINIMAX.md → issue file |
| Product behavior | jarvis-product skill → PERSONA → SCOPE → DESIGN.md |
| Device bridge / Field Body | SYNC_PROTOCOL → FLUTTER_FIELD → ISSUE-101 |

---

*This file is the sync hub. If another doc lists “Related” links, it should include [DOCS_MAP.md](DOCS_MAP.md) once per doc set (vision or dev), not duplicate the full matrix.*
