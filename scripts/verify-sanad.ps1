param(
    [int]$WaitSeconds = 60
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Wait-ForUrl([string]$Url, [int]$TimeoutSec) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -MaximumRedirection 5
            if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400) { return $true }
        } catch {
            Start-Sleep -Seconds 3
        }
    }
    return $false
}

Write-Host "==> Verify backend health"
if (-not (Wait-ForUrl "http://localhost:8000/api/v1/health/live" $WaitSeconds)) {
    Write-Host "FAIL: backend not healthy on :8000" -ForegroundColor Red
    exit 1
}
Write-Host "OK  backend :8000"

Write-Host "==> Verify frontend + API proxy"
if (-not (Wait-ForUrl "http://localhost:3000/api/v1/health/live" $WaitSeconds)) {
    Write-Host "FAIL: frontend API proxy not working on :3000" -ForegroundColor Red
    exit 1
}
Write-Host "OK  frontend proxy /api -> backend"

Write-Host "==> Verify welcome page"
if (-not (Wait-ForUrl "http://localhost:3000/welcome" $WaitSeconds)) {
    Write-Host "FAIL: /welcome not reachable" -ForegroundColor Red
    exit 1
}
Write-Host "OK  /welcome"

Write-Host "==> Verify root redirect to welcome"
try {
    $root = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -MaximumRedirection 0 -ErrorAction Stop
} catch {
    if ($_.Exception.Response.StatusCode -eq 307 -or $_.Exception.Response.StatusCode -eq 308) {
        $loc = $_.Exception.Response.Headers.Location
        if ($loc -match "welcome") {
            Write-Host "OK  / -> /welcome redirect"
        } else {
            Write-Host "FAIL: / redirects to $loc (expected /welcome)" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "FAIL: / redirect check: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "==> Verify auth register + login"
$email = "verify{0}@example.com" -f (Get-Random)
$password = "SecurePass123!"
$registerBody = @{ email = $email; password = $password; locale = "en" } | ConvertTo-Json
try {
    $reg = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/register" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "OK  register ($($reg.email))"
} catch {
    Write-Host "FAIL: register - $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

$loginBody = @{ email = $email; password = $password } | ConvertTo-Json
try {
    $login = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    if ($login.access_token) {
        Write-Host "OK  login (JWT received)"
    } else {
        Write-Host "FAIL: login - no token" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "FAIL: login - $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All checks passed." -ForegroundColor Green
exit 0
