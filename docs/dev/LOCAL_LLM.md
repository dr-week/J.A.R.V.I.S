# Local LLM — LM Studio / Ollama

**Major:** Point Jarvis Mind at a local OpenAI-compatible server. Soul + Hands stay in the brain.

## LM Studio (recommended local)

1. Load a model in LM Studio → start server (default `http://127.0.0.1:1234`).
2. In repo `.env`:

```env
JARVIS_LLM_PROVIDER=openai
JARVIS_LLM_BASE_URL=http://127.0.0.1:1234/v1
JARVIS_LLM_MODEL=your-loaded-model-id
JARVIS_LLM_API_KEY=lm-studio
```

3. Restart brain: `python scripts/run_brain.py`
4. Check `GET /health` → `llm_ready: true`

## Ollama

```env
JARVIS_LLM_PROVIDER=ollama
JARVIS_LLM_BASE_URL=http://127.0.0.1:11434/v1
JARVIS_LLM_MODEL=llama3.2
```

(Ollama’s OpenAI-compatible port may vary by version — use the `/v1` chat endpoint.)

## Jinja / Ministral note

Jarvis stores **assistant replies as plain text strings**. Tool calls use OpenAI `tool_calls` on the wire, not multimodal content chunks — avoids `Only text chunks are supported in assistant message contents`.

If LM Studio alone still errors in agent mode with tools, use a tool-capable template or disable tools for that model in LM Studio UI.

## Velocity

```env
JARVIS_VELOCITY_URL=http://127.0.0.1:5174
# JARVIS_VELOCITY_ROOT=path/to/velocity
```

Tool: `velocity_build` (confirm_always).

**IPC (ISSUE-132):** Velocity posts progress to:

`POST http://<brain>:8787/internal/webhook/velocity`

```json
{
  "app_id": "app-xxx",
  "status": "building",
  "message": "Generating screens",
  "step": 2,
  "progress": 0.4,
  "device_id": ""
}
```

Jarvis broadcasts `{ "type": "velocity_update", "data": { ... } }` on the sync WebSocket. Optional `device_id` unicasts first.

## Related

[LLM.md](../LLM.md) · [AI_CODER_AUTOMATION.md](AI_CODER_AUTOMATION.md) · ISSUE-131 · ISSUE-132
