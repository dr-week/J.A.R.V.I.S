"""Jarvis Windows Client — voice helpers (STT + TTS).

Provides offline-friendly speech-to-text and text-to-speech wrappers with
graceful fallback when optional dependencies (pyttsx3, speech_recognition) or
a microphone are unavailable.

Used by ISSUE-050 (STT and TTS on one client).
"""
from __future__ import annotations

import os
from typing import Callable

# Optional imports — each is guarded so the client still works without voice.
try:
    import pyttsx3
    _TTS = True
except ImportError:  # pragma: no cover
    _TTS = False

try:
    import speech_recognition as sr
    _STT = True
except ImportError:  # pragma: no cover
    _STT = False


# ─────────────────────────────────────────────────────────────────────────────
# TTS
# ─────────────────────────────────────────────────────────────────────────────

def tts_available() -> bool:
    """True if a text-to-speech engine could be initialized."""
    return _TTS


def speak(
    text: str,
    *,
    rate: int = 180,
    on_status: Callable[[str], None] | None = None,
) -> bool:
    """Speak `text` aloud using an offline TTS engine.

    Returns True if the text was actually spoken, False if TTS is unavailable.
    Falls back to printing the text if the engine cannot be started.
    """
    if not text.strip():
        return False
    if not tts_available():
        if on_status:
            on_status("[voice: pyttsx3 not installed, text only]")
        print("\n[voice] (TTS unavailable — replying as text)", flush=True)
        print(text)
        return False
    try:
        if on_status:
            on_status("[voice: speaking…]")
        engine = pyttsx3.init()
        try:
            engine.setProperty("rate", rate)
            engine.say(text)
            engine.runAndWait()
        finally:
            try:
                engine.stop()
            except Exception:  # pragma: no cover
                pass
        return True
    except Exception as exc:  # noqa: BLE001
        if on_status:
            on_status(f"[voice: TTS error {exc!r}, text only]")
        print(f"\n[voice] TTS error ({exc}) — replying as text", flush=True)
        print(text)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# STT
# ─────────────────────────────────────────────────────────────────────────────

def stt_available() -> bool:
    """True if speech recognition could be initialized."""
    return _STT


def listen(
    *,
    timeout: float = 5.0,
    phrase_time_limit: float | None = 15.0,
    energy_threshold: int = 300,
    on_status: Callable[[str], None] | None = None,
    recognizer: str | None = None,
) -> str:
    """Capture one spoken turn from the default microphone and return text.

    `recognizer`: optional override, e.g. "google" or "sphinx". When None,
    picks the first available recognizer (prefers Google's free network
    recognizer, then offline Sphinx).

    Returns the transcribed text, or "" if speech was not understood.
    """
    if not stt_available():
        if on_status:
            on_status("[voice: speech_recognition not installed]")
        print("[voice] speech_recognition not installed — install to use STT.", flush=True)
        return ""

    mic = None
    try:
        mic = sr.Microphone()
    except (OSError, AttributeError, ImportError) as exc:  # noqa: BLE001
        if on_status:
            on_status(f"[voice: no microphone ({exc})]")
        print(f"[voice] No microphone available ({exc})", flush=True)
        return ""

    if on_status:
        on_status("🎙️ listening…")

    r = sr.Recognizer()
    r.energy_threshold = energy_threshold
    r.dynamic_energy_threshold = True

    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        if on_status:
            on_status("[voice: timeout, no speech detected]")
        print("[voice] No speech detected (timeout).", flush=True)
        return ""
    except Exception as exc:  # noqa: BLE001
        if on_status:
            on_status(f"[voice: listen error {exc!r}]")
        print(f"[voice] Could not listen: {exc}", flush=True)
        return ""

    if on_status:
        on_status("🧠 transcribing…")

    engines: list[tuple[str, Callable[[sr.AudioData], str]]] = []
    if recognizer:
        engines.append((recognizer, _recognizer_fn(r, recognizer)))
    else:
        # Prefer network-free fallback ordering: google free, then sphinx.
        engines = [
            ("google", _recognizer_fn(r, "google")),
            ("sphinx", _recognizer_fn(r, "sphinx")),
        ]

    for name, fn in engines:
        try:
            text = fn(audio)
            text = (text or "").strip()
            if text:
                return text
        except sr.UnknownValueError:
            continue  # try next engine
        except sr.RequestError as exc:  # noqa: BLE001
            # Google network request failed — try offline engine next.
            if on_status:
                on_status(f"[voice: {name} request failed ({exc}); retrying offline]")
            continue
        except Exception:  # noqa: BLE001
            continue

    if on_status:
        on_status("[voice: could not understand audio]")
    print("[voice] Sorry, I could not understand that.", flush=True)
    return ""


def _recognizer_fn(r: sr.Recognizer, name: str) -> Callable[[sr.AudioData], str]:
    if name == "google":
        return r.recognize_google
    return r.recognize_sphinx  # offline (requires pocketsphinx)


# ─────────────────────────────────────────────────────────────────────────────
# Wake word (ISSUE-052)
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULT_WAKE_WORD = "jarvis"


def wake_word_available() -> bool:
    """True if a microphone + STT are available so the wake loop can run."""
    return stt_available()


def _match_wake_word(text: str, wake_word: str) -> bool:
    """True if `wake_word` appears as a whole word (case-insensitive) in text."""
    import re

    if not text.strip():
        return False
    pattern = rf"(?<![a-z0-9]){re.escape(wake_word.lower())}(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None


def listen_for_wake_word(
    wake_word: str = _DEFAULT_WAKE_WORD,
    *,
    timeout: float = 5.0,
    phrase_time_limit: float | None = 3.0,
    energy_threshold: int = 300,
    on_status: Callable[[str], None] | None = None,
) -> bool:
    """Block until the wake phrase is heard, then return True.

    Uses the same `listen()` STT path as ISSUE-050 but inspects each captured
    phrase for the configured wake word. If the user does not say the phrase,
    it keeps listening. This is an *opt-in* loop — it only runs when the caller
    enables a wake-word session (e.g. via the `--wake-word` CLI flag).

    Audio is processed locally/in a normal STT request; nothing is recorded or
    stored beyond the transient transcription. No commercial always-on
    keyword engine is used by default.
    """
    if not wake_word_available():
        if on_status:
            on_status("[voice: wake word unavailable (need mic + SpeechRecognition)]")
        print("[voice] Wake word disabled — SpeechRecognition/mic unavailable.", flush=True)
        return False

    while True:
        if on_status:
            on_status(f"🔊 listening for '{wake_word}'…")
        phrase = listen(
            timeout=timeout,
            phrase_time_limit=phrase_time_limit,
            energy_threshold=energy_threshold,
            on_status=None,
        )
        if not phrase:
            continue
        if _match_wake_word(phrase, wake_word):
            if on_status:
                on_status(f"✓ wake word detected: '{wake_word}'")
            print(f"[voice] Wake word detected: {phrase}", flush=True)
            return True
        # Not the wake word — silently keep listening (no chat trigger).


def configure_from_env() -> dict[str, object]:
    """Read any JARVIS_VOICE_* / JARVIS_WAKE_* env overrides.

    Returns a dict with the resolved voice settings so callers can log or
    adapt behaviour without re-parsing env.
    """
    settings: dict[str, object] = {
        "rate": int(os.environ.get("JARVIS_VOICE_RATE", "180") or 180),
        "wake_word": os.environ.get("JARVIS_WAKE_WORD", _DEFAULT_WAKE_WORD).strip(),
        "wake_enabled": os.environ.get("JARVIS_WAKE_ENABLED", "false").lower()
        in ("true", "1", "yes"),
    }
    return settings

