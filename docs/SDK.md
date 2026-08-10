# Jarvis Plugin SDK

Jarvis is designed to be indefinitely extensible. By creating **Plugins**, you can give Jarvis new tools and capabilities without ever needing to modify the core `brain` code.

## How Plugins Work

Jarvis scans the `backend/plugins/` directory on startup. Any folder found in this directory is treated as a plugin. 

To create a new plugin:
1. Create a new folder in `backend/plugins/` (e.g., `backend/plugins/my_plugin/`).
2. Add an `__init__.py` file inside that folder.
3. Import the `registry` from `backend.app.hands` and call `registry.register()` with your tool definitions.

Jarvis will automatically discover your folder, import your `__init__.py`, and register your tools!

**Reference connector (ISSUE-071):** See [`backend/plugins/weather/`](../backend/plugins/weather/README.md)

**Other languages (Phase 6):** Lua (embedded), Go/R (subprocess) — [POLYGLOT_TOOLS.md](../docs/dev/POLYGLOT_TOOLS.md). Design **ISSUE-128**, Lua **ISSUE-129**.

---

## 1. Defining a Tool

Every tool must provide a JSON Schema that defines its inputs, outputs, and behaviour. See `docs/TOOL_SCHEMA.md` for the full schema details.

Here is a minimal plugin example (`backend/plugins/hello_world/__init__.py`):

```python
from backend.app.hands import registry

def _say_hello(name: str = "world") -> str:
    return f"Hello, {name}! This is a custom plugin."

registry.register(
    {
        "name": "plugin_hello_world",
        "description": "A template plugin tool.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "auto",  # See "Risk Levels" below
        "executor": "brain",   # See "Executors" below
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet"}
            },
            "required": [],
        },
        "returns": {
            "type": "object",
            "properties": {"result": {"type": "string"}}
        },
        "scopes": [],
        "tags": ["plugin", "demo"],
    },
    _say_hello,
)
```

---

## 2. Risk Levels (Confirmation Gate)

Not all tools should run automatically. Some actions (like sending emails or deleting files) require the user's explicit permission.

You control this via the `"risk_level"` field in your tool definition:

| Level | Behavior | Example Use Case |
|-------|----------|------------------|
| `auto` | Executes silently and immediately. | Fetching weather, reading data. |
| `confirm_once` | Jarvis will ask the user for permission the *first* time this tool is used on a device. If approved, it is allowlisted for future use. | Writing to a calendar, setting reminders. |
| `confirm_always` | Jarvis will ask the user for permission *every single time* this tool is called. | Sending money, deleting data, unlocking doors. |

When a tool requires confirmation, Jarvis's brain intercepts the execution, stores it in the `pending_confirmations` table, and asks the user. You don't need to write any code to handle this—the Brain handles the gatekeeping for you.

---

## 3. Executors (Where does the tool run?)

Jarvis is a distributed system. The Brain runs in a central location, but the user might be talking to Jarvis from their Windows PC, an Android phone, or a Home Hub in the living room.

You control where the code actually executes using the `"executor"` field:

- **`executor: "brain"`**: The tool executes directly on the server hosting the Jarvis Brain. This is perfect for calling web APIs, doing database lookups, or heavy processing.
- **`executor: "client"`**: The tool executes on the *device the user is currently using*. 
  - *Example:* If you want Jarvis to "Open Spotify", the brain shouldn't open Spotify on the server—it needs to open it on the user's phone or PC.
  - When you set `executor: "client"`, you **do not provide a python function** to `registry.register()`. Instead, the Brain automatically routes the tool execution request over WebSockets to the connected client. The client is responsible for executing the action and returning the result.

---

## 4. Dependencies

If your plugin requires third-party Python packages, simply include a `requirements.txt` file in your plugin folder. 
*(Note: Dependency auto-installation is coming in a future update, so for now, you should manually install your plugin's dependencies in your Python environment).*

---

## 5. Reference example: weather connector

The best end-to-end example of a real third-party connector built **only** from
this SDK + the `backend/plugins/template` is the **weather plugin**
(`backend/plugins/weather/`). It exposes two tools against the free
[Open-Meteo](https://open-meteo.com/) API (no API key required):

- `weather_current` — current conditions for a city / lat-lon / default location.
- `weather_forecast` — up to 16-day forecast (high/low/condition per day).

It demonstrates the full plugin pattern:

- A folder under `backend/plugins/` with an `__init__.py` that self-registers.
- `httpx` used for outbound HTTP (see its own `requirements.txt`).
- Brain-local configuration via environment variables (`JARVIS_WEATHER_DEFAULT_LAT` /
  `JARVIS_WEATHER_DEFAULT_LON`) so **no secrets or config ever appear in tool
  arguments or results**.
- Multiple tools registered from one plugin, each conforming to the canonical
  schema in `docs/TOOL_SCHEMA.md`.

Copy `backend/plugins/template`, then model your executor + registration on the
weather plugin to build your own connector.
