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
# Note: Silero models are now auto-downloaded on first use
# If you need to pre-download, use: python -c "from livekit.plugins import silero; silero.VAD.load()"
python -c "
try:
    from livekit.plugins import silero
    print('Silero plugin available - models will be downloaded on first use')
except ImportError as e:
    print(f'Warning: Could not import Silero plugin: {e}')
    print('Agent will continue without VAD (Voice Activity Detection)')
"

# Run the agent
echo "Starting AI agent..."
python agent.py dev