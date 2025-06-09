#!/bin/bash
# Script to run the LiveKit AI agent

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download required models
echo "Downloading required models..."
python -m livekit.plugins.silero download

# Run the agent
echo "Starting AI agent..."
python agent.py dev