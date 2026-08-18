"""Soul store — user memories (LWW v1)."""
from __future__ import annotations

from typing import Any

from ..db import _db, _utc


def upsert_memory(
    key: str,
    value: str,
    source: str = "explicit",
    device_id: str = "",
    updated_at: str | None = None,
) -> bool:
    ts = updated_at or _utc()
    with _db() as conn:
        existing = conn.execute(
            "SELECT updated_at FROM memories WHERE key=?", (key,)
        ).fetchone()
        if existing:
            if ts <= existing["updated_at"]:
                return False
            conn.execute(
                """UPDATE memories SET value=?, source=?, updated_at=?, device_id=?
                   WHERE key=?""",
                (value, source, ts, device_id, key),
            )
            return True
        conn.execute(
            """INSERT INTO memories(key,value,source,updated_at,device_id)
               VALUES(?,?,?,?,?)""",
            (key, value, source, ts, device_id),
        )
        return True


def get_memory(key: str) -> str | None:
    with _db() as conn:
        row = conn.execute("SELECT value FROM memories WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None


def list_memories() -> list[dict[str, Any]]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT key, value, source, updated_at FROM memories ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_memory(key: str) -> bool:
    with _db() as conn:
        cur = conn.execute("DELETE FROM memories WHERE key=?", (key,))
        return cur.rowcount > 0


def search_semantic_memories(query: str, limit: int = 3) -> list[dict[str, Any]]:
    """Retrieve top-K relevant memories using native SQLite FTS5 BM25 ranking."""
    import re
    # Strip FTS5 operators and reserved punctuation: * ( ) [ ] { } " ^ ~ :
    clean_query = re.sub(r'[\*\(\)\[\]\{\}\"\^\~\:\']', '', (query or "").lower()).strip()
    if not clean_query:
        return []

    reserved = {"and", "or", "not", "near"}
    terms = [f'"{t}"*' for t in clean_query.split() if len(t) > 1 and t not in reserved]
    if not terms:
        return []

    fts_query = " OR ".join(terms)

    with _db() as conn:
        try:
            sql = """
                SELECT m.key, m.value, m.source, m.updated_at, bm25(memories_fts, 2.5, 1.0) AS rank
                FROM memories_fts f
                JOIN memories m ON m.id = f.rowid
                WHERE memories_fts MATCH ?
                ORDER BY rank ASC, m.updated_at DESC
                LIMIT ?
            """
            rows = conn.execute(sql, (fts_query, limit)).fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["relevance_score"] = round(abs(float(item.pop("rank", 1.0))), 2)
                results.append(item)
            if results:
                return results
        except Exception:
            pass

    # Fallback to in-memory scanning if FTS5 query encounters any issue
    query_terms = [t for t in clean_query.split() if len(t) > 1]
    all_mems = list_memories()
    scored_mems = []

    for mem in all_mems:
        key_text = str(mem.get("key", "")).lower()
        val_text = str(mem.get("value", "")).lower()

        score = 0.0
        for term in query_terms:
            if term in key_text:
                score += 3.0
            if term in val_text:
                score += 1.0

        if score > 0:
            mem_item = dict(mem)
            mem_item["relevance_score"] = round(score, 2)
            scored_mems.append(mem_item)

    scored_mems.sort(key=lambda x: (x["relevance_score"], x.get("updated_at", "")), reverse=True)
    return scored_mems[:limit]

