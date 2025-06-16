#!/usr/bin/env python3
"""
Stage 7 MVP: AI agent for AiGroupchat with configurable personalities and RAG
Uses OpenAI for LLM and ElevenLabs for TTS with document context retrieval
"""

import json
import logging
import os
import time
import asyncio
from typing import Dict, Any, Optional, List
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
    
    def __init__(self, instructions: str, context_manager: DocumentContextManager, owner_id: str, room_name: str, agent_name: str = "Agent", other_agents: List[str] = None):
        super().__init__(instructions=instructions)
        self._context_manager = context_manager
        self._owner_id = owner_id
        self._room_name = room_name
        self._agent_name = agent_name
        self._other_agents = other_agents or []
        self._rag_enabled = True
        self._last_agent_spoke_time = 0
        self._last_response = None  # Track last generated response
        self._last_user_message = None  # Track last user message to avoid duplicates
        self._last_user_message_time = 0
        logger.info(f"RAGVoiceAgent initialized with owner_id: {owner_id}, room: {room_name}")
    
    async def on_user_turn_completed(self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage) -> None:
        """Called when user completes a turn - inject conversation memory and RAG context"""
        try:
            # Get the user's message content
            user_message = new_message.content
            logger.info(f"[TURN] User turn completed: '{user_message}' (type: {type(user_message)})")
            
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
            
            # Store user message in conversation history (with deduplication)
            current_time = time.time()
            if user_message != self._last_user_message or (current_time - self._last_user_message_time) > 2.0:
                await self._store_message("human", "User", user_message)
                logger.info(f"[STORED] User message stored: '{user_message[:50]}...'")
                self._last_user_message = user_message
                self._last_user_message_time = current_time
            else:
                logger.debug(f"[SKIP] Duplicate user message skipped: '{user_message[:50]}...'")
            
            # Check if another agent spoke recently (simple turn-taking)
            await self._check_turn_taking()
            
            # Get conversation history
            history = await self._get_conversation_history()
            if history:
                history_text = "Previous conversation:\n" + history
                
                # Add agent awareness if there are other agents
                if self._other_agents:
                    agent_info = f"\n\nOther agents in this conversation: {', '.join(self._other_agents)}. Be aware of their contributions and build upon them when relevant."
                    history_text += agent_info
                
                turn_ctx.add_message(
                    role="system",
                    content=history_text
                )
                logger.info("Injected conversation history")
            
            # Retrieve relevant context if RAG is enabled
            if self._rag_enabled and self._context_manager and self._owner_id:
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
            logger.error(f"Failed to process user turn: {e}")
            # Continue without enhancements on error
    
    async def on_turn_completed(self, turn_ctx: llm.ChatContext) -> None:
        """Called after agent generates a response - store it in history"""
        try:
            logger.info(f"[TURN] Agent turn completed for {self._agent_name}")
            
            # Log all messages for debugging
            logger.debug(f"[TURN] Total messages in context: {len(turn_ctx.messages)}")
            for i, msg in enumerate(turn_ctx.messages):
                logger.debug(f"[TURN] Message {i}: role={msg.role}, content={str(msg.content)[:50]}...")
            
            # Get the last assistant message (agent's response)
            messages = turn_ctx.messages
            found_message = False
            
            # Look for the most recent assistant message
            for msg in reversed(messages):
                if msg.role == "assistant":
                    content = msg.content
                    
                    # Handle different content types
                    if isinstance(content, list):
                        content = " ".join(str(part) for part in content)
                    elif not isinstance(content, str):
                        content = str(content)
                    
                    # Only store if it's different from last stored response
                    if content and content != self._last_response:
                        self._last_response = content
                        await self._store_message("agent", self._agent_name, content)
                        logger.info(f"[STORED] Agent response stored: '{content[:50]}...'")
                        found_message = True
                        break
            
            if not found_message:
                logger.warning(f"[TURN] No new assistant message found for {self._agent_name}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to store agent response: {e}", exc_info=True)
    
    
    async def _get_conversation_history(self) -> Optional[str]:
        """Get recent conversation history from backend with smart limits"""
        try:
            # Fetch more messages initially to have room for smart selection
            response = await self._context_manager.client.get(
                f"{self._context_manager.backend_url}/api/conversation/{self._room_name}",
                params={"limit": 30}  # Fetch more to filter intelligently
            )
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                if messages:
                    # Smart message selection:
                    # - Take last 20 messages max
                    # - Estimate ~4 tokens per word, ~10 words per message average
                    # - Target ~2000 tokens max for history (leaving room for system prompts)
                    MAX_TOKENS = 2000
                    MAX_MESSAGES = 20
                    ESTIMATED_TOKENS_PER_CHAR = 0.25  # Conservative estimate
                    
                    selected_messages = []
                    total_tokens = 0
                    
                    # Process messages in reverse order (most recent first)
                    for msg in reversed(messages[-MAX_MESSAGES:]):
                        # Skip system messages or empty messages
                        if not msg.get('message') or len(msg['message'].strip()) < 2:
                            continue
                            
                        # Estimate tokens for this message
                        msg_tokens = len(msg['message']) * ESTIMATED_TOKENS_PER_CHAR
                        
                        # Check if adding this message would exceed token limit
                        if total_tokens + msg_tokens > MAX_TOKENS:
                            break
                            
                        speaker = f"[{msg['participant_name']}]"
                        selected_messages.append(f"{speaker}: {msg['message']}")
                        total_tokens += msg_tokens
                    
                    # Return in chronological order
                    if selected_messages:
                        selected_messages.reverse()
                        logger.debug(f"Selected {len(selected_messages)} messages (~{int(total_tokens)} tokens) for context")
                        return "\n".join(selected_messages)
            return None
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return None
    
    async def _store_message(self, participant_type: str, participant_name: str, message: str):
        """Store a message in conversation history"""
        try:
            logger.debug(f"[STORE] Attempting to store {participant_type} message from {participant_name}")
            response = await self._context_manager.client.post(
                f"{self._context_manager.backend_url}/api/conversation/message",
                json={
                    "room_name": self._room_name,
                    "participant_name": participant_name,
                    "participant_type": participant_type,
                    "message": message,
                    "owner_id": self._owner_id  # Include owner_id for RLS
                }
            )
            if response.status_code == 200:
                logger.debug(f"[STORE] Successfully stored {participant_type} message")
            else:
                logger.error(f"[STORE] Failed to store message: HTTP {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"[STORE] Exception storing message: {e}")
    
    async def _check_turn_taking(self):
        """Simple turn-taking: wait if another agent spoke recently"""
        if not self._other_agents:
            return
            
        # Check if an agent message was added in the last 2 seconds
        current_time = time.time()
        if current_time - self._last_agent_spoke_time < 2.0:
            await asyncio.sleep(1.5)  # Wait a bit
        
        # Update last spoke time
        self._last_agent_spoke_time = current_time


async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the agent - called when a room needs an agent"""
    
    logger.info(f"Agent starting for room: {ctx.room.name}")
    
    # Get agent type and owner_id from job metadata if available
    agent_type = "study_partner"  # Default
    agent_id = None
    owner_id = None
    if ctx.job and ctx.job.metadata:
        try:
            job_metadata = json.loads(ctx.job.metadata)
            if "agent_type" in job_metadata:
                agent_type = job_metadata["agent_type"]
                logger.info(f"Agent type from job metadata: {agent_type}")
            if "agent_id" in job_metadata:
                agent_id = job_metadata["agent_id"]
                logger.info(f"Agent ID from job metadata: {agent_id}")
            if "owner_id" in job_metadata:
                owner_id = job_metadata["owner_id"]
                logger.info(f"Owner ID from job metadata: {owner_id}")
        except json.JSONDecodeError:
            logger.warning("Failed to parse job metadata")
    
    # Connect to the room first
    await ctx.connect()
    
    # Check room metadata for agent types
    if ctx.room.metadata:
        try:
            room_metadata = json.loads(ctx.room.metadata)
            agent_types = room_metadata.get("agent_types", [])
            if "owner_id" in room_metadata and not owner_id:
                owner_id = room_metadata["owner_id"]
                logger.info(f"Owner ID from room metadata: {owner_id}")
            
            # Simple approach: each agent instance picks the next available type
            # For now, just use the first available type since we can't access participants yet
            # Multiple agent processes will coordinate through metadata
            if agent_types and len(agent_types) > 0:
                # Use environment variable or process ID to determine which agent to be
                import os
                agent_index = int(os.environ.get('AGENT_INDEX', '0'))
                if agent_index < len(agent_types):
                    agent_type = agent_types[agent_index]
                    agent_id = str(agent_index)
                    logger.info(f"Selected agent type {agent_type} with ID {agent_id}")
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
    
    # Get other agent names from room metadata
    other_agents = []
    if ctx.room.metadata:
        try:
            room_metadata = json.loads(ctx.room.metadata)
            agent_types = room_metadata.get("agent_types", [])
            for a_type in agent_types:
                if a_type != agent_type:  # Don't include self
                    other_template = AGENT_TEMPLATES.get(a_type, {})
                    if other_template:
                        other_agents.append(other_template.get("name", a_type))
        except:
            pass
    
    # Initialize document context manager for RAG
    context_manager = DocumentContextManager()
    
    # Create the voice agent with RAG support
    agent_name = f"{template['name']}-{agent_id}" if agent_id else template["name"]
    agent = RAGVoiceAgent(
        instructions=template["instructions"],
        context_manager=context_manager,
        owner_id=owner_id,
        room_name=ctx.room.name,
        agent_name=agent_name,
        other_agents=other_agents
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
    
    # Add event handler to track agent messages
    @session.on("conversation_item_added")
    def on_conversation_item_added(event):
        """Store messages when added to conversation - handles interruptions"""
        async def store_conversation_item():
            try:
                logger.debug(f"[CONVERSATION] Item added to conversation")
                if hasattr(event, 'item') and hasattr(event.item, 'role'):
                    # Store both user and assistant messages for complete history
                    role = event.item.role
                    content = event.item.content
                    
                    # Convert content to string if needed
                    if isinstance(content, list):
                        content = " ".join(str(part) for part in content)
                    elif not isinstance(content, str):
                        content = str(content)
                    
                    # Store assistant messages
                    if role == "assistant" and content:
                        if content != agent._last_response:
                            agent._last_response = content
                            await agent._store_message("agent", agent_name, content)
                            logger.info(f"[STORED] Agent message via conversation_item_added: '{content[:50]}...'")
                    
                    # Also store user messages as backup (in case on_user_turn_completed fails)
                    elif role == "user" and content and len(content.strip()) >= 3:
                        # Only store if not recently stored (avoid duplicates)
                        current_time = time.time()
                        if content != agent._last_user_message or (current_time - agent._last_user_message_time) > 2.0:
                            await agent._store_message("human", "User", content)
                            logger.info(f"[STORED] User message via conversation_item_added: '{content[:50]}...'")
                            agent._last_user_message = content
                            agent._last_user_message_time = current_time
                        else:
                            logger.debug(f"[SKIP] Duplicate user message in conversation_item_added: '{content[:50]}...'")
                        
            except Exception as e:
                logger.error(f"[ERROR] Failed to store conversation item: {e}", exc_info=True)
        
        asyncio.create_task(store_conversation_item())
    
    # Start the session with the agent
    await session.start(room=ctx.room, agent=agent)
    
    # Try to update participant metadata with agent info
    try:
        # Set metadata for the agent participant
        await ctx.room.local_participant.set_metadata(json.dumps({
            "agent_type": agent_type,
            "agent_name": agent_name,
            "is_agent": True
        }))
        logger.info(f"Set agent metadata: {agent_name} ({agent_type})")
    except Exception as e:
        logger.warning(f"Could not set participant metadata: {e}")
    
    # Generate initial greeting
    try:
        # Store greeting first
        await agent._store_message("agent", agent_name, template["greeting"])
        # Then send it
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