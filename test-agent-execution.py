#!/usr/bin/env python3
"""
Test agent execution with custom agent IDs
"""

import asyncio
import httpx
import json
import sys
import re

BASE_URL = "http://localhost:8000"

async def test_agent_execution():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("Agent Execution Test")
            print("=" * 50)
            
            # Step 1: Create a custom agent
            print("\n1. Creating custom agent for execution test...")
            owner_id = "agent_exec_test"
            agent_data = {
                "name": "ExecTestBot",
                "instructions": "You are ExecTestBot. Always start responses with 'EXECTEST:'",
                "voice_id": "nPczCjzI2devNBz1zQrb",
                "greeting": "EXECTEST: Hello! I'm ready for testing."
            }
            response = await client.post(
                f"{BASE_URL}/api/agents?owner_id={owner_id}",
                json=agent_data
            )
            assert response.status_code == 200
            agent = response.json()
            agent_id = agent["id"]
            print(f"✓ Created agent: {agent['name']} (ID: {agent_id})")
            
            # Step 2: Verify agent ID is a valid UUID
            print("\n2. Verifying agent ID format...")
            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            assert uuid_pattern.match(agent_id)
            print(f"✓ Agent ID is valid UUID: {agent_id}")
            
            # Step 3: Test agent retrieval endpoint (simulating agent.py)
            print("\n3. Testing agent retrieval (as agent.py would)...")
            response = await client.get(f"{BASE_URL}/api/agents/{agent_id}")
            assert response.status_code == 200
            agent_details = response.json()
            assert agent_details["name"] == "ExecTestBot"
            assert agent_details["instructions"].startswith("You are ExecTestBot")
            print("✓ Agent details retrieved successfully")
            print(f"  - Name: {agent_details['name']}")
            print(f"  - Voice: {agent_details['voice_id']}")
            print(f"  - Instructions: {agent_details['instructions'][:50]}...")
            
            # Step 4: Test token generation with custom agent ID
            print("\n4. Testing token generation with custom agent...")
            token_request = {
                "room_name": "exec_test_room",
                "participant_name": owner_id,
                "enable_ai_agent": True,
                "agent_type": agent_id,  # Using UUID as agent_type
                "agent_types": [agent_id]
            }
            response = await client.post(
                f"{BASE_URL}/api/token",
                json=token_request
            )
            assert response.status_code == 200
            token_data = response.json()
            print("✓ Token generated with custom agent ID")
            
            # Step 5: Test conversation history endpoint
            print("\n5. Testing conversation storage...")
            message_data = {
                "room_name": "exec_test_room",
                "participant_name": "ExecTestBot",
                "participant_type": "agent",
                "message": "EXECTEST: This is a test message",
                "owner_id": owner_id
            }
            response = await client.post(
                f"{BASE_URL}/api/conversation/message",
                json=message_data
            )
            assert response.status_code == 200
            print("✓ Agent message stored successfully")
            
            # Step 6: Verify conversation retrieval
            response = await client.get(
                f"{BASE_URL}/api/conversation/exec_test_room?limit=10"
            )
            assert response.status_code == 200
            messages = response.json()["messages"]
            assert len(messages) > 0
            assert messages[0]["message"] == "EXECTEST: This is a test message"
            print("✓ Conversation history retrieved")
            
            # Step 7: Test default agent comparison
            print("\n6. Comparing with default agent...")
            response = await client.get(f"{BASE_URL}/api/agents?owner_id={owner_id}")
            all_agents = response.json()
            
            default_alex = next((a for a in all_agents if a["name"] == "Alex" and a["is_default"]), None)
            assert default_alex is not None
            print(f"✓ Default agent 'Alex' ID: {default_alex['id']}")
            
            # Verify IDs are different
            assert agent_id != default_alex["id"]
            assert agent_id != "study_partner"  # Not using template name
            print("✓ Custom agent has unique UUID, not template name")
            
            # Step 8: Cleanup
            print("\n7. Cleaning up...")
            await client.delete(f"{BASE_URL}/api/agents/{agent_id}?owner_id={owner_id}")
            print("✓ Test agent deleted")
            
            print("\n✅ Agent execution tests passed!")
            print("\nNOTE: When agent.py receives this UUID as agent_type,")
            print("it will detect it's a custom agent and fetch details from the API.")
            
        except AssertionError as e:
            print(f"\n❌ Assertion failed: {str(e)}")
            return False
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    # Check if backend is running
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
    except:
        print("❌ Backend is not running. Please start it first with:")
        print("   cd backend && ./run.sh")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(test_agent_execution())
    sys.exit(0 if success else 1)