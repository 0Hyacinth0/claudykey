@echo off
cd /d "%~dp0"
title ClaudyKey Bundle Builder

echo.
echo  ============================================================
echo   ClaudyKey - Build Standalone Bundle
echo  ============================================================
echo.

REM -- Step 1: Download Python embeddable using PowerShell --
if exist "env\python.exe" (
    echo  [SKIP] env\python.exe already exists.
    echo  Delete env\ folder if you want a fresh build.
    echo.
    goto RUN_BUILD
)

echo  [1] Downloading Python 3.11.9 embeddable...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'env_tmp.zip' -UseBasicParsing; Write-Host '    Download OK' } catch { Write-Host ('    Download FAILED: ' + $_.Exception.Message); exit 1 }"

if %errorlevel% neq 0 (
    echo  [ERROR] Failed to download Python. Check your internet.
    pause
    exit /b 1
)

echo  [2] Extracting Python...
mkdir env 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path 'env_tmp.zip' -DestinationPath 'env' -Force"
del env_tmp.zip

echo  [3] Enabling pip support...
powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-Content 'env\python311._pth') -replace '^#import site','import site' | Set-Content 'env\python311._pth'"

echo  [4] Installing pip...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'env\get-pip.py' -UseBasicParsing"
"env\python.exe" "env\get-pip.py" --no-warn-script-location -q
del "env\get-pip.py"

:RUN_BUILD
echo.
echo  [5] Running build script...
echo.
"env\python.exe" "build_bundle.py"

pause
