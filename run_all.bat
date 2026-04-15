@echo off
setlocal
set ROOT=%~dp0
if exist "%ROOT%\.venv\Scripts\activate.bat" (
  call "%ROOT%\.venv\Scripts\activate.bat"
)

set LOGDIR=%ROOT%logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

set BACKEND_LOG=%LOGDIR%\backend.log
set FRONTEND_LOG=%LOGDIR%\frontend.log

powershell -Command "Get-Process | Where-Object { $_.ProcessName -match 'wikilive|python|node' } | Stop-Process -Force" >nul 2>nul

start "WikiLive Backend" /D "%ROOT%" cmd /c "run_wikilive.ps1 > \"%BACKEND_LOG%\" 2>&1"

start "WikiLive Frontend" /D "%ROOT%" cmd /c "python frontend\app.py > \"%FRONTEND_LOG%\" 2>&1"

echo Backend log: %BACKEND_LOG%
echo Frontend log: %FRONTEND_LOG%
endlocal