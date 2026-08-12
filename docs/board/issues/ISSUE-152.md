---
id: ISSUE-152
title: LiteLLM gateway contract and config shape
status: done
priority: P1
phase: 3
labels: [oss, integrations, docs]
owner: claude
claimed_at: 2026-08-12T18:57:27Z
blocked_by: []
acceptance:
  - LiteLLM gateway config is defined for Gemini plus one OpenAI-compatible/local endpoint
  - Provider/model selection stays in `.env` and is documented in the integration inventory
  - The first slice is small enough to verify without changing client prompts or exposing secrets
---

## Context

Start the LiteLLM integration in the smallest possible slice so the model gateway
contract is explicit before runtime wiring.

## Work

- [x] Define the provider contract and `.env` keys for gateway routing.
- [x] Keep Gemini as the default until the gateway passes acceptance.
- [x] Sync the inventory and OSS plan wording if the slice changes the plan.

## Notes

- [2026-08-12T18:59:41Z] Marked done


- [2026-08-12T18:58:58Z] Added LiteLLM config contract keys, relaxed llm_ready for litellm, documented env vars, and added config regression test.
- [2026-08-12T19:00:00Z] Marked done after config contract slice passed tests.


- Claimed by claude at 2026-08-12T18:57:27Z


Created for the LiteLLM first slice. This is intentionally only the contract/config
step; runtime wiring and acceptance proof belong to later slices.

## Links

- [GITHUB_INTEGRATIONS.md](../../GITHUB_INTEGRATIONS.md)
- [OSS.md](../../OSS.md)
- [OSS_DEV_PLAN.md](../dev/OSS_DEV_PLAN.md)
