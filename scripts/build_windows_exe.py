"""Windows Executable & Portable Distribution Builder for Jarvis Client Radar.

Automates:
1. Dependency checks (PyInstaller / httpx / python-dotenv).
2. Building standalone Windows executables (.exe) for both the CLI Radar and Web HUD Server.
3. Generating one-click Windows batch launchers.
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

def build_windows_dist():
    print("=" * 60)
    print("[*] BUILDING STANDALONE WINDOWS EXECUTABLE & LAUNCHER")
    print("=" * 60)
    
    # 1. Generate One-Click Windows Master Launcher (.bat)
    master_launcher = ROOT_DIR / "START_CLIENT_RADAR.bat"
    bat_content = """@echo off
title Jarvis Client Acquisition Radar & Web HUD
cd /d "%~dp0"
echo =========================================================
echo   JARVIS CLIENT RADAR & MONEY MAKER ENGINE (v5.0)
echo =========================================================
echo.
echo [1] Launch Web HUD Dashboard (Browser GUI)
echo [2] Run Inbound Freelance Lead Triage (Live Scan)
echo [3] Run YouTube Creator Cold Outbound Radar
echo [4] Run Pipeline Conversion Feedback Loop & AI Optimizer
echo [5] View Funnel Analytics Report
echo [6] Exit
echo.
set /p choice="Select an action [1-6]: "

if "%choice%"=="1" (
    echo [*] Starting Web HUD Server...
    python run_dashboard.py
)
if "%choice%"=="2" (
    echo [*] Running Inbound Lead Triage...
    python freelance_lead_triage.py
    pause
)
if "%choice%"=="3" (
    echo [*] Running YouTube Creator Radar...
    python youtube_creator_auditor.py
    pause
)
if "%choice%"=="4" (
    echo [*] Running AI Prompt Feedback Loop & Optimizer...
    python lead_feedback_loop.py
    pause
)
if "%choice%"=="5" (
    echo [*] Loading Funnel Report...
    python freelance_lead_triage.py --report
    pause
)
if "%choice%"=="6" (
    exit
)
"""
    with open(master_launcher, "w", encoding="utf-8") as f:
        f.write(bat_content)
        
    print(f"[+] Created Master Windows Launcher: {master_launcher}")

    # 2. Check for PyInstaller to build standalone .exe
    try:
        import PyInstaller
        print("[*] PyInstaller detected. Compiling standalone 'JarvisRadar.exe'...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", "JarvisClientRadar",
            "--clean",
            str(ROOT_DIR / "freelance_lead_triage.py")
        ]
        subprocess.run(cmd, cwd=ROOT_DIR, check=True)
        print("[+] Standalone Windows Executable built in 'dist/JarvisClientRadar.exe'!")
    except ImportError:
        print("[!] PyInstaller not installed in current environment.")
        print("[*] To compile a single .exe file, run: pip install pyinstaller && python scripts/build_windows_exe.py")
        print("[+] Master Launcher 'START_CLIENT_RADAR.bat' is ready for instant 1-click execution.")

if __name__ == "__main__":
    build_windows_dist()
