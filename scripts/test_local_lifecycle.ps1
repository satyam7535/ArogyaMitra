# ArogyaMitra — Helper Scripts Sanity Test Driver
# Tests: health_check -> stop_local -> health_check (all dead) -> start_local -> health_check (all healthy)

$ErrorActionPreference = "Continue"

$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

$evidenceFile = Join-Path $repoRoot "docs\evidence\local_scripts_sanity.txt"
$evidenceDir = Split-Path $evidenceFile -Parent
if (-not (Test-Path $evidenceDir)) {
    New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
}

$output = @()

function Log-Output([string]$msg) {
    Write-Host $msg
    $script:output += $msg
}

Log-Output "================================================================================"
Log-Output "AROGYAMITRA LOCAL SCRIPTS SANITY VERIFICATION (start_local / stop_local / health_check)"
Log-Output "Timestamp: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
Log-Output "================================================================================`n"

Log-Output "--- STEP 1: Running initial health check on currently active services ---"
$step1 = & (Join-Path $PSScriptRoot "health_check.ps1") 2>&1
$step1 | ForEach-Object { Log-Output $_ }
Log-Output "Exit code: $LASTEXITCODE`n"

Log-Output "--- STEP 2: Running stop_local.ps1 to cleanly stop all services and free ports ---"
$step2 = & (Join-Path $PSScriptRoot "stop_local.ps1") 2>&1
$step2 | ForEach-Object { Log-Output $_ }
Log-Output "Exit code: $LASTEXITCODE`n"

Log-Output "--- STEP 3: Running health_check.ps1 after stop (ALL SERVICES MUST BE DOWN) ---"
$step3 = & (Join-Path $PSScriptRoot "health_check.ps1") 2>&1
$step3 | ForEach-Object { Log-Output $_ }
Log-Output "Exit code: $LASTEXITCODE (Expected non-zero)`n"

Log-Output "--- STEP 4: Running start_local.ps1 to launch all services and verify health convergence ---"
$step4 = & (Join-Path $PSScriptRoot "start_local.ps1") 2>&1
$step4 | ForEach-Object { Log-Output $_ }
Log-Output "Exit code: $LASTEXITCODE`n"

Log-Output "--- STEP 5: Final health_check.ps1 (ALL 4 SERVICES MUST BE HEALTHY) ---"
$step5 = & (Join-Path $PSScriptRoot "health_check.ps1") 2>&1
$step5 | ForEach-Object { Log-Output $_ }
Log-Output "Exit code: $LASTEXITCODE (Expected 0)`n"

$output | Out-File -FilePath $evidenceFile -Encoding utf8
Write-Host "`nSanity verification transcript written to: $evidenceFile" -ForegroundColor Green
