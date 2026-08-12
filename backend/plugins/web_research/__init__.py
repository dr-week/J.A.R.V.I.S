"""Jarvis Web Research Plugin using crawl4ai.

This plugin enables Jarvis to scrape web pages and extract clean, LLM-ready
markdown using the async crawl4ai library.
"""
from __future__ import annotations

import asyncio
from typing import Any

from app.hands import registry


async def _web_scrape(url: str) -> dict[str, Any]:
    """Scrape a webpage and return its content as Markdown."""
    try:
        from crawl4ai import AsyncWebCrawler
    except ImportError:
        return {"error": "crawl4ai is not installed. Run: uv add crawl4ai"}

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                word_count_threshold=10,
                bypass_cache=True,
                remove_overlay_elements=True,
            )
            if not result.success:
                return {"error": f"Failed to crawl {url}: {result.error_message}"}
            
            # The markdown might be long, so we take the first 10,000 chars to avoid token limits
            md = result.markdown
            if md and len(md) > 10000:
                md = md[:10000] + "\n...[Content Truncated]..."
                
            return {
                "url": result.url,
                "markdown": md,
                "media": len(result.media) if hasattr(result, "media") else 0,
            }
    except Exception as exc:
        return {"error": f"Crawl failed: {exc}"}

registry.register(
    {
        "name": "web_scrape",
        "description": "Scrape a webpage and return its content as clean Markdown using crawl4ai.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to scrape"},
            },
            "required": ["url"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "markdown": {"type": "string"},
                "error": {"type": "string"}
            }
        },
        "scopes": ["web:read"],
        "tags": ["research", "web"],
    },
    _web_scrape,
)
