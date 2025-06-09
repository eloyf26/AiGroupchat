# Supabase Setup Guide for Stage 6

## Prerequisites

1. Create a Supabase account at https://supabase.com
2. Create a new project

## Setup Steps

### 1. Enable pgvector Extension

1. Go to your Supabase Dashboard
2. Navigate to Database → Extensions
3. Search for "vector"
4. Click "Enable" on the pgvector extension

### 2. Run Database Schema

1. Go to SQL Editor in your Supabase Dashboard
2. Copy the contents of `backend/schema.sql`
3. Run the SQL script

### 3. Get Your API Credentials

1. Go to Settings → API
2. Copy your:
   - Project URL (SUPABASE_URL)
   - Anon/Public key (SUPABASE_KEY)

### 4. Update Environment Variables

Add to `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 5. Test the Setup

Run the test script:

```bash
./test-stage6.sh
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