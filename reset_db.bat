@echo off
echo Stopping all Python processes...
taskkill /IM python.exe /F
taskkill /IM uvicorn.exe /F
taskkill /IM py.exe /F

timeout /t 2

echo Deleting old database...
del waste_app.db

echo Database deleted. It will be recreated on next start.
echo.
echo Now you can run start.bat again.
pause