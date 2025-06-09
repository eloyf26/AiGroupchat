#!/bin/bash

echo "========================================="
echo "Stage 2 Test: LiveKit Voice Room"
echo "========================================="
echo ""
echo "Prerequisites:"
echo "- LiveKit API credentials configured in backend/.env"
echo "- For testing locally, install LiveKit server or use LiveKit Cloud"
echo ""
echo "To install LiveKit server locally:"
echo "  Option 1 (Docker): docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp -p 50000-60000:50000-60000/udp livekit/livekit-server --dev"
echo "  Option 2 (Homebrew): brew update && brew install livekit && livekit-server --dev"  
echo ""
echo "Testing steps:"
echo ""
echo "1. Starting backend server..."
echo "   - Installing dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "   - Starting FastAPI server..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
sleep 3

echo ""
echo "2. Starting frontend..."
cd ../frontend
echo "   - Installing dependencies (if needed)..."
npm install > /dev/null 2>&1

echo "   - Starting Next.js development server..."
npm run dev &
FRONTEND_PID=$!
sleep 5

echo ""
echo "========================================="
echo "✅ Stage 2 Setup Complete!"
echo "========================================="
echo ""
echo "Test Instructions:"
echo "1. Configure LiveKit credentials in backend/.env:"
echo "   - For local development (with livekit-server --dev):"
echo "     LIVEKIT_API_KEY=devkey"
echo "     LIVEKIT_API_SECRET=secret" 
echo "     LIVEKIT_URL=ws://localhost:7880"
echo "   - For LiveKit Cloud: Get credentials from https://cloud.livekit.io"
echo "     Update LIVEKIT_API_KEY, LIVEKIT_API_SECRET, and LIVEKIT_URL"
echo ""
echo "2. Open http://localhost:3000 in your browser"
echo ""
echo "3. Enter your name and join the 'test-room'"
echo ""
echo "4. Open another browser tab/window in incognito mode"
echo ""
echo "5. Join with a different name"
echo ""
echo "6. Test voice communication between the two participants"
echo ""
echo "Press Ctrl+C to stop all servers..."
echo ""

# Wait for user to press Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait