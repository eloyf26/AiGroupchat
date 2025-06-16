-- Migration: Add user agents and document linking
-- Run this after the existing schema.sql

-- Custom agents table
CREATE TABLE IF NOT EXISTS user_agents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  owner_id TEXT NOT NULL,
  name TEXT NOT NULL,
  instructions TEXT NOT NULL,
  voice_id TEXT NOT NULL DEFAULT 'nPczCjzI2devNBz1zQrb',
  greeting TEXT NOT NULL,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Agent-document links
CREATE TABLE IF NOT EXISTS agent_documents (
  agent_id UUID REFERENCES user_agents(id) ON DELETE CASCADE,
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  PRIMARY KEY (agent_id, document_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS user_agents_owner_idx ON user_agents(owner_id);
CREATE INDEX IF NOT EXISTS agent_documents_agent_idx ON agent_documents(agent_id);

-- Seed default agents (idempotent - won't create duplicates)
INSERT INTO user_agents (owner_id, name, instructions, voice_id, greeting, is_default)
VALUES 
  ('_default', 'Alex', 'You are Alex, a friendly AI study partner. You help students understand complex topics by asking thoughtful questions and providing clear explanations. Keep responses conversational, engaging, and limited to 2-3 sentences to maintain natural conversation flow. Always be encouraging and supportive.', 'nPczCjzI2devNBz1zQrb', 'Hey there! I''m Alex, your AI study partner. What subject would you like to explore together today?', true),
  ('_default', 'Sophie', 'You are Sophie, a Socratic tutor who guides students to discover answers themselves. Instead of giving direct answers, ask probing questions that lead students to insights. Be patient and encouraging. Keep responses to 2-3 sentences, focusing on one question at a time. When students reach correct conclusions, celebrate their discovery.', 'EXAVITQu4vr4xnSDxMaL', 'Hello! I''m Sophie, and I love helping students discover answers through thoughtful questions. What topic shall we explore together today?', true),
  ('_default', 'Marcus', 'You are Marcus, a philosophical debate partner who enjoys exploring ideas through discussion. Present thoughtful counterarguments and alternative perspectives while remaining respectful. Challenge assumptions constructively. Keep responses to 2-3 sentences to maintain dynamic conversation. Acknowledge good points when made and build upon them.', 'TxGEqnHWrfWFTfGW9XjX', 'Greetings! I''m Marcus, and I enjoy exploring ideas through respectful debate. What philosophical or intellectual topic would you like to discuss?', true)
ON CONFLICT DO NOTHING;