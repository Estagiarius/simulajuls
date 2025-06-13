@echo off
setlocal

REM --- Configuration ---
set PYTHON_CMD=python
set NODE_VERSION_TO_USE=20
set NVM_CHECK_COMMAND=nvm --version

REM --- Helper function to check if a command exists ---
:command_exists
where %1 >nul 2>nul
if %errorlevel% equ 0 (
    exit /b 0
) else (
    exit /b 1
)

echo Starting script...

REM --- Backend Setup ---
echo.
echo Starting backend setup...
cd backend

REM Check for Python
call :command_exists %PYTHON_CMD%
if %errorlevel% neq 0 (
    echo Python (%PYTHON_CMD%) not found in PATH.
    echo Please install Python from https://www.python.org/downloads/ and ensure it's added to your PATH.
    goto :eof
)
echo Python found.

REM Create Python virtual environment if it doesn't exist
if not exist venv (
    echo Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create Python virtual environment. Exiting.
        goto :eof
    )
)

REM Activate virtual environment and install packages
echo Activating virtual environment and installing packages...
call venv\Scripts\activate.bat
pip install fastapi uvicorn pydantic
if %errorlevel% neq 0 (
    echo Failed to install Python packages. Exiting.
    goto :eof
)

REM Launch backend server
echo Launching backend server...
start "Backend Server" /B %PYTHON_CMD% -m uvicorn main:app --reload --port 8000
echo Backend server started in background. Attempting to access at http://localhost:8000
timeout /t 5 /nobreak >nul

REM Navigate back to project root
cd ..
echo Backend setup complete.
echo.

REM --- Frontend Setup ---
echo.
echo Starting frontend setup...

REM Check for NVM for Windows
call :command_exists nvm
if %errorlevel% neq 0 (
    echo NVM for Windows (nvm) not found.
    echo Please install NVM for Windows from https://github.com/coreybutler/nvm-windows/releases
    echo After installation, please open a new terminal and re-run this script.
    goto :eof
)
echo NVM for Windows found.

REM Install and use the specified Node.js version
echo Installing and using Node.js v%NODE_VERSION_TO_USE% (if not already installed)...
nvm install %NODE_VERSION_TO_USE%
if %errorlevel% neq 0 (
    echo Failed to install Node.js v%NODE_VERSION_TO_USE% using NVM.
    echo Please ensure NVM for Windows is correctly installed and configured.
    goto :eof
)
nvm use %NODE_VERSION_TO_USE%
if %errorlevel% neq 0 (
    echo Failed to use Node.js v%NODE_VERSION_TO_USE% using NVM.
    goto :eof
)

echo Verifying Node.js version:
node -v
npm -v
echo.

cd frontend

REM Clean up old dependencies
echo Removing old frontend dependencies (if they exist)...
if exist node_modules (
    echo Removing node_modules...
    rd /s /q node_modules
)
if exist package-lock.json (
    echo Removing package-lock.json...
    del package-lock.json
)

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo Failed to install Node.js dependencies. Exiting.
    goto :eof
)

REM Launch frontend server
echo Launching frontend server...
echo Frontend server starting. Attempting to access at http://localhost:5173 (or similar port shown by npm)
REM Using start to run npm run dev, as it can be a long-running process
start "Frontend Server" npm run dev

cd ..
echo Frontend setup complete.
echo.

echo Script finished.
echo Backend is running in the background (http://localhost:8000).
echo Frontend dev server is running (check terminal for exact address, usually http://localhost:5173).
echo Press Ctrl+C in the terminal where the frontend is running to stop it.
echo To stop the backend, you may need to close the terminal or find the Python process.

endlocal
goto :eof
