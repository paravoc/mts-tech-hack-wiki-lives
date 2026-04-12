param(
    [switch]$ForceConfigure
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Red
}

function Resolve-Python {
    try {
        $resolved = (& python -c "import sys; print(sys.executable)" 2>$null | Select-Object -First 1).Trim()
        if ($resolved -and (Test-Path $resolved)) {
            return $resolved
        }
    }
    catch {
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -and (Test-Path $pythonCommand.Source)) {
        return $pythonCommand.Source
    }

    $fallbacks = @(
        "C:\Users\smidr\AppData\Local\Programs\Python\Python313\python.exe",
        "C:\Users\smidr\AppData\Local\Microsoft\WindowsApps\python.exe",
        "C:\Users\smidr\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"
    )

    foreach ($candidate in $fallbacks) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "Python was not found. Update run_wikilive.ps1 with a valid interpreter path."
}

function Resolve-CMake {
    $cmakeCommand = Get-Command cmake -ErrorAction SilentlyContinue
    if ($cmakeCommand -and $cmakeCommand.Source) {
        return $cmakeCommand.Source
    }

    $fallbacks = @(
        "C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe",
        "C:\Program Files\Microsoft Visual Studio\17\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
    )

    foreach ($candidate in $fallbacks) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Resolve-VcVars {
    $fallbacks = @(
        "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat",
        "C:\Program Files\Microsoft Visual Studio\17\Community\VC\Auxiliary\Build\vcvars64.bat"
    )

    foreach ($candidate in $fallbacks) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Stop-Existing {
    Get-Process wikilive_backend -ErrorAction SilentlyContinue | Stop-Process -Force

    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match "python|streamlit|powershell|cmd" -and
            $_.CommandLine -and (
                $_.CommandLine -like "*frontend\\app.py*" -or
                $_.CommandLine -like "*wikilive_backend.exe*"
            )
        } |
        ForEach-Object {
            try { Stop-Process -Id $_.ProcessId -Force } catch {}
        }
}

function Invoke-CMakeCommand {
    param(
        [string]$CMakeExe,
        [string]$VcVarsBat,
        [string[]]$Arguments
    )

    if ($VcVarsBat) {
        $cmakeWithArgs = '"' + $CMakeExe + '" ' + ($Arguments -join " ")
        $cmdLine = 'call "' + $VcVarsBat + '" && ' + $cmakeWithArgs
        cmd.exe /c $cmdLine
    } else {
        & $CMakeExe @Arguments
    }

    if ($LASTEXITCODE -ne 0) {
        throw "CMake command failed with exit code $LASTEXITCODE"
    }
}

function Invoke-BuildIfAvailable {
    param(
        [string]$CMakeExe,
        [string]$VcVarsBat,
        [string]$BackendExe,
        [bool]$ShouldConfigure
    )

    if (-not $CMakeExe) {
        Write-Warning "CMake was not found in PATH or known locations. Using existing build if available."
        return
    }

    try {
        if ($ShouldConfigure) {
            Write-Step "Configuring project"
            Invoke-CMakeCommand -CMakeExe $CMakeExe -VcVarsBat $VcVarsBat -Arguments @("--preset", "windows-debug")
        }

        Write-Step "Building backend"
        Invoke-CMakeCommand -CMakeExe $CMakeExe -VcVarsBat $VcVarsBat -Arguments @("--build", "--preset", "windows-debug")
    }
    catch {
        if (Test-Path $BackendExe) {
            Write-Warning "Build failed, but an existing backend binary was found. Continuing with the current exe."
            Write-Warning $_
            return
        }

        throw
    }
}

$pythonExe = Resolve-Python
$cmakeExe = Resolve-CMake
$vcVarsBat = Resolve-VcVars
$buildDir = Join-Path $projectRoot "out\build\x64-Debug"
$backendExe = Join-Path $buildDir "wikilive_backend.exe"
$backendOut = Join-Path $projectRoot "server-debug.out.log"
$backendErr = Join-Path $projectRoot "server-debug.err.log"
$frontendOut = Join-Path $projectRoot "streamlit.out.log"
$frontendErr = Join-Path $projectRoot "streamlit.err.log"

Write-Step "Stopping old processes"
Stop-Existing

$hasBuildSystem = (Test-Path (Join-Path $buildDir "build.ninja")) -and (Test-Path (Join-Path $buildDir "CMakeCache.txt"))
Invoke-BuildIfAvailable -CMakeExe $cmakeExe -VcVarsBat $vcVarsBat -BackendExe $backendExe -ShouldConfigure ($ForceConfigure.IsPresent -or -not $hasBuildSystem)

if (-not (Test-Path $backendExe)) {
    throw "Backend was not found: $backendExe"
}

Write-Step "Checking Streamlit"
& $pythonExe -c "import streamlit" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Streamlit is not available for $pythonExe"
}

Write-Step "Starting backend"
$backendRunner = "& '$backendExe' 1>> '$backendOut' 2>> '$backendErr'"
$backendProcess = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $backendRunner -WorkingDirectory $projectRoot -PassThru

Start-Sleep -Milliseconds 800

Write-Step "Starting frontend"
$frontendRunner = "& '$pythonExe' -m streamlit run 'frontend\app.py' --server.headless true --server.port 8501 1>> '$frontendOut' 2>> '$frontendErr'"
$frontendProcess = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $frontendRunner -WorkingDirectory $projectRoot -PassThru

Write-Step "Ready"
Write-Host "Backend:  http://127.0.0.1:3000" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:8501" -ForegroundColor Green
Write-Host "Backend launcher PID:  $($backendProcess.Id)"
Write-Host "Frontend launcher PID: $($frontendProcess.Id)"
Write-Host ""
Write-Host "Logs:"
Write-Host "  $backendOut"
Write-Host "  $backendErr"
Write-Host "  $frontendOut"
Write-Host "  $frontendErr"
Write-Host ""
Write-Host "Tip: use -ForceConfigure only when you changed CMake files or need full regeneration."
