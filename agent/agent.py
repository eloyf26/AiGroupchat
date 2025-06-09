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
from livekit.agents import Agent, AgentSession
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
        "greeting": "Greet the user warmly as Alex and ask what subject they'd like to study today."
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
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_context(self, query: str, owner_id: str) -> Optional[str]:
        """Get relevant document context for a query"""
        try:
            response = await self.client.post(
                f"{self.backend_url}/api/documents/context",
                json={
                    "query": query,
                    "owner_id": owner_id
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("context", "")
            else:
                logger.warning(f"Failed to get document context: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting document context: {e}")
            return None
    
    async def close(self):
        await self.client.aclose()


class ConfigurableAgent(Agent):
    """Agent with configurable personality based on template and RAG support"""
    def __init__(self, agent_type: str, context_manager: Optional[DocumentContextManager] = None, owner_id: Optional[str] = None) -> None:
        template = AGENT_TEMPLATES.get(agent_type, AGENT_TEMPLATES["study_partner"])
        
        # Base instructions from template
        base_instructions = template["instructions"]
        
        # Initialize with base instructions
        super().__init__(instructions=base_instructions)
        
        self.agent_type = agent_type
        self.template = template
        self.context_manager = context_manager
        self.owner_id = owner_id
        self.base_instructions = base_instructions
    
    async def think(self, messages: list) -> str | None:
        """Override think method to inject document context"""
        # Get the last user message
        if not messages or not self.context_manager or not self.owner_id:
            return await super().think(messages)
        
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            # Get relevant document context
            context = await self.context_manager.get_context(last_message.content, self.owner_id)
            if context:
                # Update instructions with context for this query
                context_instructions = f"""{self.base_instructions}

You have access to the following relevant information from the user's documents:

{context}

Please use this information to provide accurate and helpful responses when relevant."""
                self._instructions = context_instructions
            else:
                # Reset to base instructions if no context
                self._instructions = self.base_instructions
        
        return await super().think(messages)


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
    
    # Create the agent with context support
    agent = ConfigurableAgent(
        agent_type=agent_type,
        context_manager=context_manager,
        owner_id=owner_id
    )
    
    # Configure the voice pipeline with appropriate voice
    session = AgentSession(
        # Voice Activity Detection
        vad=silero.VAD.load(),
        
        # Speech-to-Text
        stt=deepgram.STT(
            model="nova-2",
            language="en-US",
        ),
        
        # Large Language Model with context injection
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.8,
        ),
        
        # Text-to-Speech using ElevenLabs with agent-specific voice
        tts=elevenlabs.TTS(
            model="eleven_flash_v2_5",  # Flash model for lowest latency
            voice_id=template["voice_id"],  # Voice based on agent type
            language="en",
            voice_settings=elevenlabs.VoiceSettings(
                stability=0.5,  # Balanced stability for natural conversation
                similarity_boost=1.0,  # Maximum clarity
                style=0.0,  # Natural speaking style
            ),
        ),
    )
    
    # We'll handle context injection in the agent's message processing
    
    # Start the session with configured agent
    await session.start(
        room=ctx.room,
        agent=agent,
    )
    
    # Generate initial greeting based on agent type
    await session.generate_reply(
        instructions=template["greeting"]
    )
    
    logger.info(f"Agent {template['name']} ready and listening with RAG support")
    
    # The session will run until the participant leaves or the room is closed
    # Context manager cleanup will happen when the agent worker shuts down


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