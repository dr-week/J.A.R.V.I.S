"""Home Assistant bridge plugin facade (Phase 5 — house Hands).

Exposes Home Assistant tools using the HA REST API.
"""
from __future__ import annotations

import httpx
from .client import (
    ha_url as _ha_url,
    ha_token as _ha_token,
    ha_entity as _ha_entity,
    ha_configured as _ha_configured,
    headers as _headers,
    entity_list as _entity_list,
    call_service,
)
from .tools import (
    _home_entity_list,
    _home_entity_set,
    _home_scene,
    register_homeassistant_tools,
)

# Auto-register tools on import
register_homeassistant_tools()

__all__ = [
    "httpx",
    "_ha_url",
    "_ha_token",
    "_ha_entity",
    "_ha_configured",
    "_headers",
    "_entity_list",
    "call_service",
    "_home_entity_list",
    "_home_entity_set",
    "_home_scene",
    "register_homeassistant_tools",
]
