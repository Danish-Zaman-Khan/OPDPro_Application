@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-OPDPro.ps1"
if errorlevel 1 (
  echo.
  echo OPDPro installation did not complete. Read INSTALL-AND-USE.md or contact your clinic administrator.
  pause
  exit /b 1
)
echo.
pause
