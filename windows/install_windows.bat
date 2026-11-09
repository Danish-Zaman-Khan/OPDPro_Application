@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_windows.ps1"
if errorlevel 1 (
  echo.
  echo OPDPro could not be installed. Please contact your clinic administrator.
  pause
  exit /b 1
)
echo.
pause
