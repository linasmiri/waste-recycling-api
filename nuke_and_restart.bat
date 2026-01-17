@echo off
echo ===================================================
echo     NUKE AND RESTART (The "Hammer" Script)
echo ===================================================
cd /d %~dp0

echo 1. KILLING ZOMBIE PROCESSES...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM py.exe >nul 2>&1
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM php.exe >nul 2>&1
echo Zombies killed.

echo 2. Checking Python...
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

echo 3. Recreating VENV (Fresh install)...
if exist venv (
    echo Removing old/broken virtual environment...
    rmdir /s /q venv
)
echo Creating virtual environment...
"%PYTHON_CMD%" -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo 4. Cleaning old DB...
if exist waste_app.db (
    del waste_app.db
    echo Database deleted.
)

echo 5. Installing dependencies (Quick check)...
venv\Scripts\python.exe -m pip install -r requirements.txt

echo 6. STARTING SERVER...
echo Opening Swagger UI...
start http://localhost:8000/docs
echo WAITING FOR "Application startup complete" message...
echo ---------------------------------------------------
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo ---------------------------------------------------
pause