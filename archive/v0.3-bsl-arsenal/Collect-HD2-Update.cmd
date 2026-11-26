@echo off
setlocal
set "PYTHONUTF8=1"
chcp 65001 >nul
cd /d "%~dp0"
if exist "%~dp0P11-Update.exe" (
  "%~dp0P11-Update.exe" %*
  goto finished
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 tools\offline_update.py %*
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.10+ is required. No files have been changed.
    pause
    exit /b 2
  )
  python tools\offline_update.py %*
)
:finished
set "collector_exit=%errorlevel%"
echo.
echo Result code: %collector_exit%. See diagnostics for the local report.
pause
exit /b %collector_exit%
