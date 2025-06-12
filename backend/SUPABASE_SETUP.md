# Supabase Setup Guide with Contextual Retrieval Support

## Prerequisites

1. Create a Supabase account at https://supabase.com
2. Create a new project

## Setup Steps

### 1. Enable pgvector Extension

1. Go to your Supabase Dashboard
2. Navigate to Database → Extensions
3. Search for "vector"
4. Click "Enable" on the pgvector extension

### 2. Run Database Schema with Contextual Retrieval Support

1. Go to SQL Editor in your Supabase Dashboard
2. Copy the contents of `backend/schema.sql`
3. Run the SQL script

**What's included in the schema:**
- ✅ Documents and document_sections tables (original RAG)
- ✅ Contextual retrieval fields (`contextual_content`, `is_contextualized`)
- ✅ Statistics table for cost tracking (`contextual_processing_stats`)
- ✅ All performance indexes including GIN indexes for metadata
- ✅ Row Level Security (RLS) policies for all tables
- ✅ Search functions (standard and contextual)
- ✅ Statistics and utility functions

### 3. Get Your API Credentials

1. Go to Settings → API
2. Copy your:
   - Project URL (SUPABASE_URL)
   - Anon/Public key (SUPABASE_KEY)

### 4. Update Environment Variables

Add to `backend/.env`:

```env
# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# AI Provider API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# RAG Configuration
USE_HYBRID_SEARCH=true
USE_RERANK=true

# Contextual Retrieval Configuration (optional but recommended)
ENABLE_CONTEXTUAL_RETRIEVAL=true
CONTEXTUAL_RETRIEVAL_MODEL=claude-3-haiku-20240307
MAX_CONTEXTUAL_TOKENS_PER_DOCUMENT=100000
MAX_DAILY_CONTEXTUAL_REQUESTS=1000
CONTEXTUAL_PROCESSING_TIMEOUT=120
```

### 5. Test the Setup

Test the basic setup:
```bash
./test-stage6.sh
```

Test contextual retrieval:
```bash
cd backend
python test_contextual_retrieval.py
```

### 6. Optional: Migrate Existing Documents

If you have existing documents from before contextual retrieval, you can upgrade them:

```bash
cd backend
# Dry run first to see what would be migrated
python migrate_existing_documents.py --dry-run

# Migrate specific user's documents
python migrate_existing_documents.py --owner-id your-user-id

# Or migrate all documents (be careful with costs!)
python migrate_existing_documents.py
```

## Security Notes

- The schema uses Row Level Security (RLS) to ensure users can only access their own documents
- In production, you should use a service role key for admin operations
- The current implementation uses simplified auth for MVP purposes

## Troubleshooting

### pgvector not found error
- Make sure you've enabled the pgvector extension in Supabase Dashboard

### Permission denied errors
- Check that RLS policies are properly created
- Verify your API key is correct

### Connection errors
- Ensure SUPABASE_URL includes https:// prefix
- Check that your project is not paused in Supabase Dashboard