# ArogyaMitra — Service Health Check (PowerShell)
# Probes ports 8000, 8001, 5000, 8501 and returns a single-line status per service

$ErrorActionPreference = "Continue"

$services = @(
    @{ Name = "ML Microservice (:8000)";       Url = "http://127.0.0.1:8000/health" },
    @{ Name = "Graph AI Service (:8001)";      Url = "http://127.0.0.1:8001/health" },
    @{ Name = "Backend Gateway API (:5000)";   Url = "http://127.0.0.1:5000/health" },
    @{ Name = "Streamlit Thin-Client (:8501)";  Url = "http://127.0.0.1:8501/_stcore/health" }
)

$allHealthy = $true

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AROGYAMITRA SERVICES HEALTH STATUS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

foreach ($svc in $services) {
    try {
        $res = Invoke-WebRequest -Uri $svc.Url -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        if ($res.StatusCode -ge 200 -and $res.StatusCode -lt 400) {
            Write-Host ("{0,-35} : HEALTHY (HTTP {1})" -f $svc.Name, $res.StatusCode) -ForegroundColor Green
        } else {
            Write-Host ("{0,-35} : UNHEALTHY (HTTP {1})" -f $svc.Name, $res.StatusCode) -ForegroundColor Red
            $allHealthy = $false
        }
    } catch {
        # Fallback check for root of UI if _stcore/health is not available
        if ($svc.Url -like "*8501*") {
            try {
                $uiRes = Invoke-WebRequest -Uri "http://127.0.0.1:8501/" -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                Write-Host ("{0,-35} : HEALTHY (HTTP {1})" -f $svc.Name, $uiRes.StatusCode) -ForegroundColor Green
                continue
            } catch {}
        }
        Write-Host ("{0,-35} : DOWN ({1})" -f $svc.Name, $_.Exception.Message) -ForegroundColor Red
        $allHealthy = $false
    }
}

Write-Host "============================================================" -ForegroundColor Cyan
if ($allHealthy) {
    Write-Host "STATUS: ALL 4 SERVICES OPERATIONAL" -ForegroundColor Green
    exit 0
} else {
    Write-Host "STATUS: ONE OR MORE SERVICES DOWN OR DEGRADED" -ForegroundColor Red
    exit 1
}
