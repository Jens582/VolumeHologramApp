@echo off
set VENV_DIR=venv
set REQUIREMENTS=requirements.txt

setlocal enabledelayedexpansion

echo Do you want to set up a Python virtual environment and install required packages? (Yes/No)
set /p user_input=

if /I "%user_input%"=="No" (
    echo Setup aborted.
	pause
    exit /b
)

if /I "%user_input%"=="Yes" (
    echo Setting up the virtual environment...

) else (
    echo Invalid input. Please restart the script and enter Yes or No.
	pause
    exit /b
)


endlocal

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    exit /b 1
)

:: Create virtual environment
python -m venv %VENV_DIR%
if %errorlevel% neq 0 (
    echo Error while creating the virtual environment.
    exit /b 1
)

:: Activate virtual environment
call %VENV_DIR%\Scripts\activate
if %errorlevel% neq 0 (
    echo Error while activating the virtual environment.
    exit /b 1
)

:: Install requirements if file exists
if exist %REQUIREMENTS% (
    echo Installing dependencies from %REQUIREMENTS%...
    pip install -r %REQUIREMENTS%
    if %errorlevel% neq 0 (
        echo Error installing dependencies.
        exit /b 1
    )
) else (
    echo No %REQUIREMENTS% file found. Skipping dependencies installation.
)

:: Display activation instructions
echo Virtual environment has been created and dependencies installed. To activate:
echo.
echo Windows CMD:   %VENV_DIR%\Scripts\activate
echo Windows PowerShell:   .\%VENV_DIR%\Scripts\Activate.ps1
echo To deactivate: deactivate
echo .
echo To Start app 
echo. python app.py
:: Keep window open
pause
