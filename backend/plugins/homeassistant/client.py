"""Home Assistant REST API client."""
from __future__ import annotations

from typing import Any
import httpx
from backend.app import config

_HOME_ASSISTANT = "/api"


def ha_url() -> str:
    from backend.plugins.homeassistant import _ha_url as patched_url
    if patched_url != ha_url:
        return patched_url()
    return config.HA_URL.rstrip("/")


def ha_token() -> str:
    from backend.plugins.homeassistant import _ha_token as patched_token
    if patched_token != ha_token:
        return patched_token()
    return config.HA_TOKEN


def ha_entity() -> str:
    from backend.plugins.homeassistant import _ha_entity as patched_entity
    if patched_entity != ha_entity:
        return patched_entity()
    return config.HA_ENTITY


def ha_configured() -> bool:
    from backend.plugins.homeassistant import _ha_configured as patched_conf
    if patched_conf != ha_configured:
        return patched_conf()
    return bool(ha_url() and ha_token())


def headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {ha_token()}",
        "Content-Type": "application/json",
    }


def entity_list() -> list[dict[str, Any]]:
    """Fetch all HA entity states. Raises on failure."""
    import backend.plugins.homeassistant as ha_mod
    client_httpx = getattr(ha_mod, "httpx", httpx)
    url = ha_url() + _HOME_ASSISTANT + "/states"
    resp = client_httpx.get(url, headers=headers(), timeout=10.0)
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


def call_service(domain: str, service: str, service_data: dict[str, Any]) -> None:
    """Call a Home Assistant domain service (e.g. light/turn_on)."""
    import backend.plugins.homeassistant as ha_mod
    client_httpx = getattr(ha_mod, "httpx", httpx)
    url = f"{ha_url()}{_HOME_ASSISTANT}/services/{domain}/{service}"
    resp = client_httpx.post(url, headers=headers(), json=service_data, timeout=10.0)
    resp.raise_for_status()
