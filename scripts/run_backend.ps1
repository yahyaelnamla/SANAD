# Run SANAD API locally (outside Docker) with correct PYTHONPATH.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

& (Join-Path $Root "scripts\sync_agents.ps1")

$env:PYTHONPATH = $Root
Write-Host "Starting SANAD backend on http://0.0.0.0:8000 (PYTHONPATH=$Root)"
Write-Host ""
Write-Host "WARNING: Stop Docker backend first if running (docker stop sanad-backend)" -ForegroundColor Yellow
Write-Host "         Or use .\scripts\start-sanad.ps1 for the full Docker stack instead." -ForegroundColor Yellow
Write-Host ""
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
