#!/usr/bin/env python3
"""
Test script to diagnose conversation message storage issues
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_message_storage():
    """Test storing and retrieving messages"""
    async with httpx.AsyncClient() as client:
        room_name = f"test-room-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        owner_id = "test-user"
        
        print(f"Testing room: {room_name}")
        print(f"Owner ID: {owner_id}\n")
        
        # Test 1: Store human message
        print("1. Testing human message storage...")
        response = await client.post(
            f"{BASE_URL}/api/conversation/message",
            json={
                "room_name": room_name,
                "participant_name": "TestUser",
                "participant_type": "human",
                "message": "Hello, this is a test message from a human",
                "owner_id": owner_id
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
        
        # Test 2: Store agent message with owner_id
        print("\n2. Testing agent message storage (with owner_id)...")
        response = await client.post(
            f"{BASE_URL}/api/conversation/message",
            json={
                "room_name": room_name,
                "participant_name": "Alex",
                "participant_type": "agent",
                "message": "Hi! I'm Alex, your AI study partner.",
                "owner_id": owner_id
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
        
        # Test 3: Store agent message without owner_id (to test auto-detection)
        print("\n3. Testing agent message storage (without owner_id)...")
        response = await client.post(
            f"{BASE_URL}/api/conversation/message",
            json={
                "room_name": room_name,
                "participant_name": "Sophie",
                "participant_type": "agent",
                "message": "Hello! I'm Sophie, your Socratic tutor."
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
        
        # Test 4: Retrieve conversation history
        print("\n4. Retrieving conversation history...")
        response = await client.get(
            f"{BASE_URL}/api/conversation/{room_name}",
            params={"limit": 10}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            print(f"   Found {len(messages)} messages:")
            for msg in messages:
                print(f"   - [{msg['participant_type']}] {msg['participant_name']}: {msg['message'][:50]}...")
                print(f"     owner_id: {msg.get('owner_id', 'NOT SET')}")
        else:
            print(f"   Error: {response.text}")
        
        # Test 5: Test rapid message storage (simulating interruptions)
        print("\n5. Testing rapid message storage (simulating interruptions)...")
        messages_sent = []
        
        # Send messages rapidly
        for i in range(5):
            msg_data = {
                "room_name": room_name,
                "participant_name": "Alex" if i % 2 == 0 else "User",
                "participant_type": "agent" if i % 2 == 0 else "human",
                "message": f"Message {i}: {'Agent speaking...' if i % 2 == 0 else 'Human interrupting!'}",
                "owner_id": owner_id
            }
            messages_sent.append(msg_data)
            
            response = await client.post(
                f"{BASE_URL}/api/conversation/message",
                json=msg_data
            )
            print(f"   Message {i}: {response.status_code}")
            await asyncio.sleep(0.1)  # Small delay
        
        # Check if all messages were stored
        print("\n   Verifying rapid messages...")
        response = await client.get(
            f"{BASE_URL}/api/conversation/{room_name}",
            params={"limit": 20}
        )
        if response.status_code == 200:
            data = response.json()
            stored_messages = data.get("messages", [])
            recent_messages = [m for m in stored_messages if any(
                sent['message'] == m['message'] for sent in messages_sent
            )]
            print(f"   Sent: {len(messages_sent)}, Stored: {len(recent_messages)}")
            if len(recent_messages) < len(messages_sent):
                print("   WARNING: Some messages were lost!")

if __name__ == "__main__":
    print("=== Conversation Message Storage Test ===\n")
    asyncio.run(test_message_storage())
    print("\n=== Test Complete ===")