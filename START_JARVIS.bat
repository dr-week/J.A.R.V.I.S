@echo off
setlocal enabledelayedexpansion
title JARVIS AI System Launcher
cd /d "%~dp0"

echo ======================================================================
echo           J.A.R.V.I.S. SYSTEM LAUNCH & DIAGNOSTICS
echo ======================================================================
echo.

:: 1. Diagnostic: Python
echo [1/4] Checking Python Environment...
python --version > logs\python_check.tmp 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in system PATH!
    pause
    exit /b 1
)
set /p PY_VER=<logs\python_check.tmp
echo       Found: %PY_VER%
del logs\python_check.tmp >nul 2>&1

:: 2. Diagnostic: Node / npm
echo [2/4] Checking Node.js / npm Environment...
call npm --version > logs\npm_check.tmp 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm / Node.js not found in system PATH!
    pause
    exit /b 1
)
set /p NPM_VER=<logs\npm_check.tmp
echo       Found npm version: %NPM_VER%
del logs\npm_check.tmp >nul 2>&1

:: 3. Ensure logs directory exists
if not exist "logs" mkdir logs

:: 4. Start Brain Backend
echo [3/4] Launching Jarvis Brain Backend (FastAPI on :8787)...
start "Jarvis Brain Backend" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8787"

:: 5. Start Web Client (Vite Preview on Production Build or Dev)
echo [4/4] Launching Jarvis Web Client UI...
cd clients\web
if exist "dist\index.html" (
    echo       Using compiled production UI bundle (port 4173)...
    start "Jarvis Web UI" cmd /k "npm run preview -- --port 4173 --host 127.0.0.1"
    set TARGET_URL=http://localhost:4173/
) else (
    echo       Starting dev server...
    start "Jarvis Web UI" cmd /k "npm run dev -- --host 127.0.0.1"
    set TARGET_URL=http://localhost:5173/
)
cd ..\..

:: 6. Health Check wait
echo.
echo [*] Waiting 3 seconds for services to initialize...
timeout /t 3 /nobreak >nul

echo [*] Opening J.A.R.V.I.S. in your default web browser...
start %TARGET_URL%

echo.
echo ======================================================================
echo   [SUCCESS] J.A.R.V.I.S. Launched!
echo   * Web UI:        %TARGET_URL%
echo   * Backend Brain: http://127.0.0.1:8787/health
echo   * Metrics:       http://127.0.0.1:8787/metrics
echo ======================================================================
echo.
