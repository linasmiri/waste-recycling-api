@echo off
echo Starting Frontend Server...
cd /d %~dp0

REM Find Python (Same logic as start.bat)
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :run_server
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :run_server
)

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
        goto :run_server
    )
)

echo Python not found! Please ensure Python is installed and added to PATH.
pause
exit /b 1

:run_server
echo Using Python at: "%PYTHON_CMD%"
cd frontend
echo.
echo Starting web server...
echo Open http://localhost:3000 in your browser
echo.
"%PYTHON_CMD%" -m http.server 3000
pause