@echo off
REM AI Therapy Platform - Backend Startup Script (Windows)
REM Breaking Barriers UK 2026 compliant

echo Starting AI Therapy Platform Backend...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

echo Python found
python --version

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo Creating virtual environment...
    python -m venv backend\venv
)

REM Activate virtual environment
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q --upgrade pip
pip install -q -r backend\requirements.txt

REM Start the local development server
echo.
echo Starting local development server...
echo ================================================================
echo.

cd backend
python local_server.py
