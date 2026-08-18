"""Fast 3-Tier CPU Intent Router (< 1ms, 0 VRAM overhead)."""
from __future__ import annotations

import re

EXACT_PREFIX_ROUTES: dict[str, list[str]] = {
    # System & Hardware
    "screenshot": ["screenshot_take"],
    "screen": ["screenshot_take"],
    "volume": ["media_volume_set", "media_volume_get"],
    "mute": ["media_mute_toggle"],
    "unmute": ["media_mute_toggle"],
    "vitals": ["system_vitals"],
    "cpu": ["system_vitals"],
    "ram": ["system_vitals"],
    "gpu": ["system_vitals"],
    "memory": ["system_vitals"],
    # Productivity & Life
    "note": ["note_create", "note_search"],
    "remember": ["note_create"],
    "remind": ["remind_create"],
    "timer": ["remind_create"],
    "alarm": ["remind_create"],
    "contact": ["contact_search", "contact_add"],
    "email": ["email_inbox", "email_send"],
    "mail": ["email_inbox", "email_send"],
    "weather": ["weather_current"],
    "news": ["news_headlines"],
    "clipboard": ["clipboard_get", "clipboard_set"],
    "code": ["dev_eval_python", "dev_run_tests", "workspace_map_tree", "file_ast_outline", "file_read_chunk", "file_edit_strict"],
    "python": ["dev_eval_python", "file_ast_outline"],
    "test": ["dev_run_tests"],
    "tree": ["workspace_map_tree"],
    "workspace": ["workspace_map_tree"],
    "outline": ["file_ast_outline"],
    "ast": ["file_ast_outline"],
    "read": ["file_read_chunk"],
    "edit": ["file_edit_strict"],
    "modify": ["file_edit_strict"],
    "patch": ["file_edit_strict"],
}

DOMAIN_SYNONYMS: dict[str, set[str]] = {
    "system": {"disk", "storage", "hardware", "temp", "battery", "performance", "taskmgr", "specs"},
    "notes": {"write", "jot", "memo", "diary", "draft", "document"},
    "calendar": {"schedule", "meeting", "event", "calendar", "agenda", "appointment"},
    "search": {"lookup", "search", "google", "online", "who is", "what is"},
    "code": {"evaluate", "execute", "run", "script", "benchmark", "pytest", "refactor", "fix", "inspect", "debug", "file", "tree", "lines", "docker", "container"},
}

DOMAIN_TOOL_CLUSTERS: dict[str, list[str]] = {
    "system": ["system_vitals"],
    "notes": ["note_create", "note_search"],
    "calendar": ["calendar_list", "calendar_add"],
    "search": ["search_web"],
    "code": ["workspace_map_tree", "file_ast_outline", "file_read_chunk", "file_edit_strict"],
}


def classify_intent_fast(user_text: str) -> list[str]:
    """Classify user query using 3-tier cascade and return active tool names."""
    clean_text = re.sub(r"[^\w\s]", "", (user_text or "").lower()).strip()
    if not clean_text:
        return []

    # Tier 1: Exact prefix lookup (< 0.5ms)
    words = clean_text.split()
    first_word = words[0] if words else ""
    if first_word in EXACT_PREFIX_ROUTES:
        return EXACT_PREFIX_ROUTES[first_word]

    # Tier 2: Tokenized set overlap (< 1ms)
    tokens = set(words)
    for domain, keywords in DOMAIN_SYNONYMS.items():
        if tokens & keywords:
            return DOMAIN_TOOL_CLUSTERS.get(domain, [])

    # Tier 3: General conversation mode (0 tools injected)
    return []
