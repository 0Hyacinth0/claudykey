@echo off
cd /d "%~dp0"
if not exist "env\python.exe" (
    echo [ERROR] env\python.exe not found. Run: python build_bundle.py
    pause
    exit /b 1
)
start "" "env\python.exe" "main.py"
