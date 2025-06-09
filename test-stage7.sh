#!/bin/bash

echo "========================================="
echo "Stage 7 Test: Basic RAG with Document Upload"
echo "========================================="
echo ""
echo "Prerequisites:"
echo "- All Stage 5 requirements"
echo "- Supabase database with pgvector configured"
echo "- OpenAI API key for embeddings"
echo "- Backend and agent code updated for Stage 7"
echo ""
echo "Changes in Stage 7:"
echo "- Document upload endpoint with PDF/TXT support"
echo "- Automatic text chunking (512 tokens per chunk)"
echo "- Embedding generation using OpenAI text-embedding-3-small"
echo "- Semantic search endpoint"
echo "- Agent queries document context before responding"
echo ""
echo "Testing steps:"
echo ""

# Copy .env file from backend to agent if it exists
if [ -f "backend/.env" ] && [ ! -f "agent/.env" ]; then
    echo "Copying credentials to agent directory..."
    cp backend/.env agent/.env
fi

echo "1. Starting backend server with RAG support..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "   - Starting FastAPI server..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
sleep 5

echo ""
echo "2. Starting AI agent with document context support..."
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

echo "   - Starting LiveKit agent with RAG support..."
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
echo "✅ Stage 7 Setup Complete!"
echo "========================================="
echo ""
echo "Test Instructions:"
echo ""
echo "1. Document Upload Test:"
echo "   a) Use curl to upload a test document:"
echo "      curl -X POST http://localhost:8000/api/documents \\"
echo "        -F 'file=@backend/test_doc.txt' \\"
echo "        -F 'title=Test Document' \\"
echo "        -F 'owner_id=test-user'"
echo ""
echo "   b) List documents:"
echo "      curl 'http://localhost:8000/api/documents?owner_id=test-user'"
echo ""
echo "2. Document Search Test:"
echo "   a) Search documents:"
echo "      curl -X POST http://localhost:8000/api/documents/search \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"query\": \"your search query\", \"owner_id\": \"test-user\"}'"
echo ""
echo "3. Voice Chat with RAG Test:"
echo "   a) Open http://localhost:3000 in your browser"
echo "   b) Enter 'test-user' as your name (same as owner_id used above)"
echo "   c) Join with AI agent enabled"
echo "   d) Ask questions related to your uploaded document"
echo "   e) Verify the agent uses document context in responses"
echo ""
echo "4. Test Different Document Types:"
echo "   - Upload a PDF file if available"
echo "   - Upload multiple documents"
echo "   - Test search relevance with different queries"
echo ""
echo "API Endpoints added in Stage 7:"
echo "- POST /api/documents - Upload document with embeddings"
echo "- GET /api/documents?owner_id=<id> - List user documents"
echo "- POST /api/documents/search - Semantic search"
echo "- POST /api/documents/context - Get context for agent"
echo ""
echo "Press Ctrl+C to stop all servers..."
echo ""

# Wait for user to press Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $AGENT_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait