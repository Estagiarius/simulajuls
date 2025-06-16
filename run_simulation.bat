@echo off
title Educational Simulation Environment Launcher (Windows)

echo.
echo --- Educational Simulation Environment ---
echo.
echo This script will set up and start the backend and frontend servers.
echo Two new command prompt windows will be opened:
echo   1. Backend Server (Python/FastAPI)
echo   2. Frontend Server (Node.js/SvelteKit)
echo.
echo Please monitor those windows for progress and error messages.
echo.
echo --- Checking Prerequisites ---
echo.

echo Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not found in PATH. Please install Python and try again.
    echo.
    pause
    exit /b 1
)
echo Python found.
echo.

echo Checking for Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not found in PATH. Please install Node.js and try again.
    echo.
    pause
    exit /b 1
)
echo Node.js found.
echo.

echo.
echo --- Checking for npm ---
echo Attempting to run 'npm --version' in a subshell. Please wait...
echo If the script hangs here, there might be an issue with your npm installation or PATH.

REM Define a temporary file for npm version output
set NPM_VERSION_TMP_FILE=%TEMP%\npm_version_output.txt

cmd /c "npm --version > "%NPM_VERSION_TMP_FILE%" 2>&1"
set NPM_CMD_EXIT_CODE=0
for /f "tokens=*" %%a in ("%errorlevel%") do set NPM_CMD_EXIT_CODE=%%a

echo Captured errorlevel from 'cmd /c npm --version': [%NPM_CMD_EXIT_CODE%]

echo DBG: About to check if NPM_CMD_EXIT_CODE is "0" using IF ==
IF "%NPM_CMD_EXIT_CODE%" == "0" (
    echo DBG: Condition "%NPM_CMD_EXIT_CODE%" == "0" is TRUE.
    GOTO NpmCheckSuccess
) ELSE (
    echo DBG: Condition "%NPM_CMD_EXIT_CODE%" == "0" is FALSE.
    GOTO NpmError
)

:ContinueAfterNpmCheck
echo --- Backend Setup ---
echo.

if not exist backend\venv (
    echo Creating Python virtual environment in backend\venv...
    python -m venv backend\venv
    if errorlevel 1 (
        echo Error: Failed to create Python virtual environment.
        echo.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Python virtual environment backend\venv already exists.
)
echo.

echo Activating virtual environment for main script (for pip install)...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate Python virtual environment in main script.
    echo.
    pause
    exit /b 1
)
echo Virtual environment activated for main script.
echo.

echo Installing Python dependencies (fastapi, uvicorn, pydantic)...
pip install fastapi uvicorn pydantic
if errorlevel 1 (
    echo Error: Failed to install Python dependencies. Check pip command output.
    echo.
    pause
    exit /b 1
)
echo Python dependencies installed successfully.
echo.

echo Starting Backend Server in a new window...
start "Backend Server" cmd /c "echo Backend Window: Activating venv... && call backend\venv\Scripts\activate.bat && echo Backend Window: Starting FastAPI server... && python -m uvicorn backend.main:app --reload --port 8000 || (echo Backend Window: Error starting server. && pause)"
echo Backend server process started. (Check new window)
echo.

echo --- Frontend Setup ---
echo.
echo Navigating to frontend directory...
cd frontend
if errorlevel 1 (
    echo Error: Failed to change directory to frontend.
    echo.
    pause
    exit /b 1
)
echo Currently in: %cd%
echo.

echo Starting Frontend Server in a new window...
REM Using /k to keep window open for npm run dev output
start "Frontend Server" cmd /k "echo Frontend Window: Installing Node.js dependencies (npm install)... && npm install && if errorlevel 1 (echo Frontend Window: Error during npm install. && pause && exit /b 1) && echo Frontend Window: Starting SvelteKit dev server (npm run dev)... && npm run dev"
echo Frontend server process started. (Check new window)
echo.

echo Returning to root directory...
cd ..
echo Currently in: %cd%
echo.
echo --- Setup Complete ---
echo.
echo Backend should be running on http://localhost:8000
echo Frontend should be running on http://localhost:5173 (or similar)
echo.
echo Press any key to close this main script window.
echo Note: Closing this window will NOT stop the backend or frontend servers.
echo You must close their respective windows to stop them.
pause
GOTO :EOF

REM --- LABELS FOR NPM CHECK START HERE ---
:NpmError
echo.
echo Error: 'npm --version' command failed.
echo The specific exit code captured was: [%NPM_CMD_EXIT_CODE%]
echo Output/Error from npm (if any) should be in "%NPM_VERSION_TMP_FILE%"
echo Please ensure Node.js and npm are correctly installed and accessible.
echo You can try running 'npm --version' manually in a new command prompt to diagnose.
echo.
if exist "%NPM_VERSION_TMP_FILE%" (
    echo Contents of "%NPM_VERSION_TMP_FILE%":
    type "%NPM_VERSION_TMP_FILE%"
    echo Deleting temp file "%NPM_VERSION_TMP_FILE%"
    del "%NPM_VERSION_TMP_FILE%"
)
pause
echo Script will now terminate due to npm check failure.
EXIT /B 1

:NpmCheckSuccess
echo DBG: Reached NpmCheckSuccess label.
echo 'npm --version' command executed successfully.
echo Specific exit code from npm command: [%NPM_CMD_EXIT_CODE%]

echo Attempting to display and delete the npm version temporary file ("%NPM_VERSION_TMP_FILE%")...
echo Contents (if file exists):
type "%NPM_VERSION_TMP_FILE%" 2>nul
echo Attempting to delete temp file...
del "%NPM_VERSION_TMP_FILE%" 2>nul
echo Temporary file processing attempted.

echo npm found.
echo.
REM This GOTO allows the main script flow to continue from where Npm check was initiated.
GOTO :ContinueAfterNpmCheck
REM --- LABELS FOR NPM CHECK END HERE ---
