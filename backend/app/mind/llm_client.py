"""LLM connection config: base URL and auth headers.

Single responsibility: resolve where the local LLM endpoint lives and
format the Authorization header. Nothing else.
"""
from __future__ import annotations

from .. import config


def base_url() -> str:
    """Resolve the OpenAI-compatible /v1 base URL from config."""
    raw = (config.LLM_BASE_URL or "").rstrip("/")
    if not raw:
        # LM Studio default
        return "http://127.0.0.1:1234/v1"
    if raw.endswith("/v1"):
        return raw
    return f"{raw}/v1"


def auth_headers() -> dict[str, str]:
    """Return Authorization + Content-Type headers for the LLM API."""
    key = config.LLM_API_KEY or "lm-studio"
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
