# Setup Instructions for Custom Agents Feature

## Database Migration Required

To enable the custom agents feature, you need to run a database migration in your Supabase project.

### Steps:

1. **Go to your Supabase Dashboard**
   - Navigate to the SQL Editor

2. **Run the Migration**
   - Copy and paste the contents of `backend/migrations/add_user_agents.sql`
   - Click "Run" to execute the migration

3. **Verify the Migration**
   - Check that the following tables were created:
     - `user_agents` - Stores custom agent configurations
     - `agent_documents` - Links documents to specific agents

4. **Test the Feature**
   - The migration includes 3 default agents (Alex, Sophie, Marcus)
   - Run `python test-custom-agents.py` to verify everything is working

## What This Feature Adds

1. **Agent Customization**
   - Users can create custom AI agents with unique personalities
   - Each agent has configurable:
     - Name
     - Instructions (personality)
     - Voice (ElevenLabs voice ID)
     - Greeting message

2. **Document Filtering**
   - Users can link specific documents to agents
   - Agents only access documents they are linked to
   - Provides knowledge isolation between agents

3. **Frontend UI**
   - AgentManager component for creating/selecting agents
   - Document linking UI in DocumentManager
   - Visual indicators for agent document counts

## Testing

After running the migration, test with:

```bash
cd backend
source venv/bin/activate
python ../test-custom-agents.py
```

This will verify:
- Agent CRUD operations
- Document filtering
- RAG integration with agent-specific knowledge

## Next Steps

Once this is working, you can proceed to implement Section 2: Multiple Agent Chats.