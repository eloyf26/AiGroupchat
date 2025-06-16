#!/bin/bash
# Script to run multiple LiveKit AI agents

# Number of agents to run (default 2)
NUM_AGENTS=${1:-2}

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

# Run multiple agent instances
echo "Starting $NUM_AGENTS AI agents..."
for i in $(seq 0 $((NUM_AGENTS-1))); do
    echo "Starting agent $i..."
    AGENT_INDEX=$i python agent.py dev &
    sleep 2  # Small delay between starts
done

echo "All agents started. Press Ctrl+C to stop all agents."
wait