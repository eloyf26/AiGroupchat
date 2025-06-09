# MVP Implementation Plan - 10 Stages

## Stage 1: Minimal Infrastructure ✅
**Status: COMPLETE**
- ✅ Create Next.js app with single page
- ✅ Create FastAPI backend with health endpoint
- ✅ Skip database, use in-memory storage
- ✅ Skip authentication
- ✅ Deploy locally only

**Test Script**: `./test-stage1.sh`

## Stage 2: LiveKit Voice Room ✅
**Status: COMPLETE**
- ✅ Add LiveKit Cloud SDK to frontend
- ✅ Create basic voice room UI (join/leave button)
- ✅ Implement LiveKit token generation in backend
- ✅ Test human-to-human voice calls
- ✅ No AI agents yet

**Implemented Features:**
- Token generation API endpoint (`POST /api/token`)
- VoiceRoom React component with LiveKit integration
- Audio controls (mute/unmute)
- Participant list display
- Room join/leave functionality

**Test Script**: `./test-stage2.sh`  
**Test Results**: `STAGE2-TEST-RESULTS.md`

## Stage 3: Single Hardcoded AI Agent ✅
**Status: COMPLETE**
- ✅ Create one Python LiveKit agent with fixed personality
- ✅ Use OpenAI for LLM responses
- ✅ Agent uses system TTS initially (not ElevenLabs)
- ✅ Agent joins room automatically
- ✅ Test human-to-AI conversations

**Implemented Features:**
- Python agent with "Alex" study partner personality
- Silero VAD for voice activity detection
- Deepgram STT for speech recognition
- OpenAI GPT-4o-mini for LLM
- OpenAI TTS (alloy voice) for speech synthesis
- Automatic agent dispatch when room is created
- Enhanced UI to distinguish AI from human participants

**Test Script**: `./test-stage3.sh`

## Stage 4: ElevenLabs Voice Integration ✅
**Status: COMPLETE**
- ✅ Replace OpenAI TTS with ElevenLabs streaming
- ✅ Use single pre-selected voice (Brian - warm, friendly male)
- ✅ Optimize for low latency (Flash v2.5 model)
- ✅ No voice customization UI

**Implemented Features:**
- ElevenLabs TTS integration with Flash v2.5 model
- Brian voice (voice_id: nPczCjzI2devNBz1zQrb)
- Optimized voice settings for natural conversation
- Low latency streaming configuration
- Required environment variable: ELEVEN_API_KEY

**Test Script**: `./test-stage4.sh`

## Stage 5: Minimal Agent Configuration ✅
**Status: COMPLETE**
- ✅ Add 3 hardcoded agent templates
- ✅ Simple selection dropdown in UI
- ✅ Agent personality switching via API
- ✅ No custom agent builder
- ✅ No knowledge documents

**Implemented Features:**
- Three agent templates: Alex (Study Partner), Sophie (Socratic Tutor), Marcus (Debate Partner)
- Agent selection dropdown in frontend
- Each agent has unique voice and personality
- Agent type passed via room metadata (primary) and participant metadata (fallback)
- API endpoints for template discovery
- Room creation with metadata to ensure correct agent personality

**Recent Fix:**
- Fixed agent selection mechanism to properly read agent type from room metadata
- Agent now checks multiple sources: job metadata, room metadata, and participant metadata
- Backend creates/updates room with metadata when AI agent is enabled

**Test Script**: `./test-stage5.sh`

## Stage 6: Supabase Vector Database Setup ⏳
**Status: PLANNED**
- Install Supabase client and set up pgvector extension
- Create schema: `documents` table (id, owner_id, title, type, metadata) and `document_sections` table (id, document_id, content, embedding vector(1536), metadata)
- Implement Row Level Security (RLS) policies for document access control
- Add file upload endpoint to backend API

**Test Script**: `./test-stage6.sh` (to be created)

## Stage 7: Basic RAG Implementation ⏳
**Status: PLANNED**
- Add document processing: PDF parsing (pypdf2), text extraction, basic fixed-size chunking (512 tokens)
- Generate embeddings using OpenAI's text-embedding-3-small model
- Store chunks with embeddings in Supabase
- Implement basic semantic search endpoint using cosine similarity
- Update agent to query document context before responding

**Test Script**: `./test-stage7.sh` (to be created)

## Stage 8: Hybrid Search Implementation ⏳
**Status: PLANNED**
- Add BM25 index using rank-bm25 library for keyword search
- Implement Reciprocal Rank Fusion (RRF) to combine vector and keyword results
- Create hybrid search endpoint that merges both search types
- Add search configuration options (weights for semantic vs keyword)

**Test Script**: `./test-stage8.sh` (to be created)

## Stage 9: Advanced Chunking & Reranking ⏳
**Status: PLANNED**
- Implement semantic chunking using sentence-transformers
- Add proposition-based chunking for factual content
- Integrate reranking model (ms-marco-MiniLM or BGE reranker)
- Implement dynamic chunk size selection based on content type

**Test Script**: `./test-stage9.sh` (to be created)

## Stage 10: Contextual Retrieval ⏳
**Status: PLANNED**
- Generate contextual chunk headers using LLM summarization
- Prepend context to chunks before embedding
- Implement contextual BM25 with enriched metadata
- Add document-level summaries for better context understanding
- Follow Anthropic's contextual retrieval approach

**Test Script**: `./test-stage10.sh` (to be created)
