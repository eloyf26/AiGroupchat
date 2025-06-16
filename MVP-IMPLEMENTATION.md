# AiGroupchat MVP Implementation Guide

## Overview
This document provides a comprehensive implementation guide for the AiGroupchat MVP. All 10 stages plus multi-agent support have been successfully implemented, creating an AI-powered group voice chat application with configurable agent personalities, RAG (Retrieval-Augmented Generation) capabilities, conversation memory, and multi-agent support using LiveKit, OpenAI, Deepgram, ElevenLabs, and Supabase.

## Implementation Status

### ✅ Completed Stages (10/10)

#### Stage 1: Minimal Infrastructure
**Status: COMPLETE**
- ✅ Next.js frontend with React 19
- ✅ FastAPI backend with health endpoint
- ✅ CORS configured for local development
- ✅ No authentication or database
- ✅ Local development setup

**Test Script**: `./test-stage1.sh`

#### Stage 2: LiveKit Voice Room
**Status: COMPLETE**
- ✅ LiveKit Cloud integration
- ✅ Token generation API endpoint
- ✅ Voice room React component
- ✅ Audio controls (mute/unmute)
- ✅ Participant list with visual indicators
- ✅ Human-to-human voice calls

**Implemented Features:**
- Token generation API endpoint (`POST /api/token`)
- VoiceRoom React component with LiveKit integration
- Audio controls and participant management
- Room join/leave functionality

**Test Script**: `./test-stage2.sh`

#### Stage 3: Single AI Agent
**Status: COMPLETE**
- ✅ Python LiveKit agent framework
- ✅ Fixed "Alex" study partner personality
- ✅ Silero VAD for voice activity detection
- ✅ Deepgram STT for speech recognition
- ✅ OpenAI GPT-4o-mini for LLM
- ✅ OpenAI TTS for initial voice synthesis
- ✅ Automatic agent dispatch

**Technical Implementation:**
- Enhanced UI to distinguish AI from human participants
- Voice pipeline: Silero VAD → Deepgram STT → OpenAI LLM → TTS
- Automatic agent joining when room is created

**Test Script**: `./test-stage3.sh`

#### Stage 4: ElevenLabs Integration
**Status: COMPLETE**
- ✅ Replaced OpenAI TTS with ElevenLabs
- ✅ Using Flash v2.5 model for lowest latency
- ✅ Brian voice (warm, friendly male)
- ✅ Optimized voice settings for conversation
- ✅ Streaming enabled by default

**Voice Configuration:**
```python
tts=elevenlabs.TTS(
    model="eleven_flash_v2_5",  # Flash model for lowest latency
    voice_id="nPczCjzI2devNBz1zQrb",  # Brian voice
    language="en",
    voice_settings=elevenlabs.VoiceSettings(
        stability=0.5,  # Natural variability
        similarity_boost=1.0,  # Maximum clarity
        style=0.0,  # Natural speaking style
    ),
)
```

**Test Script**: `./test-stage4.sh`

#### Stage 5: Agent Configuration
**Status: COMPLETE**
- ✅ 3 hardcoded agent templates:
  - Alex: Study Partner (Brian voice)
  - Sophie: Socratic Tutor (Sarah voice)
  - Marcus: Debate Partner (Josh voice)
- ✅ Agent selection dropdown in UI
- ✅ Dynamic personality switching
- ✅ Agent type passed via room metadata
- ✅ API endpoints for template discovery

**Agent Templates:**

1. **Alex (Study Partner)**
   - Voice: Brian (warm, friendly male)
   - Style: Helps students understand complex topics
   - Approach: Encouraging and supportive

2. **Sophie (Socratic Tutor)**
   - Voice: Sarah (clear, professional female)
   - Style: Guides students to discover answers themselves
   - Approach: Asks probing questions

3. **Marcus (Debate Partner)**
   - Voice: Josh (confident, articulate male)
   - Style: Explores ideas through philosophical debate
   - Approach: Presents thoughtful counterarguments

**Recent Fix:**
- Fixed agent selection mechanism to properly read agent type from room metadata
- Agent now checks multiple sources: job metadata → room metadata → participant metadata
- Backend creates/updates room with metadata when AI agent is enabled

**Test Script**: `./test-stage5.sh`

#### Stage 6: Supabase Vector Database
**Status: COMPLETE**
- ✅ PostgreSQL database with pgvector extension
- ✅ Document storage with Row Level Security (RLS)
- ✅ Vector embeddings using OpenAI text-embedding-3-small
- ✅ Document sections table for chunked content
- ✅ RESTful API for document management

**Database Schema:**
- **documents**: Stores document metadata (id, owner_id, title, type, metadata)
- **document_sections**: Stores chunks with embeddings (id, document_id, content, embedding vector(1536), metadata)
- **search_document_sections**: PostgreSQL function for vector similarity

**Test Script**: `./test-stage6.sh`

#### Stage 7: RAG Implementation
**Status: COMPLETE**
- ✅ Document upload and processing (PDF support)
- ✅ Text chunking with 512-token fixed-size chunks
- ✅ Semantic search using cosine similarity
- ✅ Voice agent integration with LiveKit's `on_user_turn_completed`
- ✅ Context injection for document-aware responses
- ✅ HTTP client for real-time context retrieval

**RAG Agent Implementation:**
- **DocumentContextManager**: Handles HTTP requests to backend for context retrieval
- **RAGVoiceAgent**: Extends LiveKit's Agent class with RAG capabilities
- **Context Injection**: Uses `on_user_turn_completed` to inject document context as system messages
- **Error Handling**: Robust timeout and HTTP error handling for document retrieval

**API Endpoints:**
```python
# Upload document with automatic processing
POST /api/documents
  - Accepts: PDF, TXT files
  - Returns: document_id, chunk_count

# Search documents semantically
POST /api/documents/search
  - Input: query, owner_id
  - Returns: relevant chunks with similarity scores

# Get context for agent
POST /api/documents/context
  - Input: query, owner_id
  - Returns: formatted context for LLM
```

**Test Script**: `./test-stage7.sh`

### ✅ Completed Advanced RAG Stages (8-10)

#### Stage 8: Hybrid Search Implementation
**Status: COMPLETE**
- ✅ BM25 index using rank-bm25 library for keyword search
- ✅ Reciprocal Rank Fusion (RRF) to combine vector and keyword results
- ✅ Hybrid search with concurrent vector and BM25 queries
- ✅ Configurable via USE_HYBRID_SEARCH environment variable
- ✅ Performance-optimized with caching and pre-built indexes

**Test Script**: `./test-stage8.sh`

#### Stage 9: Advanced Chunking & Reranking
**Status: COMPLETE**
- ✅ Intelligent chunking with content-aware strategies
- ✅ Dynamic chunk sizing (800 tokens with 10% overlap)
- ✅ CrossEncoder reranking model integration (ms-marco-MiniLM-L-6-v2)
- ✅ Configurable via USE_RERANK environment variable
- ✅ Pre-loaded reranker model for better performance

**Reranking Configuration:**
```python
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
```

**Test Script**: `./test-stage9.sh` (planned)

#### Stage 10: Contextual Retrieval
**Status: COMPLETE**
- ✅ Official Anthropic Contextual Retrieval implementation
- ✅ Claude-3-Haiku model for optimal cost efficiency
- ✅ Prompt caching with 90%+ cost reduction
- ✅ Batch API for documents ≥10 chunks (50% additional savings)
- ✅ Contextual content for both embeddings and BM25 search
- ✅ Comprehensive monitoring and statistics

**Contextual Configuration:**
```bash
ANTHROPIC_API_KEY=your-key
ENABLE_CONTEXTUAL_RETRIEVAL=true
CONTEXTUAL_RETRIEVAL_MODEL=claude-3-haiku-20240307
```

**Test Script**: `./test-stage10.sh` (planned)

## Technical Architecture

### Frontend (Next.js)
- **Main Page**: Agent selection and room join UI
- **VoiceRoom Component**: LiveKit integration with audio controls
- **Real-time Updates**: Participant state synchronization

### Backend (FastAPI)
- **Token Generation**: Secure JWT tokens for LiveKit
- **Room Creation**: Sets metadata for agent configuration
- **Agent Templates**: Hardcoded personality definitions
- **Document Management**: Upload, processing, and storage APIs
- **Vector Search**: Semantic similarity search with Supabase
- **RAG Context**: Real-time document context retrieval
- **CORS Support**: Configured for local development

### Agent (Python)
- **LiveKit Agent Framework**: Handles room events and audio pipeline
- **Voice Pipeline**: Silero VAD → Deepgram STT → OpenAI LLM → ElevenLabs TTS
- **RAG Integration**: Document context retrieval and injection
- **Multi-source Configuration**: Checks job, room, and participant metadata
- **Personality System**: Instructions and voice per agent type
- **Context Management**: Real-time HTTP client for backend API calls

## Environment Configuration

### Backend (.env)
```bash
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
LIVEKIT_URL=wss://your-project.livekit.cloud
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
OPENAI_API_KEY=your-openai-api-key
```

### Agent (.env)
```bash
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
LIVEKIT_URL=wss://your-project.livekit.cloud
OPENAI_API_KEY=your-openai-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key
ELEVEN_API_KEY=your-elevenlabs-api-key
```

**Note**: The ElevenLabs plugin requires the environment variable `ELEVEN_API_KEY` (not `ELEVENLABS_API_KEY`).

## API Reference

### Core Endpoints
- `GET /health` - Health check endpoint
- `POST /api/token` - Generate LiveKit access token
  - Request body: `{ "room_name": string, "participant_name": string, "enable_ai_agent": boolean, "agent_type": string }`
  - Response: `{ "token": string, "url": string, "ai_agent_enabled": boolean, "agent_type": string }`
- `GET /api/agent-templates` - Get available agent templates
- `GET /api/agent-templates/{template_type}` - Get specific agent template details

### RAG Endpoints
- `GET /api/documents?owner_id={owner_id}` - Get documents for a specific owner
- `POST /api/documents/context` - Retrieve relevant document context for RAG
  - Request body: `{ "query": string, "owner_id": string }`
  - Response: `{ "context": string, "has_context": boolean }`
- `POST /api/documents/upload` - Upload and process documents for RAG
- `POST /api/documents/search` - Search documents using semantic similarity

## Testing

All completed stages have test scripts:
- `./test-stage1.sh` - Basic infrastructure
- `./test-stage2.sh` - Voice room functionality
- `./test-stage3.sh` - AI agent with OpenAI TTS
- `./test-stage4.sh` - ElevenLabs integration
- `./test-stage5.sh` - Agent configuration UI
- `./test-stage6.sh` - Supabase vector database
- `./test-stage7.sh` - RAG implementation

## Recent Improvements

### RAG Implementation (Stages 6-7)
- **Supabase Integration**: Vector database with pgvector extension
- **Document Processing**: PDF parsing, chunking, and embedding generation
- **Semantic Search**: OpenAI embeddings with cosine similarity
- **Agent RAG**: LiveKit integration using `on_user_turn_completed` method
- **Context Injection**: Document context added as system messages
- **Error Handling**: Robust timeout and HTTP error handling

### Agent System Fixes
- Fixed agent selection bug where only default agent was used
- Agent now properly reads configuration from room metadata
- Backend creates/updates rooms with agent type metadata
- Fallback chain: job metadata → room metadata → participant metadata

## Multi-Agent Implementation (Bonus Features)

### Conversation Memory
**Status: COMPLETE**
- ✅ Supabase table for conversation storage
- ✅ API endpoints for message storage/retrieval
- ✅ Agent integration with conversation history
- ✅ Last 10 messages injected as context

**Implementation**:
```sql
-- conversation_messages table
CREATE TABLE conversation_messages (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  room_name text NOT NULL,
  participant_name text NOT NULL,
  participant_type text NOT NULL CHECK (participant_type IN ('human', 'agent')),
  message text NOT NULL,
  metadata jsonb DEFAULT '{}',
  created_at timestamp with time zone DEFAULT NOW()
);
```

### Multi-Agent Support
**Status: COMPLETE**
- ✅ Backend supports `agent_types` array
- ✅ Frontend dual agent selection
- ✅ Agent awareness of other agents
- ✅ Simple turn-taking mechanism
- ✅ Agent numbering (Alex-0, Sophie-1)

**Running Multiple Agents**:
```bash
# Single agent
cd agent && ./run.sh

# Two agents
cd agent && ./run-multi.sh 2
```

**Agent Awareness**:
- Agents receive list of other agents in room
- Conversation history includes all participants
- Simple 2-second delay prevents overlap

## Next Steps (Post-MVP)

### Advanced RAG Features
- Hybrid search (BM25 + vector similarity)
- Advanced chunking strategies
- Reranking models
- Contextual retrieval

### System Enhancements
- Document management UI
- Custom agent builder
- Multi-agent conversations
- User authentication
- Production deployment

## Frontend Components

- **Main Page (page.tsx)**: Agent selection and room join form
- **VoiceRoom Component**: LiveKit integration with participant management
- **DocumentManager Component**: Document upload interface with real-time updates
  - PDF and TXT file upload support
  - Document list with metadata display
  - Integration with backend RAG system

## Key Technologies

### Core Stack
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

---

This implementation guide provides a complete overview of the AiGroupchat MVP development process, from basic infrastructure to advanced RAG capabilities. The application successfully demonstrates AI-powered voice conversations with document-aware responses, setting the foundation for future enhancements in stages 8-10.