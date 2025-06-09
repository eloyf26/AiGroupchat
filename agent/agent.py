#!/usr/bin/env python3
"""
Stage 5 MVP: AI agent for AiGroupchat with configurable personalities
Uses OpenAI for LLM and ElevenLabs for TTS
"""

import json
import logging
import os
from typing import Dict, Any

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


class ConfigurableAgent(Agent):
    """Agent with configurable personality based on template"""
    def __init__(self, agent_type: str) -> None:
        template = AGENT_TEMPLATES.get(agent_type, AGENT_TEMPLATES["study_partner"])
        super().__init__(instructions=template["instructions"])
        self.agent_type = agent_type
        self.template = template


async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the agent - called when a room needs an agent"""
    
    logger.info(f"Agent starting for room: {ctx.room.name}")
    
    # Get agent type from job metadata if available
    agent_type = "study_partner"  # Default
    if ctx.job and ctx.job.metadata:
        try:
            job_metadata = json.loads(ctx.job.metadata)
            if "agent_type" in job_metadata:
                agent_type = job_metadata["agent_type"]
                logger.info(f"Agent type from job metadata: {agent_type}")
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
        except json.JSONDecodeError:
            logger.warning("Failed to parse room metadata")
    
    # Wait for the first participant to join and check their metadata as last resort
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant joined: {participant.identity}")
    
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
    
    # Configure the voice pipeline with appropriate voice
    session = AgentSession(
        # Voice Activity Detection
        vad=silero.VAD.load(),
        
        # Speech-to-Text
        stt=deepgram.STT(
            model="nova-2",
            language="en-US",
        ),
        
        # Large Language Model
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
    
    # Start the session with configured agent
    await session.start(
        room=ctx.room,
        agent=ConfigurableAgent(agent_type),
    )
    
    # Generate initial greeting based on agent type
    await session.generate_reply(
        instructions=template["greeting"]
    )
    
    logger.info(f"Agent {template['name']} ready and listening")


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