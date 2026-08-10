# Stop Jarvis Windows client, orphaned Flet desktops, and optional brain on :8787.
$ErrorActionPreference = "SilentlyContinue"

function Stop-ProcId {
    param([int]$Pid, [string]$Label)
    if ($Pid -le 0) { return }
    Write-Host "Stopping $Label PID $Pid"
    Stop-Process -Id $Pid -Force -ErrorAction SilentlyContinue
}

# Flet desktop helpers (Task Manager: "Flet description") — taskkill is most reliable.
$null = cmd /c "taskkill /F /IM flet.exe 2>nul"

$cmdPatterns = @(
    '(?i)jarvis',
    '(?i)clients[\\/]windows[\\/]client',
    '(?i)test_ui_smoke',
    '(?i)\\flet\\',
    '(?i)flet_desktop',
    '(?i)flet\.exe',
    '(?i)uvicorn.*app\.main'
)

Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '(?i)^flet$' } | ForEach-Object {
    Stop-ProcId -Pid $_.Id -Label "flet"
}

Get-CimInstance Win32_Process | ForEach-Object {
    $name = $_.Name
    $cmd = $_.CommandLine
    $match = $false
    if ($name -match '(?i)flet\.exe') { $match = $true }
    if ($cmd) {
        foreach ($p in $cmdPatterns) {
            if ($cmd -match $p) { $match = $true; break }
        }
    }
    if ($match) {
        Stop-ProcId -Pid $_.ProcessId -Label $name
    }
}

foreach ($p in 8787) {
    Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue | ForEach-Object {
        Stop-ProcId -Pid $_.OwningProcess -Label "port $p listener"
    }
}

Start-Sleep -Milliseconds 400
$null = cmd /c "taskkill /F /IM flet.exe 2>nul"

$fletLeft = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '(?i)^flet$' }).Count
$clientLeft = @(
    Get-CimInstance Win32_Process |
        Where-Object { $_.CommandLine -match '(?i)clients[\\/]windows[\\/]client' }
).Count
Write-Host "Done. flet.exe left: $fletLeft | client.py left: $clientLeft"
