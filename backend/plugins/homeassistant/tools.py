"""Home Assistant tool executors and registry schemas."""
from __future__ import annotations

from typing import Any
from backend.app.hands import registry
from .client import (
    ha_configured,
    ha_entity,
    entity_list,
    call_service,
)


def _home_entity_list() -> dict[str, Any]:
    """List available Home Assistant entities (read-only)."""
    if not ha_configured():
        raise RuntimeError(
            "Home Assistant not configured. Set JARVIS_HA_URL and JARVIS_HA_TOKEN."
        )
    entities = entity_list()
    return {"count": len(entities), "entities": entities}


def _home_entity_set(
    entity_id: str = "",
    state: str = "on",
    brightness: int | None = None,
) -> dict[str, Any]:
    """Control a HA entity. Defaults to the configured light entity."""
    if not ha_configured():
        raise RuntimeError(
            "Home Assistant not configured. Set JARVIS_HA_URL and JARVIS_HA_TOKEN."
        )
    target = entity_id or ha_entity()
    state = (state or "on").lower()

    service_data: dict[str, Any] = {"entity_id": target}
    if brightness is not None and state == "on":
        service_data["brightness"] = int(brightness)

    if state == "on":
        domain = target.split(".")[0] or "light"
        service = "turn_on"
    elif state == "off":
        domain = target.split(".")[0] or "light"
        service = "turn_off"
    else:
        raise ValueError(f"Unsupported state ''{state}''; use ''on'' or ''off''.")

    call_service(domain, service, service_data)

    return {
        "entity_id": target,
        "requested_state": state,
        "brightness": brightness,
        "confirmed_by_service": True,
    }


def _home_scene(scene_id: str = "") -> dict[str, Any]:
    """Activate a Home Assistant scene by entity_id (e.g. scene.movie_night)."""
    if not ha_configured():
        raise RuntimeError(
            "Home Assistant not configured. Set JARVIS_HA_URL and JARVIS_HA_TOKEN."
        )
    target = (scene_id or "").strip()
    if not target:
        raise ValueError("scene_id is required (e.g. ''scene.movie_night'').")
    if not target.startswith("scene."):
        target = f"scene.{target}"

    call_service("scene", "turn_on", {"entity_id": target})
    return {"scene_id": target, "activated": True}


def register_homeassistant_tools() -> None:
    """Register Home Assistant tools into Hands registry."""
    if "home_entity_list" not in registry.REGISTRY:
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

    if "home_entity_set" not in registry.REGISTRY:
        registry.register(
            {
                "name": "home_entity_set",
                "description": (
                    "Turn a Home Assistant entity on or off (e.g. a light). "
                    "Pass entity_id (e.g. ''light.living_room'') or leave empty to use "
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
                            "description": "Desired state: ''on'' or ''off''.",
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

    if "home_scene" not in registry.REGISTRY:
        registry.register(
            {
                "name": "home_scene",
                "description": (
                    "Activate a Home Assistant scene (e.g. movie night, good night). "
                    "Pass scene_id as ''scene.movie_night'' or short name ''movie_night''."
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
                            "description": "HA scene entity_id or short name without ''scene.''.",
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
