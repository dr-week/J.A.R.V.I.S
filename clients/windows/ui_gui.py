"""Flet desktop chat UI for the Windows Jarvis client."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable

BG = "#0f0f13"
SURFACE = "#19191e"
SURFACE_ELEVATED = "#232328"
BORDER = "#333333"
ACCENT = "#0a84ff"
TEXT = "#f0f0f2"
TEXT_MUTED = "#8e8e93"
USER_BUBBLE = "#0a84ff"
ASSIST_BUBBLE = "#1e1e2e"
ERROR = "#f87171"
SUCCESS = "#34d399"
MAX_BUBBLE_W = 340
# Win32 FindWindow title — must stay stable for single-instance focus (instance_lock.py).
WINDOW_TITLE = "Jarvis"


def mount_jarvis_desktop(
    page: Any,
    args: Any,
    *,
    brain: str,
    device_id: str,
    session_holder: dict[str, str],
    token_holder: dict[str, str | None],
    pair_fn: Callable[..., str],
    auth_headers_fn: Callable[[str | None], dict[str, str]],
    brain_start_hint: Callable[[str], str],
    bridge_slot: dict[str, Any] | None = None,
) -> None:
    import flet as ft
    import httpx

    bridge_slot = bridge_slot if bridge_slot is not None else {}
    state: dict[str, Any] = {
        "brain_ok": False,
        "assistant_name": "Jarvis",
        "pair_failed": False,
        "announced_offline": False,
    }

    bridge_slot["page"] = page
    page.title = WINDOW_TITLE
    page.window.title = WINDOW_TITLE
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 420
    page.window.height = 720
    page.window.min_width = 360
    page.window.min_height = 520
    page.padding = 0
    page.bgcolor = BG
    page.window.prevent_close = True

    page.theme = ft.Theme(
        color_scheme_seed=ACCENT,
        scrollbar_theme=ft.ScrollbarTheme(
            track_color={ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
            thumb_color={ft.ControlState.DEFAULT: BORDER},
            thickness=5,
            radius=8,
            interactive=True,
        ),
    )

    status_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor=TEXT_MUTED)
    status_text = ft.Text("Starting…", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_500)
    bridge_text = ft.Text("", size=11, color=TEXT_MUTED)
    wake_text = ft.Text("Mic off", size=11, color=TEXT_MUTED)
    llm_hint = ft.Text("", size=10, color=TEXT_MUTED)
    header_title = ft.Text("Jarvis", size=18, weight=ft.FontWeight.W_700, color=TEXT)
    chat_list = ft.ListView(expand=True, spacing=12, auto_scroll=True, padding=16)

    def set_status(label: str, *, ok: bool | None = None, error: bool = False) -> None:
        status_text.value = label
        if error:
            status_dot.bgcolor = ERROR
            status_text.color = ERROR
        elif ok:
            status_dot.bgcolor = SUCCESS
            status_text.color = TEXT_MUTED
        else:
            status_dot.bgcolor = TEXT_MUTED
            status_text.color = TEXT_MUTED
        page.update()

    def append_chat(control: ft.Control) -> None:
        chat_list.controls.append(control)
        page.update()

    def system_line(text: str, *, error: bool = False) -> None:
        append_chat(
            ft.Container(
                content=ft.Text(
                    text,
                    size=12,
                    color=ERROR if error else TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.alignment.Alignment(0, 0),
                padding=8,
            )
        )

    def add_bubble(role: str, text: str, *, markdown: bool = True) -> ft.Markdown | ft.Text:
        is_user = role == "user"
        if role == "system":
            system_line(text, error=False)
            return ft.Text("")

        ts = datetime.now().strftime("%H:%M")
        label = "You" if is_user else state["assistant_name"]

        if markdown and not is_user:
            body: ft.Control = ft.Markdown(
                text or "…",
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                code_theme=ft.MarkdownCodeTheme.ATOM_ONE_DARK,
            )
        else:
            body = ft.Text(text, selectable=True, color=TEXT, size=14)

        bubble = ft.Container(
            content=ft.Column(
                [ft.Text(f"{label} · {ts}", size=10, color=TEXT_MUTED), body],
                spacing=4,
                tight=True,
            ),
            padding=12,
            border_radius=16,
            bgcolor=USER_BUBBLE if is_user else ASSIST_BUBBLE,
            border=None if not is_user else None,
            width=MAX_BUBBLE_W,
        )
        append_chat(
            ft.Row(
                [bubble],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
            )
        )
        return body  # type: ignore[return-value]

    user_input = ft.TextField(
        hint_text="Message Jarvis…",
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        expand=True,
        autofocus=True,
        border=ft.InputBorder.NONE,
        bgcolor=ft.Colors.TRANSPARENT,
        color=TEXT,
        cursor_color=ACCENT,
        content_padding=12,
        disabled=True,
    )

    send_btn = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color=TEXT,
        bgcolor=ACCENT,
        disabled=True,
        width=44,
        height=44,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=22)),
    )

    reconnect_btn = ft.TextButton("Reconnect", icon=ft.Icons.REFRESH)
    new_chat_btn = ft.TextButton("New chat", icon=ft.Icons.ADD_COMMENT)

    def on_new_chat(_e: ft.ControlEvent | None) -> None:
        session_holder["session_id"] = str(uuid.uuid4())
        chat_list.controls.clear()
        add_bubble("system", "New chat started.", markdown=False)
        page.update()

    new_chat_btn.on_click = on_new_chat

    def refresh_connection(*, try_pair: bool = False, announce: bool = True) -> None:
        reconnect_btn.disabled = True
        page.update()

        if try_pair and args.pair:
            secret = args.pairing_secret or __import__("os").environ.get(
                "JARVIS_PAIRING_SECRET", "change-me"
            )
            try:
                token_holder["token"] = pair_fn(brain, secret, device_id)
                state["pair_failed"] = False
                if announce:
                    system_line("Paired with brain. Token saved.")
            except Exception as exc:
                state["pair_failed"] = True
                if announce:
                    system_line(str(exc), error=True)
                set_status("Pair failed", error=True)
                user_input.disabled = True
                send_btn.disabled = True
                reconnect_btn.disabled = False
                page.update()
                return

        try:
            r = httpx.get(f"{brain}/health", timeout=4)
            r.raise_for_status()
            data = r.json()
            state["brain_ok"] = True
            state["announced_offline"] = False
            state["assistant_name"] = data.get("assistant_name", "Jarvis")
            header_title.value = state["assistant_name"]
            tok = "paired" if token_holder.get("token") else "no token"
            llm_ready = bool(data.get("llm_ready"))
            llm = "LLM on" if llm_ready else "LLM off"
            llm_hint.value = (
                ""
                if llm_ready
                else "Add GEMINI_API_KEY to backend .env — see .env.example"
            )
            if not state["pair_failed"]:
                set_status(f"{llm} · {tok}", ok=True)
            if announce and not state.get("_announced_online"):
                state["_announced_online"] = True
                system_line(f"Online at {brain}")
        except httpx.ConnectError:
            state["brain_ok"] = False
            set_status("Brain offline — start backend on :8787", error=True)
            if announce and not state["announced_offline"]:
                system_line(brain_start_hint(brain), error=True)
                state["announced_offline"] = True
        except Exception as exc:
            state["brain_ok"] = False
            set_status("Connection error", error=True)
            if announce:
                system_line(str(exc), error=True)

        user_input.disabled = not state["brain_ok"]
        send_btn.disabled = not state["brain_ok"]
        reconnect_btn.disabled = False
        page.update()

    async def send_click(_e: ft.ControlEvent | None = None, override_text: str | None = None) -> None:
        text = (override_text or user_input.value or "").strip()
        if not text or not state["brain_ok"]:
            return

        user_input.value = ""
        user_input.disabled = True
        send_btn.disabled = True
        set_status("Thinking…", ok=None)
        page.update()

        add_bubble("user", text, markdown=False)
        body_control = add_bubble("assistant", "", markdown=True)

        full_reply: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=120) as http:
                async with http.stream(
                    "POST",
                    f"{brain}/chat",
                    json={
                        "text": text,
                        "session_id": session_holder["session_id"],
                        "device_id": device_id,
                        "client_msg_id": str(uuid.uuid4()),
                    },
                    headers={
                        "Accept": "text/event-stream",
                        **auth_headers_fn(token_holder.get("token")),
                    },
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        chunk = line[6:]
                        if chunk == "[DONE]":
                            break
                        full_reply.append(chunk)
                        if isinstance(body_control, ft.Markdown):
                            body_control.value = "".join(full_reply)
                        page.update()
            
            final_reply = "".join(full_reply).strip()
            if getattr(args, "voice", False) and final_reply:
                try:
                    from voice import speak
                    if speak:
                        speak(final_reply, on_status=_set_wake_status)
                except ImportError:
                    pass
        except Exception as exc:
            system_line(f"Send failed: {exc}", error=True)

        refresh_connection(announce=False)
        user_input.disabled = not state["brain_ok"]
        send_btn.disabled = not state["brain_ok"]
        if state["brain_ok"]:
            user_input.focus()
        page.update()

    user_input.on_submit = send_click
    send_btn.on_click = send_click

    def on_reconnect(_e: ft.ControlEvent | None) -> None:
        state["announced_offline"] = False
        state.pop("_announced_online", None)
        refresh_connection(try_pair=bool(args.pair), announce=True)

    reconnect_btn.on_click = on_reconnect

    input_row = ft.Container(
        content=ft.Row([user_input, send_btn], spacing=4),
        bgcolor=SURFACE_ELEVATED,
        border=None,
        border_radius=28,
        padding=6,
        margin=10,
    )

    page.add(
        ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.AUTO_AWESOME, color=ACCENT, size=22),
                            header_title,
                            ft.Container(expand=True),
                            new_chat_btn,
                            reconnect_btn,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=14,
                    bgcolor=SURFACE,
                    border=None,
                ),
                ft.Container(content=chat_list, expand=True, bgcolor=BG),
                input_row,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [status_dot, status_text, ft.Container(expand=True), wake_text, ft.Text(" · ", size=11, color=TEXT_MUTED), bridge_text],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Text(f"Device · {device_id}", size=10, color=TEXT_MUTED),
                            llm_hint,
                        ],
                        spacing=4,
                        tight=True,
                    ),
                    padding=10,
                    bgcolor=SURFACE,
                ),
            ],
            expand=True,
            spacing=0,
        )
    )

    add_bubble("system", "Welcome. Connect the brain, then chat.", markdown=False)

    if args.bridge:
        bridge_text.value = "Bridge: starting…"
    elif bridge_slot.get("tray"):
        bridge_text.value = "Tray: minimize to hide"

    def _set_bridge_status(msg: str) -> None:
        setattr(bridge_text, "value", msg)
        page.update()

    def _set_wake_status(msg: str) -> None:
        setattr(wake_text, "value", msg)
        setattr(wake_text, "color", ACCENT if "Listening" in msg or "Wake" in msg else TEXT_MUTED)
        page.update()

    bridge_slot["bridge_text"] = bridge_text
    bridge_slot["set_bridge_status"] = _set_bridge_status
    bridge_slot["set_wake_status"] = _set_wake_status

    install_tray = bridge_slot.get("install_tray")
    if install_tray:
        install_tray(page)

    def _wake_word_loop() -> None:
        try:
            from voice import listen, listen_for_wake_word
        except ImportError:
            _set_wake_status("Mic missing")
            return
            
        ww = getattr(args, "wake_word", "").strip() or "jarvis"
        while True:
            heard = listen_for_wake_word(ww, on_status=_set_wake_status)
            if not heard:
                break
            _set_wake_status("Listening...")
            spoken = listen(on_status=_set_wake_status)
            if spoken:
                _set_wake_status("Heard you!")
                # trigger send_click asynchronously in the Flet event loop
                page.run_task(send_click, override_text=spoken)
            else:
                _set_wake_status("Listening for wake...")
                
    if getattr(args, "wake_word", None):
        import threading
        threading.Thread(target=_wake_word_loop, daemon=True).start()
    else:
        _set_wake_status("Mic off")

    refresh_connection(try_pair=bool(args.pair), announce=True)


def launch_flet_desktop(
    args: Any,
    *,
    brain: str,
    device_id: str,
    session_holder: dict[str, str],
    token_holder: dict[str, str | None],
    pair_fn: Callable[..., str],
    auth_headers_fn: Callable[[str | None], dict[str, str]],
    brain_start_hint: Callable[[str], str],
    bridge_slot: dict[str, Any] | None = None,
) -> int:
    try:
        import flet as ft
    except ImportError:
        print("Flet not installed. Use --once for CLI, or:")
        print("  pip install flet")
        return 1

    bridge_slot = bridge_slot if bridge_slot is not None else {}

    def main_gui(page: ft.Page) -> None:
        mount_jarvis_desktop(
            page,
            args,
            brain=brain,
            device_id=device_id,
            session_holder=session_holder,
            token_holder=token_holder,
            pair_fn=pair_fn,
            auth_headers_fn=auth_headers_fn,
            brain_start_hint=brain_start_hint,
            bridge_slot=bridge_slot,
        )

    print(f"Opening Jarvis desktop UI -> {brain}  (device={device_id})", flush=True)
    if args.pair:
        print("Pairing on launch (brain must be running).", flush=True)
    print("Quit from the tray menu (Quit) — do not start a second copy.", flush=True)
    try:
        ft.run(main_gui)
    finally:
        from instance_lock import release_gui_instance

        release_gui_instance()
    return 0
