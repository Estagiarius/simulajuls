@echo off
setlocal
echo Starting script...

REM --- Configuration ---
set PYTHON_CMD=python
set NODE_VERSION_TO_USE=20
echo PYTHON_CMD set to: %PYTHON_CMD%
echo NODE_VERSION_TO_USE set to: %NODE_VERSION_TO_USE%

REM --- Backend Setup ---
echo.
echo Starting backend setup...
pushd backend
echo Current directory: %CD%

REM Check for Python
echo Checking for Python command: %PYTHON_CMD%
where %PYTHON_CMD% >nul 2>nul
set PYTHON_FOUND_ERRORLEVEL=%errorlevel%

if %PYTHON_FOUND_ERRORLEVEL% neq 0 goto python_not_found
echo Python command was found.
goto python_check_done

:python_not_found
echo Python (%PYTHON_CMD%) not found in PATH.
echo Please install Python from https://www.python.org/downloads/ and ensure it's added to your PATH.
goto :eof_error_popped

:python_check_done
echo Python check complete.
echo.

REM Create Python virtual environment if it doesn't exist
echo Checking for venv directory at: %CD%+env
IF EXIST "venv" (
    echo 'venv' directory ALREADY exists.
) ELSE (
    echo 'venv' directory does NOT exist. Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create Python virtual environment. Exiting.
        goto :eof_error_popped
    )
    echo Virtual environment created.
)
echo Finished venv check/creation.
echo.

REM Activate virtual environment
echo Activating virtual environment: call venv\Scriptsctivate.bat
call venv\Scriptsctivate.bat
set VENV_ACTIVATION_ERRORLEVEL=%errorlevel%
echo Errorlevel from venv activation: %VENV_ACTIVATION_ERRORLEVEL%
if %VENV_ACTIVATION_ERRORLEVEL% neq 0 (
    echo WARNING: Virtual environment activation might have failed (Errorlevel: %VENV_ACTIVATION_ERRORLEVEL%).
    echo This can happen if already active or due to path issues.
) ELSE (
    echo Virtual environment seems activated.
)
echo.

REM Install Python packages
echo Attempting to install Python packages: fastapi uvicorn pydantic
pip install fastapi uvicorn pydantic
if %errorlevel% neq 0 (
    echo Failed to install Python packages. Exiting.
    goto :eof_error_popped
)
echo Python packages installed successfully.
echo.

REM Launch backend server
echo Attempting to launch backend server from %CD%
echo Setting PYTHONPATH to include project root for module resolution.
set PYTHONPATH=%CD%\..
echo PYTHONPATH set to: %PYTHONPATH%

start "Backend Server" /B %PYTHON_CMD% -m uvicorn main:app --reload --port 8000
echo Backend server launch command issued. It should be running in the background.
echo Check http://localhost:8000 after a few seconds.
timeout /t 5 /nobreak >nul
set PYTHONPATH=
popd
echo Current directory after POPD from backend: %CD%
echo Backend setup complete.
echo.

REM --- Frontend Setup ---
echo.
echo Starting frontend setup...

REM Check for NVM for Windows
echo Checking for NVM for Windows (nvm command)...
where nvm >nul 2>nul
if %errorlevel% neq 0 (
    echo NVM for Windows (nvm command) not found.
    echo Please install NVM for Windows from https://github.com/coreybutler/nvm-windows/releases
    echo After installation, please open a NEW terminal and re-run this script.
    goto :eof_error
)
echo NVM for Windows found.
echo.

REM Install and use the specified Node.js version
echo Installing and using Node.js v%NODE_VERSION_TO_USE% (if not already installed)...
nvm install %NODE_VERSION_TO_USE%
if %errorlevel% neq 0 (
    echo Failed to install Node.js v%NODE_VERSION_TO_USE% using NVM.
    echo Please ensure NVM for Windows is correctly installed and configured.
    goto :eof_error
)
nvm use %NODE_VERSION_TO_USE%
if %errorlevel% neq 0 (
    echo Failed to use Node.js v%NODE_VERSION_TO_USE% using NVM.
    goto :eof_error
)
echo Successfully using Node.js v%NODE_VERSION_TO_USE%.
echo Verifying Node.js and npm versions:
node -v
npm -v
echo.

pushd frontend
echo Current directory: %CD%

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
echo Old dependencies cleanup finished.
echo.

REM Install Node.js dependencies
echo Installing Node.js dependencies with npm install...
npm install
if %errorlevel% neq 0 (
    echo Failed to install Node.js dependencies. Exiting.
    goto :eof_error_popped_frontend
)
echo Node.js dependencies installed successfully.
echo.

REM Launch frontend server
echo Launching frontend server with 'npm run dev'...
echo Frontend server starting. Attempting to access at http://localhost:5173 (or similar port shown by npm)
start "Frontend Server" npm run dev

popd
echo Current directory after POPD from frontend: %CD%
echo Frontend setup complete.
echo.

goto :eof_success

:eof_error_popped_frontend
popd
goto :eof_error

:eof_error_popped
popd
goto :eof_error

:eof_error
echo Script ended with an error.
pause
endlocal
exit /b 1

:eof_success
echo Script finished successfully.
echo Backend should be running at http://localhost:8000
echo Frontend should be running at http://localhost:5173 (or similar)
pause
endlocal
exit /b 0
