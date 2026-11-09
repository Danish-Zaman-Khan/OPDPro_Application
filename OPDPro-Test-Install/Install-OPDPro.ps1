$ErrorActionPreference = "Stop"

function Find-Python {
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        foreach ($version in @("3.13", "3.12", "3.11")) {
            & $launcher.Source "-$version" -c "import sys" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return ,@($launcher.Source, "-$version")
            }
        }
    }

    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        & $pythonCommand.Source -c "import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 14) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return ,@($pythonCommand.Source)
        }
    }

    return $null
}

$pythonCommand = Find-Python
if (-not $pythonCommand) {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "Python 3.11-3.13 is required. Install Python 3.13 from https://www.python.org/downloads/windows/, then run this installer again."
    }

    Write-Host "Installing Python 3.13 for your Windows user. This requires an internet connection."
    & $winget.Source install --id Python.Python.3.13 --exact --scope user --silent `
        --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "Python could not be installed by winget. Install Python 3.13 from https://www.python.org/downloads/windows/, then run this installer again."
    }

    $pythonCommand = Find-Python
    if (-not $pythonCommand) {
        throw "Python was installed. Close this window and run Install-OPDPro.bat again to finish setup."
    }
}

$installDirectory = Join-Path $env:LOCALAPPDATA "Programs\OPDPro"
$sourceDirectory = Join-Path $PSScriptRoot "App"
$appDirectory = Join-Path $installDirectory "App"
$venvPython = Join-Path $installDirectory ".venv\Scripts\python.exe"

if (-not (Test-Path (Join-Path $sourceDirectory "desktop_launcher.py"))) {
    throw "The OPDPro application files are missing. Extract the complete shared folder and run this installer again."
}

New-Item -ItemType Directory -Force -Path $installDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $appDirectory | Out-Null
Get-ChildItem -LiteralPath $sourceDirectory -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $appDirectory -Recurse -Force
}

if (-not (Test-Path $venvPython)) {
    $pythonExecutable = $pythonCommand[0]
    if ($pythonCommand.Count -gt 1) {
        & $pythonExecutable $pythonCommand[1] -m venv (Join-Path $installDirectory ".venv")
    } else {
        & $pythonExecutable -m venv (Join-Path $installDirectory ".venv")
    }
    if ($LASTEXITCODE -ne 0) {
        throw "A private Python environment could not be created."
    }
}

Write-Host "Installing OPDPro components. Keep this window open; the first install needs internet."
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "The Python package installer could not be updated."
}
& $venvPython -m pip install -r (Join-Path $appDirectory "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "OPDPro components could not be downloaded. Check the internet connection and rerun this installer."
}

$pythonw = Join-Path $installDirectory ".venv\Scripts\pythonw.exe"
$startMenuDirectory = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$desktopDirectory = [Environment]::GetFolderPath("Desktop")
New-Item -ItemType Directory -Force -Path $startMenuDirectory, $desktopDirectory | Out-Null
$shell = New-Object -ComObject WScript.Shell

foreach ($shortcutPath in @(
    (Join-Path $startMenuDirectory "OPDPro.lnk"),
    (Join-Path $desktopDirectory "OPDPro.lnk")
)) {
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $pythonw
    $shortcut.Arguments = "`"$(Join-Path $appDirectory "desktop_launcher.py")`""
    $shortcut.WorkingDirectory = $appDirectory
    $shortcut.Description = "Open the local OPDPro clinic application"
    $shortcut.Save()
}

Write-Host "OPDPro is installed. Clinic records are stored separately under %LOCALAPPDATA%\OPDPro."
Write-Host "Opening OPDPro now. On first launch, create your clinic administrator account."
Start-Process -FilePath $pythonw `
    -ArgumentList "`"$(Join-Path $appDirectory "desktop_launcher.py")`"" `
    -WorkingDirectory $appDirectory
