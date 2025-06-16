-- Migration: Add security and performance improvements to conversation memory
-- Run this migration to upgrade existing conversation_messages table

-- 1. Add owner_id column for Row Level Security
ALTER TABLE conversation_messages 
ADD COLUMN IF NOT EXISTS owner_id text;

-- Update existing messages to set owner_id from participant_name for human participants
-- This assumes human participants use their identity as owner_id
UPDATE conversation_messages 
SET owner_id = participant_name 
WHERE participant_type = 'human' AND owner_id IS NULL;

-- For agent messages, set owner_id from the room's human participant
UPDATE conversation_messages cm
SET owner_id = (
    SELECT participant_name 
    FROM conversation_messages 
    WHERE room_name = cm.room_name 
    AND participant_type = 'human' 
    LIMIT 1
)
WHERE cm.participant_type = 'agent' AND cm.owner_id IS NULL;

-- 2. Add performance index for room queries
CREATE INDEX IF NOT EXISTS conversation_messages_room_created_idx 
ON conversation_messages(room_name, created_at DESC);

-- 3. Enable Row Level Security
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

-- 4. Create RLS policies for secure access
-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view own conversations" ON conversation_messages;
DROP POLICY IF EXISTS "Users can insert own conversations" ON conversation_messages;

-- Policy: Users can only view conversations they own
CREATE POLICY "Users can view own conversations" 
ON conversation_messages FOR SELECT
USING (owner_id = current_setting('app.current_user_id')::text);

-- Policy: Users can only insert messages for their own conversations
CREATE POLICY "Users can insert own conversations" 
ON conversation_messages FOR INSERT
WITH CHECK (owner_id = current_setting('app.current_user_id')::text);

-- 5. Grant necessary permissions
GRANT ALL ON conversation_messages TO authenticated;
GRANT ALL ON conversation_messages TO service_role;

-- Note: To run the cleanup function periodically, execute:
-- SELECT cleanup_old_conversations();
-- This can be scheduled as a cron job in your database or application