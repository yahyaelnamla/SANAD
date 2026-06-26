$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$EnvFile = if ($args.Count -gt 0) { $args[0] } else { ".env" }

if (-not (Test-Path $EnvFile)) {
    Write-Error "Environment file not found: $EnvFile. Copy .env.example to .env first."
}

docker compose -p sanad-prod -f docker-compose.prod.yml --env-file $EnvFile up -d --build
Write-Host "==> Production stack started. Verify: curl http://127.0.0.1/api/v1/health/ready"
