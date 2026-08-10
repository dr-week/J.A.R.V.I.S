# Jarvis — presentation launcher (Windows)
# Starts brain + web dev server. See docs/DEMO.md
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host ""
Write-Host "  Jarvis demo" -ForegroundColor Cyan
Write-Host "  -----------" -ForegroundColor DarkGray
Write-Host ""

if (-not (Test-Path "$Root\.env")) {
    Copy-Item "$Root\.env.example" "$Root\.env"
    Write-Host "  Created .env from .env.example" -ForegroundColor Yellow
    Write-Host "  Set GEMINI_API_KEY in .env for live chat." -ForegroundColor Yellow
    Write-Host ""
}

python scripts/check_dev_env.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Fix environment errors above, then re-run demo_up." -ForegroundColor Red
    exit $LASTEXITCODE
}

$portTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 8787 -WarningAction SilentlyContinue
if (-not $portTest.TcpTestSucceeded) {
    Write-Host "  Starting brain..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "scripts/run_brain.py" -WorkingDirectory $Root
    Start-Sleep -Seconds 3
} else {
    Write-Host "  Brain already on :8787" -ForegroundColor Green
}

$webDir = Join-Path $Root "clients\web"
if (-not (Test-Path (Join-Path $webDir "node_modules"))) {
    Write-Host "  Installing web dependencies (first run)..." -ForegroundColor Yellow
    Push-Location $webDir
    npm install
    Pop-Location
}

$viteTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 5173 -WarningAction SilentlyContinue
if (-not $viteTest.TcpTestSucceeded) {
    Write-Host "  Starting web UI..." -ForegroundColor Yellow
    Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory $webDir
    Start-Sleep -Seconds 4
} else {
    Write-Host "  Web dev server already on :5173" -ForegroundColor Green
}

Write-Host ""
Write-Host "  Open:  http://localhost:5173" -ForegroundColor Green
Write-Host "  Health: http://localhost:8787/health" -ForegroundColor DarkGray
Write-Host "  Guide:  docs\DEMO.md" -ForegroundColor DarkGray
Write-Host ""

try {
    Start-Process "http://localhost:5173"
} catch {
    Write-Host "  Open the URL above in your browser." -ForegroundColor Yellow
}
