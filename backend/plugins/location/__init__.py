"""Location Services plugin — geopy wrapper.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

from typing import Any
from backend.app.hands import registry

try:
    from geopy.geocoders import Nominatim
    _HAS_GEOPY = True
except ImportError:
    _HAS_GEOPY = False


def _location_geocode(address: str) -> dict[str, Any]:
    """Geocode address string to lat/lng using OpenStreetMap Nominatim."""
    if not _HAS_GEOPY:
        return {"error": "geopy is not installed. Run: pip install geopy"}
    try:
        geolocator = Nominatim(user_agent="jarvis_assistant")
        loc = geolocator.geocode(address)
        if not loc:
            return {"error": f"Address '{address}' not found."}
        return {"address": loc.address, "latitude": loc.latitude, "longitude": loc.longitude}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "location_geocode",
        "description": "Geocode address string to latitude, longitude, and full address.",
        "version": "1.0.0",
        "phase": 7,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {"address": {"type": "string"}},
            "required": ["address"],
        },
        "returns": {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}},
        "scopes": ["location:read"],
        "tags": ["location", "maps", "geocoding"],
    },
    _location_geocode,
)
