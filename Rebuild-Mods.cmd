@echo off
setlocal
set "PYTHONUTF8=1"
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 tools\build_release.py --mods-only
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.10+ is required. No mods have been deployed.
    pause
    exit /b 2
  )
  python tools\build_release.py --mods-only
)
set "build_exit=%errorlevel%"
echo.
echo Result: %build_exit%. The integrated mod ZIP is in dist. Rebuilding does not port an unknown game version.
pause
exit /b %build_exit%
