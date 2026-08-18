@echo off
setlocal enabledelayedexpansion
title JARVIS AI System Launcher
cd /d "%~dp0"

echo ======================================================================
echo           J.A.R.V.I.S. SYSTEM LAUNCH AND INITIALIZATION
echo ======================================================================
echo.

:: 1. Diagnostic: Python check
echo [1/3] Checking Python Environment...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "C:\Python314\python.exe" (
        set "PYTHON_EXE=C:\Python314\python.exe"
        echo       Found Python at C:\Python314\python.exe
    ) else (
        echo [ERROR] Python not found in system PATH.
        pause
        exit /b 1
    )
) else (
    set "PYTHON_EXE=python"
    echo       Python is ready in PATH.
)

:: 2. Launch Brain Backend
echo [2/3] Launching Jarvis Brain Backend (FastAPI on http://127.0.0.1:8787)...
start "Jarvis Brain Backend" cmd /k "%PYTHON_EXE% -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8787"

:: 3. Launch Web Client
echo [3/3] Launching Jarvis Web Client UI...
cd clients\web
start "Jarvis Web UI" cmd /k "npm run preview -- --port 4173 --host 127.0.0.1"
cd ..\..

:: 4. Health Check wait
echo.
echo [*] Waiting 3 seconds for services to initialize...
timeout /t 3 /nobreak >nul

echo [*] Opening J.A.R.V.I.S. in your default web browser...
start http://localhost:4173/

echo.
echo ======================================================================
echo   [SUCCESS] J.A.R.V.I.S. Launched!
echo   * Web UI:        http://localhost:4173/
echo   * Backend Brain: http://127.0.0.1:8787/health
echo   * Metrics:       http://127.0.0.1:8787/metrics
echo ======================================================================
echo.
