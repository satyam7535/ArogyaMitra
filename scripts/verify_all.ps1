# PowerShell verification runner for ArogyaMitra
# Runs: lint -> ML tests -> Backend tests -> Graph tests -> UI tests
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
Run-Step -Name "ML Tests (ML_Model contract & explainability)" -OutputFile "verify_ml.txt" -Action {
    $env:PYTHONPATH = (Join-Path $repoRoot "ML_Model")
    Push-Location (Join-Path $repoRoot "ML_Model")
    try {
        uv run pytest tests/test_phase1.py -v
    } finally {
        Pop-Location
    }
}

# 3. Backend Tests Step
Run-Step -Name "Backend Tests (Security, Auth, Concurrency, Crypto)" -OutputFile "verify_backend.txt" -Action {
    Push-Location (Join-Path $repoRoot "Backend")
    try {
        npm test
    } finally {
        Pop-Location
    }
}

# 4. Graph Tests Step
Run-Step -Name "Graph Tests (AI Reasoning, Fallback, Prompt Defense, PDF)" -OutputFile "verify_graph.txt" -Action {
    $env:PYTHONPATH = (Join-Path $repoRoot "graph")
    Push-Location (Join-Path $repoRoot "graph")
    try {
        uv run pytest tests/test_phase3.py -v
    } finally {
        Pop-Location
    }
}

# 5. UI Tests Step
Run-Step -Name "UI Tests (Streamlit AppTest headless suite)" -OutputFile "verify_ui.txt" -Action {
    $env:PYTHONPATH = (Join-Path $repoRoot "ui")
    Push-Location (Join-Path $repoRoot "ui")
    try {
        uv run pytest tests/test_streamlit.py -v
    } finally {
        Pop-Location
    }
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  ALL SUITES PASSED VERIFICATION" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
exit 0
