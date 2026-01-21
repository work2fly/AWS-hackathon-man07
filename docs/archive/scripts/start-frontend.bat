@echo off
REM AI Therapy Platform - Frontend Startup Script (Windows)
REM Breaking Barriers UK 2026 compliant

echo.
echo ========================================
echo   AI Therapy Platform Frontend
echo   Breaking Barriers UK 2026
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed.
    echo Please install Node.js 18+ from https://nodejs.org/
    exit /b 1
)

echo [OK] Node.js found
node --version
echo.

REM Navigate to frontend directory
cd ai-therapy-frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    echo This may take a few minutes...
    echo.
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed successfully
    echo.
)

REM Start the development server
echo ========================================
echo   Starting Development Server
echo ========================================
echo.
echo [INFO] Frontend will be available at:
echo        http://localhost:3000
echo.
echo [INFO] Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

call npm run dev
