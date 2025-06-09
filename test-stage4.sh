#!/bin/bash

echo "========================================="
echo "Stage 4 Test: ElevenLabs Voice Integration"
echo "========================================="
echo ""
echo "Prerequisites:"
echo "- All Stage 3 requirements"
echo "- ElevenLabs API key configured in agent/.env"
echo ""
echo "Changes in Stage 4:"
echo "- Replaced OpenAI TTS with ElevenLabs"
echo "- Using 'eleven_flash_v2_5' model for low latency"
echo "- Selected 'Brian' voice (warm, friendly male)"
echo ""
echo "Testing steps:"
echo ""

# Copy .env file from backend to agent if it exists
if [ -f "backend/.env" ] && [ ! -f "agent/.env" ]; then
    echo "Copying LiveKit credentials to agent directory..."
    cp backend/.env agent/.env
    echo "IMPORTANT: Add your ElevenLabs API key to agent/.env"
fi

echo "1. Starting backend server..."
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
echo "2. Starting AI agent with ElevenLabs..."
cd ../agent
echo "   - Setting up agent environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "   - Installing dependencies (including ElevenLabs)..."
pip install -r requirements.txt > /dev/null 2>&1

echo "   - Downloading required models..."
python -m livekit.plugins.silero download 2>/dev/null || true

echo "   - Starting LiveKit agent with ElevenLabs TTS..."
python agent.py dev &
AGENT_PID=$!
sleep 5

echo ""
echo "3. Starting frontend..."
cd ../frontend
echo "   - Installing dependencies (if needed)..."
npm install > /dev/null 2>&1

echo "   - Starting Next.js development server..."
npm run dev &
FRONTEND_PID=$!
sleep 5

echo ""
echo "========================================="
echo "✅ Stage 4 Setup Complete!"
echo "========================================="
echo ""
echo "Test Instructions:"
echo "1. Ensure you have added these API keys to agent/.env:"
echo "   - OPENAI_API_KEY=your-openai-api-key"
echo "   - DEEPGRAM_API_KEY=your-deepgram-api-key"
echo "   - ELEVEN_API_KEY=your-elevenlabs-api-key"
echo ""
echo "2. Open http://localhost:3000 in your browser"
echo ""
echo "3. Enter your name and join the room"
echo ""
echo "4. The AI agent 'Alex' should join with ElevenLabs voice"
echo ""
echo "5. Test the voice quality and latency:"
echo "   - Voice should sound more natural than OpenAI TTS"
echo "   - Latency should be low (< 1 second)"
echo "   - Voice should be warm and friendly (Brian)"
echo ""
echo "Expected improvements over Stage 3:"
echo "- More natural and expressive voice"
echo "- Better emotional range"
echo "- Smoother speech patterns"
echo "- Professional voice quality"
echo ""
echo "Press Ctrl+C to stop all servers..."
echo ""

# Wait for user to press Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $AGENT_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait