"""AnythingLLM RAG Knowledge Base Plugin Facade.

Enables full RAG capabilities (document ingestion, vector search, chunking, workspace chat)
via self-hosted AnythingLLM Docker sidecar or REST endpoint.
"""
from __future__ import annotations

from .client import (
    ANYTHINGLLM_DEFAULT_URL,
    ANYTHINGLLM_DEFAULT_WORKSPACE,
    get_base_url as _get_base_url,
    get_api_key as _get_api_key,
    get_workspace as _get_workspace,
    build_headers as _build_headers,
)
from .tools import (
    anythingllm_query,
    anythingllm_upload_doc,
    register_anythingllm_tools,
)

# Auto-register tools upon package import
register_anythingllm_tools()

__all__ = [
    "ANYTHINGLLM_DEFAULT_URL",
    "ANYTHINGLLM_DEFAULT_WORKSPACE",
    "_get_base_url",
    "_get_api_key",
    "_get_workspace",
    "_build_headers",
    "anythingllm_query",
    "anythingllm_upload_doc",
    "register_anythingllm_tools",
]
