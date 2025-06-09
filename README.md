# AiGroupchat MVP

AI-powered group voice chat application built with Next.js and FastAPI.

## Stage 1: Minimal Infrastructure ✅

Current implementation includes:
- Next.js frontend with single page
- FastAPI backend with health endpoint
- Basic connectivity between frontend and backend
- In-memory storage (no database)
- Local development only

## Stage 2: LiveKit Voice Room ✅

### Features Implemented
- LiveKit token generation endpoint in backend (`POST /api/token`)
- Voice room UI component with join/leave functionality
- Real-time voice communication between participants
- Audio controls (mute/unmute)
- Participant list display

### Technical Implementation

#### Backend API
The token generation endpoint creates secure JWT tokens for LiveKit room access:
```python
# POST /api/token
# Request: { "room_name": "string", "participant_name": "string" }
# Response: { "token": "jwt_token", "url": "wss://..." }
```

#### Frontend Components
- **VoiceRoom.tsx**: Main component using LiveKit React SDK
  - Handles WebRTC connection management
  - Audio track publishing/subscribing
  - Participant state synchronization

#### Key Technical Decisions
1. **LiveKit Cloud**: Using managed service for faster MVP development
2. **Server-side tokens**: API secrets never exposed to frontend
3. **Audio-only**: Simplified implementation without video
4. **Component architecture**: Single component with LiveKit hooks for simplicity

## Stage 3: Single AI Agent ✅

### Features Implemented
- Python LiveKit agent with hardcoded "Alex" study partner personality
- OpenAI integration for LLM responses (GPT-4o-mini)
- OpenAI TTS for voice synthesis (not ElevenLabs yet)
- Automatic agent joining when room is created
- Visual distinction between AI and human participants

### Technical Implementation

#### Agent Architecture
- **agent/agent.py**: LiveKit Python agent worker
  - Uses Silero VAD for voice activity detection
  - Deepgram for speech-to-text
  - OpenAI for both LLM and TTS
  - Fixed personality as friendly study partner

#### Backend Updates
- Modified token endpoint to support agent dispatch
- Added `enable_ai_agent` flag (default: true)
- Room metadata triggers agent to join automatically

#### Frontend Updates
- Enhanced participant display with AI/Human indicators
- Shows speaking status for each participant
- Different styling for AI agents (blue background)

### Required API Keys
Add these to `agent/.env`:
```
OPENAI_API_KEY=your-openai-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key
```

## Stage 4: ElevenLabs Voice Integration ✅

### Features Implemented
- Replaced OpenAI TTS with ElevenLabs streaming
- Using "eleven_flash_v2_5" model for lowest latency
- Selected "Brian" voice - warm, friendly male voice
- Optimized voice settings for natural conversation
- No voice customization UI (single voice only)

### Technical Changes

#### Voice Configuration
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

#### Performance Optimizations
- Flash v2.5 model: Fastest ElevenLabs model for real-time conversation
- Streaming enabled by default for low latency
- Optimized settings for conversational flow

### Additional Required API Keys
Add to `agent/.env`:
```
ELEVEN_API_KEY=your-elevenlabs-api-key
```

**Note**: The ElevenLabs plugin requires the environment variable `ELEVEN_API_KEY` (not `ELEVENLABS_API_KEY`).

## Stage 5: Minimal Agent Configuration ✅

### Features Implemented
- 3 hardcoded agent templates with distinct personalities
- Simple dropdown selection in UI
- Agent personality switching via API
- Each agent has unique voice and conversation style
- No custom agent builder or knowledge documents

### Agent Templates

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

### Technical Implementation
- Agent templates defined in backend and agent code
- Agent type passed via participant metadata
- Dynamic voice and personality switching
- API endpoints for template discovery

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+
- LiveKit API credentials (get from https://cloud.livekit.io)
- OpenAI API key (for Stage 3+)
- Deepgram API key (for Stage 3+)
- ElevenLabs API key (for Stage 4+)

### Running the Application

1. **Configure LiveKit** (for Stage 2):
   - Copy `backend/.env.example` to `backend/.env` (if exists) or create `backend/.env`
   - Add your LiveKit credentials:
     ```
     LIVEKIT_API_KEY=your-api-key
     LIVEKIT_API_SECRET=your-api-secret
     LIVEKIT_URL=wss://your-project.livekit.cloud
     ```

2. **Start Backend**:
   ```bash
   cd backend && ./run.sh
   ```
   Backend will run on http://localhost:8000

3. **Start Frontend** (in another terminal):
   ```bash
   cd frontend && npm run dev
   ```
   Frontend will run on http://localhost:3000

4. **Test Stage 1 (Minimal Infrastructure)**:
   ```bash
   ./test-stage1.sh
   ```

5. **Test Stage 2 (Voice Room)**:
   ```bash
   ./test-stage2.sh
   ```

6. **Test Stage 3 (AI Agent)**:
   ```bash
   # First add API keys to agent/.env
   ./test-stage3.sh
   ```

7. **Test Stage 4 (ElevenLabs Voice)**:
   ```bash
   # Ensure ELEVEN_API_KEY is added to agent/.env
   ./test-stage4.sh
   ```

8. **Test Stage 5 (Agent Configuration)**:
   ```bash
   # All API keys should be configured
   ./test-stage5.sh
   ```

### Development Commands

See [CLAUDE.md](./CLAUDE.md) for complete development commands.

## Project Structure

```
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── components/
│   │   │   └── VoiceRoom.tsx   # LiveKit voice room component
│   │   └── page.tsx            # Main page with room UI
│   └── package.json            # Frontend dependencies
├── backend/                    # FastAPI application
│   ├── main.py                # API endpoints
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # LiveKit credentials
├── agent/                     # LiveKit Python agent (Stage 3)
│   ├── agent.py              # AI agent implementation
│   ├── requirements.txt      # Agent dependencies
│   ├── run.sh               # Agent run script
│   └── .env                 # Agent credentials
├── documentation/             # Technical documentation
├── test-stage1.sh            # Stage 1 test script
├── test-stage2.sh            # Stage 2 test script
├── test-stage3.sh            # Stage 3 test script
├── test-stage4.sh            # Stage 4 test script
├── test-stage5.sh            # Stage 5 test script
├── CLAUDE.md                 # Development guidance
└── MVP-implementation-plan.md # 5-stage implementation plan
```

## Completed Stages

- ✅ Stage 1: Minimal Infrastructure
- ✅ Stage 2: LiveKit Voice Room
- ✅ Stage 3: Single AI Agent implementation
- ✅ Stage 4: ElevenLabs voice integration
- ✅ Stage 5: Basic agent configuration UI

All MVP stages are now complete! The application supports voice conversations with configurable AI agents.

## Planned Stages (RAG Implementation)

- ⏳ Stage 6: Supabase Vector Database Setup
- ⏳ Stage 7: Basic RAG with Document Upload
- ⏳ Stage 8: Hybrid Search Implementation
- ⏳ Stage 9: Advanced Chunking & Reranking
- ⏳ Stage 10: Contextual Retrieval

### Stage 6: Supabase Vector Database Setup (Planned)
- Install Supabase client and set up pgvector extension
- Create schema: `documents` table (id, owner_id, title, type, metadata) and `document_sections` table (id, document_id, content, embedding vector(1536), metadata)
- Implement RLS policies for document access control
- Add file upload endpoint to backend API

### Stage 7: Basic RAG Implementation (Planned)
- Add document processing: PDF parsing (pypdf2), text extraction, basic fixed-size chunking (512 tokens)
- Generate embeddings using OpenAI's text-embedding-3-small model
- Store chunks with embeddings in Supabase
- Implement basic semantic search endpoint using cosine similarity
- Update agent to query document context before responding

### Stage 8: Hybrid Search Implementation (Planned)
- Add BM25 index using rank-bm25 library for keyword search
- Implement Reciprocal Rank Fusion (RRF) to combine vector and keyword results
- Create hybrid search endpoint that merges both search types
- Add search configuration options (weights for semantic vs keyword)

### Stage 9: Advanced Chunking & Reranking (Planned)
- Implement semantic chunking using sentence-transformers
- Add proposition-based chunking for factual content
- Integrate reranking model (ms-marco-MiniLM or BGE reranker)
- Implement dynamic chunk size selection based on content type

### Stage 10: Contextual Retrieval (Planned)
- Generate contextual chunk headers using LLM summarization
- Prepend context to chunks before embedding
- Implement contextual BM25 with enriched metadata
- Add document-level summaries for better context understanding
- Follow Anthropic's contextual retrieval approach
