param(
    [switch]$Background = $False
)

$ErrorActionPreference = "Stop"

$JarvisRoot = Split-Path -Parent $PSScriptRoot
$VelocityLink = Join-Path $JarvisRoot "plugins\velocity_builder"

# If JARVIS_VELOCITY_ROOT is provided, ensure the junction is correct
if ($env:JARVIS_VELOCITY_ROOT) {
    $Target = $env:JARVIS_VELOCITY_ROOT
    if (-not (Test-Path $Target)) {
        Write-Error "JARVIS_VELOCITY_ROOT points to an invalid path: $Target"
        exit 1
    }
    
    $NeedsLink = $true
    if (Test-Path $VelocityLink) {
        $item = Get-Item $VelocityLink -Force
        if ($item.Target -eq $Target -or $item.LinkTarget -eq $Target) {
            $NeedsLink = $false
        } else {
            Remove-Item $VelocityLink -Force
        }
    }
    
    if ($NeedsLink) {
        # Create directory junction
        New-Item -ItemType Junction -Path $VelocityLink -Target $Target | Out-Null
        Write-Host "Linked $VelocityLink -> $Target" -ForegroundColor Green
    }
}

if (-not (Test-Path $VelocityLink)) {
    Write-Error "Velocity path not found: $VelocityLink. Please set JARVIS_VELOCITY_ROOT to the Velocity source code directory."
    exit 1
}

Write-Host "Booting Velocity App Builder from $VelocityLink ..." -ForegroundColor Cyan

Push-Location $VelocityLink

Write-Host "Installing dependencies..." -ForegroundColor Cyan
pnpm install

if ($Background) {
    Start-Process "pnpm" -ArgumentList "dev" -WorkingDirectory $VelocityLink -NoNewWindow
    Write-Host "Velocity booted in background." -ForegroundColor Green
} else {
    pnpm dev
}

Pop-Location
