# Plan cross-check audit



Cross-check of [SYNC_PLAN.md](SYNC_PLAN.md), [PRESENCE_STACKS.md](PRESENCE_STACKS.md), board **101–107**, **142**, and [REQUIREMENTS.md](../REQUIREMENTS.md).



**Last reviewed:** 2026-08-10 · Board truth: `python scripts/devloop.py sync` → [LIVE_PLAN.md](../board/LIVE_PLAN.md)



---



## Board snapshot (truth = issue frontmatter + LIVE_PLAN)



| Issue | Status | Notes |

|-------|--------|--------|

| 101 | NOW / minimax | Epic — **112–114** done; close after Windows `tool_execute` smoke |

| 102 | done | Web sessions |

| 103 | todo | Strip Flutter chat — blocked on **101** |

| 104 | done | Backend WS `confirm_request` push |

| 142 | backlog | Flutter Field approve/deny (follow-up to **104**) |

| 105 | done | Web QA 098/099 |

| 106 | todo | PWA |

| 107 | todo | WS token auth |

| 108–114 | done | Dev + Field slices |

| 115–118 | backlog | pytest, mypy, devloop — [STRATEGY_FORWARD.md](STRATEGY_FORWARD.md) |

| 130–132 | backlog | **Velocity** integration (not pydantic/loguru — see **122/124**) |



---



## Satisfied



| Requirement / plan item | Evidence |

|-------------------------|----------|

| FR-B1–B4 build OS | Docs, board, devloop |

| FR-H1 device bridges | ISSUE-032/033; Windows + Kotlin Android |

| FR-M4 audit | action_log, hands API |

| One chat UI (policy) | PRESENCE_STACKS, ADR-0023, jarvis-product Don't |

| Web pair/health/chat SSE | `clients/web`, `brainApi.ts` |

| FR-P3 session list (web) | `useJarvisApp` + sessions (102) |

| Session API (brain) | `GET /sessions`, `GET /sessions/{id}` |

| ISSUE-103 blocked on 101 | `blocked_by: [ISSUE-101]` |



---



## Mistakes found (historical — keep for agents)



### 1. Flutter vs Android bridge duplicate



**Was:** ISSUE-101 implied Flutter `android_open`. **Fix:** Kotlin **033** owns Android; Flutter = desktop Field only.



### 2. `confirm_request` split backend vs Field



**Was:** Treated as one issue. **Fix:** **104** = brain push (done). **142** = Flutter handle + UI (backlog).



### 3. False `done` without acceptance ticks



**Was:** 098–099 (and risk on 102/105). **Fix:** tick `[ ]` → `[x]` in issue bodies when verified.



### 4. STRATEGY broken markdown



**Was:** Code fence swallowed “Next actions” table. **Fixed** in STRATEGY.md.



### 5. SYNC_PLAN table implied confirm on Flutter today



**Was:** Row listed `confirm_request` as shipped on Field. **Fixed** — **142** for Field.



### 6. Flutter still ships chat UI



**Open:** ISSUE-103 after 101.



### 7. WS `/ws` no token validation



**Open:** **107**; document in SECURITY.



### 8. Issue ID collision (130/131)



**Was:** Plan docs used **130/131** for pydantic/loguru deps; issue files are **Velocity**. **Fix:** Wave Y = **119→122**, **124**; Velocity = **130–132** only ([MINIMAX_QUEUE.md](MINIMAX_QUEUE.md)).



---



## Requirement trace (presence)



| ID | Owner |

|----|--------|

| FR-P-web | `clients/web/` chat + sessions |

| FR-P1 Android | Kotlin bridge + open web for chat |

| FR-P2 Windows | Flet agent + web chat |

| FR-P3 Session sync | Web UI (102) + brain API |

| FR-M1 Conversational UI | Web |

| FR-M3 Confirmations | Web chat text; Field **142** after **104** |

| FR-H1 Bridges | 032/033; Flutter desktop tools in **101** |



---



## Suggested improvements (next plan iteration)



| # | Improvement | Why |

|---|-------------|-----|

| 1 | **ISSUE-106:** Web PWA | Desktop daily driver |

| 2 | **ISSUE-107:** `/ws` token auth | SECURITY + PLAN_AUDIT §7 |

| 3 | **Merge FLUTTER_UI.md → FLUTTER_FIELD.md** | One Flutter doc |

| 4 | **`devloop done` requires acceptance `[x]`** | Done — `--force` when children satisfy parent |

| 5 | **Android README** — chat via web | Done |

| 6 | **STRATEGY “Where we are”** | Point at LIVE_PLAN, not static issue lists |

| 7 | **102/105:** Human smoke sessions | FR-P3 E2E |

| 8 | **Close 101** after Windows smoke | Frees NOW slot |

| 9 | **Ruff** | ✅ habit |

| 10 | **pre-commit (108)** | ✅ |

| 11 | `devloop verify ISSUE-XXX` | ✅ — run before claim |

| 12 | **check_dev_env + dev_up** | ✅ |



---



## Open backlog (action)



```bash

python scripts/devloop.py sync

# Free slot: claim ISSUE-115 (minimax2) or ISSUE-107 (cursor) while minimax closes 101

```


