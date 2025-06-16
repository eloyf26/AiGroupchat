# Conversation Memory Cleanup Guide

## Overview
The conversation memory system includes a cleanup function to prevent unbounded database growth. This guide explains how to set up automatic cleanup of old conversations.

## Cleanup Function
The database includes a built-in cleanup function that deletes conversations older than 7 days:

```sql
SELECT cleanup_old_conversations();
```

## Setup Options

### Option 1: PostgreSQL Cron Job (Recommended for Supabase)
If using Supabase or PostgreSQL with pg_cron extension:

```sql
-- Enable pg_cron extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule weekly cleanup (runs every Sunday at 2 AM UTC)
SELECT cron.schedule(
    'cleanup-old-conversations',
    '0 2 * * 0',  -- Cron expression
    'SELECT cleanup_old_conversations();'
);

-- To view scheduled jobs
SELECT * FROM cron.job;

-- To remove the scheduled job
SELECT cron.unschedule('cleanup-old-conversations');
```

### Option 2: Application-Level Scheduling
Add to your backend startup or use a task scheduler like APScheduler:

```python
# In backend/main.py
import asyncio
from datetime import datetime, timedelta

async def scheduled_cleanup():
    """Run cleanup every 24 hours"""
    while True:
        try:
            await asyncio.sleep(86400)  # 24 hours
            result = document_store.supabase.rpc('cleanup_old_conversations').execute()
            logger.info(f"Conversation cleanup completed: {result}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# Add to startup event
@app.on_event("startup")
async def startup_event():
    # ... existing code ...
    asyncio.create_task(scheduled_cleanup())
```

### Option 3: External Cron Job
Create a cron job on your server:

```bash
# Add to crontab (crontab -e)
# Run every day at 2 AM
0 2 * * * curl -X POST http://localhost:8000/api/admin/cleanup-conversations
```

Then add the endpoint to your backend:

```python
@app.post("/api/admin/cleanup-conversations")
async def cleanup_conversations(api_key: str = Header(None)):
    """Manual trigger for conversation cleanup"""
    if api_key != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    result = document_store.supabase.rpc('cleanup_old_conversations').execute()
    return {"status": "success", "result": result}
```

## Customizing Retention Period

To change the retention period from 7 days, modify the function in your database:

```sql
-- Example: Change to 30 days retention
CREATE OR REPLACE FUNCTION cleanup_old_conversations()
RETURNS void AS $$
BEGIN
  DELETE FROM conversation_messages 
  WHERE created_at < now() - interval '30 days';
END;
$$ LANGUAGE plpgsql;
```

## Monitoring

To check how many messages will be deleted:

```sql
SELECT COUNT(*) FROM conversation_messages 
WHERE created_at < now() - interval '7 days';
```

To see disk space used by conversations:

```sql
SELECT 
    pg_size_pretty(pg_total_relation_size('conversation_messages')) as total_size,
    COUNT(*) as message_count
FROM conversation_messages;
```