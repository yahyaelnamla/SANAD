# SANAD — one-command Docker startup (recommended)
#
# Usage:
#   .\scripts\start-sanad.ps1           # start full stack
#   .\scripts\start-sanad.ps1 -Rebuild  # rebuild images + fresh .next cache
#   .\scripts\stop-sanad.ps1              # stop stack
#   .\scripts\verify-sanad.ps1            # health + auth smoke test
#
# IMPORTANT: Do NOT also run these while Docker is up:
#   - python -m uvicorn ... --port 8000
#   - cd frontend && npm run dev
# They conflict on ports 8000 and 3000.

param(
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Test-PortInUse([int]$Port) {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $conn
}

Write-Host ""
Write-Host "=== SANAD startup ===" -ForegroundColor Cyan
Write-Host ""

# Warn if local dev servers would conflict (not owned by Docker is hard to detect; warn on listeners)
foreach ($port in @(3000, 8000)) {
    if (Test-PortInUse $port) {
        Write-Host "WARNING: Port $port is already in use." -ForegroundColor Yellow
        Write-Host "  Stop local uvicorn/npm OR run: docker compose down" -ForegroundColor Yellow
    }
}

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example ..."
    Copy-Item ".env.example" ".env"
    Write-Host "  Edit .env and set JWT_SECRET + POSTGRES_PASSWORD if needed." -ForegroundColor Yellow
}

Write-Host "==> Sync agents package (if empty)"
& (Join-Path $Root "scripts\sync_agents.ps1")

$composeArgs = @("compose", "up", "-d", "--remove-orphans")
if ($Rebuild) {
    Write-Host "==> Rebuilding Docker images + clearing frontend cache volume ..."
    docker compose down
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    docker volume rm sanad_frontend_next_cache -f 2>$null | Out-Null
    $composeArgs += "--build"
}

Write-Host "==> Starting Docker stack (postgres, redis, backend, celery, frontend) ..."
docker @composeArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "==> Waiting for services (up to 2 min) ..."
& (Join-Path $Root "scripts\verify-sanad.ps1") -WaitSeconds 120
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Stack started but verification failed. Check logs:" -ForegroundColor Red
    Write-Host "  docker compose logs -f backend frontend" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== SANAD is ready ===" -ForegroundColor Green
Write-Host "  Welcome:  http://localhost:3000/welcome"
Write-Host "  Chat:     http://localhost:3000/chat   (after login)"
Write-Host "  API docs: http://localhost:8000/api/v1/docs"
Write-Host ""
Write-Host "Tips:" -ForegroundColor Cyan
Write-Host "  - Hard refresh browser: Ctrl+Shift+R (clears stale UI cache)"
Write-Host "  - Do NOT run uvicorn or npm run dev while Docker is running"
Write-Host "  - Logs: docker compose logs -f frontend backend"
Write-Host ""
