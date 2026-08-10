# Weather Connector Plugin

A real third-party connector built **only** from the Jarvis plugin SDK
(`docs/SDK.md` + the `backend/plugins/template`). It proves the repo is
expandable without touching the core brain.

## Data source

Uses the free [Open-Meteo](https://open-meteo.com/) forecast + geocoding
APIs. **No API key required** — it works out of the box.

## Tools

| Tool | Risk | Executor | Description |
|------|------|----------|-------------|
| `weather_current` | `auto` | `brain` | Current temperature, feels-like, humidity, wind, and condition for a city / lat-lon / default location. |
| `weather_forecast` | `auto` | `brain` | Up to 16-day forecast (high/low/condition per day). |

## Configuration (optional, brain-local)

Set a default location on the brain host so the user can ask about "the
weather" without specifying a place:

```bash
export JARVIS_WEATHER_DEFAULT_LAT=40.7128
export JARVIS_WEATHER_DEFAULT_LON=-74.0060
```

Otherwise pass a `city` name or explicit `latitude`/`longitude` to each tool.
No secrets are ever exposed in tool arguments or results.

## Example

```json
{"name": "weather_current", "arguments": {"city": "London"}}
```

Follows the canonical tool schema in `docs/TOOL_SCHEMA.md`.
