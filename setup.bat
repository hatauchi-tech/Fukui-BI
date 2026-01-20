@echo off
cd /d "%~dp0"

echo ========================================
echo   Setup Script for PL BI Tool
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found.
python --version

echo.
echo Installing required libraries...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install libraries.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup completed successfully\!
echo   You can now run the application.
echo ========================================
pause
