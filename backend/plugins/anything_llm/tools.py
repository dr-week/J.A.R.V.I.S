"""AnythingLLM tool registration functions."""
from __future__ import annotations

from typing import Any
from backend.app.hands import registry
from .client import (
    execute_query,
    execute_upload,
    get_base_url,
    get_api_key,
    get_workspace,
    build_headers,
)

# Function signatures for backwards compatibility
async def anythingllm_query(
    query: str,
    workspace: str = "",
    mode: str = "query",
    url: str = "",
    api_key: str = "",
    timeout: float = 10.0,
) -> dict[str, Any]:
    return await execute_query(query, workspace, mode, url, api_key, timeout)


async def anythingllm_upload_doc(
    file_path: str = "",
    text_content: str = "",
    doc_name: str = "",
    workspace: str = "",
    url: str = "",
    api_key: str = "",
    timeout: float = 30.0,
) -> dict[str, Any]:
    return await execute_upload(file_path, text_content, doc_name, workspace, url, api_key, timeout)


def register_anythingllm_tools() -> None:
    """Register AnythingLLM RAG tools into the Hands registry."""
    if "anythingllm_query" not in registry.REGISTRY:
        registry.register(
            {
                "name": "anythingllm_query",
                "description": (
                    "Query self-hosted AnythingLLM RAG knowledge base sidecar for document retrieval and context."
                ),
                "version": "1.0.0",
                "phase": 3,
                "risk_level": "auto",
                "executor": "brain",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Question or search query for the RAG knowledge base.",
                        },
                        "workspace": {
                            "type": "string",
                            "description": "Target AnythingLLM workspace slug (default: ''default'').",
                        },
                        "mode": {
                            "type": "string",
                            "description": "Query mode: ''query'' (pure RAG context) or ''chat'' (conversational).",
                        },
                        "url": {
                            "type": "string",
                            "description": "Optional custom AnythingLLM base URL override.",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "Optional custom AnythingLLM API key override.",
                        },
                    },
                    "required": ["query"],
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "query": {"type": "string"},
                        "workspace": {"type": "string"},
                        "mode": {"type": "string"},
                        "response": {"type": "string"},
                        "sources": {"type": "array"},
                        "error": {"type": "string"},
                    },
                },
                "scopes": ["rag:read", "knowledge:read"],
                "tags": ["rag", "anythingllm", "knowledge_base", "documents", "zero-code"],
            },
            anythingllm_query,
        )

    if "anythingllm_upload_doc" not in registry.REGISTRY:
        registry.register(
            {
                "name": "anythingllm_upload_doc",
                "description": (
                    "Upload or ingest a document/text into self-hosted AnythingLLM RAG knowledge base sidecar."
                ),
                "version": "1.0.0",
                "phase": 3,
                "risk_level": "confirm_once",
                "executor": "brain",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Local file path to document to upload (PDF, TXT, MD, DOCX, etc.).",
                        },
                        "text_content": {
                            "type": "string",
                            "description": "Raw text content to ingest into the knowledge base directly.",
                        },
                        "doc_name": {
                            "type": "string",
                            "description": "Document name or title (e.g. ''manual.txt'').",
                        },
                        "workspace": {
                            "type": "string",
                            "description": "Target AnythingLLM workspace slug (default: ''default'').",
                        },
                        "url": {
                            "type": "string",
                            "description": "Optional custom AnythingLLM base URL override.",
                        },
                        "api_key": {
                            "type": "string",
                            "description": "Optional custom AnythingLLM API key override.",
                        },
                    },
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "workspace": {"type": "string"},
                        "doc_name": {"type": "string"},
                        "response": {"type": "object"},
                        "error": {"type": "string"},
                    },
                },
                "scopes": ["rag:write", "knowledge:write"],
                "tags": ["rag", "anythingllm", "knowledge_base", "documents", "zero-code"],
            },
            anythingllm_upload_doc,
        )
