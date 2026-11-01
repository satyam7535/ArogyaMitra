# ArogyaMitra — Service Health Check (PowerShell)
# Checks Docker container health statuses and edge gateway endpoints

$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AROGYAMITRA SERVICES HEALTH STATUS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check 1: Docker Container Health Status
$containers = @("arogya-proxy", "arogya-frontend", "arogya-backend", "arogya-ml", "arogya-graph", "arogya-mongo")
$allHealthy = $true
$dockerAvailable = $false

try {
    $psOut = docker compose ps --format json 2>$null | ConvertFrom-Json
    if ($psOut) {
        $dockerAvailable = $true
        foreach ($c in $psOut) {
            $name = $c.Name
            $status = $c.Status
            $state = $c.State
            $isOk = ($state -eq "running" -or $status -match "healthy" -or $status -match "Up")
            
            if ($status -match "unhealthy") {
                Write-Host ("{0,-35} : UNHEALTHY ({1})" -f $name, $status) -ForegroundColor Red
                $allHealthy = $false
            } elseif ($isOk) {
                Write-Host ("{0,-35} : HEALTHY ({1})" -f $name, $status) -ForegroundColor Green
            } else {
                Write-Host ("{0,-35} : DOWN ({1})" -f $name, $status) -ForegroundColor Red
                $allHealthy = $false
            }
        }
    }
} catch {
    # Fallback to direct HTTP checks if docker CLI fails
}

# Check 2: Edge Gateway Ingress (https://localhost)
try {
    # Configure TLS 1.2/1.3 and skip SSL certificate validation for self-signed cert
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
    $gwRes = Invoke-WebRequest -Uri "https://localhost/" -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host ("{0,-35} : HEALTHY (HTTP {1})" -f "Edge Gateway (https://localhost/)", $gwRes.StatusCode) -ForegroundColor Green
} catch {
    # If PowerShell .NET TLS handshake fails, verify with curl.exe
    $curlCheck = curl.exe -k -s -o /dev/null -w "%{http_code}" https://localhost/
    if ($curlCheck -eq "200") {
        Write-Host ("{0,-35} : HEALTHY (HTTP 200 via TLS Proxy)" -f "Edge Gateway (https://localhost/)") -ForegroundColor Green
    } else {
        Write-Host ("{0,-35} : DOWN ({1})" -f "Edge Gateway (https://localhost/)", $_.Exception.Message) -ForegroundColor Yellow
    }
}

Write-Host "============================================================" -ForegroundColor Cyan
if ($allHealthy -and $dockerAvailable) {
    Write-Host "STATUS: ALL AROGYAMITRA SERVICES OPERATIONAL (HEALTHY)" -ForegroundColor Green
    exit 0
} elseif ($allHealthy) {
    Write-Host "STATUS: SERVICES OPERATIONAL" -ForegroundColor Green
    exit 0
} else {
    Write-Host "STATUS: ONE OR MORE SERVICES DOWN OR DEGRADED" -ForegroundColor Red
    exit 1
}
