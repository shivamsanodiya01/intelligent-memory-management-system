
@echo off
title Intelligent Memory Management System
cd /d "%~dp0"

if not exist "app.py" (
    echo ERROR: app.py not found in project folder.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Checking project dependencies...

if exist "requirements.txt" (
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
) else (
    "venv\Scripts\python.exe" -m pip install streamlit pandas numpy matplotlib
)

if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo Starting project...
"venv\Scripts\python.exe" -m streamlit run app.py

if errorlevel 1 (
    echo Project stopped. Check the error above.
    pause
)

