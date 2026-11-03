# PowerShell verification runner for ArogyaMitra
# Runs: lint -> ML tests -> Backend tests -> Graph tests -> UI tests
# Dynamically parses passed/failed counts from test tool outputs.
# Exits non-zero on any failure and writes each output to docs/evidence/verify_<suite>.txt

$ErrorActionPreference = "Continue"
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSNativeCommandUseErrorActionPreference = $false
}
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

$evidenceDir = Join-Path $repoRoot "docs\evidence"
if (!(Test-Path $evidenceDir)) {
    New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
}

function Run-Step {
    param (
        [string]$Name,
        [string]$OutputFile,
        [scriptblock]$Action
    )
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  RUNNING: $Name" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    $fullOutputPath = Join-Path $evidenceDir $OutputFile

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $exitCode = 0
    try {
        $output = & $Action 2>&1
        $exitCode = $LASTEXITCODE
        if ($null -eq $exitCode) { $exitCode = 0 }
        $output | Out-File -FilePath $fullOutputPath -Encoding utf8
        $output | ForEach-Object { Write-Host $_ }
    } catch {
        $_ | Out-File -FilePath $fullOutputPath -Append -Encoding utf8
        Write-Host $_ -ForegroundColor Red
        $exitCode = 1
    }
    $sw.Stop()

    if ($exitCode -ne 0) {
        Write-Host "FAILED: $Name (exit code $exitCode) in $($sw.ElapsedMilliseconds)ms" -ForegroundColor Red
        Write-Host "See logs at: $fullOutputPath" -ForegroundColor Red
        exit $exitCode
    } else {
        Write-Host "PASSED: $Name in $($sw.ElapsedMilliseconds)ms" -ForegroundColor Green
    }
}

# 1. Lint Step
Run-Step -Name "Lint (Python Ruff & Node ESLint)" -OutputFile "verify_lint.txt" -Action {
    Write-Host "# Running ruff check on ML_Model, graph, ui..."
    uv run ruff check ML_Model graph ui
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "# Running ESLint on Backend/src..."
    npm --prefix Backend run lint
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "# Running Node syntax check on Backend/src..."
    $files = Get-ChildItem -Path "Backend\src" -Filter "*.js" -Recurse
    foreach ($file in $files) {
        node --check $file.FullName
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    Write-Host "Lint checks completed successfully."
}

# 2. ML Tests Step
Run-Step -Name "ML Tests (ML_Model Phase 0 & Phase 1 contracts)" -OutputFile "verify_ml.txt" -Action {
    uv run pytest ML_Model/tests/ -v
}

# 3. Backend Tests Step
Run-Step -Name "Backend Tests (Security, Auth, Concurrency, Crypto)" -OutputFile "verify_backend.txt" -Action {
    npm --prefix Backend test
}

# 4. Graph Tests Step
Run-Step -Name "Graph Tests (AI Reasoning, Fallback, Prompt Defense, PDF)" -OutputFile "verify_graph.txt" -Action {
    uv run pytest graph/tests/ -v
}

# 5. UI Tests Step
Run-Step -Name "UI Tests (Streamlit AppTest headless suite)" -OutputFile "verify_ui.txt" -Action {
    uv run pytest ui/tests/ -v
}

# ── Dynamic Result Parsing ───────────────────────────────────────────────────
$mlFile = Join-Path $evidenceDir "verify_ml.txt"
$backendFile = Join-Path $evidenceDir "verify_backend.txt"
$graphFile = Join-Path $evidenceDir "verify_graph.txt"
$uiFile = Join-Path $evidenceDir "verify_ui.txt"

$mlPassed = 0
$backendPassed = 0
$graphPassed = 0
$uiPassed = 0

if (Test-Path $mlFile) {
    $content = (Get-Content $mlFile -Raw)
    if ($content -match '=\s*(\d+)\s+passed') { $mlPassed = [int]$matches[1] }
}

if (Test-Path $backendFile) {
    $rawContent = (Get-Content $backendFile -Raw)
    # Strip ANSI escape codes
    $cleanContent = $rawContent -replace "\x1b\[[0-9;]*[a-zA-Z]", ""
    if ($cleanContent -match 'Tests\s+(\d+)\s+passed') {
        $backendPassed = [int]$matches[1]
    } elseif ($cleanContent -match '(\d+)\s+passed') {
        $backendPassed = [int]$matches[1]
    }
}

if (Test-Path $graphFile) {
    $content = (Get-Content $graphFile -Raw)
    if ($content -match '=\s*(\d+)\s+passed') { $graphPassed = [int]$matches[1] }
}

if (Test-Path $uiFile) {
    $content = (Get-Content $uiFile -Raw)
    if ($content -match '=\s*(\d+)\s+passed') { $uiPassed = [int]$matches[1] }
}

$totalPassed = $mlPassed + $backendPassed + $graphPassed + $uiPassed

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  ALL SUITES PASSED VERIFICATION" -ForegroundColor Green
Write-Host "  Test Summary (Dynamically Parsed):" -ForegroundColor Green
Write-Host "    - ML Tests:      $mlPassed passed" -ForegroundColor Green
Write-Host "    - Backend Tests: $backendPassed passed" -ForegroundColor Green
Write-Host "    - Graph Tests:   $graphPassed passed" -ForegroundColor Green
Write-Host "    - UI Tests:      $uiPassed passed" -ForegroundColor Green
Write-Host "    - Total Tests:   $totalPassed passed (0 failed)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
