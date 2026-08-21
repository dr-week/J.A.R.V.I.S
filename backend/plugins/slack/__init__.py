"""Slack Communications Connector Plugin (Phase 3+).

Provides clean, non-monolithic Slack workspace integration for CoreBrain.
Supports sending messages, querying channels, fetching conversation history, and incoming webhook triggers.

Architecture & Security Rationale:
- Token is read brain-locally from `JARVIS_SLACK_BOT_TOKEN` or `SLACK_BOT_TOKEN`.
- Webhooks can be triggered directly or via `JARVIS_SLACK_WEBHOOK_URL`.
- Sensitive bot tokens are never passed through LLM tool arguments or returned in audit payloads.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from backend.app.hands import registry

_SLACK_API = "https://slack.com/api"


def _token() -> str:
    """Retrieve Slack Bot token from environment variables."""
    return (os.environ.get("JARVIS_SLACK_BOT_TOKEN") or os.environ.get("SLACK_BOT_TOKEN") or "").strip()


def _default_webhook_url() -> str:
    """Retrieve default Slack Webhook URL if configured."""
    return (os.environ.get("JARVIS_SLACK_WEBHOOK_URL") or os.environ.get("SLACK_WEBHOOK_URL") or "").strip()


def _get_headers() -> dict[str, str]:
    """Construct Slack REST API headers with bearer token."""
    token = _token()
    if not token:
        raise RuntimeError("Slack is not configured. Set JARVIS_SLACK_BOT_TOKEN or SLACK_BOT_TOKEN.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }


def _slack_post_message(channel: str = "", text: str = "") -> dict[str, Any]:
    """Post a message to a Slack channel or conversation ID."""
    if not channel.strip():
        raise ValueError("channel cannot be empty (e.g. '#general' or channel ID).")
    if not text.strip():
        raise ValueError("text cannot be empty.")

    payload = {"channel": channel.strip(), "text": text.strip()}
    response = httpx.post(
        f"{_SLACK_API}/chat.postMessage",
        headers=_get_headers(),
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack API error: {data.get('error', 'unknown')}")

    return {
        "status": "sent",
        "channel": channel,
        "ts": data.get("ts"),
        "message": text,
    }


def _slack_list_channels(types: str = "public_channel,private_channel", limit: int = 50) -> dict[str, Any]:
    """List public and private channels in the Slack workspace."""
    if not 1 <= limit <= 200:
        raise ValueError("limit must be between 1 and 200.")

    params = {"types": types, "limit": limit, "exclude_archived": "true"}
    response = httpx.get(
        f"{_SLACK_API}/conversations.list",
        headers=_get_headers(),
        params=params,
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack API error: {data.get('error', 'unknown')}")

    channels = [
        {
            "id": ch.get("id"),
            "name": ch.get("name"),
            "is_private": ch.get("is_private", False),
            "num_members": ch.get("num_members", 0),
            "topic": ch.get("topic", {}).get("value", ""),
        }
        for ch in data.get("channels", [])
    ]
    return {"count": len(channels), "channels": channels}


def _slack_get_history(channel: str = "", limit: int = 20) -> dict[str, Any]:
    """Retrieve recent message history from a channel."""
    if not channel.strip():
        raise ValueError("channel ID cannot be empty.")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")

    params = {"channel": channel.strip(), "limit": limit}
    response = httpx.get(
        f"{_SLACK_API}/conversations.history",
        headers=_get_headers(),
        params=params,
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack API error: {data.get('error', 'unknown')}")

    messages = [
        {
            "user": msg.get("user", "bot"),
            "text": msg.get("text", ""),
            "ts": msg.get("ts"),
        }
        for msg in data.get("messages", [])
    ]
    return {"channel": channel, "count": len(messages), "messages": messages}


def _slack_send_webhook(webhook_url: str = "", text: str = "") -> dict[str, Any]:
    """Send an alert or message payload directly to a Slack Incoming Webhook."""
    target_url = (webhook_url or _default_webhook_url()).strip()
    if not target_url or not target_url.startswith("https://hooks.slack.com/"):
        raise ValueError("A valid Slack webhook URL (https://hooks.slack.com/...) is required.")
    if not text.strip():
        raise ValueError("text cannot be empty.")

    payload = {"text": text.strip()}
    response = httpx.post(
        target_url,
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    return {"status": "dispatched", "message": text}


# Register Slack tools in Hands registry
if "slack_post_message" not in registry.REGISTRY:
    registry.register(
        {
            "name": "slack_post_message",
            "description": "Send a message to a Slack channel or conversation ID.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Target channel name or ID (e.g., 'C12345678')."},
                    "text": {"type": "string", "description": "Message text to post."},
                },
                "required": ["channel", "text"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "channel": {"type": "string"},
                    "ts": {"type": "string"},
                },
            },
            "scopes": ["slack:chat:write"],
            "tags": ["slack", "connector", "comms"],
        },
        _slack_post_message,
    )

if "slack_list_channels" not in registry.REGISTRY:
    registry.register(
        {
            "name": "slack_list_channels",
            "description": "List conversations and channels in the Slack workspace.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "types": {"type": "string", "default": "public_channel,private_channel"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
                },
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "channels": {"type": "array"},
                },
            },
            "scopes": ["slack:channels:read"],
            "tags": ["slack", "connector", "comms"],
        },
        _slack_list_channels,
    )

if "slack_get_history" not in registry.REGISTRY:
    registry.register(
        {
            "name": "slack_get_history",
            "description": "Fetch recent message history from a Slack channel.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel ID."},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                },
                "required": ["channel"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "count": {"type": "integer"},
                    "messages": {"type": "array"},
                },
            },
            "scopes": ["slack:history:read"],
            "tags": ["slack", "connector", "comms"],
        },
        _slack_get_history,
    )

if "slack_send_webhook" not in registry.REGISTRY:
    registry.register(
        {
            "name": "slack_send_webhook",
            "description": "Send a direct message payload to a Slack Incoming Webhook URL.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "webhook_url": {"type": "string", "description": "Optional incoming webhook URL."},
                    "text": {"type": "string", "description": "Message content."},
                },
                "required": ["text"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
            "scopes": ["slack:webhook:write"],
            "tags": ["slack", "connector", "notifications"],
        },
        _slack_send_webhook,
    )
