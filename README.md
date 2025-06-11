# AiGroupchat MVP

AI-powered group voice chat application with RAG capabilities, built with Next.js, FastAPI, LiveKit, and Supabase.

## 🎯 Current Status
**7 out of 10 planned stages completed** - The application now supports voice conversations with AI agents that can reference uploaded documents in real-time!

## ✅ Completed Features

### Core Voice Chat (Stages 1-5)
- **Next.js Frontend**: Agent selection and voice room UI
- **FastAPI Backend**: Token generation and agent management
- **LiveKit Integration**: Real-time voice communication
- **AI Agents**: 3 configurable personalities (Alex, Sophie, Marcus)
- **ElevenLabs Voice**: High-quality, low-latency speech synthesis

### RAG Capabilities (Stages 6-7)
- **Document Upload**: PDF and text file processing
- **Vector Database**: Supabase with pgvector for semantic search
- **Smart Chunking**: 512-token chunks with overlap
- **Context Injection**: AI agents reference uploaded documents during conversations
- **Real-time Retrieval**: Document context fetched and injected seamlessly

## 🔧 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+
- LiveKit API credentials (get from https://cloud.livekit.io)
- OpenAI API key
- Deepgram API key  
- ElevenLabs API key
- Supabase project with pgvector extension

### Setup

1. **Configure Environment**:
   ```bash
   # Backend
   cp backend/.env.example backend/.env  # Add your API keys
   
   # Agent  
   cp agent/.env.example agent/.env      # Add your API keys
   ```

2. **Start Services**:
   ```bash
   # Terminal 1: Backend
   cd backend && ./run.sh
   
   # Terminal 2: Agent
   cd agent && ./run.sh
   
   # Terminal 3: Frontend
   cd frontend && npm run dev
   ```

3. **Test the Application**:
   - Open http://localhost:3000
   - Select an AI agent (Alex, Sophie, or Marcus)
   - Join a voice room
   - Upload documents via the backend API
   - Have conversations where agents reference your documents!

## 🧪 Testing

Run automated tests for each stage:
```bash
./test-stage1.sh  # Infrastructure
./test-stage2.sh  # Voice rooms
./test-stage3.sh  # AI agents
./test-stage4.sh  # ElevenLabs voice
./test-stage5.sh  # Agent configuration
./test-stage6.sh  # Vector database
./test-stage7.sh  # RAG implementation
```

## 🤖 AI Agent Personalities

### Alex (Study Partner)
- **Voice**: Brian (warm, friendly male)
- **Style**: Encouraging explanations and supportive guidance
- **Best for**: Learning new concepts, homework help

### Sophie (Socratic Tutor)  
- **Voice**: Sarah (clear, professional female)
- **Style**: Guides discovery through thoughtful questions
- **Best for**: Critical thinking, problem-solving

### Marcus (Debate Partner)
- **Voice**: Josh (confident, articulate male)
- **Style**: Philosophical discussions and counterarguments
- **Best for**: Exploring complex ideas, developing arguments

## 📄 Document-Aware Conversations

Upload documents via the API and watch as agents reference them during conversations:

```bash
# Upload a document
curl -X POST http://localhost:8000/api/documents \
  -F "file=@your-document.pdf" \
  -F "owner_id=your-name"

# Then ask questions about it in voice chat!
# "What did the document say about X?"
# "Can you summarize the main points?"
```

## 📁 Project Structure

```
├── frontend/                 # Next.js application
│   ├── app/components/       # React components
│   │   └── VoiceRoom.tsx    # LiveKit voice room component
│   └── app/page.tsx         # Main page with agent selection
├── backend/                 # FastAPI application  
│   ├── main.py             # API endpoints
│   ├── document_store.py   # RAG document processing
│   └── agent_templates.py  # Agent personality definitions
├── agent/                  # LiveKit Python agent
│   └── agent.py           # RAG-enabled voice agent
├── documentation/          # Technical guides
├── test-stage*.sh         # Automated test scripts
└── MVP-IMPLEMENTATION.md  # Complete implementation guide
```

## 📚 Documentation

- **[MVP-IMPLEMENTATION.md](./MVP-IMPLEMENTATION.md)**: Complete implementation guide with all stages
- **[CLAUDE.md](./CLAUDE.md)**: Development guidance and commands
- **[documentation/](./documentation/)**: Technical guides for LiveKit, ElevenLabs, etc.

## 🚀 Current Capabilities

✅ **7 out of 10 stages complete**
- Real-time voice communication
- 3 AI agent personalities  
- Document upload and processing
- Semantic search and retrieval
- Context-aware AI responses

## 🔮 Planned Enhancements (Stages 8-10)

### Stage 8: Hybrid Search
- BM25 keyword search + vector similarity
- Reciprocal Rank Fusion (RRF) 
- Configurable search weights

### Stage 9: Advanced Processing
- Semantic chunking strategies
- Reranking models integration
- Dynamic chunk sizing

### Stage 10: Contextual Retrieval  
- LLM-generated context headers
- Enhanced metadata enrichment
- Document-level summaries

---

**Ready to explore AI-powered voice conversations with document awareness? Get started with the Quick Start guide above!** 🎤✨
