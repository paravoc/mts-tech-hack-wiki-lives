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
        if ($resolved -and (Test-Path $resolved) -and ($resolved -notlike "*WindowsApps*")) {
            return $resolved
        }
    }
    catch {
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -and (Test-Path $pythonCommand.Source) -and ($pythonCommand.Source -notlike "*WindowsApps*")) {
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

function Format-CmdArgument {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return '""'
    }

    if ($Value.Contains('"') -or $Value.Contains(' ')) {
        return '"' + $Value.Replace('"', '\"') + '"'
    }

    return $Value
}

function Start-DetachedProcess {
    param(
        [string]$Executable,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$StdOutPath,
        [string]$StdErrPath
    )

    $formattedArgs = @()
    foreach ($argument in $Arguments) {
        $formattedArgs += (Format-CmdArgument -Value $argument)
    }

    $commandLine = '"' + $Executable + '"'
    if ($formattedArgs.Count -gt 0) {
        $commandLine += " " + ($formattedArgs -join " ")
    }
    $commandLine += ' 1>> "' + $StdOutPath + '" 2>> "' + $StdErrPath + '"'

    $result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine = $commandLine
        CurrentDirectory = $WorkingDirectory
    }

    if ($result.ReturnValue -ne 0 -or -not $result.ProcessId) {
        throw "Failed to start detached process for $Executable (Win32_Process return code $($result.ReturnValue))."
    }

    return [int]$result.ProcessId
}

function Wait-HttpReady {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 15
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        }
        catch {
        }

        Start-Sleep -Milliseconds 400
    }

    return $false
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
$backendPid = Start-DetachedProcess `
    -Executable $backendExe `
    -Arguments @() `
    -WorkingDirectory $projectRoot `
    -StdOutPath $backendOut `
    -StdErrPath $backendErr

if (-not (Wait-HttpReady -Url "http://127.0.0.1:3000/health" -TimeoutSeconds 15)) {
    throw "Backend did not become ready on http://127.0.0.1:3000/health. Check $backendOut and $backendErr."
}

Write-Step "Starting frontend"
$frontendRunner = "& '$pythonExe' -m streamlit run 'frontend\\app.py' --server.headless true --server.port 8501 1>> '$frontendOut' 2>> '$frontendErr'"
$frontendProcess = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $frontendRunner -WorkingDirectory $projectRoot -PassThru

if (-not (Wait-HttpReady -Url "http://127.0.0.1:8501/" -TimeoutSeconds 20)) {
    Write-Warning "Frontend did not respond on http://127.0.0.1:8501 yet. It may still be warming up; check $frontendOut and $frontendErr if needed."
}

Write-Step "Ready"
Write-Host "Backend:  http://127.0.0.1:3000" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:8501" -ForegroundColor Green
Write-Host "Backend PID:  $backendPid"
Write-Host "Frontend PID: $($frontendProcess.Id)"
Write-Host ""
Write-Host "Logs:"
Write-Host "  $backendOut"
Write-Host "  $backendErr"
Write-Host "  $frontendOut"
Write-Host "  $frontendErr"
Write-Host ""
Write-Host "Tip: use -ForceConfigure only when you changed CMake files or need full regeneration."
