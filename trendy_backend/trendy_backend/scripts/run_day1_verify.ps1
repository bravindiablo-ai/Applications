# PowerShell helper: create venv, install Day-1 deps, create tables, start backend and check /health
param(
    [switch]$InstallOnly
)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-Not (Test-Path "$root\.venv")) {
    Write-Output "Creating .venv..."
    python -m venv .venv
}
Write-Output "Upgrading pip and installing packages..."
.\.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python -m pip install -r ..\requirements-day1.txt
Write-Output "Downloading textblob corpora..."
.\.venv\Scripts\python -m textblob.download_corpora
Write-Output "Creating DB tables..."
.\.venv\Scripts\python ..\trendy_backend\scripts\create_tables.py
if ($InstallOnly) { Write-Output "Install-only complete"; exit 0 }
Write-Output "Starting uvicorn (background)..."
Start-Process -FilePath .\.venv\Scripts\python.exe -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory $root -NoNewWindow -PassThru | Out-Null
Start-Sleep -Seconds 3
try {
    $r = Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing -TimeoutSec 5
    Write-Output "HEALTH_STATUS: $($r.StatusCode)"
    Write-Output $r.Content
} catch {
    Write-Output "HEALTH_CHECK_FAILED: $_"
    Write-Output "Check uvicorn logs or run uvicorn in foreground to see errors."
}
