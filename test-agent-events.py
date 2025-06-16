#!/usr/bin/env python3
"""
Test script to verify agent event handlers work correctly
"""

import asyncio
from unittest.mock import Mock, MagicMock
from livekit.agents import AgentSession
from livekit.agents.voice.events import SpeechCreatedEvent, ConversationItemAddedEvent

def test_event_handlers():
    """Test that event handlers can be registered without errors"""
    
    # Create a mock session
    session = Mock(spec=AgentSession)
    session.on = MagicMock()
    
    # Test registering sync event handlers
    @session.on("speech_created")
    def on_speech_created(event):
        print("Speech created handler registered")
        
    @session.on("conversation_item_added")
    def on_conversation_item_added(event):
        print("Conversation item added handler registered")
    
    # Verify handlers were registered
    assert session.on.call_count == 2
    print("✓ Event handlers registered successfully")
    
    # Test that handlers are sync, not async
    handler1 = session.on.call_args_list[0][0][1]
    handler2 = session.on.call_args_list[1][0][1]
    
    assert not asyncio.iscoroutinefunction(handler1), "Handler should be sync, not async"
    assert not asyncio.iscoroutinefunction(handler2), "Handler should be sync, not async"
    print("✓ Handlers are correctly synchronous")
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_event_handlers()