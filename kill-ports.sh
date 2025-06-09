#!/bin/bash

echo "========================================="
echo "Killing processes on project ports..."
echo "========================================="

# Define ports used by the project
PORTS=(8000 3000 8080 5000 4000)

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    echo "Checking port $port..."
    
    # Find PIDs using the port
    PIDS=$(lsof -ti :$port 2>/dev/null)
    
    if [ -n "$PIDS" ]; then
        echo "  Found processes on port $port: $PIDS"
        # Kill the processes
        for pid in $PIDS; do
            echo "  Killing process $pid..."
            kill -9 $pid 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "  ✅ Process $pid killed successfully"
            else
                echo "  ❌ Failed to kill process $pid"
            fi
        done
    else
        echo "  No processes found on port $port"
    fi
}

# Kill processes on each port
for port in "${PORTS[@]}"; do
    kill_port $port
done

echo ""
echo "========================================="
echo "Additional cleanup..."
echo "========================================="

# Kill any remaining uvicorn processes (FastAPI)
echo "Killing any remaining uvicorn processes..."
pkill -f "uvicorn" 2>/dev/null && echo "  ✅ Uvicorn processes killed" || echo "  No uvicorn processes found"

# Kill any remaining npm/node processes from this project
echo "Killing any remaining npm/node dev processes..."
pkill -f "npm run dev" 2>/dev/null && echo "  ✅ npm dev processes killed" || echo "  No npm dev processes found"
pkill -f "next" 2>/dev/null && echo "  ✅ Next.js processes killed" || echo "  No Next.js processes found"

# Kill any remaining python agent processes
echo "Killing any remaining python agent processes..."
pkill -f "agent.py" 2>/dev/null && echo "  ✅ Agent processes killed" || echo "  No agent processes found"

echo ""
echo "========================================="
echo "✅ Port cleanup complete!"
echo "========================================="
echo ""
echo "Ports cleaned: ${PORTS[*]}"
echo "You can now start your servers without port conflicts." 