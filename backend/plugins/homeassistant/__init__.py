"""Home Assistant bridge plugin (Phase 5 — house Hands).

Exposes a subset of Home Assistant as Jarvis tools using the HA REST API.

Config (env, see .env.example):
  JARVIS_HA_URL    e.g. http://192.168.1.10:8123
  JARVIS_HA_TOKEN  a long-lived access token from your HA profile
  JARVIS_HA_ENTITY e.g. light.living_room (default light to control)

Tools registered:
  - home_entity_list  (risk: auto)          list available HA entities
  - home_entity_set   (risk: confirm_once)   turn a light on/off / set brightness
  - home_scene        (risk: confirm_once)   activate a HA scene

The bridge talks to Home Assistant over its REST API. If HA is not configured
(JARVIS_HA_URL empty), tools fail visibly with a clear error — never silently.
"""
from __future__ import annotations

from typing import Any

import httpx
from backend.app import config
from backend.app.hands import registry

_HOME_ASSISTANT = "/api"


def _ha_url() -> str:
    return config.HA_URL.rstrip("/")


def _ha_token() -> str:
    return config.HA_TOKEN


def _ha_entity() -> str:
    return config.HA_ENTITY


def _ha_configured() -> bool:
    return bool(_ha_url() and _ha_token())


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_ha_token()}",
        "Content-Type": "application/json",
    }


def _entity_list() -> list[dict[str, Any]]:
    """Fetch all HA entity states. Raises on failure."""
    url = _ha_url() + _HOME_ASSISTANT + "/states"
    resp = httpx.get(url, headers=_headers(), timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    return [
        {
            "entity_id": e.get("entity_id"),
            "state": e.get("state"),
            "attributes": {
                "friendly_name": e.get("attributes", {}).get("friendly_name", ""),
            },
        }
        for e in data
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Tool executors
# ─────────────────────────────────────────────────────────────────────────────

def _home_entity_list() -> dict[str, Any]:
    """List available Home Assistant entities (read-only)."""
    if not _ha_configured():
        raise RuntimeError(
            "Home Assistant not configured. Set JARVIS_HA_URL and JARVIS_HA_TOKEN."
        )
    entities = _entity_list()
    return {"count": len(entities), "entities": entities}


def _home_entity_set(
    entity_id: str = "",
    state: str = "on",
    brightness: int | None = None,
) -> dict[str, Any]:
    """Control a HA entity. Defaults to the configured light entity.

    state: 'on' | 'off' (for lights, brightness uses HA 0-255 scale).
    brightness: optional 0-255 value applied when turning on a light.
    """
    if not _ha_configured():
        raise RuntimeError(
            "Home Assistant not configured. Set JARVIS_HA_URL and JARVIS_HA_TOKEN."
        )
    target = entity_id or _ha_entity()
    state = (state or "on").lower()

    service_data: dict[str, Any] = {"entity_id": target}
    if brightness is not None and state == "on":
        service_data["brightness"] = int(brightness)

    if state == "on":
        domain = target.split(".")[0] or "light"
        service = f"{domain}/turn_on"
    elif state == "off":
        domain = target.split(".")[0] or "light"
        service = f"{domain}/turn_off"
    else:
        raise ValueError(f"Unsupported state '{state}'; use 'on' or 'off'.")

    url = _ha_url() + _HOME_ASSISTANT + "/services/" + service
    resp = httpx.post(url, headers=_headers(), json=service_data, timeout=10.0)
    resp.raise_for_status()

    return {
        "entity_id": target,
        "requested_state": state,
        "brightness": brightness,
        "confirmed_by_service": True,
    }


def _home_scene(scene_id: str = "") -> dict[str, Any]:
    """Activate a Home Assistant scene by entity_id (e.g. scene.movie_night)."""
    if not _ha_configured():
        raise RuntimeError(
            "Home Assistant not configured. Set JARVIS_HA_URL and JARVIS_HA_TOKEN."
        )
    target = (scene_id or "").strip()
    if not target:
        raise ValueError("scene_id is required (e.g. 'scene.movie_night').")
    if not target.startswith("scene."):
        target = f"scene.{target}"

    url = _ha_url() + _HOME_ASSISTANT + "/services/scene/turn_on"
    resp = httpx.post(
        url,
        headers=_headers(),
        json={"entity_id": target},
        timeout=10.0,
    )
    resp.raise_for_status()
    return {"scene_id": target, "activated": True}


# ─────────────────────────────────────────────────────────────────────────────
# Registration (self-register on import via discover_plugins)
# ─────────────────────────────────────────────────────────────────────────────

registry.register(
    {
        "name": "home_entity_list",
        "description": (
            "List available Home Assistant entities and their states. "
            "Use this before controlling an entity to confirm its entity_id."
        ),
        "version": "1.0.0",
        "phase": 5,
        "risk_level": "auto",
        "executor": "house",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "entities": {"type": "array"},
            },
        },
        "scopes": ["house:read"],
        "tags": ["house", "iot", "homeassistant"],
    },
    _home_entity_list,
)

registry.register(
    {
        "name": "home_entity_set",
        "description": (
            "Turn a Home Assistant entity on or off (e.g. a light). "
            "Pass entity_id (e.g. 'light.living_room') or leave empty to use "
            "the configured default. Optional brightness 0-255 for lights."
        ),
        "version": "1.0.0",
        "phase": 5,
        "risk_level": "confirm_once",
        "executor": "house",
        "parameters": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "HA entity_id, e.g. light.living_room.",
                },
                "state": {
                    "type": "string",
                    "enum": ["on", "off"],
                    "default": "on",
                    "description": "Desired state: 'on' or 'off'.",
                },
                "brightness": {
                    "type": "integer",
                    "description": "Optional brightness 0-255 (lights only).",
                },
            },
            "required": [],
        },
        "returns": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string"},
                "requested_state": {"type": "string"},
            },
        },
        "scopes": ["house:write"],
        "tags": ["house", "iot", "homeassistant"],
    },
    _home_entity_set,
)

registry.register(
    {
        "name": "home_scene",
        "description": (
            "Activate a Home Assistant scene (e.g. movie night, good night). "
            "Pass scene_id as 'scene.movie_night' or short name 'movie_night'."
        ),
        "version": "1.0.0",
        "phase": 5,
        "risk_level": "confirm_once",
        "executor": "house",
        "parameters": {
            "type": "object",
            "properties": {
                "scene_id": {
                    "type": "string",
                    "description": "HA scene entity_id or short name without 'scene.'.",
                },
            },
            "required": ["scene_id"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "scene_id": {"type": "string"},
                "activated": {"type": "boolean"},
            },
        },
        "scopes": ["house:write"],
        "tags": ["house", "iot", "homeassistant", "scene"],
    },
    _home_scene,
)

