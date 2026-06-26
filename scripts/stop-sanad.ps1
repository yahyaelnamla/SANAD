$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Stopping SANAD Docker stack ..."
docker compose down --remove-orphans
Write-Host "Done. Ports 3000 and 8000 are free for local dev if needed."
