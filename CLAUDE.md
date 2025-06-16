# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AiGroupchat is an AI-powered group voice chat application that enables users to have natural conversations with AI agents. The application focuses on educational and discussion-based use cases like study groups and philosophical debates. 

**Note**: The current MVP implementation supports only one AI agent per conversation. Multi-agent support is planned for future development.

## Architecture

The application follows a multi-service architecture:

```
ai-group-call-mvp/
├── frontend/                 # Next.js app
│   ├── app/                 # App router pages
│   │   ├── components/      # React components
│   │   │   └── VoiceRoom.tsx # LiveKit voice room component
│   │   └── page.tsx        # Main page with agent selection
│   └── public/              # Static assets
├── backend/                 # Python FastAPI
│   ├── main.py             # API endpoints & token generation
│   ├── agent_templates.py  # Agent personality definitions
│   ├── requirements.txt    # Python dependencies
│   └── .env                # LiveKit credentials
├── agent/                   # LiveKit Python agent
│   ├── agent.py            # AI agent implementation
│   ├── requirements.txt    # Agent dependencies
│   ├── run.sh             # Agent run script
│   └── .env               # Agent API keys
└── documentation/          # Technical docs
```

### Current Implementation Status

- **Stage 1**: ✅ Basic infrastructure (Next.js + FastAPI)
- **Stage 2**: ✅ LiveKit voice room for human-to-human calls
- **Stage 3**: ✅ Single AI agent (completed)
- **Stage 4**: ✅ ElevenLabs integration (completed)
- **Stage 5**: ✅ Agent configuration UI (completed)
- **Stage 6**: ✅ Supabase Vector Database Setup (completed)
- **Stage 7**: ✅ Basic RAG with Document Upload (completed)
- **Stage 8**: ✅ Hybrid Search Implementation (completed)
- **Stage 9**: ✅ Advanced Chunking & Reranking (completed)
- **Stage 10**: ✅ Contextual Retrieval (completed)

### Key Components

1. **Frontend (Next.js)**: Handles user interface, agent configuration, and WebRTC room management
2. **Backend (FastAPI)**: Manages agent orchestration, personality definitions, and API endpoints
3. **LiveKit Infrastructure**: Provides real-time communication via WebRTC and agent orchestration
4. **Voice Synthesis**: ElevenLabs for high-quality, low-latency voice generation
5. **LLM Integration**: OpenAI/Anthropic for agent intelligence and personality
6. **Vector Database**: Supabase with pgvector for document storage and similarity search
7. **RAG System**: LangChain for document processing and retrieval orchestration

## Technology Stack

### Current Implementation
- **LiveKit**: Real-time communication and WebRTC infrastructure
- **LiveKit Agents Framework**: Single agent orchestration (Python)
- **ElevenLabs**: Voice synthesis with conversational AI capabilities
- **Next.js**: Frontend framework
- **Python FastAPI**: Backend API framework
- **OpenAI**: LLM provider for agent intelligence (GPT-4o-mini)
- **Deepgram**: Speech-to-text recognition
- **Silero**: Voice activity detection

### RAG Technologies (Stages 6-7 Completed)
- **Supabase**: PostgreSQL database with pgvector extension for vector storage
- **LangChain**: RAG orchestration and document processing framework
- **OpenAI Embeddings**: text-embedding-3-small for vector generation
- **pypdf2**: PDF document parsing

### Implemented Advanced RAG Technologies (Stages 8-10)
- **rank-bm25**: BM25 keyword search implementation
- **sentence-transformers**: CrossEncoder reranking models
- **anthropic**: Claude API for contextual retrieval

## Development Commands

### Frontend Commands
- Development server: `cd frontend && npm run dev`
- Build: `cd frontend && npm run build`
- Lint: `cd frontend && npm run lint`
- Start production: `cd frontend && npm start`
- Install dependencies: `cd frontend && npm install`

### Backend Commands
- Database setup (first time): Follow `backend/SUPABASE_SETUP.md` guide
- Verify setup: `cd backend && ./setup_database.sh`
- Run server (recommended): `cd backend && ./run.sh`
- Manual install: `cd backend && pip install -r requirements.txt`
- Manual run: `cd backend && uvicorn main:app --reload --port 8000`

### Agent Commands
- Run agent (recommended): `cd agent && ./run.sh`
- Manual install: `cd agent && pip install -r requirements.txt`
- Manual run: `cd agent && python agent.py dev`

### Testing Commands
- Stage 1 test: `./test-stage1.sh`
- Stage 2 test: `./test-stage2.sh`
- Stage 3 test: `./test-stage3.sh`
- Stage 4 test: `./test-stage4.sh`
- Stage 5 test: `./test-stage5.sh`
- Stage 6 test: `./test-stage6.sh`
- Stage 7 test: `./test-stage7.sh`
- Stage 8 test: `./test-stage8.sh`

## Implementation Details

### Backend API Endpoints
- `GET /health` - Health check endpoint
- `POST /api/token` - Generate LiveKit access token
  - Request body: `{ "room_name": string, "participant_name": string, "enable_ai_agent": boolean, "agent_type": string, "agent_types": string[] }`
  - Response: `{ "token": string, "url": string, "ai_agent_enabled": boolean, "agent_type": string }`
- `GET /api/agent-templates` - Get available agent templates
- `GET /api/agent-templates/{template_type}` - Get specific agent template details
- `GET /api/documents?owner_id={owner_id}` - Get documents for a specific owner
- `POST /api/documents/context` - Retrieve relevant document context for RAG
  - Request body: `{ "query": string, "owner_id": string }`
  - Response: `{ "context": string, "has_context": boolean }`
- `POST /api/documents/upload` - Upload and process documents for RAG
- `POST /api/documents/search` - Search documents using semantic similarity
- `POST /api/conversation/message` - Store a conversation message
  - Request body: `{ "room_name": string, "participant_name": string, "participant_type": string, "message": string }`
- `GET /api/conversation/{room_name}` - Get conversation history
  - Query params: `limit` (default: 20)

### Frontend Components
- `page.tsx` - Main page with room join form and agent selection
- `VoiceRoom.tsx` - LiveKit voice room component
  - Handles room connection and disconnection
  - Manages audio track publishing/subscribing
  - Displays participant list with AI/Human indicators
- `DocumentManager.tsx` - Document upload and management component
  - File upload interface for PDF and TXT files
  - Document list display with metadata
  - Real-time document fetching for users

### Agent Configuration
Three hardcoded agent templates:
1. **Alex (study_partner)** - Friendly study helper with Brian voice
2. **Sophie (socratic_tutor)** - Socratic questioner with Sarah voice  
3. **Marcus (debate_partner)** - Philosophical debater with Josh voice

### Environment Configuration
Backend `.env`:
```
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

Backend `.env` (Official Contextual Retrieval):
```
ANTHROPIC_API_KEY=your-anthropic-api-key
ENABLE_CONTEXTUAL_RETRIEVAL=true
CONTEXTUAL_RETRIEVAL_MODEL=claude-3-haiku-20240307
MAX_CONTEXTUAL_TOKENS_PER_DOCUMENT=100000
MAX_DAILY_CONTEXTUAL_REQUESTS=1000
CONTEXTUAL_PROCESSING_TIMEOUT=120
```

Agent `.env`:
```
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
LIVEKIT_URL=wss://your-project.livekit.cloud
OPENAI_API_KEY=your-openai-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key
ELEVEN_API_KEY=your-elevenlabs-api-key
```

## Key Implementation Guidelines

### Agent System
- Agents are built on LiveKit's Agent Framework with voice capabilities
- Each agent has a personality defined through prompts with RAG document access
- Agents can interrupt and engage in natural turn-taking conversations
- RAG integration using `on_user_turn_completed` method for context injection
- Document context retrieved per-user from Supabase vector database
- Currently supports only 1 AI agent per room (multi-agent planned for future)

### Real-time Communication
- Use LiveKit's WebRTC infrastructure for audio/video
- Implement proper noise and echo cancellation
- Handle connection states and reconnection logic
- Use LiveKit's state synchronization for room metadata

### Voice Integration
- ElevenLabs for text-to-speech with low latency requirements
- Implement streaming TTS for natural conversation flow
- Consider voice consistency across sessions
- Handle voice selection and customization per agent

### Frontend Patterns
- Use Next.js app router conventions
- Implement real-time state management for call rooms
- Create reusable components for agent configuration
- Follow LiveKit SDK patterns for media handling

### Backend Patterns
- Use FastAPI async endpoints for real-time operations
- Create/update rooms with metadata for agent configuration
- Create modular agent personality system
- Room metadata is the primary source for agent type configuration

## Important Resources

- LiveKit documentation is provided in `documentation/LiveKit-llms.md`
- ElevenLabs documentation is provided in `documentation/Elevenlabs-llms.md`
- MVP implementation plan is detailed in `MVP-implementation-plan.md`
- Implementation summary is available in `IMPLEMENTATION-SUMMARY.md`
- Quick start guide is available in `README.md`

When implementing features, always refer to the provided documentation for best practices and examples. If you find a url you are interested in for the current feature, please crawl the url and add the content to the documentation file.

## Dependencies

### Backend
- `livekit-api==0.7.0` - LiveKit Python SDK for token generation
- `python-dotenv==1.0.1` - Environment variable management
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `supabase==2.10.0` - Supabase client for vector database
- `langchain==0.3.14` - RAG orchestration framework
- `langchain-openai==0.2.14` - OpenAI integration for embeddings
- `pypdf2==3.0.1` - PDF document parsing
- `openai==1.58.1` - OpenAI API client
- `anthropic>=0.40.0` - Anthropic Claude API for contextual retrieval

### Frontend
- `@livekit/components-react@^2.9.9` - LiveKit React components
- `@livekit/components-styles@^1.1.6` - LiveKit component styles
- `livekit-client@^2.13.3` - LiveKit JavaScript client SDK
- `next` - React framework
- `react` & `react-dom` - UI library

### Agent
- `livekit-agents[openai,silero,deepgram,elevenlabs]~=1.0` - LiveKit agent framework with plugins
- `python-dotenv==1.0.1` - Environment variable management
- `httpx==0.27.2` - HTTP client for RAG context retrieval

## Recent Changes

- **Multi-Agent Support (2025)**:
  - **Conversation Memory**: All messages stored in Supabase with room context
  - **Multi-Agent Rooms**: Support for 1-2 AI agents per conversation
  - **Agent Awareness**: Agents know about each other and reference contributions
  - **Simple Turn-Taking**: 2-second delay prevents agent overlap
  - **Frontend Updates**: Dual agent selection with dropdown UI
  - **Minimal Implementation**: ~140 lines of code total
- **Performance Optimizations (2025)**:
  - **Cache-Aware Rate Limiting**: Upgraded to Claude 3.5 Sonnet where cached tokens don't count against ITPM limits
  - **Batch API Integration**: Automatic batch processing for documents ≥10 chunks (50% cost reduction)
  - **Smart Processing Logic**: Streaming for small docs, batch for large docs
  - **Combined Cost Savings**: Up to 95% cost reduction (90% caching + 50% batch discount)
  - **Simplified Implementation**: Clean, deterministic processing pipeline

- **Completed Contextual Retrieval Implementation (Stage 10)**:
  - Integrated Anthropic Claude API for contextual chunk enhancement
  - Implemented prompt caching for cost optimization (90% reduction)
  - Enhanced document processing with contextual information generation
  - Updated hybrid search and BM25 indexing to use contextual content
  - Added migration tools for existing documents
  - Created comprehensive testing and monitoring tools
  - Added new API endpoints for contextual features and statistics

- **Completed RAG Implementation (Stages 6-7)**:
  - Integrated Supabase vector database with pgvector extension
  - Implemented document upload, processing, and embedding generation
  - Added semantic search using OpenAI embeddings (text-embedding-3-small)
  - Built RAG voice agent using LiveKit's `on_user_turn_completed` method
  - Added document context retrieval API with configurable similarity thresholds
  - Successfully tested voice queries with document context injection

- **Agent System Improvements**:
  - Fixed agent selection mechanism to properly use room metadata
  - Agent checks multiple sources in order: job metadata → room metadata → participant metadata
  - Backend creates rooms with metadata containing agent type
  - All 7 MVP stages are now complete and tested

## RAG Implementation Details

### Stage 6: Supabase Vector Database Setup (✅ Completed)
- ✅ Installed Supabase client and set up pgvector extension
- ✅ Created schema: `documents` table (id, owner_id, title, type, metadata) and `document_sections` table (id, document_id, content, embedding vector(1536), metadata)
- ✅ Implemented Row Level Security (RLS) policies for document access control
- ✅ Added file upload endpoint to backend API

### Stage 7: Basic RAG Implementation (✅ Completed)
- ✅ Added document processing: PDF parsing (pypdf2), text extraction, basic fixed-size chunking (512 tokens)
- ✅ Generated embeddings using OpenAI's text-embedding-3-small model
- ✅ Store chunks with embeddings in Supabase
- ✅ Implemented basic semantic search endpoint using cosine similarity
- ✅ Updated agent to query document context using `on_user_turn_completed` method

### RAG Agent Implementation Details
- **DocumentContextManager**: Handles HTTP requests to backend for context retrieval
- **RAGVoiceAgent**: Extends LiveKit's Agent class with RAG capabilities
- **Context Injection**: Uses `on_user_turn_completed` to inject document context as system messages
- **Error Handling**: Robust timeout and error handling for document retrieval
- **Voice Integration**: Seamless integration with existing voice agent personalities

## Future RAG Enhancements (Stages 8-10)

### Stage 8: Hybrid Search Implementation (✅ Completed)
- ✅ Added BM25 index using rank-bm25 library for keyword search
- ✅ Implemented Reciprocal Rank Fusion (RRF) to combine vector and keyword results
- ✅ Created hybrid search endpoint that merges both search types
- ✅ Added search configuration options via environment variables

### Stage 9: Advanced Chunking & Reranking (✅ Completed)
- ✅ Implemented intelligent chunking with dynamic strategies
- ✅ Added content-aware chunking (800 tokens with 10% overlap)
- ✅ Integrated CrossEncoder reranking (ms-marco-MiniLM-L-6-v2)
- ✅ Implemented dynamic chunk size selection based on content type

### Stage 10: Contextual Retrieval (✅ Completed - Official Implementation)
- ✅ Implemented official Anthropic Contextual Retrieval using exact specifications
- ✅ Official beta prompt caching API with proper headers and token tracking
- ✅ Claude-3-Haiku model for optimal cost efficiency
- ✅ Exact prompt template matching Anthropic documentation
- ✅ 800-token chunks with 10% overlap as recommended
- ✅ Comprehensive cache metrics and cost monitoring
- ✅ 90%+ cost reduction through proper caching implementation

### Key Technologies for RAG
- **Supabase + pgvector**: Vector storage with built-in RLS
- **LangChain**: RAG orchestration and document processing
- **OpenAI embeddings**: text-embedding-3-small for vectors
- **rank-bm25**: Keyword search implementation
- **sentence-transformers**: Advanced chunking and reranking