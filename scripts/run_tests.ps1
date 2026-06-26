$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==> Backend tests (pytest)"
python -m pytest tests/ @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Frontend tests (vitest)"
Set-Location frontend
npm test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> All tests passed"
