#!/bin/bash
# Start the FastAPI backend

echo "Setting up Python environment..."

# Try to create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || {
        echo "Failed to create venv. Install with: sudo apt install python3-venv"
        echo "Or use system packages: python3 -m pip install --break-system-packages fastapi uvicorn[standard]"
        exit 1
    }
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
uvicorn main:app --reload --port 8000