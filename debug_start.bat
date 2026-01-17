@echo off
echo ===================================================
echo     DEBUG START SCRIPT (Keeps window open)
echo ===================================================
cd /d %~dp0

echo 1. Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
) else (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=py"
    ) else (
        echo PYTHON NOT FOUND.
        pause
        exit /b 1
    )
)
echo Using: %PYTHON_CMD%

echo 2. Activating VENV...
if not exist venv (
    echo VENV missing, creating...
    "%PYTHON_CMD%" -m venv venv
)
call venv\Scripts\activate

echo 3. Installing dependencies (forcing upgrade)...
venv\Scripts\python.exe -m pip install --upgrade --force-reinstall -r requirements.txt
if %errorlevel% neq 0 (
    echo !!!!!!!!!!!!!!!!
    echo INSTALL FAILED
    echo !!!!!!!!!!!!!!!!
    pause
    exit /b 1
)

echo 4. Starting Server...echo Opening Swagger UI...
start http://localhost:8000/docsecho If this crashes, READ THE ERROR MESSAGE BELOW.
echo ---------------------------------------------------
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo ---------------------------------------------------
echo SERVER EXITED.
pause