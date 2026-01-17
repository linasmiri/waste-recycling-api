@echo off
echo Starting Waste Recycling API locally...
cd /d %~dp0

echo Checking for Python...

REM Try 'python' command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :setup
)

REM Try 'py' command
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :setup
)

REM Search common locations
echo Python not found in PATH. Searching known locations...
for %%d in (
    "C:\Python312"
    "C:\Python311"
    "C:\Python310"
    "C:\Python39"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311"
    "C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps"
) do (
    if exist "%%~d\python.exe" (
        set "PYTHON_CMD=%%~d\python.exe"
        goto :setup
    )
)

echo.
echo ! Error !
echo Python was not found on this computer.
echo Please install it from https://www.python.org/downloads/
echo Important: Check "Add Python to PATH" during installation.
pause
exit /b 1

:setup
echo Using Python found at: "%PYTHON_CMD%"

if not exist venv (
    echo Creating virtual environment...
    "%PYTHON_CMD%" -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate venv.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Server starting !
echo Open http://localhost:8000/docs for Swagger UI
echo Open frontend/index.html for the Interface
echo.
start http://localhost:8000/docs
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause