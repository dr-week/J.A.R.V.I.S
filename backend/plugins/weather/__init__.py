"""Weather connector plugin (Phase 6 example third-party connector).

Built purely from the Jarvis plugin SDK (see docs/SDK.md and
backend/plugins/template).  Uses the free Open-Meteo API which requires no
API key, so it works out of the box as a real connector.

Authentication/configuration is brain-local: an optional default location is
read from the brain process environment (JARVIS_WEATHER_DEFAULT_LAT /
JARVIS_WEATHER_DEFAULT_LON), never from tool arguments or results.
"""
from __future__ import annotations

import math
from typing import Any

import httpx
from backend.app.hands import registry

_WEATHER_API = "https://api.open-meteo.com/v1/forecast"
_MAX_FORECAST_DAYS = 16


def _geocode(city: str) -> tuple[float, float]:
    """Resolve a city name to (latitude, longitude) via Open-Meteo geocoding."""
    response = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10.0,
    )
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        raise ValueError(f"Could not resolve city '{city}'.")
    return float(results[0]["latitude"]), float(results[0]["longitude"])


def _default_lat_lon() -> tuple[float, float] | None:
    """Return the configured default location, if any."""
    import os
    lat = os.environ.get("JARVIS_WEATHER_DEFAULT_LAT", "").strip()
    lon = os.environ.get("JARVIS_WEATHER_DEFAULT_LON", "").strip()
    if lat and lon:
        try:
            return float(lat), float(lon)
        except ValueError:
            return None
    return None


def _resolve_location(city: str, latitude: float | None, longitude: float | None) -> tuple[float, float]:
    """Resolve a location from explicit coords, a city name, or the default."""
    if latitude is not None and longitude is not None:
        if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
            raise ValueError("latitude/longitude out of range.")
        return latitude, longitude
    if city:
        return _geocode(city)
    default = _default_lat_lon()
    if default:
        return default
    raise ValueError("Provide a city, latitude/longitude, or set JARVIS_WEATHER_DEFAULT_LAT/LON.")


def _fetch(lat: float, lon: float, forecast_days: int) -> dict[str, Any]:
    """Query the Open-Meteo forecast API for current conditions + forecast."""
    if not 0 <= forecast_days <= _MAX_FORECAST_DAYS:
        raise ValueError(f"forecast_days must be between 0 and {_MAX_FORECAST_DAYS}.")
    response = httpx.get(
        _WEATHER_API,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "forecast_days": forecast_days or 1,
            "timezone": "auto",
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def _weather_code_label(code: int) -> str:
    """Map a WMO weather code to a short human label."""
    if code == 0:
        return "clear"
    if code in (1, 2):
        return "partly cloudy"
    if code == 3:
        return "overcast"
    if code in (45, 48):
        return "foggy"
    if code in (51, 53, 55, 56, 57):
        return "drizzle"
    if code in (61, 63, 65, 66, 67):
        return "rain"
    if code in (71, 73, 75, 77):
        return "snow"
    if code in (80, 81, 82):
        return "rain showers"
    if code in (85, 86):
        return "snow showers"
    if code in (95, 96, 99):
        return "thunderstorm"
    return "unknown"


def _location_summary(lat: float, lon: float) -> str:
    return f"{lat:.4f},{lon:.4f}"


def weather_current(city: str = "", latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
    """Return current weather conditions for a location."""
    lat, lon = _resolve_location(city, latitude, longitude)
    data = _fetch(lat, lon, 0)
    current = data.get("current", {})
    return {
        "location": _location_summary(lat, lon),
        "temperature_c": current.get("temperature_2m"),
        "apparent_temperature_c": current.get("apparent_temperature"),
        "relative_humidity_pct": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "condition": _weather_code_label(current.get("weather_code", -1)),
        "observed_at": current.get("time"),
    }


def weather_forecast(city: str = "", latitude: float | None = None, longitude: float | None = None, days: int = 3) -> dict[str, Any]:
    """Return a multi-day weather forecast for a location."""
    lat, lon = _resolve_location(city, latitude, longitude)
    if not 1 <= days <= _MAX_FORECAST_DAYS:
        raise ValueError(f"days must be between 1 and {_MAX_FORECAST_DAYS}.")
    data = _fetch(lat, lon, days)
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    codes = daily.get("weather_code", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    forecast = [
        {
            "date": dates[i],
            "condition": _weather_code_label(codes[i]),
            "high_c": highs[i],
            "low_c": lows[i],
        }
        for i in range(len(dates))
    ]
    return {
        "location": _location_summary(lat, lon),
        "days": len(forecast),
        "forecast": forecast,
    }


registry.register(
    {
        "name": "weather_current",
        "description": "Get the current weather conditions for a city, latitude/longitude, or the configured default location.",
        "version": "1.0.0", "phase": 6, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "city": {"type": "string", "description": "City name (e.g. 'London'). Optional if lat/lon or default is set."},
            "latitude": {"type": "number", "minimum": -90, "maximum": 90},
            "longitude": {"type": "number", "minimum": -180, "maximum": 180},
        }, "required": []},
        "returns": {"type": "object", "properties": {
            "location": {"type": "string"}, "temperature_c": {"type": "number"},
            "apparent_temperature_c": {"type": "number"}, "relative_humidity_pct": {"type": "number"},
            "wind_speed_kmh": {"type": "number"}, "condition": {"type": "string"}, "observed_at": {"type": "string"},
        }},
        "scopes": ["weather:read"], "tags": ["weather", "connector", "life"],
    },
    weather_current,
)

registry.register(
    {
        "name": "weather_forecast",
        "description": "Get a multi-day weather forecast for a city, latitude/longitude, or the configured default location.",
        "version": "1.0.0", "phase": 6, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "city": {"type": "string", "description": "City name (e.g. 'Paris'). Optional if lat/lon or default is set."},
            "latitude": {"type": "number", "minimum": -90, "maximum": 90},
            "longitude": {"type": "number", "minimum": -180, "maximum": 180},
            "days": {"type": "integer", "minimum": 1, "maximum": 16, "default": 3},
        }, "required": []},
        "returns": {"type": "object", "properties": {
            "location": {"type": "string"}, "days": {"type": "integer"},
            "forecast": {"type": "array"},
        }},
        "scopes": ["weather:read"], "tags": ["weather", "connector", "life"],
    },
    weather_forecast,
)
