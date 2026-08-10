param(
    [switch] = False
)

 = Join-Path  "..\plugins\velocity_builder"
Write-Host "Booting Velocity App Builder from ..." -ForegroundColor Cyan

if () {
    Start-Process "pnpm" -ArgumentList "dev" -WorkingDirectory  -NoNewWindow
    Write-Host "Velocity booted in background." -ForegroundColor Green
} else {
    Set-Location 
    pnpm dev
}
