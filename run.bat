@echo off
title Library Management System
cd /d "%~dp0"

echo ==== Library Management System ====
echo.

set PY=
python --version >nul 2>nul
if not errorlevel 1 set PY=python
if defined PY goto found

py --version >nul 2>nul
if not errorlevel 1 set PY=py
if defined PY goto found

echo Python was not found on this computer.
echo Please install Python from https://www.python.org/downloads/
echo During installation, tick "Add python.exe to PATH".
echo Then close this window and double-click run.bat again.
echo.
pause
exit /b 1

:found
echo Using %PY%
%PY% --version
echo.
echo Installing Flask (the first run may take a minute)...
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Flask could not be installed. Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Starting the project. Your browser will open automatically.
echo If it does not, open http://127.0.0.1:5000 in your browser.
echo To stop the project, press Ctrl + C in this window.
echo.
%PY% app.py
echo.
echo The project has stopped. Read any error message above.
pause
