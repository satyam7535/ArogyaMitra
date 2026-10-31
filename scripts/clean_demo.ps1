<#
.SYNOPSIS
  Clean teardown and fresh bootstrap of ArogyaMitra Docker stack with pristine demo data.
.DESCRIPTION
  Tears down running containers and wipes the MongoDB volume (down -v),
  starts all 6 services with fresh health probes (up -d),
  waits for MongoDB and backend to report healthy,
  and seeds fresh baseline demo accounts and patients without any load-test records.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AROGYAMITRA — CLEAN DEMO STACK RESET" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "[1/4] Stopping stack and removing all volumes (-v)..." -ForegroundColor Yellow
docker compose down -v --remove-orphans

Write-Host "[2/4] Starting fresh container stack..." -ForegroundColor Yellow
docker compose up -d

Write-Host "[3/4] Waiting for all services to report healthy..." -ForegroundColor Yellow
$timeout = 90
$elapsed = 0
while ($elapsed -lt $timeout) {
    Start-Sleep -Seconds 3
    $elapsed += 3
    $unhealthy = docker ps --filter "label=com.docker.compose.project=arogyamitra" --format "{{.Names}}: {{.Status}}" | Select-String "starting|unhealthy"
    if (-not $unhealthy) {
        Write-Host "  All containers healthy after ${elapsed}s." -ForegroundColor Green
        break
    }
    Write-Host "  Waiting for containers to become healthy (${elapsed}s)..." -ForegroundColor Gray
}

Write-Host "[4/4] Seeding pristine demo fixtures (fake data only, 0 load-test records)..." -ForegroundColor Yellow
docker exec -e NODE_ENV=development arogya-backend node src/scripts/seedDemo.js

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  CLEAN DEMO READY at https://localhost" -ForegroundColor Green
Write-Host "  Seeded Accounts:" -ForegroundColor Green
Write-Host "    - Worker:  worker1@arogyamitra.org / Password123!" -ForegroundColor White
Write-Host "    - Doctor:  doc1@arogyamitra.org    / Password123!" -ForegroundColor White
Write-Host "    - Admin:   admin1@arogyamitra.org  / Password123!" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green

