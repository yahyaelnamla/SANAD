# Restore agents/ from .vite/agents backup when the package is missing or empty.
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Source = Join-Path $Root ".vite\agents"
$Target = Join-Path $Root "agents"

if (-not (Test-Path $Source)) {
    Write-Error "Backup not found: $Source"
}

$targetFiles = @(Get-ChildItem -Path $Target -Recurse -File -ErrorAction SilentlyContinue)

if ($targetFiles.Count -gt 0) {
    Write-Host "agents/ already has $($targetFiles.Count) files - skipping sync."
    exit 0
}

Write-Host "Restoring agents/ from .vite\agents ..."

robocopy $Source $Target /E /NFL /NDL /NJH /NJS /NC /NS /NP | Out-Null

if ($LASTEXITCODE -ge 8) {
    Write-Error "robocopy failed with exit code $LASTEXITCODE"
}

Write-Host "agents/ restored successfully."