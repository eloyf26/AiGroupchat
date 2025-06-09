 #!/bin/bash

echo "========================================="
echo "Stage 5 Test: Minimal Agent Configuration"
echo "========================================="
echo ""
echo "Prerequisites:"
echo "- All Stage 4 requirements"
echo "- Backend and agent code updated for Stage 5"
echo ""
echo "Changes in Stage 5:"
echo "- 3 hardcoded agent templates available"
echo "- Simple dropdown selection in UI"
echo "- Agent personality switching via API"
echo ""
echo "Available Agents:"
echo "1. Alex (Study Partner) - Friendly helper with Brian's voice"
echo "2. Sophie (Socratic Tutor) - Guides through questions with Sarah's voice"
echo "3. Marcus (Debate Partner) - Philosophical debater with Josh's voice"
echo ""
echo "Testing steps:"
echo ""

# Copy .env file from backend to agent if it exists
if [ -f "backend/.env" ] && [ ! -f "agent/.env" ]; then
    echo "Copying LiveKit credentials to agent directory..."
    cp backend/.env agent/.env
    echo "IMPORTANT: Ensure all API keys are configured in agent/.env"
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
echo "2. Starting AI agent with personality switching..."
cd ../agent
echo "   - Setting up agent environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "   - Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "   - Downloading required models..."
python -m livekit.plugins.silero download 2>/dev/null || true

echo "   - Starting LiveKit agent with configurable personalities..."
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
echo "✅ Stage 5 Setup Complete!"
echo "========================================="
echo ""
echo "Test Instructions:"
echo ""
echo "1. Open http://localhost:3000 in your browser"
echo ""
echo "2. Enter your name to join"
echo ""
echo "3. You'll see a checkbox to 'Enable AI Agent' (checked by default)"
echo ""
echo "4. You'll see a dropdown to 'Select AI Agent' with three options:"
echo "   - Alex - Friendly study partner who helps with learning"
echo "   - Sophie - Socratic tutor who guides through questioning"
echo "   - Marcus - Philosophical debate partner"
echo ""
echo "5. Test each agent type:"
echo "   a) Join with Alex and ask about a subject to study"
echo "   b) Leave and rejoin with Sophie, ask a question"
echo "   c) Leave and rejoin with Marcus, propose a topic to debate"
echo ""
echo "6. Verify each agent:"
echo "   - Has a different voice (male/female/different tone)"
echo "   - Has a different personality and conversation style"
echo "   - Maintains their character throughout the conversation"
echo ""
echo "7. Test disabling AI agent:"
echo "   - Uncheck 'Enable AI Agent' and join"
echo "   - Verify no agent joins the room"
echo ""
echo "API Endpoints to test:"
echo "- GET http://localhost:8000/api/agent-templates"
echo "- GET http://localhost:8000/api/agent-templates/study_partner"
echo "- GET http://localhost:8000/api/agent-templates/socratic_tutor"
echo "- GET http://localhost:8000/api/agent-templates/debate_partner"
echo ""
echo "Press Ctrl+C to stop all servers..."
echo ""

# Wait for user to press Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $AGENT_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait