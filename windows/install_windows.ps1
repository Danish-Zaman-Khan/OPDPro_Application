$ErrorActionPreference = "Stop"

$sourceExe = Join-Path $PSScriptRoot "OPDPro.exe"
$sourceUninstaller = Join-Path $PSScriptRoot "uninstall_windows.ps1"
if (-not (Test-Path $sourceExe)) {
    throw "OPDPro.exe was not found. Extract the complete OPDPro release ZIP and run this installer again."
}
if (-not (Test-Path $sourceUninstaller)) {
    throw "The OPDPro uninstall helper was not found. Extract the complete OPDPro release ZIP and run this installer again."
}
if (Get-Process -Name "OPDPro" -ErrorAction SilentlyContinue) {
    throw "Close OPDPro before installing or updating it."
}

$installDirectory = Join-Path $env:LOCALAPPDATA "Programs\OPDPro"
$startMenuDirectory = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$desktopDirectory = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $startMenuDirectory "OPDPro.lnk"
$desktopShortcutPath = Join-Path $desktopDirectory "OPDPro.lnk"
$uninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\OPDPro"

New-Item -ItemType Directory -Force -Path $installDirectory | Out-Null
Copy-Item -Path $sourceExe -Destination (Join-Path $installDirectory "OPDPro.exe") -Force
Copy-Item -Path $sourceUninstaller -Destination (Join-Path $installDirectory "uninstall_windows.ps1") -Force
New-Item -ItemType Directory -Force -Path $startMenuDirectory | Out-Null

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $installDirectory "OPDPro.exe"
$shortcut.WorkingDirectory = $installDirectory
$shortcut.Description = "Open the local OPDPro clinic application"
$shortcut.Save()

$desktopShortcut = $shell.CreateShortcut($desktopShortcutPath)
$desktopShortcut.TargetPath = Join-Path $installDirectory "OPDPro.exe"
$desktopShortcut.WorkingDirectory = $installDirectory
$desktopShortcut.Description = "Open the local OPDPro clinic application"
$desktopShortcut.Save()

New-Item -Path $uninstallKey -Force | Out-Null
New-ItemProperty -Path $uninstallKey -Name "DisplayName" -Value "OPDPro" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $uninstallKey -Name "DisplayVersion" -Value "1.0.0" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $uninstallKey -Name "Publisher" -Value "OPDPro" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $uninstallKey -Name "InstallLocation" -Value $installDirectory -PropertyType String -Force | Out-Null
New-ItemProperty -Path $uninstallKey -Name "UninstallString" -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$installDirectory\uninstall_windows.ps1`"" -PropertyType String -Force | Out-Null

Write-Host "OPDPro is installed. Use the desktop shortcut or Windows Start menu."
Write-Host "OPDPro opens as one application window with the clinic and backup tools together."
Write-Host "Clinic data is stored separately under %LOCALAPPDATA%\OPDPro and is not removed when the app is uninstalled."
