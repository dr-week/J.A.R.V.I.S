"""Soul — Persona loader.

Builds the system prompt from:
  1. Persona defaults (aligned with docs/PERSONA.md) + runtime name
  2. Injected memories (all key/value pairs)
  3. Active habits (top-10 by confidence)
  4. Proactive habit suggestions (time/day match, confidence ≥ 0.6)
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import config
from .learner import get_proactive_context
from .memory import get_config, list_habits, list_memories


@dataclass(frozen=True)
class PersonaProfile:
    """Static persona baseline — mirrors docs/PERSONA.md."""

    role: str = "Close personal operator — not a corporate helpdesk"
    tone: str = (
        "Capable, concise, lightly dry humour. Never servile, never cruel."
    )
    rules: tuple[str, ...] = (
        "Prefer action with confirmation when risk is non-trivial.",
        "Remember preferences; ask once, then reuse.",
        "Say what you did, what failed, and what's next — no fake success.",
        "Do not lecture when a tool can finish the job.",
        "Never pretend to be human.",
        "Never claim capabilities that tools cannot perform.",
        "In shared rooms, do not volunteer sensitive data aloud.",
    )
    trust_summary: str = (
        "Ask always: send messages, payments, unlocks, deletes. "
        "Ask once then allow: calendar, reminders, routine home scenes. "
        "Auto: read-only lookups, list/search, status."
    )


DEFAULT_PERSONA = PersonaProfile()

_SYSTEM_TEMPLATE = """\
You are {name}, {role}

Tone: {tone}

Behaviour rules:
{rules_block}

Trust levels: {trust_summary}

{memory_block}
{habits_block}
{proactive_block}
"""

_MEMORY_HEADER = "## What you know about the user"
_HABITS_HEADER = "## Learned patterns (habits)"
_PROACTIVE_HEADER = "## Proactive suggestions (act if relevant — do not force)"


def get_persona_profile() -> PersonaProfile:
    """Return baseline persona (env/DB may override name separately)."""
    return DEFAULT_PERSONA


def get_assistant_name() -> str:
    """Runtime name — DB override takes precedence over env."""
    return get_config("assistant_name") or config.ASSISTANT_NAME


def build_system_prompt() -> str:
    name = get_assistant_name()
    profile = get_persona_profile()

    memories = list_memories()
    if memories:
        mem_lines = "\n".join(f"- {m['key']}: {m['value']}" for m in memories)
        memory_block = f"{_MEMORY_HEADER}\n{mem_lines}"
    else:
        memory_block = ""

    habits = list_habits(active_only=True)[:10]
    if habits:
        hab_lines = "\n".join(
            f"- [{h['pattern_type']}] {h['pattern_key']} → {h['pattern_value']} "
            f"(confidence {h['confidence']:.0%})"
            for h in habits
        )
        habits_block = f"{_HABITS_HEADER}\n{hab_lines}"
    else:
        habits_block = ""

    proactive = get_proactive_context()
    if proactive:
        pro_lines = "\n".join(f"- {s}" for s in proactive)
        proactive_block = f"{_PROACTIVE_HEADER}\n{pro_lines}"
    else:
        proactive_block = ""

    rules_block = "\n".join(f"- {r}" for r in profile.rules)

    return _SYSTEM_TEMPLATE.format(
        name=name,
        role=profile.role,
        tone=profile.tone,
        rules_block=rules_block,
        trust_summary=profile.trust_summary,
        memory_block=memory_block,
        habits_block=habits_block,
        proactive_block=proactive_block,
    ).strip()
