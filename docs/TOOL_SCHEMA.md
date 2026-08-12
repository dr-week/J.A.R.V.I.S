# Tool Schema

## Canonical tool definition

Every tool in the registry MUST conform to this schema:

```python
{
  "name": str,                    # snake_case, globally unique
  "description": str,             # one sentence for LLM context
  "version": str,                 # semver e.g. "1.0.0"
  "phase": int,                   # minimum phase this tool is available
  "risk_level": str,              # "auto" | "confirm_once" | "confirm_always"
  "executor": str,                # "brain" | "client" | "house"
  "runtime": str,                 # optional: "python" (default) | "lua" | "subprocess"
  "entry": str,                   # optional: script path or binary
  "argv_template": [str],         # optional: arguments template for subprocess
  "timeout_seconds": int,         # optional: execution timeout
  "sandbox": str,                 # optional: "strict" etc.
  "parameters": {                 # JSON Schema object
    "type": "object",
    "properties": { ... },
    "required": [...]
  },
  "returns": {                    # JSON Schema for return value
    "type": "object",
    "properties": { ... }
  },
  "scopes": [str],               # permissions needed e.g. ["calendar:read"]
  "tags": [str]                  # domain tags e.g. ["productivity", "calendar"]
}
```

## Risk levels

| Level | Behaviour | Examples |
|-------|-----------|----------|
| `auto` | Execute silently | Read-only lookups, status queries |
| `confirm_once` | Ask once, then allowlist | Calendar writes, reminder creation |
| `confirm_always` | Always confirm | Send messages, payments, deletes, unlocks |

## Executor locations

| Executor | Where it runs | Examples |
|----------|--------------|----------|
| `brain` | Central brain process | Web search, LLM summarise, cloud APIs |
| `client` | On the requesting device | Open app, read file, control screen |
| `house` | Home hub | Smart lights, locks, camera triggers |

## Example — hello_world tool

```python
{
  "name": "hello_world",
  "description": "Returns a greeting. Used to verify the tool registry works.",
  "version": "1.0.0",
  "phase": 0,
  "risk_level": "auto",
  "executor": "brain",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {"type": "string", "description": "Name to greet"}
    },
    "required": ["name"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "message": {"type": "string"}
    }
  },
  "scopes": [],
  "tags": ["test"]
}
```

## Registration

Tools register on brain startup via `tools/` directory scan or explicit `registry.register()` call.
Clients cannot register tools without brain approval.

## Tool audit

Every `confirm_once` and `confirm_always` tool call is written to `action_log` table with:
`(ts, tool_name, parameters_hash, result_summary, device_id, confirmed_by)`
