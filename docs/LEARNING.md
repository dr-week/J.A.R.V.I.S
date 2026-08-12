# Learning Engine

## Philosophy

Jarvis observes, infers, and adapts — without being taught explicitly. The user never needs to say "remember that I...". Jarvis notices.

## What gets learned

| Signal | Example | Phase |
|--------|---------|-------|
| Time patterns | Always asks for news at 8am | 1 |
| Topic clusters | Often asks about fitness + nutrition together | 1 |
| Workflow habits | Monday = planning mode, Friday = wrap-up | 1 |
| Response style | Prefers bullet lists over paragraphs | 1 |
| App usage context | Opens Spotify → often asks for focus playlists | 2 |
| Location patterns | At gym → fitness mode auto-activates | 3 |
| Calendar-backed habits | Free Tuesday evenings = personal project time | 3 |
| Sentiment drift | Stress signals on certain days → tone adjustment | 4 |

## Architecture

```text
Interaction → Observer → Event log (SQLite)
                           ↓
                     Pattern Detector (cron/trigger)
                           ↓
                     Habit Store (memories table, type=habit)
                           ↓
                     Proactive Engine ← time/context trigger
                           ↓
                     Suggestion surfaced to user
```

## Data model

```sql
-- Interaction log (raw signal)
CREATE TABLE interaction_log (
  id INTEGER PRIMARY KEY,
  ts DATETIME NOT NULL,
  topic TEXT,
  intent TEXT,
  device_id TEXT,
  context_json TEXT
);

-- Learned habits (structured patterns)
CREATE TABLE habits (
  id INTEGER PRIMARY KEY,
  pattern_type TEXT,        -- 'time_of_day', 'day_of_week', 'topic_cluster'
  pattern_key TEXT,
  pattern_value TEXT,
  confidence REAL DEFAULT 0.5,
  last_seen DATETIME,
  created_at DATETIME,
  active INTEGER DEFAULT 1
);
```

## Confidence model

- Pattern needs ≥3 occurrences before stored as habit (confidence = 0.5)
- Confidence grows with repetition (max 1.0), decays with absence
- Habits below 0.2 confidence are archived, not deleted

## Proactive triggers

- **Time trigger**: fires at learned time ± 15 min window
- **Context trigger**: device event (app open, location) matches pattern
- **User-dismissable**: one dismiss drops confidence −0.2; two dismisses archives habit

**Implemented (Phase 1 exit):** `learner.get_proactive_context()` injects matching habits
(confidence ≥ 0.6) into the Mind system prompt via `persona.build_system_prompt()` under
“Proactive suggestions”. Memories upserted via `/soul/memories` are always injected
(cross-session / cross-device = same brain SQLite — ISSUE-022 LWW sync).

## Privacy

- All learning data stays on the brain (never sent to LLM provider raw)
- User can export, inspect, and delete any habit via `/soul/habits` API
- Learning can be disabled: `LEARNING_ENABLED=false`

## Phase rollout

| Phase | Learning feature |
|-------|------------------|
| 1 | Interaction log + basic time/topic pattern detector |
| 2 | App/device context signals |
| 3 | Calendar + location-backed habits |
| 4 | Voice tone + sentiment signals |
| 5 | Cross-room presence patterns |


**Note**: Phase 1 (Interaction log + basic time/topic pattern detector) is fully complete and wired into the system prompt.
