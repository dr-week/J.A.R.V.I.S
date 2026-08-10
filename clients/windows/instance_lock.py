"""Windows single-instance guard for the Flet GUI (prevents Flet process herds)."""
from __future__ import annotations

import atexit
import sys

MUTEX_NAME = r"Global\JarvisWindowsClient_v1"
_WINDOW_TITLE = "Jarvis"

_mutex_handle: int | None = None


def _kernel32():
    import ctypes

    return ctypes.windll.kernel32  # type: ignore[attr-defined]


def release_gui_instance() -> None:
    global _mutex_handle
    if sys.platform != "win32" or not _mutex_handle:
        return
    k = _kernel32()
    k.ReleaseMutex(_mutex_handle)
    k.CloseHandle(_mutex_handle)
    _mutex_handle = None


def acquire_gui_instance() -> bool:
    """Return True if this process owns the GUI slot; False if another instance is running."""
    global _mutex_handle
    if sys.platform != "win32":
        return True
    if _mutex_handle:
        return True

    k = _kernel32()
    ERROR_ALREADY_EXISTS = 183
    handle = k.CreateMutexW(None, True, MUTEX_NAME)
    if not handle:
        return False
    if k.GetLastError() == ERROR_ALREADY_EXISTS:
        k.CloseHandle(handle)
        return False
    _mutex_handle = handle
    atexit.register(release_gui_instance)
    return True


def try_focus_existing_window(title: str = _WINDOW_TITLE) -> bool:
    if sys.platform != "win32":
        return False
    import ctypes

    user32 = ctypes.windll.user32  # type: ignore[attr-defined]
    hwnd = user32.FindWindowW(None, title)
    if not hwnd:
        return False
    SW_RESTORE = 9
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    return True


def ensure_single_gui_instance() -> bool:
    """
    If another GUI is running, try to focus it and return False.
    If this process may start the GUI, return True.
    """
    if acquire_gui_instance():
        return True
    focused = try_focus_existing_window()
    if focused:
        print("Jarvis is already running — brought the existing window to the front.")
    else:
        print(
            "Jarvis desktop UI is already running (or a stale lock exists).\n"
            "  Use the tray icon: Open Jarvis / Quit\n"
            "  Or run: .\\clients\\windows\\kill_stale.ps1\n"
            "Then start one instance: python clients\\windows\\client.py --pair"
        )
    return False
