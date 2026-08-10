# LLM Provider

## Decision (ADR-0007)

- **Provider v1:** Google Gemini (gemini-2.0-flash or gemini-2.5-pro via `google-genai` SDK)
- **Fallback / override:** Any OpenAI-compatible endpoint (`JARVIS_LLM_BASE_URL` + `JARVIS_LLM_API_KEY`)
- **Tool-call format:** Google Gemini native function calling (JSON schema per tool)
- **Streaming:** Server-sent events (SSE) from brain → clients

## Environment variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google AI Studio / Vertex key | Yes (if Gemini) |
| `JARVIS_LLM_PROVIDER` | `gemini` \| `openai` \| `ollama` | Yes |
| `JARVIS_LLM_MODEL` | Model name override | No |
| `JARVIS_LLM_BASE_URL` | Base URL for OpenAI-compatible endpoints | No |

## Agent loop format

```text
system_prompt (persona + injected memories + active habits)
  + user_message
    → LLM (tool calls?)
      → tool executor
        → result back to LLM
          → final reply streamed to client
```

## Provider swap

Change `JARVIS_LLM_PROVIDER` in `.env`. No code change needed. Brain restarts.

## Notes

- Context window: Gemini Flash 2.0 = 1M tokens. Use full context for memory injection v1.
- Rate limits: track per-user turn counts in Soul DB for future quota management.
- Local LLM: Ollama support planned for Phase 6 (local-first option).
