# AiGroupchat Setup Guide

Complete setup guide for the AiGroupchat project with Contextual Retrieval support.

## Prerequisites

### Required Software
- **Node.js** (v18 or later) for the frontend
- **Python** (3.9 or later) for backend and agent
- **PostgreSQL client** (`psql`) for database setup
- **Git** for version control

### Required Services
- **Supabase Account** - For vector database with pgvector
- **LiveKit Account** - For real-time voice communication
- **OpenAI API Key** - For embeddings and agent intelligence
- **Anthropic API Key** - For contextual retrieval (optional but recommended)
- **Deepgram API Key** - For speech-to-text
- **ElevenLabs API Key** - For text-to-speech

## Step 1: Clone and Setup Project

```bash
# Clone the repository
git clone <your-repo-url>
cd AiGroupchat

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install agent dependencies
cd agent
pip install -r requirements.txt
cd ..
```

## Step 2: Database Setup

### 2.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the project to be fully provisioned
3. Go to Settings > Database
4. Copy your database connection string

### 2.2 Enable pgvector Extension
1. In Supabase Dashboard, go to Database → Extensions
2. Search for "vector"
3. Click "Enable" on the pgvector extension

### 2.3 Run Database Schema
1. In Supabase Dashboard, go to SQL Editor
2. Copy the contents of `backend/schema.sql`
3. Run the SQL script

This will create:
- ✅ All tables (documents, document_sections, contextual_processing_stats)
- ✅ Contextual retrieval fields and indexes
- ✅ Row Level Security policies
- ✅ Search functions (standard and contextual)
- ✅ Statistics and utility functions

### 2.4 Verify Database Setup
```bash
cd backend
./setup_database.sh
```

This verification script will:
- ✅ Test Supabase connection
- ✅ Verify all tables and functions exist
- ✅ Check contextual retrieval fields
- ✅ Test Python dependencies

## Step 3: Environment Configuration

### 3.1 Backend Environment
```bash
cd backend
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# LiveKit
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
LIVEKIT_URL=wss://your-project.livekit.cloud

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# RAG Configuration
USE_HYBRID_SEARCH=true
USE_RERANK=true

# Contextual Retrieval (optional but recommended)
ENABLE_CONTEXTUAL_RETRIEVAL=true
CONTEXTUAL_RETRIEVAL_MODEL=claude-3-5-sonnet-20241022
MAX_CONTEXTUAL_TOKENS_PER_DOCUMENT=100000
MAX_DAILY_CONTEXTUAL_REQUESTS=1000
```

### 3.2 Agent Environment
```bash
cd agent
cp .env.example .env
```

Edit `agent/.env`:
```bash
# LiveKit
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
LIVEKIT_URL=wss://your-project.livekit.cloud

# AI Services
OPENAI_API_KEY=your-openai-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key
ELEVEN_API_KEY=your-elevenlabs-api-key

# Agent Configuration
AGENT_NAME=Alex
AGENT_IDENTITY=AI_Alex
```

## Step 4: Test the Setup

### 4.1 Test Database Connection
```bash
cd backend
python -c "from document_store import DocumentStore; ds = DocumentStore(); print('✅ Database connection successful')"
```

### 4.2 Test Contextual Retrieval
```bash
cd backend
python test_contextual_retrieval.py
```

### 4.3 Start Services

**Terminal 1 - Backend:**
```bash
cd backend
./run.sh
```

**Terminal 2 - Agent:**
```bash
cd agent
./run.sh
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### 4.4 Test the Application
1. Open http://localhost:3000
2. Create a room with an AI agent
3. Upload a document (PDF or TXT)
4. Ask questions about the document in voice chat

## Step 5: Monitoring and Maintenance

### Check Contextual Processing Stats
```bash
curl "http://localhost:8000/api/contextual/stats?owner_id=your-user-id"
```

### Check System Status
```bash
curl "http://localhost:8000/api/contextual/status"
```

### Migrate Existing Documents (if you have any)
```bash
cd backend
# Dry run first
python migrate_existing_documents.py --dry-run

# Actual migration
python migrate_existing_documents.py --owner-id specific_user
```

## Architecture Overview

```
Frontend (Next.js) ←→ Backend (FastAPI) ←→ Supabase (PostgreSQL + pgvector)
                ↓
            LiveKit Room
                ↓
        AI Agent (Python) ←→ Claude (Contextual) + OpenAI (Embeddings/Chat)
                ↓
        ElevenLabs (TTS) + Deepgram (STT)
```

## Contextual Retrieval Flow

```
Document Upload → 
Claude generates contextual descriptions → 
OpenAI creates embeddings with context → 
Stored in Supabase → 
Enhanced search (Semantic + BM25 + Reranking)
```

## Cost Optimization

### Contextual Processing
- **One-time cost** during document upload (~$1.02 per million tokens)
- **90% cost reduction** through Claude's prompt caching
- **Rate limiting** to control daily usage

### Monitoring Costs
- Track tokens and costs via `/api/contextual/stats`
- Set daily limits in environment variables
- Monitor cache hit rates for optimization

## Troubleshooting

### Database Issues
- Ensure pgvector extension is enabled in Supabase
- Check connection string format
- Verify database permissions

### API Key Issues
- Ensure all API keys are valid and have sufficient credits
- Check API key permissions and rate limits
- Test individual services separately

### Contextual Processing Issues
- Check ANTHROPIC_API_KEY is set correctly
- Verify `ENABLE_CONTEXTUAL_RETRIEVAL=true`
- Monitor rate limits and daily usage

### Performance Issues
- Monitor database query performance
- Check embedding generation speed
- Optimize batch sizes for processing

## Advanced Configuration

### Custom Models
```bash
# Use different Claude model
CONTEXTUAL_RETRIEVAL_MODEL=claude-3-haiku-20240307

# Use different reranking model
RERANK_MODEL=cross-encoder/ms-marco-MiniLM-L-12-v2
```

### Fine-tuning Performance
```bash
# Adjust chunk size for documents
# (Modify text_splitter settings in document_store.py)

# Adjust batch processing
MIGRATION_BATCH_SIZE=10
MIGRATION_DELAY_SECONDS=1.0
```

## Support

For issues and questions:
1. Check the logs in backend and agent terminals
2. Test individual components with provided test scripts
3. Review the CLAUDE.md file for implementation details
4. Check the CONTEXTUAL_RETRIEVAL_IMPLEMENTATION.md for technical details

Your AiGroupchat setup with Contextual Retrieval is now complete! 🎉