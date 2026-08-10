"""Soul — Self-Learning Engine.

Passively observes interactions and builds habit patterns over time.
Runs synchronously after each chat turn (lightweight); heavy analysis
is deferred to a background scan that can run on a schedule.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime

from .. import config
from .memory import list_habits, log_interaction, upsert_habit, upsert_memory

# ─────────────────────────────────────────────────────────────────────────────
# Public API — called after every user turn
# ─────────────────────────────────────────────────────────────────────────────

def observe(text: str, device_id: str = "") -> list[dict]:
    """Log this interaction and run lightweight pattern detection. Returns list of updated habits."""
    if not config.LEARNING_ENABLED:
        return []

    now = datetime.now(UTC)
    topic = _classify_topic(text)
    intent = _classify_intent(text)

    # 1. Raw signal
    log_interaction(
        topic=topic,
        intent=intent,
        device_id=device_id,
        context={
            "hour": now.hour,
            "weekday": now.strftime("%A"),
            "text_len": len(text),
        },
    )

    updated_habits = []

    # 2. Lightweight pattern detectors (immediate)
    h1 = _detect_time_pattern(now, topic)
    if h1:
        updated_habits.append(h1)

    h2 = _detect_day_pattern(now, topic)
    if h2:
        updated_habits.append(h2)
        
    _detect_preference_signals(text) # memory updates are broadcast from api, but here they might just be logged

    return updated_habits


# ─────────────────────────────────────────────────────────────────────────────
# Pattern detectors
# ─────────────────────────────────────────────────────────────────────────────

def _detect_time_pattern(now: datetime, topic: str) -> dict | None:
    """Bucket interactions by hour-of-day + topic."""
    if not topic:
        return None
    hour_bucket = f"{now.hour:02d}:00"
    return upsert_habit(
        pattern_type="time_of_day",
        pattern_key=f"{hour_bucket}_{topic}",
        pattern_value=f"User often asks about {topic} around {hour_bucket}",
    )


def _detect_day_pattern(now: datetime, topic: str) -> dict | None:
    """Bucket interactions by day-of-week + topic."""
    if not topic:
        return None
    day_str = now.strftime("%A")
    return upsert_habit(
        pattern_type="day_of_week",
        pattern_key=f"{day_str}_{topic}",
        pattern_value=f"User often asks about {topic} on {day_str}s",
    )


_PREF_SIGNALS = [
    # (regex pattern, memory_key, value_template)
    (r"\b(short|brief|concise)\b.*answer", "response_style", "prefers concise answers"),
    (r"\b(detailed|full|long)\b.*answer", "response_style", "prefers detailed answers"),
    (r"\bbullet\b.*list", "response_format", "prefers bullet lists"),
    (r"\bdon.t (use|add) emoji", "emoji_preference", "no emoji in responses"),
    (r"\buse emoji", "emoji_preference", "use emoji in responses"),
]


def _detect_preference_signals(text: str) -> None:
    """Detect explicit style/preference signals and write them to memory."""
    lower = text.lower()
    for pattern, key, value in _PREF_SIGNALS:
        if re.search(pattern, lower):
            upsert_memory(key, value, source="learned")


# ─────────────────────────────────────────────────────────────────────────────
# Topic classifier (lightweight keyword-based; replace with LLM in Phase 3)
# ─────────────────────────────────────────────────────────────────────────────

_TOPIC_MAP = {
    "news": ["news", "headline", "latest", "today's"],
    "fitness": ["workout", "exercise", "gym", "run", "calories", "steps"],
    "productivity": ["task", "todo", "reminder", "calendar", "meeting", "schedule"],
    "music": ["music", "song", "playlist", "play", "spotify"],
    "finance": ["money", "budget", "expense", "payment", "bill"],
    "weather": ["weather", "rain", "temperature", "forecast"],
    "food": ["food", "eat", "recipe", "restaurant", "cook"],
    "coding": ["code", "bug", "debug", "python", "error", "function"],
    "home": ["light", "thermostat", "lock", "door", "home", "alarm"],
}


def _classify_topic(text: str) -> str:
    lower = text.lower()
    for topic, keywords in _TOPIC_MAP.items():
        if any(kw in lower for kw in keywords):
            return topic
    return "general"


def _classify_intent(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["set", "create", "add", "remind", "schedule"]):
        return "create"
    if any(w in lower for w in ["what", "how", "why", "tell me", "explain"]):
        return "query"
    if any(w in lower for w in ["delete", "remove", "cancel"]):
        return "delete"
    if any(w in lower for w in ["update", "change", "edit"]):
        return "update"
    return "other"


# ─────────────────────────────────────────────────────────────────────────────
# Habit summary for proactive surfacing (called by Mind)
# ─────────────────────────────────────────────────────────────────────────────

def get_proactive_context(now: datetime | None = None) -> list[str]:
    """Return habit-based suggestions relevant to current time."""
    if not config.LEARNING_ENABLED:
        return []

    now = now or datetime.now(UTC)
    hour_bucket = f"{now.hour:02d}:00"
    day = now.strftime("%A")

    habits = list_habits(active_only=True)
    suggestions: list[str] = []

    for h in habits:
        if h["confidence"] < 0.6:
            continue
        key = h["pattern_key"]
        if hour_bucket in key or day in key:
            suggestions.append(h["pattern_value"])

    return suggestions[:3]  # top 3 to avoid overwhelming the system prompt
