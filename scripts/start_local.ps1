# ArogyaMitra — Local Services Startup Script (PowerShell)
# Starts ML (:8000), Graph (:8001), Backend (:5000), and Streamlit (:8501)
# Polls for health and records PIDs into .pids

$ErrorActionPreference = "Stop"

$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

$pidFile = Join-Path $repoRoot ".pids"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  STARTING AROGYAMITRA LOCAL SERVICES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check if .pids already exists
if (Test-Path $pidFile) {
    Write-Host "[!] Found existing .pids file. Cleaning up prior processes first..." -ForegroundColor Yellow
    & (Join-Path $PSScriptRoot "stop_local.ps1")
}

$pidsMap = [ordered]@{}

# 1. Start ML Microservice (:8000)
Write-Host "[*] Launching ML Microservice on port 8000..." -ForegroundColor Cyan
$mlProc = Start-Process -FilePath $pythonExe -ArgumentList "ML_Model\app.py" -WorkingDirectory $repoRoot -PassThru -WindowStyle Hidden
$pidsMap["ml"] = $mlProc.Id

# 2. Start Graph AI Service (:8001)
Write-Host "[*] Launching Graph AI Reasoning Service on port 8001..." -ForegroundColor Cyan
$graphProc = Start-Process -FilePath $pythonExe -ArgumentList "graph\server.py" -WorkingDirectory $repoRoot -PassThru -WindowStyle Hidden
$pidsMap["graph"] = $graphProc.Id

# 3. Start Backend Gateway (:5000)
Write-Host "[*] Launching Node Backend Gateway on port 5000..." -ForegroundColor Cyan
$backendDir = Join-Path $repoRoot "Backend"
$backendProc = Start-Process -FilePath "node" -ArgumentList "src/index.js" -WorkingDirectory $backendDir -PassThru -WindowStyle Hidden
$pidsMap["backend"] = $backendProc.Id

# 4. Start Streamlit UI (:8501)
Write-Host "[*] Launching Streamlit Clinical UI on port 8501..." -ForegroundColor Cyan
$uiDir = Join-Path $repoRoot "ui"
$uiProc = Start-Process -FilePath $pythonExe -ArgumentList @("-m", "streamlit", "run", "Home.py", "--server.port", "8501", "--server.headless", "true") -WorkingDirectory $uiDir -PassThru -WindowStyle Hidden
$pidsMap["ui"] = $uiProc.Id

# Write PIDs to .pids
$pidContent = @()
foreach ($k in $pidsMap.Keys) {
    $pidContent += "$k=$($pidsMap[$k])"
}
$pidContent | Out-File -FilePath $pidFile -Encoding ascii
Write-Host "[+] Saved process IDs to: $pidFile" -ForegroundColor Green

# Poll for health on all 4 endpoints (up to 30 seconds)
Write-Host "`n[*] Awaiting health convergence on all 4 endpoints..." -ForegroundColor Cyan
$maxAttempts = 15
$endpoints = @(
    @{ Name = "ML Microservice (:8000)";       Url = "http://127.0.0.1:8000/health" },
    @{ Name = "Graph AI Service (:8001)";      Url = "http://127.0.0.1:8001/health" },
    @{ Name = "Backend Gateway API (:5000)";   Url = "http://127.0.0.1:5000/health" },
    @{ Name = "Streamlit Thin-Client (:8501)";  Url = "http://127.0.0.1:8501/" }
)

$allUp = $false
for ($i = 1; $i -le $maxAttempts; $i++) {
    Start-Sleep -Seconds 2
    $pending = 0
    foreach ($ep in $endpoints) {
        try {
            $r = Invoke-WebRequest -Uri $ep.Url -Method Get -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            if ($r.StatusCode -lt 200 -or $r.StatusCode -ge 400) { $pending++ }
        } catch {
            $pending++
        }
    }
    if ($pending -eq 0) {
        $allUp = $true
        break
    }
    Write-Host "    Attempt $i of ${maxAttempts}: $pending service(s) still warming up..." -ForegroundColor Yellow
}

if ($allUp) {
    Write-Host "`n[+] All 4 services confirmed healthy and operational!" -ForegroundColor Green
    & (Join-Path $PSScriptRoot "health_check.ps1")
    exit 0
} else {
    Write-Host "`n[!] Timeout waiting for services to converge." -ForegroundColor Red
    & (Join-Path $PSScriptRoot "health_check.ps1")
    exit 1
}
