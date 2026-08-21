@echo off
title Jarvis Client Acquisition Radar & Web HUD (v5.0)
color 0B
cd /d "%~dp0"

:MENU
cls
echo ==============================================================================
echo        JARVIS CLIENT RADAR & MONEY MAKER ENGINE (v5.0)
echo ==============================================================================
echo.
echo   [1] Launch Web HUD Dashboard (Browser GUI)
echo   [2] Run Inbound Freelance Lead Triage (Live Scan & Pitch Generator)
echo   [3] Run YouTube Creator Cold Outbound Radar (Dynamic Niche Discovery)
echo   [4] Run AI Prompt Feedback Loop & Optimizer (Auto-Evolve Prompts)
echo   [5] Generate Productized Retainer Upsell (For Replied Leads)
echo   [6] View Full Funnel & Conversion Analytics Report
echo   [7] Build Standalone Windows Executable (.EXE)
echo   [8] Exit
echo.
echo ==============================================================================
set /p choice="Select an action [1-8]: "

if "%choice%"=="1" (
    echo.
    echo [*] Starting Web HUD Server on http://localhost:5050...
    start python run_dashboard.py
    goto MENU
)
if "%choice%"=="2" (
    echo.
    echo [*] Running Inbound Lead Triage...
    python freelance_lead_triage.py
    echo.
    pause
    goto MENU
)
if "%choice%"=="3" (
    echo.
    set /p niche="Enter niche query (or press Enter for default): "
    if "%niche%"=="" (
        python youtube_creator_auditor.py
    ) else (
        python youtube_creator_auditor.py "%niche%"
    )
    echo.
    pause
    goto MENU
)
if "%choice%"=="4" (
    echo.
    echo [*] Running Continuous Conversion Feedback Loop & AI Optimizer...
    python lead_feedback_loop.py
    echo.
    pause
    goto MENU
)
if "%choice%"=="5" (
    echo.
    set /p lead_id="Enter Lead ID (e.g. 8 chars): "
    python freelance_lead_triage.py --followup %lead_id%
    echo.
    pause
    goto MENU
)
if "%choice%"=="6" (
    echo.
    echo [*] Generating Funnel Report...
    python freelance_lead_triage.py --report
    echo.
    pause
    goto MENU
)
if "%choice%"=="7" (
    echo.
    echo [*] Compiling Standalone Windows Executable...
    python scripts/build_windows_exe.py
    echo.
    pause
    goto MENU
)
if "%choice%"=="8" (
    exit
)

goto MENU
