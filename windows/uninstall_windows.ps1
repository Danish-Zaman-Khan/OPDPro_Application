$ErrorActionPreference = "Stop"

$installDirectory = Join-Path $env:LOCALAPPDATA "Programs\OPDPro"
$startMenuShortcut = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\OPDPro.lnk"
$desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "OPDPro.lnk"
$uninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\OPDPro"

if (Get-Process -Name "OPDPro" -ErrorAction SilentlyContinue) {
    throw "Close OPDPro before uninstalling it."
}

$confirmation = Read-Host "Remove OPDPro from this computer? Clinic records and backups will be kept"
if ($confirmation -notin @("Y", "y", "YES", "yes")) {
    Write-Host "Uninstall cancelled."
    exit 0
}

foreach ($shortcut in @($startMenuShortcut, $desktopShortcut)) {
    if (Test-Path -LiteralPath $shortcut) {
        Remove-Item -LiteralPath $shortcut -Force
    }
}
if (Test-Path -LiteralPath $uninstallKey) {
    Remove-Item -LiteralPath $uninstallKey -Recurse -Force
}
if (Test-Path -LiteralPath $installDirectory) {
    Remove-Item -LiteralPath $installDirectory -Recurse -Force
}

Write-Host "OPDPro has been removed. Clinic records in %LOCALAPPDATA%\OPDPro were not changed."
