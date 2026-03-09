@echo off
cd /d "%~dp0"
title ClaudyKey Updater
echo.
if exist "env\python.exe" (
    "env\python.exe" "update.py"
) else (
    echo  [NOTE] env not found, using system Python...
    python update.py
)
pause
