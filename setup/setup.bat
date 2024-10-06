@echo off
setlocal

REM Check if the OS is Windows
ver | find "Windows" >nul
if errorlevel 1 (
    echo This script can only be run on Windows.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

REM Check Python version (must be 3.7 or higher)
for /f "tokens=2 delims= " %%a in ('python --version') do set py_ver=%%a
for /f "tokens=1,2 delims=." %%a in ("%py_ver%") do (
    if %%a LSS 3 (
        echo Python version is lower than 3.7. Please upgrade Python.
        pause
        exit /b 1
    )
    if %%a EQU 3 if %%b LSS 7 (
        echo Python version is lower than 3.7. Please upgrade Python.
        pause
        exit /b 1
    )
)

REM Install requirements from requirements.txt
echo Installing requirements...
pip install -r requirements.txt

REM Run setup.py
echo Running setup.py...
python setup.py

endlocal