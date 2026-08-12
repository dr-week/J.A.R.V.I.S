# LLM Provider

## Decision (ADR-0007)

- **Provider v1:** Google Gemini (gemini-2.0-flash or gemini-2.5-pro via `google-genai` SDK)
- **Fallback / override:** Any OpenAI-compatible endpoint (`JARVIS_LLM_BASE_URL` + `JARVIS_LLM_API_KEY`)
- **Gateway contract:** LiteLLM can sit in front of Gemini/OpenAI-compatible/local models via its own env keys, but the brain still treats it as an OpenAI-compatible path until the runtime slice lands
- **Tool-call format:** Google Gemini native function calling (JSON schema per tool)
- **Streaming:** Server-sent events (SSE) from brain → clients

## Environment variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google AI Studio / Vertex key | Yes (if Gemini) |
| `JARVIS_LLM_PROVIDER` | `gemini` \| `openai` \| `ollama` | Yes |
| `JARVIS_LLM_MODEL` | Model name override | No |
| `JARVIS_LLM_BASE_URL` | Base URL for OpenAI-compatible endpoints | No |
| `JARVIS_LITELLM_MODEL` | Optional model routed through LiteLLM | No |
| `JARVIS_LITELLM_BASE_URL` | LiteLLM gateway URL | No |
| `JARVIS_LITELLM_API_KEY` | LiteLLM gateway key | No |

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
- Local LLM: [dev/LOCAL_LLM.md](dev/LOCAL_LLM.md) — LM Studio / Ollama via `openai` | `ollama` providers (implemented).
- LiteLLM is a planned gateway contract, not a separate provider path yet.
