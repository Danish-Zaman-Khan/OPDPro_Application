$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $PSScriptRoot ".venv-build"
$python = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $python)) {
    python -m venv $venvPath
}

& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "The Python package installer could not be updated."
}
& $python -m pip install -r (Join-Path $repoRoot "requirements.txt") pyinstaller
if ($LASTEXITCODE -ne 0) {
    throw "OPDPro build dependencies could not be installed."
}

$originalSecretKey = $env:SECRET_KEY
try {
    if ([string]::IsNullOrWhiteSpace($env:SECRET_KEY)) {
        $env:SECRET_KEY = "opdpro-pyinstaller-analysis-" + [Guid]::NewGuid().ToString("N")
    }
    & $python -m PyInstaller --clean --noconfirm `
        --distpath (Join-Path $PSScriptRoot "dist") `
        --workpath (Join-Path $PSScriptRoot "build") `
        (Join-Path $PSScriptRoot "OPDPro.spec")
    if ($LASTEXITCODE -ne 0) {
        throw "The OPDPro executable could not be built by PyInstaller."
    }
}
finally {
    if ($null -eq $originalSecretKey) {
        Remove-Item Env:SECRET_KEY -ErrorAction SilentlyContinue
    }
    else {
        $env:SECRET_KEY = $originalSecretKey
    }
}

$distPath = Join-Path $PSScriptRoot "dist"
Copy-Item (Join-Path $PSScriptRoot "install_windows.ps1") $distPath -Force
Copy-Item (Join-Path $PSScriptRoot "install_windows.bat") $distPath -Force
Copy-Item (Join-Path $PSScriptRoot "uninstall_windows.ps1") $distPath -Force

$programFilesX86 = [Environment]::GetFolderPath("ProgramFilesX86")
$isccPath = Join-Path $programFilesX86 "Inno Setup 6\ISCC.exe"
$setupCompiled = $false
if (-not (Test-Path $isccPath)) {
    $isccPath = Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"
}
if (Test-Path $isccPath) {
    $env:OPDPRO_SOURCE_DIR = $PSScriptRoot
    & $isccPath (Join-Path $PSScriptRoot "OPDPro.iss")
    if ($LASTEXITCODE -ne 0) {
        throw "The OPDPro setup installer could not be compiled by Inno Setup."
    }
    $setupCompiled = $true
}
else {
    Write-Warning "Inno Setup 6 was not found. The ZIP installer will still be created, but OPDPro-Setup.exe will be omitted."
}

$archivePath = Join-Path $distPath "OPDPro-Windows.zip"
$releaseFiles = @(
    (Join-Path $distPath "OPDPro.exe"),
    (Join-Path $distPath "install_windows.ps1"),
    (Join-Path $distPath "install_windows.bat"),
    (Join-Path $distPath "uninstall_windows.ps1")
)
$obsoleteArchive = Join-Path $distPath "OPDPro-Test-Install-Windows.zip"
if (Test-Path -LiteralPath $obsoleteArchive) {
    Remove-Item -LiteralPath $obsoleteArchive -Force
}
$setupInstaller = Join-Path $distPath "OPDPro-Setup.exe"
if ($setupCompiled -and (Test-Path $setupInstaller)) {
    $releaseFiles += $setupInstaller
}
Compress-Archive -Path $releaseFiles -DestinationPath $archivePath -Force

Write-Host "Build complete: $archivePath"
if ($setupCompiled -and (Test-Path $setupInstaller)) {
    Write-Host "GUI installer: $setupInstaller"
}
