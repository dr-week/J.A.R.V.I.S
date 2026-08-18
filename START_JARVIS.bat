@echo off
title JARVIS AI System Launcher
cd /d "%~dp0"

echo ===================================================
echo   [*] STARTING J.A.R.V.I.S. UNIFIED LOCAL SYSTEM
echo ===================================================
echo.

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo [*] Starting Jarvis Brain Backend on http://localhost:8787 ...
start "Jarvis Brain Server" /min python scripts/run_brain.py

echo [*] Starting Jarvis Web UI Client ...
cd clients\web
start "Jarvis Web UI" /min cmd /c "npm run dev"
cd ..\..

timeout /t 2 /nobreak >nul
echo [*] Opening J.A.R.V.I.S. in browser...
start http://localhost:5174/

echo.
echo ===================================================
echo   [+] J.A.R.V.I.S. IS RUNNING!
echo   - Web UI:  http://localhost:5174/
echo   - Backend: http://localhost:8787/health
echo ===================================================
