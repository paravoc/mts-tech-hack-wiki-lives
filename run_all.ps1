$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Join-Path $root "logs"
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$backendLog = Join-Path $logDir "backend.log"
$frontendLog = Join-Path $logDir "frontend.log"

Get-Process | Where-Object { $_.ProcessName -match "wikilive|python|node|streamlit" } | ForEach-Object {
  try { Stop-Process -Id $_.Id -Force } catch {}
}

Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy Bypass -File \"$root\run_wikilive.ps1\"" -WorkingDirectory $root -RedirectStandardOutput $backendLog -RedirectStandardError $backendLog
Start-Process -FilePath "python" -ArgumentList "frontend\app.py" -WorkingDirectory $root -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendLog

Write-Host "Backend log: $backendLog"
Write-Host "Frontend log: $frontendLog"
