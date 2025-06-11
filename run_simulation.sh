#!/bin/bash
set -e
# This is an empty shell script.
# Future commands for running the simulation will be added here.

# Backend setup and launch
echo "Starting backend setup..."
cd backend

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
python -m uvicorn main:app --reload --port 8000 &
echo "Backend server started in background. Attempting to access at http://localhost:8000"
sleep 5

# Navigate back to project root
cd ..

# Frontend setup and launch
echo "Starting frontend setup..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Launch frontend server
echo "Launching frontend server..."
echo "Frontend server starting. Attempting to access at http://localhost:5173 (or similar port shown by npm)"
npm run dev

# Script finished message and wait for background jobs
echo "Script finished. If frontend is running in foreground, press Ctrl+C to stop."
wait
