"""Jarvis Windows Client — desktop presence stub (ISSUE-011).

Talks to the brain via POST /chat (SSE). Optional pairing token via /pair.
Also runs a device-bridge WebSocket loop (ISSUE-032) that executes local
'open app/URL/file' actions on behalf of the brain.

Usage:
    pip install -r clients/windows/requirements.txt
    python clients/windows/client.py --brain http://localhost:8787
    python clients/windows/client.py --once "hello" --pair
    python clients/windows/client.py --bridge --pair
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
import threading
from pathlib import Path
from typing import Callable

try:
    import httpx
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install -r clients/windows/requirements.txt")
    sys.exit(1)

DEFAULT_BRAIN = os.environ.get("JARVIS_BRAIN_URL", "http://localhost:8787")
DEVICE_ID = os.environ.get("JARVIS_DEVICE_ID", "windows-desktop")
TOKEN_PATH = Path(
    os.environ.get(
        "JARVIS_TOKEN_FILE",
        str(Path.home() / ".jarvis" / "windows_token.json"),
    )
)
TRAY_TITLE = os.environ.get("JARVIS_TRAY_TITLE", "Jarvis")


def _make_tray_icon():
    try:
        from PIL import Image, ImageDraw
        import pystray
    except ImportError:
        return None, None

    image = Image.new("RGBA", (64, 64), (13, 13, 20, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 54, 54), fill=(167, 139, 250, 255))
    draw.ellipse((22, 22, 42, 42), fill=(13, 13, 20, 255))
    return pystray, image


def _start_tray(on_open, on_quit):
    pystray, image = _make_tray_icon()
    if not pystray:
        print("[tray] pystray or Pillow is missing; running without tray support.")
        return None

    def open_item(icon, item):  # noqa: ARG001
        on_open()

    def quit_item(icon, item):  # noqa: ARG001
        on_quit(icon)

    menu = pystray.Menu(
        pystray.MenuItem("Open Jarvis", open_item, default=True),
        pystray.MenuItem("Quit", quit_item),
    )
    icon = pystray.Icon(TRAY_TITLE, image, TRAY_TITLE, menu)
    tray_thread = threading.Thread(target=icon.run, daemon=False)
    tray_thread.start()
    return icon


def load_token() -> str | None:
    if not TOKEN_PATH.exists():
        return None
    try:
        data = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
        return data.get("token")
    except Exception:
        return None


def save_token(token: str, device_id: str) -> None:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(
        json.dumps({"token": token, "device_id": device_id}, indent=2),
        encoding="utf-8",
    )


def brain_start_hint(brain: str) -> str:
    return (
        f"Brain not reachable at {brain}. "
        "Start it in another terminal:\n"
        "  cd backend\n"
        "  uvicorn app.main:app --reload --port 8787"
    )


def pair(brain: str, secret: str, device_id: str, device_name: str = "windows") -> str:
    brain = brain.rstrip("/")
    try:
        with httpx.Client(timeout=10) as client:
            r = client.post(
                f"{brain}/pair",
                json={
                    "pairing_secret": secret,
                    "device_id": device_id,
                    "device_name": device_name,
                },
            )
            r.raise_for_status()
    except httpx.ConnectError as exc:
        raise ConnectionError(brain_start_hint(brain)) from exc
    except httpx.TimeoutException as exc:
        raise ConnectionError(f"Timed out connecting to {brain}/pair") from exc
    data = r.json()
    token = data["token"]
    save_token(token, device_id)
    return token


def auth_headers(token: str | None) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def stream_chat(
    brain: str,
    text: str,
    *,
    session_id: str,
    device_id: str,
    token: str | None,
    client_msg_id: str | None = None,
) -> str:
    full = []
    payload = {
        "text": text,
        "session_id": session_id,
        "device_id": device_id,
        "client_msg_id": client_msg_id or str(uuid.uuid4()),
    }
    with httpx.Client(timeout=120) as client:
        with client.stream(
            "POST",
            f"{brain.rstrip('/')}/chat",
            json=payload,
            headers={
                "Accept": "text/event-stream",
                **auth_headers(token),
            },
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line.startswith("data: "):
                    continue
                chunk = line[6:]
                if chunk == "[DONE]":
                    break
                if chunk.startswith("[ERROR]"):
                    raise RuntimeError(chunk)
                full.append(chunk)
                print(chunk, end="", flush=True)
    print()
    return "".join(full)


def run_once(args: argparse.Namespace) -> int:
    brain = args.brain.rstrip("/")
    token = args.token or load_token()
    voice = getattr(args, "voice", False)
    if args.pair:
        secret = args.pairing_secret or os.environ.get("JARVIS_PAIRING_SECRET", "change-me")
        try:
            token = pair(brain, secret, args.device_id)
        except (ConnectionError, httpx.HTTPStatusError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Paired. Token saved to {TOKEN_PATH}")
    try:
        with httpx.Client(timeout=5) as client:
            h = client.get(f"{brain}/health")
            h.raise_for_status()
            name = h.json().get("assistant_name", "Jarvis")
    except Exception as exc:
        if isinstance(exc, httpx.ConnectError):
            print(brain_start_hint(brain), file=sys.stderr)
        else:
            print(f"Brain unreachable at {brain}: {exc}", file=sys.stderr)
        return 1

    print(f"{name} @ {brain}  device={args.device_id}  token={'yes' if token else 'no'}")
    print(f"You: {args.once}")
    print(f"{name}: ", end="", flush=True)
    reply = stream_chat(
        brain,
        args.once,
        session_id=args.session_id,
        device_id=args.device_id,
        token=token,
    )
    if voice and reply.strip():
        try:
            from voice import speak
        except ImportError:  # pragma: no cover
            speak = None
        if speak:
            speak(reply, on_status=lambda s: print(s, flush=True))
    return 0


def run_flet(args: argparse.Namespace) -> int:
    import threading

    from instance_lock import ensure_single_gui_instance, release_gui_instance
    from ui_gui import launch_flet_desktop

    if not ensure_single_gui_instance():
        return 0

    brain = args.brain.rstrip("/")
    device_id = args.device_id
    session_id = args.session_id
    session_holder: dict[str, str] = {"session_id": session_id}
    token_holder: dict[str, str | None] = {"token": args.token or load_token()}
    bridge_slot: dict = {}

    def install_tray(page) -> None:
        def show_window() -> None:
            page.window.visible = True
            page.window.minimized = False
            page.window.to_front()
            page.update()

        def hide_window() -> None:
            page.window.visible = False
            page.update()

        def quit_app(icon=None) -> None:
            """Stop tray + Flet and exit so child 'Flet' processes do not linger."""
            if icon is not None:
                try:
                    icon.stop()
                except Exception:
                    pass
            release_gui_instance()
            try:
                page.window.destroy()
            except Exception:
                pass
            # Hard exit: Flet may leave desktop helper processes after destroy().
            os._exit(0)

        def on_window_event(e) -> None:
            if getattr(e, "data", "") in {"minimize", "hide", "close"}:
                hide_window()

        page.window.on_event = on_window_event
        bridge_slot["tray"] = _start_tray(show_window, quit_app)
        bridge_slot["quit_app"] = quit_app

    bridge_slot["install_tray"] = install_tray

    if args.bridge:

        def run_bridge() -> None:
            token = token_holder.get("token")
            setter = bridge_slot.get("set_bridge_status")
            if setter:
                setter("Bridge: connecting…")
            try:
                bridge_loop(
                    brain,
                    device_id,
                    token,
                    on_status=setter,
                )
            finally:
                setter = bridge_slot.get("set_bridge_status")
                if setter:
                    setter("Bridge: disconnected")

        threading.Thread(target=run_bridge, daemon=True).start()

    return launch_flet_desktop(
        args,
        brain=brain,
        device_id=device_id,
        session_holder=session_holder,
        token_holder=token_holder,
        pair_fn=pair,
        auth_headers_fn=auth_headers,
        brain_start_hint=brain_start_hint,
        bridge_slot=bridge_slot,
    )


def bridge_loop(
    brain: str,
    device_id: str,
    token: str | None,
    *,
    on_status: Callable[[str], None] | None = None,
) -> int:
    """Run the device-bridge WebSocket loop (ISSUE-032).

    Connects to the brain /ws endpoint, registers this device, and listens for
    `tool_execute` requests. Executes local actions (open app/URL/file) via
    device_bridge and returns results to the brain.
    """
    import asyncio
    import time

    import device_bridge  # same-directory helper (run as script)
    import sync_cache  # local memory mirror (ISSUE-022)
    import websockets

    ws_url = brain.replace("http://", "ws://").replace("https://", "wss://").rstrip("/") + "/ws"
    headers = auth_headers(token)
    print(f"Bridge listening as device '{device_id}' on {ws_url}")
    print("Press Ctrl+C to stop.")

    async def _run() -> None:
        async with websockets.connect(ws_url, additional_headers=headers) as ws:
            await ws.send(json.dumps({"type": "register", "device_id": device_id}))
            # Consume the register ack
            ack = json.loads(await ws.recv())
            print(f"[ws] {ack.get('type', '?')}: {ack.get('device_id', '')}")
            if on_status:
                on_status("Bridge: connected")
            async for raw_text in ws:
                raw = json.loads(raw_text)
                msg_type = raw.get("type")

                if msg_type == "ping":
                    await ws.send(json.dumps({"type": "pong"}))
                    continue

                if msg_type == "tool_execute":
                    request_id = raw.get("request_id")
                    tool = raw.get("tool", "")
                    params = raw.get("params", {})
                    print(f"[tool] executing: {tool} {params}")
                    result = device_bridge.execute_tool(tool, params)
                    status = "ok" if result.get("ok") else "error"
                    await ws.send(
                        json.dumps(
                            {
                                "type": "tool_result",
                                "request_id": request_id,
                                "session_id": raw.get("session_id", ""),
                                "tool": tool,
                                "status": status,
                                "result": result,
                            }
                        )
                    )
                    print(
                        f"[tool] {tool} -> {status}: "
                        f"{result.get('result') or result.get('error')}"
                    )
                    continue

                if msg_type == "push_memory":
                    # Cross-device memory sync (ISSUE-022): a memory was
                    # written/deleted on another device -> mirror it locally.
                    key = raw.get("key", "")
                    value = raw.get("value", "")
                    changed = sync_cache.apply_push(key, value)
                    if changed:
                        print(
                            f"[sync] memory '{key}' "
                            f"{'deleted' if value == '' else 'updated'} in local cache"
                        )
                    continue

                # Ignore other message types (chat chunks, etc.)

    while True:
        try:
            asyncio.run(_run())
        except KeyboardInterrupt:
            print("[bridge] stopped by user.")
            return 0
        except Exception as exc:  # noqa: BLE001
            if on_status:
                on_status("Bridge: reconnecting…")
            print(f"[bridge] connection error: {exc}")
            print("[bridge] retrying in 3s...")
            time.sleep(3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis Windows client")
    parser.add_argument("--brain", default=DEFAULT_BRAIN)
    parser.add_argument("--device-id", default=DEVICE_ID)
    parser.add_argument("--session-id", default=str(uuid.uuid4()))
    parser.add_argument("--token", default=None, help="Bearer token from /pair")
    parser.add_argument("--pair", action="store_true", help="Pair with brain before chat")
    parser.add_argument(
        "--pairing-secret",
        default=None,
        help="JARVIS_PAIRING_SECRET (default from env or change-me)",
    )
    parser.add_argument("--once", default=None, help="Send one message (CLI, no TUI)")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Voice mode (ISSUE-050): capture spoken input + speak replies",
    )
    parser.add_argument(
        "--bridge",
        action="store_true",
        help="Also run device-bridge WebSocket in background (with Flet GUI)",
    )
    parser.add_argument(
        "--bridge-only",
        action="store_true",
        help="Run device-bridge WS loop only, no GUI (ISSUE-032 headless)",
    )
    parser.add_argument(
        "--wake-word",
        metavar="PHRASE",
        default=os.environ.get("JARVIS_WAKE_WORD") or "",
        help="Opt-in wake word (ISSUE-052). Keep listening in the background; "
        "when the phrase is heard a spoken turn is captured and sent to the "
        "brain. Default is the JARVIS_WAKE_WORD env (or disabled). "
        "Use --wake-word jarvis for the default phrase.",
    )
    args = parser.parse_args()

    if args.voice and args.once is None:
        # --voice alone means: capture the prompt from the mic
        try:
            from voice import listen
        except ImportError:  # pragma: no cover
            listen = None
        if listen is None:
            print("[voice] voice.py missing or deps absent. Use --once \"text\" instead.")
            return 1
        spoken = listen(on_status=lambda s: print(s, flush=True))
        if not spoken:
            print("[voice] Nothing transcribed.")
            return 1
        args.once = spoken

    if args.wake_word and args.once is None and not args.bridge_only:
        # Wake-word mode (ISSUE-052): wait for the wake phrase, then capture a
        # spoken turn and send it to the brain, looping until Ctrl+C. Opt-in.
        from voice import configure_from_env, listen, listen_for_wake_word, speak

        args.wake_word = args.wake_word if args.wake_word.strip() else "jarvis"
        print(f"[voice] Wake word enabled for '{args.wake_word}' (ISSUE-052). Ctrl+C to stop.")
        print(f"[voice] Speaking '{args.wake_word}' will start a listening session.")
        token = args.token or load_token()
        if args.pair:
            secret = args.pairing_secret or os.environ.get("JARVIS_PAIRING_SECRET", "change-me")
            try:
                token = pair(args.brain.rstrip("/"), secret, args.device_id)
            except (ConnectionError, httpx.HTTPStatusError) as exc:
                print(str(exc), file=sys.stderr)
                return 1
            print(f"Paired. Token saved to {TOKEN_PATH}")
        # Pre-flight: ensure the brain is reachable.
        try:
            with httpx.Client(timeout=5) as client:
                h = client.get(f"{args.brain.rstrip('/')}/health")
                h.raise_for_status()
                name = h.json().get("assistant_name", "Jarvis")
        except Exception as exc:
            if isinstance(exc, httpx.ConnectError):
                print(brain_start_hint(args.brain.rstrip("/")), file=sys.stderr)
            else:
                print(f"Brain unreachable at {args.brain}: {exc}", file=sys.stderr)
            return 1
        print(f"{name} @ {args.brain}  device={args.device_id}  token={'yes' if token else 'no'}")
        while True:
            try:
                heard = listen_for_wake_word(
                    args.wake_word,
                    on_status=lambda s: print(s, flush=True),
                )
                if not heard:
                    return 1
                print(f"{name}: ", end="", flush=True)
                spoken = listen(on_status=lambda s: print(s, flush=True))
                if not spoken:
                    print("[voice] Nothing transcribed — still listening for wake word.")
                    continue
                reply = stream_chat(
                    args.brain.rstrip("/"),
                    spoken,
                    session_id=args.session_id,
                    device_id=args.device_id,
                    token=token,
                )
                if reply.strip():
                    speak(reply, on_status=lambda s: print(s, flush=True))
            except KeyboardInterrupt:
                print("\n[voice] Wake-word mode stopped by user.")
                return 0

    if args.once:
        raise SystemExit(run_once(args))
    if args.bridge_only:
        token = args.token or load_token()
        if args.pair:
            secret = args.pairing_secret or os.environ.get("JARVIS_PAIRING_SECRET", "change-me")
            try:
                token = pair(args.brain.rstrip("/"), secret, args.device_id)
            except (ConnectionError, httpx.HTTPStatusError) as exc:
                print(str(exc), file=sys.stderr)
                raise SystemExit(1) from exc
            print(f"Paired. Token saved to {TOKEN_PATH}")
        raise SystemExit(bridge_loop(args.brain, args.device_id, token))
    raise SystemExit(run_flet(args))


if __name__ == "__main__":
    main()
