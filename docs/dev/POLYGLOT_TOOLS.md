# Polyglot tools — Lua, Go, R, and beyond

**Can Jarvis use other languages?** Yes — as **plugins**, not as a second brain. The Mind stays Python; other runtimes implement **Hands** behind the same tool registry.

**Phase:** primarily **6 (SDK)** after Hands exit. Design: **ISSUE-128** · Lua pilot: **ISSUE-129**.

Related: [SDK.md](../SDK.md) · [TOOL_SCHEMA.md](../TOOL_SCHEMA.md) · [SCOPE.md](../SCOPE.md)

---

## Stark rule

One **arc reactor** (Python brain + registry + gate). Other languages are **swap-in tool bodies** — like Stark swapping repulsor firmware, not building a second AI in the basement.

---

## Integration patterns (pick one per language)

| Pattern | Best for | Isolation | Speed | Jarvis fit |
|---------|----------|-----------|-------|------------|
| **A. Subprocess** | Go, R, Rust CLI | Strong | Medium | **Default** — `confirm_always` for shell |
| **B. Embedded VM** | Lua (sandboxed) | Medium | Fast | **129** — `lupa` in brain process |
| **C. Sidecar HTTP** | Go microservices | Strong | Network | Later — when multi-host |
| **D. WASM** | Untrusted user plugins | Strong | Good | Future ADR — not first slice |

**Do not** embed Go/R inside Python like Lua unless there is a mature, supported bridge (there isn’t one standard).

---

## Recommended OSS by language

| Language | Library / runtime | Install | Role |
|----------|-------------------|---------|------|
| **Lua** | **lupa** (LuaJIT in process) | `pip install lupa` | Small transforms, user scripts, hot glue |
| **Go** | `go` toolchain + compiled plugin binary | user installs Go | Fast connectors, CLIs, concurrent fetch |
| **R** | **R** + `Rscript` | user installs R | Stats, data science, research notebooks |
| **Rust** | `cargo build` → binary | optional later | Performance-critical single tools |
| **Node** | already on PATH for web | `npm` in `clients/web` only | **Not** brain plugins by default — avoid two JS runtimes in brain |

---

## Tool schema extension (ISSUE-128)

Today `executor` is `brain` | `client` | `house`. Proposed **optional** fields (Phase 6):

```json
{
  "runtime": "python",
  "runtime": "lua",
  "runtime": "subprocess",
  "entry": "plugins/my_tool/script.lua",
  "entry": "bin/my_tool",
  "argv_template": ["Rscript", "plugins/stats/run.R", "--input", "{input_path}"],
  "timeout_seconds": 30,
  "sandbox": "strict"
}
```

- **python** — current `backend/plugins/*` (default).
- **lua** — `lupa` sandbox; no filesystem/network unless explicitly allowlisted.
- **subprocess** — Go/R/Rust/**any** binary; stdin/stdout JSON; strict timeout; cwd locked to plugin dir.

Risk: subprocess tools default **`confirm_once`** or **`confirm_always`** until allowlisted.

---

## Safety (non-negotiable)

1. **No arbitrary shell** from chat — only registered tools with fixed argv templates.
2. **Timeouts** on every external process.
3. **Resource limits** (memory/CPU) for embedded Lua where OS allows.
4. **Audit log** records runtime + plugin id + redacted args (existing action_log).
5. **Phase gate** — polyglot off until Phase 2 exit (confirm WS, audit).

---

## Phased rollout

| Step | Issue | Deliverable |
|------|-------|-------------|
| 1 | **128** | ADR + TOOL_SCHEMA + `ExternalExecutor` interface (design only) |
| 2 | **129** | `lupa` + one demo Lua tool `lua_echo` |
| 3 | **132** (proposed) | Go subprocess template `plugins/go_demo/bin` |
| 4 | **133** (proposed) | R `Rscript` template for stats stub |
| 5 | Future | WASM ADR if untrusted community plugins |

MiniMax: **129** after **128** (Lua only). Go/R are **subprocess issues**, not embedded.

---

## Omni-glot roadmap (prioritized — after Lua)

Your list is directionally right; Jarvis implements it in **tiers**, not all at once.

### Tier 0 — Already Jarvis (not “Phase 6 polyglot”)

| Item | Reality in repo |
|------|-----------------|
| **SQL** | **SQLite** via `aiosqlite` + future **alembic** (**123**) — memory/habits queries are Python/SQL strings with policy, not a second SQL “engine” |
| **Dart** | **Flutter Field** runs **client-executor** tools over the bridge — not a general Dart plugin VM |
| **Kotlin** | **Android bridge** (**033**) for device tools — not arbitrary JVM sidecars yet |
| **TypeScript** | **Web** chat UI only |

### Tier 1 — Right after Lua (**recommended order**)

| Priority | Language | Pattern | Issue | Why |
|----------|----------|---------|-------|-----|
| **1** | **Go** | Subprocess JSON binary | **132** | One static binary, great for hash/file/parse jobs; no gRPC needed v1 |
| **2** | **R** | `Rscript` subprocess | **133** | Stats/time-series without **rpy2** (avoids R↔Python version hell in the brain process) |
| **3** | **Rust** | Subprocess (same as Go) | future **134** | When Go template exists, copy pattern |

**Answer: prioritize Go (132), then R via Rscript (133).** Not MATLAB, not JVM, not gRPC in the first polyglot sprint.

### Tier 2 — Subprocess legacy (on demand)

| Language | Pattern | Note |
|----------|---------|------|
| **PHP, Ruby, Perl** | Fixed-path `subprocess` + argv template | Maintenance scripts you already own — `confirm_always` |
| **Node** | Subprocess only if needed | Prefer keeping JS in `clients/web` |

### Tier 3 — ADR before code

| Idea | Jarvis stance |
|------|----------------|
| **rpy2** (embedded R) | Defer — use **Rscript** first; embed only if subprocess is proven insufficient |
| **MATLAB Engine** | Defer — license + install weight; subprocess/CLI if you already have MATLAB |
| **gRPC sidecars** (Rust/Go) | Defer — **128** ships stdin/stdout JSON; add gRPC when multi-host is real |
| **Scala/Kotlin JVM sidecar** | Defer — enterprise integration only with ADR |
| **Swift** | Future native iOS **client** executor — same model as Android bridge |
| **WASM** | Tier 3+ for untrusted community plugins |

### Out of scope / caution

- **“Network scanning”** as a default tool — conflicts with [SCOPE.md](../SCOPE.md) trust model; if ever added, `confirm_always` + explicit issue, not Phase 6 marketing.
- **Embedding every language** in Python — only **Lua** via `lupa` for v1 embedded.

### ISSUE-128 deliverable (what “universal adapter” means v1)

1. `runtime`: `python` | `lua` | `subprocess`
2. `ExternalExecutor` dispatches to **lupa** or **subprocess runner** (timeout, cwd, JSON protocol)
3. **Extension point** documented for gRPC/JVM — **no implementation** until ADR

---

## What stays Python

- FastAPI brain, Mind loop, Soul, sync protocol, `hands/gate.py`
- Most plugins (weather, reminders, HA) — Python is fine

Use Go/R/Lua when **you** have an existing asset (R model, Go CLI, Lua config DSL) — not to rewrite the brain.

---

## Related board

| ID | Title |
|----|--------|
| 128 | Polyglot executor design |
| 129 | Embedded Lua (lupa) |
| 130 | pydantic-settings dep (config — not polyglot) |
| 131 | loguru dep (logging — not polyglot) |

[OSS_DEV_PLAN.md](OSS_DEV_PLAN.md) · [STARK_OSS_INSTALL.md](STARK_OSS_INSTALL.md)
