"""LiteLLM Unified Model Gateway Plugin.

Enables unified multi-provider routing and automatic fallback across Gemini, OpenAI,
and Ollama endpoints using LiteLLM (Pattern 1: 3-line PyPI wrapper) per docs/OSS.md
and docs/GITHUB_INTEGRATIONS.md.
"""
from __future__ import annotations

import os
from typing import Any
from backend.app.hands import registry

try:
    import litellm

    litellm.telemetry = False
    litellm.suppress_debug_info = True
    _HAS_LITELLM = True
except ImportError:
    litellm = None  # type: ignore[assignment]
    _HAS_LITELLM = False

DEFAULT_FALLBACK_MODELS: list[str] = [
    "gemini/gemini-2.0-flash",
    "openai/gpt-4o-mini",
    "ollama/llama3",
]


def _resolve_provider_credentials(
    model_name: str,
    api_base: str = "",
    api_key: str = "",
) -> tuple[str, str, str]:
    """Resolve provider, API key, and base URL for a given model target."""
    model_lower = model_name.lower()

    # 1. Identify provider
    provider = "generic"
    if model_lower.startswith("gemini/") or "gemini" in model_lower:
        provider = "gemini"
    elif (
        model_lower.startswith("openai/")
        or model_lower.startswith("gpt-")
        or model_lower.startswith("o1")
        or model_lower.startswith("o3")
    ):
        provider = "openai"
    elif model_lower.startswith("ollama/") or model_lower.startswith("ollama_chat/"):
        provider = "ollama"

    # 2. Resolve API Key
    resolved_key = (
        api_key
        or os.environ.get("JARVIS_LITELLM_API_KEY", "")
        or os.environ.get("JARVIS_LLM_API_KEY", "")
    )
    if not resolved_key:
        if provider == "gemini":
            resolved_key = os.environ.get("GEMINI_API_KEY", "")
        elif provider == "openai":
            resolved_key = os.environ.get("OPENAI_API_KEY", "")

    # 3. Resolve Base URL
    resolved_base = (
        api_base
        or os.environ.get("JARVIS_LITELLM_BASE_URL", "")
        or os.environ.get("JARVIS_LLM_BASE_URL", "")
    )
    if not resolved_base and provider == "ollama":
        resolved_base = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")

    return provider, resolved_key, resolved_base


def litellm_completion(
    prompt: str = "",
    messages: list[dict[str, Any]] | None = None,
    model: str = "",
    fallback_models: list[str] | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    api_base: str = "",
    api_key: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate unified completions with fallback routing across Gemini, OpenAI, and Ollama.

    Follows Pattern 1: 3-line PyPI Wrapper per docs/OSS.md.
    """
    clean_prompt = (prompt or "").strip()
    if not clean_prompt and not messages:
        return {"error": "Completion requires non-empty 'prompt' or 'messages' list."}

    if not _HAS_LITELLM or litellm is None:
        return {
            "status": "uninitialized",
            "error": "LiteLLM is not installed. Run: pip install litellm",
            "message": "litellm package missing from Python environment.",
            "prompt": clean_prompt,
        }

    # Prepare message list
    formatted_messages: list[dict[str, Any]]
    if messages:
        formatted_messages = messages
    else:
        formatted_messages = [{"role": "user", "content": clean_prompt}]

    # Determine candidate model sequence
    primary_model = (
        model
        or os.environ.get("JARVIS_LITELLM_MODEL", "")
        or os.environ.get("JARVIS_LLM_MODEL", "")
        or DEFAULT_FALLBACK_MODELS[0]
    )

    candidate_models: list[str] = [primary_model]
    fallbacks = fallback_models if fallback_models is not None else DEFAULT_FALLBACK_MODELS
    for fb in fallbacks:
        if fb and fb not in candidate_models:
            candidate_models.append(fb)

    attempted_models: list[str] = []
    errors: list[str] = []

    for candidate in candidate_models:
        attempted_models.append(candidate)
        provider, cand_key, cand_base = _resolve_provider_credentials(
            candidate, api_base=api_base, api_key=api_key
        )

        call_kwargs: dict[str, Any] = {
            "model": candidate,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        if cand_key:
            call_kwargs["api_key"] = cand_key
        if cand_base:
            call_kwargs["api_base"] = cand_base

        try:
            response = litellm.completion(**call_kwargs)
            content = ""
            if hasattr(response, "choices") and response.choices:
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    content = choice.message.content or ""
                elif isinstance(choice, dict):
                    content = choice.get("message", {}).get("content", "")

            usage_dict = {}
            if hasattr(response, "usage") and response.usage:
                usage = response.usage
                usage_dict = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage, "completion_tokens", 0),
                    "total_tokens": getattr(usage, "total_tokens", 0),
                }

            return {
                "status": "success",
                "content": content,
                "model": candidate,
                "provider": provider,
                "usage": usage_dict,
                "fallbacks_attempted": attempted_models,
            }
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")

    return {
        "status": "error",
        "error": f"LiteLLM completion failed for all candidate models: {'; '.join(errors)}",
        "fallbacks_attempted": attempted_models,
    }


if "litellm_completion" not in registry.REGISTRY:
    registry.register(
        {
            "name": "litellm_completion",
            "description": (
                "Execute unified LLM completions with automatic fallback routing across "
                "Gemini, OpenAI, and Ollama using LiteLLM (Zero-Code PyPI wrapper)."
            ),
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "User prompt text for the LLM.",
                    },
                    "messages": {
                        "type": "array",
                        "description": "Optional list of message objects [{'role': 'user', 'content': '...'}].",
                    },
                    "model": {
                        "type": "string",
                        "description": "Primary model name (e.g. 'gemini/gemini-2.0-flash', 'gpt-4o-mini', 'ollama/llama3').",
                    },
                    "fallback_models": {
                        "type": "array",
                        "description": "Ordered list of fallback model names to attempt if the primary fails.",
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Sampling temperature (default 0.7).",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Max completion tokens to generate (default 1024).",
                    },
                    "api_base": {
                        "type": "string",
                        "description": "Optional custom API base URL override.",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional API key override.",
                    },
                },
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "content": {"type": "string"},
                    "model": {"type": "string"},
                    "provider": {"type": "string"},
                    "usage": {"type": "object"},
                    "fallbacks_attempted": {"type": "array"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["llm:complete", "llm:gateway"],
            "tags": ["llm", "litellm", "gateway", "zero-code", "routing", "fallback"],
        },
        litellm_completion,
    )
