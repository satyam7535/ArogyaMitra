<#
.SYNOPSIS
  Resets ArogyaMitra Docker database for a pristine live demo.
.DESCRIPTION
  Clears out all consultations, patients, and audit records while
  preserving seed users (Admin, Worker, Doctor) and organizations.
  After running this, the Admin Dashboard shows 0 consultations, 0 pending,
  0 reviewed, and clean empty state tables.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "Syncing reset script into arogya-backend container..." -ForegroundColor Cyan
docker cp backend/src/scripts/resetDemoData.js arogya-backend:/app/src/scripts/resetDemoData.js

Write-Host "Resetting ArogyaMitra demo database to pristine state..." -ForegroundColor Cyan
docker exec -e NODE_ENV=development arogya-backend node src/scripts/resetDemoData.js

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDemo database reset successfully. Ready for evaluation demo." -ForegroundColor Green
} else {
    Write-Error "Demo database reset failed with exit code $LASTEXITCODE"
}
