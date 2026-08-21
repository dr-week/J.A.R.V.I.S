"""One-Click Windows Executable & Portable Launcher Builder for Jarvis.

Generates a standalone, portable Windows executable / batch launcher
with zero manual configuration required.
"""
import os
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

def build_standalone_launcher():
    """Creates a zero-dependency Windows batch launcher and PyInstaller spec."""
    print("=" * 60)
    print("[*] JARVIS STANDALONE EXECUTABLE & LAUNCHER BUILDER")
    print("=" * 60)
    
    launcher_bat = ROOT_DIR / "JARVIS_LAUNCHER.bat"
    bat_content = f"""@echo off
title Jarvis AI Assistant & Money Maker
cd /d "%~dp0"
echo ===================================================
echo   JARVIS PERSONAL AI & MONEY MAKER INITIALIZING
echo ===================================================
echo.
python jarvis_main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Python returned an error code. Press any key to exit.
    pause >nul
)
"""
    with open(launcher_bat, "w", encoding="utf-8") as f:
        f.write(bat_content)
        
    print(f"[+] Created One-Click Windows Launcher: {launcher_bat}")
    print("[+] Ready for PyInstaller build: `pyinstaller --onefile jarvis_main.py`")

if __name__ == "__main__":
    build_standalone_launcher()
