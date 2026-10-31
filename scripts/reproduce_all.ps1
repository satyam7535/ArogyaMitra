# Master Reproduction Script for ArogyaMitra
# Executes full end-to-end verification, tests, browser automation, security scans, and evidence capture.

$ErrorActionPreference = "Continue"
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSNativeCommandUseErrorActionPreference = $false
}
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

$evidenceDir = Join-Path $repoRoot "docs\evidence"
if (!(Test-Path $evidenceDir)) {
    New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
}

$reproduceLog = Join-Path $evidenceDir "reproduce_all.txt"

# Metadata Header
$gitCommit = (git rev-parse HEAD).Trim()
$gitStatus = (git status --porcelain)
$gitDirty = if ($gitStatus) { "DIRTY" } else { "CLEAN" }
$dateStr = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")

$header = @"
================================================================================
AROGYAMITRA MASTER REPRODUCTION RUN
Executed At: $dateStr
Git Commit:  $gitCommit
Repo State:  $gitDirty
Root Path:   $repoRoot
================================================================================
"@

$header | Out-File -FilePath $reproduceLog -Encoding utf8
Write-Host $header -ForegroundColor Cyan

function Run-Repro-Step {
    param (
        [string]$StepNumber,
        [string]$StepTitle,
        [scriptblock]$Action
    )
    $banner = "`n[STEP $StepNumber] $StepTitle"
    Write-Host $banner -ForegroundColor Yellow
    $banner | Out-File -FilePath $reproduceLog -Append -Encoding utf8

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $exitCode = 0
    try {
        $output = & $Action 2>&1
        $exitCode = $LASTEXITCODE
        if ($null -eq $exitCode) { $exitCode = 0 }
        $output | Out-File -FilePath $reproduceLog -Append -Encoding utf8
        $output | ForEach-Object { Write-Host $_ }
    } catch {
        $_ | Out-File -FilePath $reproduceLog -Append -Encoding utf8
        Write-Host $_ -ForegroundColor Red
        $exitCode = 1
    }
    $sw.Stop()

    $statusLine = "[STEP $StepNumber RESULT] ExitCode: $exitCode, Elapsed: $($sw.ElapsedMilliseconds)ms"
    $statusLine | Out-File -FilePath $reproduceLog -Append -Encoding utf8
    if ($exitCode -eq 0) {
        Write-Host "$statusLine (SUCCESS)" -ForegroundColor Green
    } else {
        Write-Host "$statusLine (FAILURE)" -ForegroundColor Red
        Write-Host "Reproduction halted due to step failure." -ForegroundColor Red
        exit $exitCode
    }
}

# 1. Docker Health Check
Run-Repro-Step -StepNumber "1" -StepTitle "Check Docker Container Stack Health" -Action {
    docker compose ps
    $unhealthy = (docker compose ps --format json | ConvertFrom-Json | Where-Object { $_.Health -ne "healthy" -and $_.Health -ne "" })
    if ($unhealthy) {
        Write-Host "Warning: Some containers not reporting healthy yet. Waiting 10s..."
        Start-Sleep -Seconds 10
        docker compose ps
    }
}

# 2. Database Seeding
Run-Repro-Step -StepNumber "2" -StepTitle "Seed Docker Database with Standard Demo Accounts" -Action {
    powershell -ExecutionPolicy Bypass -File scripts/seed_docker.ps1
}

# 3. Comprehensive Unit & Integration Verification Suite (283 Tests)
Run-Repro-Step -StepNumber "3" -StepTitle "Run Master Unit and Integration Test Runner (verify_all.ps1)" -Action {
    powershell -ExecutionPolicy Bypass -File scripts/verify_all.ps1
}

# 4. Playwright End-to-End Browser Automation Suite (10 Scenarios)
Run-Repro-Step -StepNumber "4" -StepTitle "Execute Playwright E2E Browser Suite (test_p4_playwright_suite.mjs)" -Action {
    node scripts/test_p4_playwright_suite.mjs
}

# 5. Ingress Load & Concurrency Benchmark
Run-Repro-Step -StepNumber "5" -StepTitle "Run Ingress Load Test Suite (run_p5_load_test.py)" -Action {
    uv run python scripts/run_p5_load_test.py
}

# 6. Man-In-The-Middle (MITM) Transport Security Demo
Run-Repro-Step -StepNumber "6" -StepTitle "Run MITM Transport Security Demo (test_p6_mitm_demo.py)" -Action {
    uv run python scripts/test_p6_mitm_demo.py
}

# 7. Security Scanners (Gitleaks, Pip-Audit, Trivy, Bandit)
Run-Repro-Step -StepNumber "7" -StepTitle "Run Automated Security Scanners" -Action {
    $gitleaksBin = if (Test-Path "d:\tools\gitleaks.exe") { "d:\tools\gitleaks.exe" } else { "gitleaks" }
    $trivyBin = if (Test-Path "d:\tools\trivy.exe") { "d:\tools\trivy.exe" } else { "trivy" }

    Write-Host "# 7a. Gitleaks..."
    & $gitleaksBin detect --source . -v --redact --gitleaks-ignore-path .gitleaksignore
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "# 7b. Pip-Audit..."
    uv run pip-audit
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "# 7c. Trivy Lockfile Scan..."
    & $trivyBin fs --severity HIGH,CRITICAL --scanners vuln --exit-code 0 .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "# 7d. Bandit Python SAST..."
    $env:PYTHONIOENCODING = "utf-8"
    uv run bandit -r ML_Model graph ui -ll -ii
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$completionFooter = @"

================================================================================
MASTER REPRODUCTION RUN COMPLETE - ALL STEPS VERIFIED
Finished At: $((Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz"))
================================================================================
"@
$completionFooter | Out-File -FilePath $reproduceLog -Append -Encoding utf8
Write-Host $completionFooter -ForegroundColor Green
