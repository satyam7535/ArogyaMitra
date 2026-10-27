# ArogyaMitra — Local Environment Setup Script (PowerShell)
# Enforces Python >= 3.11, Node >= 20, uv, npm and installs all dependencies to D:

$ErrorActionPreference = "Continue"
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSNativeCommandUseErrorActionPreference = $false
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AROGYAMITRA LOCAL SETUP CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Check Python version >= 3.11
$pythonCmd = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $pythonCmd) {
    $pythonCmd = (Get-Command py -ErrorAction SilentlyContinue)
}
if (-not $pythonCmd) {
    Write-Error "Python is not installed or not in PATH."
}
$pythonVerStr = (& python --version 2>&1) -replace "Python ", ""
$pythonVer = [version]($pythonVerStr.Split('-')[0])
Write-Host "[+] Python version: $pythonVer" -ForegroundColor Green
if ($pythonVer.Major -lt 3 -or ($pythonVer.Major -eq 3 -and $pythonVer.Minor -lt 11)) {
    Write-Error "Python 3.11 or higher is required. Found: $pythonVer"
}

# 2. Check Node version >= 20
$nodeCmd = (Get-Command node -ErrorAction SilentlyContinue)
if (-not $nodeCmd) {
    Write-Error "Node.js is not installed or not in PATH."
}
$nodeVerStr = (& node -v 2>&1) -replace "v", ""
$nodeVer = [version]($nodeVerStr)
Write-Host "[+] Node version: $nodeVer" -ForegroundColor Green
if ($nodeVer.Major -lt 20) {
    Write-Error "Node.js 20 or higher is required. Found: $nodeVer"
}

# 3. Check uv
$uvCmd = (Get-Command uv -ErrorAction SilentlyContinue)
if (-not $uvCmd) {
    Write-Error "uv is not installed. Please install uv (e.g. pip install uv or via scoop/winget)."
}
Write-Host "[+] uv version: $(& uv --version)" -ForegroundColor Green

# 4. Check npm
$npmCmd = (Get-Command npm -ErrorAction SilentlyContinue)
if (-not $npmCmd) {
    Write-Error "npm is not installed."
}
Write-Host "[+] npm version: $(& npm -v)" -ForegroundColor Green

# 5. Configure D: drive caches to protect C: drive free space
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
$env:UV_CACHE_DIR = "D:\.uv_cache"
$env:npm_config_cache = "D:\.npm_cache"
$env:TEMP = "D:\temp"
$env:TMP = "D:\temp"

foreach ($dir in @("D:\.uv_cache", "D:\.npm_cache", "D:\temp")) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "[+] Configured D: caches: D:\.uv_cache, D:\.npm_cache, D:\temp" -ForegroundColor Green

# 6. Install Python dependencies via uv
Write-Host "`n[*] Installing Python virtual environment and dependencies..." -ForegroundColor Cyan
Set-Location $repoRoot
& uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Error "uv sync failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}
Write-Host "[+] Python dependencies synchronized via uv." -ForegroundColor Green

# 7. Install Backend Node dependencies
Write-Host "`n[*] Installing Backend Node dependencies..." -ForegroundColor Cyan
Set-Location (Join-Path $repoRoot "Backend")
$backendEnv = Join-Path $repoRoot "Backend\.env"
$backendEnvExample = Join-Path $repoRoot "Backend\.env.example"
if (-not (Test-Path $backendEnv) -and (Test-Path $backendEnvExample)) {
    Copy-Item $backendEnvExample $backendEnv
    Write-Host "[+] Initialized Backend\.env from .env.example" -ForegroundColor Green
}
& npm install
if ($LASTEXITCODE -ne 0) {
    Write-Error "npm install failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}
Write-Host "[+] Backend dependencies installed." -ForegroundColor Green

Set-Location $repoRoot
Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  SETUP COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
