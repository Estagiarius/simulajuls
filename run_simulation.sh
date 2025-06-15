#!/bin/bash
set -e
# This is an empty shell script.
# Future commands for running the simulation will be added here.

# Backend setup and launch
echo "Starting backend setup..."

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment and install packages
echo "Activating virtual environment and installing packages..."
source venv/bin/activate
pip install fastapi uvicorn pydantic

# Launch backend server
echo "Launching backend server..."
python -m uvicorn backend.main:app --reload --port 8000 &
echo "Backend server started in background. Attempting to access at http://localhost:8000"
sleep 5

# --- NVM Setup ---
echo "Setting up NVM and Node.js..."
export NVM_DIR="$HOME/.nvm"
# Source nvm if it exists
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Attempt to install nvm if not found
if ! command -v nvm &> /dev/null
then
    echo "NVM command not found, attempting to install NVM v0.39.7..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    # Source nvm again after installation
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# Check if NVM was successfully sourced/installed
if ! command -v nvm &> /dev/null
then
    echo "ERROR: NVM command still not available after attempting installation. Please check NVM installation."
    exit 1
else
    echo "NVM is available."
fi

NODE_VERSION_TO_USE="20"
echo "Installing Node.js v${NODE_VERSION_TO_USE} (if not already installed)..."
nvm install "${NODE_VERSION_TO_USE}" # Install Node.js v20 (or use if already installed)

echo "Setting Node.js v${NODE_VERSION_TO_USE} as default for NVM..."
nvm alias default "${NODE_VERSION_TO_USE}" # Optionally set as default

echo "Verifying Node.js version managed by NVM:"
nvm exec "${NODE_VERSION_TO_USE}" -- node -v
# --- End of NVM Setup ---

# Frontend setup and launch
echo "Starting frontend setup..."
cd frontend

# Clean up old dependencies
echo "Removing old frontend dependencies..."
rm -rf node_modules package-lock.json

# Install Node.js dependencies with Node v20
echo "Installing Node.js dependencies with Node v${NODE_VERSION_TO_USE}..."
nvm exec "${NODE_VERSION_TO_USE}" -- npm install

# Launch frontend server with Node v20
echo "Launching frontend server with Node v${NODE_VERSION_TO_USE}..."
echo "Frontend server starting. Attempting to access at http://localhost:5173 (or similar port shown by npm)"
nvm exec "${NODE_VERSION_TO_USE}" -- npm run dev

# Script finished message and wait for background jobs
echo "Script finished. If frontend is running in foreground, press Ctrl+C to stop."
wait
