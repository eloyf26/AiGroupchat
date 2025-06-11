#!/usr/bin/env python3
"""
Stage 7 MVP: AI agent for AiGroupchat with configurable personalities and RAG
Uses OpenAI for LLM and ElevenLabs for TTS with document context retrieval
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import httpx

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import llm, Agent, AgentSession
from livekit.plugins import deepgram, openai, silero, elevenlabs

load_dotenv()

# Configure logging
logger = logging.getLogger("ai-agent")
logger.setLevel(logging.INFO)

# Agent templates matching backend configuration
AGENT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "study_partner": {
        "name": "Alex",
        "instructions": (
            "You are Alex, a friendly AI study partner. "
            "You help students understand complex topics by asking thoughtful questions "
            "and providing clear explanations. Keep responses conversational, engaging, "
            "and limited to 2-3 sentences to maintain natural conversation flow. "
            "Always be encouraging and supportive."
        ),
        "voice_id": "nPczCjzI2devNBz1zQrb",  # Brian - warm, friendly male voice
        "greeting": "Hey there! I'm Alex, your AI study partner. What subject would you like to explore together today?"
    },
    "socratic_tutor": {
        "name": "Sophie",
        "instructions": (
            "You are Sophie, a Socratic tutor who guides students to discover answers themselves. "
            "Instead of giving direct answers, ask probing questions that lead students to insights. "
            "Be patient and encouraging. Keep responses to 2-3 sentences, focusing on one question at a time. "
            "When students reach correct conclusions, celebrate their discovery."
        ),
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Sarah - clear, professional female voice
        "greeting": "Hello! I'm Sophie, and I love helping students discover answers through thoughtful questions. What topic shall we explore together today?"
    },
    "debate_partner": {
        "name": "Marcus",
        "instructions": (
            "You are Marcus, a philosophical debate partner who enjoys exploring ideas through discussion. "
            "Present thoughtful counterarguments and alternative perspectives while remaining respectful. "
            "Challenge assumptions constructively. Keep responses to 2-3 sentences to maintain dynamic conversation. "
            "Acknowledge good points when made and build upon them."
        ),
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",  # Josh - confident, articulate male voice
        "greeting": "Greetings! I'm Marcus, and I enjoy exploring ideas through respectful debate. What philosophical or intellectual topic would you like to discuss?"
    }
}


class DocumentContextManager:
    """Manages document context retrieval from the backend API"""
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.client = httpx.AsyncClient(timeout=10.0)  # Longer timeout for RAG
    
    async def get_context(self, query: str, owner_id: str) -> Optional[str]:
        """Get relevant document context for a query"""
        try:
            # Validate inputs
            if not query or not isinstance(query, str):
                logger.warning(f"Invalid query: {query}")
                return None
            if not owner_id or not isinstance(owner_id, str):
                logger.warning(f"Invalid owner_id: {owner_id}")
                return None
                
            response = await self.client.post(
                f"{self.backend_url}/api/documents/context",
                json={
                    "query": query,
                    "owner_id": owner_id
                }
            )
            logger.debug(f"Backend response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                context = data.get("context", "")
                logger.debug(f"Retrieved context length: {len(context)} chars")
                return context
            elif response.status_code == 422:
                logger.warning(f"Invalid request to document context API. Query: '{query}', Owner ID: '{owner_id}'")
                logger.warning(f"Response: {response.text}")
                return None
            else:
                logger.warning(f"Failed to get document context: {response.status_code}")
                logger.warning(f"Response: {response.text}")
                return None
        except httpx.TimeoutException as e:
            logger.error(f"Timeout getting document context: {e}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error getting document context: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting document context: {e}")
            return None
    
    async def close(self):
        await self.client.aclose()


class RAGVoiceAgent(Agent):
    """Voice agent with RAG support using pipeline nodes"""
    
    def __init__(self, instructions: str, context_manager: DocumentContextManager, owner_id: str):
        super().__init__(instructions=instructions)
        self._context_manager = context_manager
        self._owner_id = owner_id
        self._rag_enabled = True
        logger.info(f"RAGVoiceAgent initialized with owner_id: {owner_id}")
    
    async def on_user_turn_completed(self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage) -> None:
        """Called when user completes a turn - inject RAG context here"""
        if not self._rag_enabled or not self._context_manager or not self._owner_id:
            return
        
        try:
            # Get the user's message content
            user_message = new_message.content
            logger.debug(f"Processing user message: '{user_message}' (type: {type(user_message)})")
            
            if not user_message:
                logger.debug("No user message content to process")
                return
            
            # Handle list content (LiveKit sends content as a list)
            if isinstance(user_message, list):
                # Join all parts of the message
                user_message = " ".join(str(part) for part in user_message)
            elif not isinstance(user_message, str):
                user_message = str(user_message)
            
            # Skip very short messages that might be partial
            if len(user_message.strip()) < 3:
                logger.debug(f"Skipping short message: '{user_message}'")
                return
            
            # Retrieve relevant context
            logger.info(f"Retrieving context for query: '{user_message}' with owner_id: '{self._owner_id}'")
            context = await self._context_manager.get_context(user_message, self._owner_id)
            
            if context:
                # Add context as a system message to inform the LLM
                context_message = f"""IMPORTANT: The user has documents stored in the system. Here is relevant information from their documents:

{context}

You MUST use this information to answer the user's question. Be specific and reference the document content directly. If the user asks about AI agent personalities, list them exactly as shown in the document."""
                turn_ctx.add_message(
                    role="system",
                    content=context_message
                )
                logger.info(f"RAG context injected into conversation: {context[:100]}...")
            else:
                logger.debug("No relevant context found for user message")
                # Still provide a helpful response even without context
                turn_ctx.add_message(
                    role="system",
                    content="No specific document context was found for this query. Provide a helpful response based on your general knowledge."
                )
                
        except Exception as e:
            logger.error(f"Failed to inject RAG context: {e}")
            # Continue without RAG context on error


async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the agent - called when a room needs an agent"""
    
    logger.info(f"Agent starting for room: {ctx.room.name}")
    
    # Get agent type and owner_id from job metadata if available
    agent_type = "study_partner"  # Default
    owner_id = None
    if ctx.job and ctx.job.metadata:
        try:
            job_metadata = json.loads(ctx.job.metadata)
            if "agent_type" in job_metadata:
                agent_type = job_metadata["agent_type"]
                logger.info(f"Agent type from job metadata: {agent_type}")
            if "owner_id" in job_metadata:
                owner_id = job_metadata["owner_id"]
                logger.info(f"Owner ID from job metadata: {owner_id}")
        except json.JSONDecodeError:
            logger.warning("Failed to parse job metadata")
    
    # Connect to the room first
    await ctx.connect()
    
    # Check room metadata as fallback
    if ctx.room.metadata:
        try:
            room_metadata = json.loads(ctx.room.metadata)
            if "agent_type" in room_metadata:
                agent_type = room_metadata["agent_type"]
                logger.info(f"Agent type from room metadata: {agent_type}")
            if "owner_id" in room_metadata and not owner_id:
                owner_id = room_metadata["owner_id"]
                logger.info(f"Owner ID from room metadata: {owner_id}")
        except json.JSONDecodeError:
            logger.warning("Failed to parse room metadata")
    
    # Wait for the first participant to join and check their metadata as last resort
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant joined: {participant.identity}")
    
    # Use participant identity as owner_id if not set
    if not owner_id:
        owner_id = participant.identity
        logger.info(f"Using participant identity as owner_id: {owner_id}")
    
    if participant.metadata and agent_type == "study_partner":  # Only check if we haven't found agent type yet
        try:
            participant_metadata = json.loads(participant.metadata)
            if "agent_type" in participant_metadata:
                agent_type = participant_metadata["agent_type"]
                logger.info(f"Agent type from participant metadata: {agent_type}")
        except json.JSONDecodeError:
            logger.warning("Failed to parse participant metadata")
    
    # Get the template for selected agent type
    template = AGENT_TEMPLATES.get(agent_type, AGENT_TEMPLATES["study_partner"])
    logger.info(f"Using agent template: {agent_type} ({template['name']})")
    
    # Initialize document context manager for RAG
    context_manager = DocumentContextManager()
    
    # Create the voice agent with RAG support
    agent = RAGVoiceAgent(
        instructions=template["instructions"],
        context_manager=context_manager,
        owner_id=owner_id
    )
    
    # Create AgentSession with speech components
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2",
            language="en-US",
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.8,
            timeout=60.0,
        ),
        tts=elevenlabs.TTS(
            model="eleven_flash_v2_5",
            voice_id=template["voice_id"],
            language="en",
            voice_settings=elevenlabs.VoiceSettings(
                stability=0.5,
                similarity_boost=1.0,
                style=0.0,
            ),
        ),
        vad=silero.VAD.load()
    )
    
    # Start the session with the agent
    await session.start(room=ctx.room, agent=agent)
    
    # Generate initial greeting
    try:
        await session.generate_reply(instructions=template["greeting"])
        logger.info(f"Initial greeting sent: {template['greeting']}")
    except Exception as e:
        logger.error(f"Failed to send initial greeting: {e}")
    
    logger.info(f"Agent {template['name']} ready and listening with RAG support")


if __name__ == "__main__":
    # Run the agent worker
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
            ws_url=os.getenv("LIVEKIT_URL"),
        ),
    )