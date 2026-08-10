# Jarvis dev session — Windows (repo root)
# Usage: .\scripts\dev_up.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "== Jarvis dev_up ==" -ForegroundColor Cyan
python scripts/check_dev_env.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$portTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 8787 -WarningAction SilentlyContinue
if (-not $portTest.TcpTestSucceeded) {
    Write-Host "Starting brain (new window)..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "scripts/run_brain.py" -WorkingDirectory $Root
    Start-Sleep -Seconds 2
} else {
    Write-Host "Brain already on :8787" -ForegroundColor Green
}

Write-Host ""
Write-Host "Primary UI (chat):" -ForegroundColor Cyan
Write-Host "  cd clients\web"
Write-Host "  npm run dev"
Write-Host ""
Write-Host "Board:" -ForegroundColor Cyan
Write-Host "  python scripts/devloop.py sync --owner cursor"
Write-Host "Smoke (brain up):" -ForegroundColor Cyan
Write-Host "  python scripts/smoke_web.py"
Write-Host "Docs:" -ForegroundColor DarkGray
Write-Host "  python scripts/verify_doc_links.py"
