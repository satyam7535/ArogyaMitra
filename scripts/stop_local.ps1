# ArogyaMitra — Local Services Shutdown Script (PowerShell)
# Reads .pids, stops background processes, frees ports 8000, 8001, 5000, 8501

$ErrorActionPreference = "Continue"

$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
$pidFile = Join-Path $repoRoot ".pids"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  STOPPING AROGYAMITRA LOCAL SERVICES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Terminate tracked PIDs
if (Test-Path $pidFile) {
    $lines = Get-Content $pidFile
    foreach ($line in $lines) {
        if ($line -match "^(\w+)=(\d+)$") {
            $name = $matches[1]
            $pidToKill = [int]$matches[2]
            try {
                $proc = Get-Process -Id $pidToKill -ErrorAction Stop
                Write-Host "[*] Stopping $name (PID $pidToKill)..." -ForegroundColor Yellow
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
            } catch {
                # Already stopped
            }
        }
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}

# 2. Port sweep to guarantee ports 8000, 8001, 5000, 8501 are completely freed
$ports = @(8000, 8001, 5000, 8501)
foreach ($port in $ports) {
    try {
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            $p = $c.OwningProcess
            if ($p -and $p -gt 4) {
                Write-Host "[*] Terminating lingering process on port $port (PID $p)..." -ForegroundColor Yellow
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        # Fallback to netstat if Get-NetTCPConnection not available
        $netstat = netstat -ano | Select-String ":$port\s+.*LISTENING\s+(\d+)"
        foreach ($match in $netstat) {
            if ($match.Line -match ":$port\s+.*LISTENING\s+(\d+)") {
                $p = [int]$matches[1]
                if ($p -gt 4) {
                    Write-Host "[*] Terminating lingering process on port $port (PID $p)..." -ForegroundColor Yellow
                    Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
                }
            }
        }
    }
}

Start-Sleep -Seconds 1
Write-Host "`n[+] All ArogyaMitra services stopped and ports freed." -ForegroundColor Green
