"""Spotify Ambient Audio & Music Control Connector Plugin (Phase 3+).

Provides clean, non-monolithic Spotify Web API integration for CoreBrain.
Supports searching music, fetching active playback, playing, pausing, and skipping tracks.

Architecture & Security Rationale:
- Token is read brain-locally from `JARVIS_SPOTIFY_ACCESS_TOKEN` or `SPOTIFY_ACCESS_TOKEN`.
- Audio control endpoints communicate with the official Spotify Web API (`https://api.spotify.com/v1`).
- Never leaks user tokens or private session IDs in tool parameters.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from backend.app.hands import registry

_SPOTIFY_API = "https://api.spotify.com/v1"


def _token() -> str:
    """Retrieve Spotify access token from environment variables."""
    return (os.environ.get("JARVIS_SPOTIFY_ACCESS_TOKEN") or os.environ.get("SPOTIFY_ACCESS_TOKEN") or "").strip()


def _get_headers() -> dict[str, str]:
    """Construct Spotify REST API request headers."""
    token = _token()
    if not token:
        raise RuntimeError("Spotify is not configured. Set JARVIS_SPOTIFY_ACCESS_TOKEN or SPOTIFY_ACCESS_TOKEN.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _spotify_get_playback() -> dict[str, Any]:
    """Retrieve current Spotify player state and currently playing track."""
    response = httpx.get(
        f"{_SPOTIFY_API}/me/player",
        headers=_get_headers(),
        timeout=10.0,
    )
    if response.status_code == 204 or not response.text:
        return {"is_playing": False, "device": None, "track": None}
    response.raise_for_status()
    data = response.json()

    item = data.get("item") or {}
    artists = [a.get("name") for a in item.get("artists", [])]
    return {
        "is_playing": data.get("is_playing", False),
        "device": data.get("device", {}).get("name"),
        "progress_ms": data.get("progress_ms"),
        "track": {
            "name": item.get("name"),
            "artists": artists,
            "album": item.get("album", {}).get("name"),
            "uri": item.get("uri"),
        } if item else None,
    }


def _spotify_search(query: str = "", search_type: str = "track", limit: int = 10) -> dict[str, Any]:
    """Search Spotify for tracks, albums, artists, or playlists."""
    if not query.strip():
        raise ValueError("query cannot be empty.")
    if search_type not in {"track", "artist", "album", "playlist"}:
        raise ValueError("search_type must be track, artist, album, or playlist.")
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50.")

    params = {"q": query.strip(), "type": search_type, "limit": limit}
    response = httpx.get(
        f"{_SPOTIFY_API}/search",
        headers=_get_headers(),
        params=params,
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()

    results = []
    if search_type == "track":
        for t in data.get("tracks", {}).get("items", []):
            artists = [a.get("name") for a in t.get("artists", [])]
            results.append({
                "name": t.get("name"),
                "artists": artists,
                "album": t.get("album", {}).get("name"),
                "uri": t.get("uri"),
            })
    elif search_type == "playlist":
        for p in data.get("playlists", {}).get("items", []):
            if p:
                results.append({
                    "name": p.get("name"),
                    "owner": p.get("owner", {}).get("display_name"),
                    "uri": p.get("uri"),
                })
    elif search_type == "artist":
        for a in data.get("artists", {}).get("items", []):
            results.append({
                "name": a.get("name"),
                "genres": a.get("genres", []),
                "uri": a.get("uri"),
            })
    elif search_type == "album":
        for alb in data.get("albums", {}).get("items", []):
            artists = [a.get("name") for a in alb.get("artists", [])]
            results.append({
                "name": alb.get("name"),
                "artists": artists,
                "uri": alb.get("uri"),
            })

    return {"query": query, "type": search_type, "count": len(results), "results": results}


def _spotify_play(context_uri: str = "", uris: list[str] | None = None) -> dict[str, Any]:
    """Start or resume playback on active Spotify device."""
    payload: dict[str, Any] = {}
    if context_uri.strip():
        payload["context_uri"] = context_uri.strip()
    elif uris:
        payload["uris"] = uris

    response = httpx.put(
        f"{_SPOTIFY_API}/me/player/play",
        headers=_get_headers(),
        json=payload if payload else None,
        timeout=10.0,
    )
    if response.status_code not in {200, 204}:
        response.raise_for_status()

    return {"status": "playing", "context_uri": context_uri, "uris": uris}


def _spotify_pause() -> dict[str, Any]:
    """Pause playback on active Spotify device."""
    response = httpx.put(
        f"{_SPOTIFY_API}/me/player/pause",
        headers=_get_headers(),
        timeout=10.0,
    )
    if response.status_code not in {200, 204}:
        response.raise_for_status()

    return {"status": "paused"}


def _spotify_next_track() -> dict[str, Any]:
    """Skip to next track on active Spotify player."""
    response = httpx.post(
        f"{_SPOTIFY_API}/me/player/next",
        headers=_get_headers(),
        timeout=10.0,
    )
    if response.status_code not in {200, 204}:
        response.raise_for_status()

    return {"status": "skipped_to_next"}


# Register Spotify tools in Hands registry
if "spotify_get_playback" not in registry.REGISTRY:
    registry.register(
        {
            "name": "spotify_get_playback",
            "description": "Get current playing song, artist, album, and player state on Spotify.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "is_playing": {"type": "boolean"},
                    "device": {"type": "string"},
                    "track": {"type": "object"},
                },
            },
            "scopes": ["spotify:playback:read"],
            "tags": ["spotify", "connector", "audio", "music"],
        },
        _spotify_get_playback,
    )

if "spotify_search" not in registry.REGISTRY:
    registry.register(
        {
            "name": "spotify_search",
            "description": "Search Spotify for tracks, artists, albums, or playlists.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "search_type": {
                        "type": "string",
                        "enum": ["track", "artist", "album", "playlist"],
                        "default": "track",
                    },
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
                },
                "required": ["query"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "type": {"type": "string"},
                    "count": {"type": "integer"},
                    "results": {"type": "array"},
                },
            },
            "scopes": ["spotify:search:read"],
            "tags": ["spotify", "connector", "audio", "music"],
        },
        _spotify_search,
    )

if "spotify_play" not in registry.REGISTRY:
    registry.register(
        {
            "name": "spotify_play",
            "description": "Start or resume music playback on Spotify.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "context_uri": {"type": "string", "description": "Album or playlist URI."},
                    "uris": {"type": "array", "items": {"type": "string"}, "description": "List of track URIs."},
                },
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                },
            },
            "scopes": ["spotify:playback:write"],
            "tags": ["spotify", "connector", "audio", "music"],
        },
        _spotify_play,
    )

if "spotify_pause" not in registry.REGISTRY:
    registry.register(
        {
            "name": "spotify_pause",
            "description": "Pause music playback on Spotify.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                },
            },
            "scopes": ["spotify:playback:write"],
            "tags": ["spotify", "connector", "audio", "music"],
        },
        _spotify_pause,
    )

if "spotify_next_track" not in registry.REGISTRY:
    registry.register(
        {
            "name": "spotify_next_track",
            "description": "Skip to the next song on Spotify.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                },
            },
            "scopes": ["spotify:playback:write"],
            "tags": ["spotify", "connector", "audio", "music"],
        },
        _spotify_next_track,
    )
