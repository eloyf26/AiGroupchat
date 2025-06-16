# AiGroupchat MVP

AI-powered group voice chat application with RAG capabilities, built with Next.js, FastAPI, LiveKit, and Supabase.

## 🎯 Current Status
**All MVP stages completed + Multi-Agent Support!** - The application now supports conversation memory and multiple AI agents in the same room!

## ✅ Completed Features

### Core Voice Chat (Stages 1-5)
- **Next.js Frontend**: Agent selection and voice room UI
- **FastAPI Backend**: Token generation and agent management
- **LiveKit Integration**: Real-time voice communication
- **AI Agents**: 3 configurable personalities (Alex, Sophie, Marcus)
- **ElevenLabs Voice**: High-quality, low-latency speech synthesis
- **Multi-Agent Support**: Run 1 or 2 AI agents simultaneously
- **Conversation Memory**: Persistent chat history stored in Supabase

### RAG Capabilities (Stages 6-10)
- **Document Upload**: PDF and text file processing
- **Vector Database**: Supabase with pgvector for semantic search
- **Smart Chunking**: 800-token chunks with 10% overlap (Anthropic recommendation)
- **Hybrid Search**: BM25 keyword search + vector similarity with Reciprocal Rank Fusion
- **Reranking**: CrossEncoder reranking for improved result quality
- **Contextual Retrieval**: Anthropic Claude-powered context enhancement with 90%+ cost reduction
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
   
2. **Database Migration** (for improved conversation memory):
   ```bash
   # If upgrading an existing installation, run:
   psql $DATABASE_URL < backend/migrate_conversation_security.sql
   
   # For cleanup job setup, see backend/CONVERSATION_CLEANUP.md
   ```

2. **Setup Database** (first time only):
   ```bash
   # Run migration in Supabase SQL editor
   cd backend && cat migrate_conversation.sql
   ```

3. **Start Services**:
   ```bash
   # Terminal 1: Backend
   cd backend && ./run.sh
   
   # Terminal 2: Agent(s)
   cd agent && ./run.sh        # Single agent
   # OR
   cd agent && ./run-multi.sh 2  # Two agents
   
   # Terminal 3: Frontend
   cd frontend && npm run dev
   ```

4. **Test the Application**:
   - Open http://localhost:3000
   - Select 1 or 2 AI agents (Alex, Sophie, or Marcus)
   - Join a voice room
   - Upload documents via the backend API
   - Have conversations where agents reference your documents and remember context!

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
./test-stage8.sh  # Hybrid search & reranking
./test-conversation-memory.sh  # Test new conversation and multi-agent features
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

# Configure enhanced search (optional)
export USE_HYBRID_SEARCH=true   # Enable BM25 + vector hybrid search
export USE_RERANK=true          # Enable reranking for better results
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

✅ **All MVP stages complete + Advanced Features**
- Real-time voice communication
- 3 AI agent personalities  
- Multi-agent conversations (1-2 agents per room)
- Persistent conversation memory
- Document upload and processing
- Semantic search and retrieval
- Hybrid search with BM25 + vector similarity
- Reranking with CrossEncoder models
- Contextual retrieval with Anthropic Claude
- Context-aware AI responses with memory

## 🎭 Multi-Agent Conversations

**New Feature**: Have conversations with multiple AI agents simultaneously!

### How it Works:
1. Select up to 2 agents in the UI
2. Agents are aware of each other and reference each other's contributions
3. Simple turn-taking prevents agents from talking over each other
4. All conversations are stored in Supabase for context

### Example Combinations:
- **Study Session**: Alex (Study Partner) + Sophie (Socratic Tutor)
- **Debate Club**: Sophie (Socratic Tutor) + Marcus (Debate Partner)
- **Learning Lab**: Alex (Study Partner) + Marcus (Debate Partner)

### Running Multiple Agents:
```bash
# Single agent (default)
cd agent && ./run.sh

# Two agents
cd agent && ./run-multi.sh 2
```

## 🎉 Completed Advanced RAG Features

### Stage 8: Hybrid Search ✅
- BM25 keyword search + vector similarity
- Reciprocal Rank Fusion (RRF) 
- Configurable search weights
- Performance-optimized with caching

### Stage 9: Advanced Processing ✅
- Intelligent chunking strategies
- CrossEncoder reranking models
- Dynamic chunk sizing based on content

### Stage 10: Contextual Retrieval ✅
- Anthropic Claude-powered context generation
- Prompt caching with 90%+ cost reduction
- Batch API for large documents
- Enhanced metadata enrichment

---

**Ready to explore AI-powered voice conversations with document awareness? Get started with the Quick Start guide above!** 🎤✨
