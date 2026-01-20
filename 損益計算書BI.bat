@echo off
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please run setup.bat first, or install Python manually.
    pause
    exit /b 1
)

python -c "import pandas; import matplotlib; import ttkbootstrap" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Required libraries are not installed.
    echo Please run setup.bat first to install dependencies.
    pause
    exit /b 1
)

pythonw -m src.main 2>nul
if errorlevel 1 (
    python -m src.main
    if errorlevel 1 (
        echo.
        echo [ERROR] Application failed to start.
        pause
    )
)
