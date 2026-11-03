# Pure Trivy command execution without manual annotations
$ErrorActionPreference = "Continue"

$images = @(
    "arogyamitra-backend:latest",
    "arogyamitra-frontend:latest",
    "arogyamitra-ml:latest",
    "arogyamitra-graph:latest"
)

$outputFile = "docs/evidence/trivy_all_images_scan.txt"
Remove-Item -Path $outputFile -Force -ErrorAction SilentlyContinue

foreach ($img in $images) {
    Write-Output "================================================================================" | Out-File -FilePath $outputFile -Append -Encoding utf8
    Write-Output "TRIVY SCAN TARGET: $img" | Out-File -FilePath $outputFile -Append -Encoding utf8
    Write-Output "COMMAND: trivy image --scanners vuln $img" | Out-File -FilePath $outputFile -Append -Encoding utf8
    Write-Output "================================================================================" | Out-File -FilePath $outputFile -Append -Encoding utf8
    & d:\tools\trivy.exe image --scanners vuln $img | Out-File -FilePath $outputFile -Append -Encoding utf8
}

