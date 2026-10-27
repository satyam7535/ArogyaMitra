# ArogyaMitra — Fresh Clone Lifecycle Driver
# Tests: clone -> setup_local -> start_local -> health_check -> stop_local
# Saves raw transcript to docs/evidence/fresh_clone_sanity.txt

$ErrorActionPreference = "Continue"

$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
$cloneDir = "D:\temp\arogyamitra_fresh_clone"
$evidenceFile = Join-Path $repoRoot "docs\evidence\fresh_clone_sanity.txt"

$log = @()
function Emit([string]$line) {
    Write-Host $line
    $script:log += $line
}

Emit "================================================================================"
Emit "AROGYAMITRA FRESH-CLONE LIFECYCLE SANITY TRANSCRIPT"
Emit "Timestamp: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
Emit "Origin Repository: $repoRoot"
Emit "Target Clone Directory: $cloneDir"
Emit "================================================================================`n"

# 1. Stop services in primary repo to ensure ports 8000, 8001, 5000, 8501 are free
Emit "[*] Freeing all local ports before starting fresh clone test..."
& (Join-Path $repoRoot "scripts\stop_local.ps1") | ForEach-Object { Emit $_ }

# 2. Clean up any previous clone dir
if (Test-Path $cloneDir) {
    Emit "[*] Removing previous clone directory $cloneDir..."
    Remove-Item -Recurse -Force $cloneDir -ErrorAction SilentlyContinue
}

# 3. Clone repository
Emit "`n--- STEP 1: git clone . $cloneDir ---"
$cloneOutput = git clone --branch remediation $repoRoot $cloneDir 2>&1
$cloneOutput | ForEach-Object { Emit $_ }
if ($LASTEXITCODE -ne 0) {
    Emit "[!] git clone failed with exit code $LASTEXITCODE"
    exit 1
}
Emit "[+] git clone completed successfully."

# Provide .env to Backend in fresh clone (since .env is gitignored for security)
if (Test-Path (Join-Path $repoRoot "Backend\.env")) {
    Copy-Item (Join-Path $repoRoot "Backend\.env") (Join-Path $cloneDir "Backend\.env")
    Emit "[+] Injected active Backend\.env (with Atlas DB_URL) into fresh clone directory."
}

# 4. Run setup_local.ps1 in clone
Emit "`n--- STEP 2: Running setup_local.ps1 in fresh clone ---"
Set-Location $cloneDir
$setupOutput = & (Join-Path $cloneDir "scripts\setup_local.ps1") 2>&1
$setupOutput | ForEach-Object { Emit $_ }
Emit "setup_local exit code: $LASTEXITCODE"

# 5. Run start_local.ps1 in clone
Emit "`n--- STEP 3: Running start_local.ps1 in fresh clone ---"
$startOutput = & (Join-Path $cloneDir "scripts\start_local.ps1") 2>&1
$startOutput | ForEach-Object { Emit $_ }
Emit "start_local exit code: $LASTEXITCODE"

# 6. Run health_check.ps1 in clone
Emit "`n--- STEP 4: Running health_check.ps1 in fresh clone ---"
$healthOutput = & (Join-Path $cloneDir "scripts\health_check.ps1") 2>&1
$healthOutput | ForEach-Object { Emit $_ }
Emit "health_check exit code: $LASTEXITCODE"

# 7. Stop services in clone
Emit "`n--- STEP 5: Running stop_local.ps1 in fresh clone ---"
$stopOutput = & (Join-Path $cloneDir "scripts\stop_local.ps1") 2>&1
$stopOutput | ForEach-Object { Emit $_ }
Emit "stop_local exit code: $LASTEXITCODE"

# 8. Clean up clone directory
Emit "`n[*] Cleaning up clone directory $cloneDir..."
Set-Location $repoRoot
Remove-Item -Recurse -Force $cloneDir -ErrorAction SilentlyContinue
Emit "[+] Cleaned up $cloneDir."

# 9. Restart primary repository services
Emit "`n[*] Restarting primary repository services..."
$restartOutput = & (Join-Path $repoRoot "scripts\start_local.ps1") 2>&1
$restartOutput | ForEach-Object { Emit $_ }

# 10. Write transcript to evidence file
$log | Out-File -FilePath $evidenceFile -Encoding utf8
Emit "`n[+] Fresh-clone transcript saved to: $evidenceFile"
