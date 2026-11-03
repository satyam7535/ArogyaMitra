<#
.SYNOPSIS
  Seeds the ArogyaMitra Docker database with demo users, organizations, patients, and consultations.
.DESCRIPTION
  Safely overrides NODE_ENV to development inside the container for the seeding script,
  preserving production safeguards on the running backend server.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "Seeding ArogyaMitra Docker database..." -ForegroundColor Cyan
docker exec -e NODE_ENV=development arogya-backend node src/scripts/seedDemo.js

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDocker database seeded successfully." -ForegroundColor Green
} else {
    Write-Error "Database seeding failed with exit code $LASTEXITCODE"
}

