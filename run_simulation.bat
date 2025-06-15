@echo off
title Educational Simulation Environment Launcher (Windows)

echo Starting backend setup...

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not found in PATH. Please install Python and try again.
    exit /b 1
)

if not exist backend\venv (
    echo Creating virtual environment...
    python -m venv backend\venv
)

echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install fastapi uvicorn pydantic

echo Starting backend server...
start "Backend Server" cmd /c "python -m uvicorn backend.main:app --reload --port 8000"

echo Starting frontend setup...

node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not found in PATH. Please install Node.js and try again.
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo Error: npm is not installed or not found in PATH. Please install npm and try again.
    exit /b 1
)

cd frontend

echo Installing Node.js dependencies...
npm install

echo Starting frontend server...
start "Frontend Server" cmd /c "npm run dev"

cd ..
pause
