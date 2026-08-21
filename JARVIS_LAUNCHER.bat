@echo off
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
