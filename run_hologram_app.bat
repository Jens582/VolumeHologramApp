@echo off
set VENV_DIR=venv
set APP_FILE=app.py

:: Check if virtual environment exists
if not exist %VENV_DIR% (
    echo Virtual environment not found!
    echo Run create_venv.bat to set up the virtual environment.
    pause
	exit /b 1
)

:: Activate virtual environment
call %VENV_DIR%\Scripts\activate
if %errorlevel% neq 0 (
    echo Error activating virtual environment.
    echo Ensure the virtual environment is correctly installed by running create_venv.bat.
	pause
    exit /b 1
)

:: Start the application
python %APP_FILE%



:: Keep window open
pause
