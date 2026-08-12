"""News plugin — RSS feed aggregation via feedparser.

Stores feed URLs in SQLite. Fetches headlines on demand.
Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime
from typing import Any

from backend.app.config import DB_PATH
from backend.app.hands import registry

try:
    import feedparser
    _HAS_FEEDPARSER = True
except ImportError:
    _HAS_FEEDPARSER = False

_DEFAULT_FEEDS = [
    ("BBC News", "https://feeds.bbci.co.uk/news/rss.xml"),
    ("Reuters", "https://www.rss-bridge.org/bridge01/?action=display&bridge=Reuters&topic=world&format=Atom"),
    ("Hacker News", "https://hnrss.org/frontpage"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
]


def _connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS news_feeds (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )"""
    )
    # Seed defaults if table is empty
    count = conn.execute("SELECT COUNT(*) FROM news_feeds").fetchone()[0]
    if count == 0:
        now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        for name, url in _DEFAULT_FEEDS:
            conn.execute(
                "INSERT OR IGNORE INTO news_feeds (id, name, url, created_at) VALUES (?, ?, ?, ?)",
                (uuid.uuid4().hex[:12], name, url, now),
            )
        conn.commit()
    return conn


def _news_headlines(limit: int = 10) -> dict[str, Any]:
    """Fetch headlines from all configured RSS feeds."""
    if not _HAS_FEEDPARSER:
        return {"error": "feedparser not installed. Run: pip install feedparser"}
    with closing(_connection()) as conn:
        feeds = [dict(r) for r in conn.execute("SELECT * FROM news_feeds").fetchall()]
    all_items: list[dict[str, str]] = []
    for feed_row in feeds:
        try:
            parsed = feedparser.parse(feed_row["url"])
            for entry in parsed.entries[:5]:  # max 5 per feed
                all_items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "source": feed_row["name"],
                    "published": entry.get("published", ""),
                })
        except Exception:
            continue
    # Sort by published if available, return top N
    all_items = all_items[:limit]
    return {"count": len(all_items), "headlines": all_items}


def _news_search(query: str, limit: int = 10) -> dict[str, Any]:
    """Search headlines by keyword across all feeds."""
    if not _HAS_FEEDPARSER:
        return {"error": "feedparser not installed. Run: pip install feedparser"}
    result = _news_headlines(limit=100)
    if "error" in result:
        return result
    q = query.lower().strip()
    matched = [h for h in result["headlines"] if q in h["title"].lower()][:limit]
    return {"count": len(matched), "query": query, "headlines": matched}


def _news_add_feed(name: str, url: str) -> dict[str, Any]:
    """Add a new RSS feed URL."""
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    feed = {"id": uuid.uuid4().hex[:12], "name": name.strip(), "url": url.strip(), "created_at": now}
    with closing(_connection()) as conn:
        with conn:
            conn.execute(
                "INSERT INTO news_feeds (id, name, url, created_at) VALUES(:id, :name, :url, :created_at)",
                feed,
            )
    return feed


# ── Register ────────────────────────────────────────────────────

registry.register(
    {
        "name": "news_headlines", "description": "Fetch latest news headlines from configured RSS feeds.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "headlines": {"type": "array"}}},
        "scopes": ["news:read"], "tags": ["information", "news"],
    }, _news_headlines,
)

registry.register(
    {
        "name": "news_search", "description": "Search news headlines by keyword.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}, "limit": {"type": "integer"},
        }, "required": ["query"]},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "headlines": {"type": "array"}}},
        "scopes": ["news:read"], "tags": ["information", "news"],
    }, _news_search,
)

registry.register(
    {
        "name": "news_add_feed", "description": "Add a new RSS feed URL for news aggregation.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string"}, "url": {"type": "string"},
        }, "required": ["name", "url"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "name": {"type": "string"}}},
        "scopes": ["news:write"], "tags": ["information", "news"],
    }, _news_add_feed,
)
