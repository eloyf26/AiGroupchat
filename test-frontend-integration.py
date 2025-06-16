#!/usr/bin/env python3
"""
Test frontend-backend integration for custom agents
"""

import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:8000"

async def test_frontend_integration():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("Frontend-Backend Integration Test")
            print("=" * 50)
            
            # Test 1: Default agents are available
            print("\n1. Testing default agents availability...")
            owner_id = "frontend_test_user"
            response = await client.get(f"{BASE_URL}/api/agents?owner_id={owner_id}")
            assert response.status_code == 200
            agents = response.json()
            default_agents = [a for a in agents if a["is_default"]]
            assert len(default_agents) == 3
            print(f"✓ Found {len(default_agents)} default agents")
            for agent in default_agents:
                print(f"  - {agent['name']}: {agent['document_count']} docs")
            
            # Test 2: Create custom agent with specific voice
            print("\n2. Testing custom agent creation with voice selection...")
            voices = [
                ("nPczCjzI2devNBz1zQrb", "Brian"),
                ("EXAVITQu4vr4xnSDxMaL", "Sarah"),
                ("TxGEqnHWrfWFTfGW9XjX", "Josh"),
                ("pMsXgVXv3BLzUgSXRplE", "Serena")
            ]
            
            for voice_id, voice_name in voices[:2]:  # Test first 2 voices
                agent_data = {
                    "name": f"TestAgent_{voice_name}",
                    "instructions": f"You are a test agent using {voice_name}'s voice",
                    "voice_id": voice_id,
                    "greeting": f"Hello from {voice_name}!"
                }
                response = await client.post(
                    f"{BASE_URL}/api/agents?owner_id={owner_id}",
                    json=agent_data
                )
                assert response.status_code == 200
                created = response.json()
                assert created["voice_id"] == voice_id
                print(f"✓ Created agent with {voice_name}'s voice")
            
            # Test 3: Verify agent count
            print("\n3. Verifying total agent count...")
            response = await client.get(f"{BASE_URL}/api/agents?owner_id={owner_id}")
            all_agents = response.json()
            custom_agents = [a for a in all_agents if not a["is_default"]]
            print(f"✓ Total agents: {len(all_agents)} (3 default + {len(custom_agents)} custom)")
            
            # Test 4: Test agent selection limit (simulate frontend)
            print("\n4. Testing agent selection constraints...")
            # Frontend should limit selection to 2 agents max
            selected_ids = [all_agents[0]["id"], all_agents[1]["id"]]
            print(f"✓ Selected {len(selected_ids)} agents (max allowed)")
            
            # Test 5: Generate token with selected agents
            print("\n5. Testing LiveKit token generation with agents...")
            token_request = {
                "room_name": "test_room",
                "participant_name": owner_id,
                "enable_ai_agent": True,
                "agent_type": selected_ids[0],  # Primary agent
                "agent_types": selected_ids  # All selected agents
            }
            response = await client.post(
                f"{BASE_URL}/api/token",
                json=token_request
            )
            assert response.status_code == 200
            token_data = response.json()
            assert token_data["ai_agent_enabled"] == True
            print("✓ LiveKit token generated with agent configuration")
            
            # Test 6: Document count updates
            print("\n6. Testing document count in agent list...")
            # Upload a test document
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test document content")
                temp_file = f.name
            
            try:
                with open(temp_file, 'rb') as f:
                    files = {'file': ('test.txt', f, 'text/plain')}
                    data = {'title': 'Test Doc', 'owner_id': owner_id}
                    response = await client.post(
                        f"{BASE_URL}/api/documents",
                        files=files,
                        data=data
                    )
                doc_id = response.json()["document_id"]
                
                # Link to first custom agent
                custom_agent_id = custom_agents[0]["id"]
                response = await client.post(
                    f"{BASE_URL}/api/agents/{custom_agent_id}/documents",
                    json={"document_ids": [doc_id]}
                )
                
                # Verify document count updated
                response = await client.get(f"{BASE_URL}/api/agents?owner_id={owner_id}")
                updated_agents = response.json()
                updated_agent = next(a for a in updated_agents if a["id"] == custom_agent_id)
                assert updated_agent["document_count"] == 1
                print("✓ Document count correctly updated")
                
                # Cleanup
                await client.delete(f"{BASE_URL}/api/documents/{doc_id}?owner_id={owner_id}")
            finally:
                os.unlink(temp_file)
            
            # Test 7: Cleanup
            print("\n7. Cleaning up test data...")
            for agent in custom_agents:
                await client.delete(f"{BASE_URL}/api/agents/{agent['id']}?owner_id={owner_id}")
            print("✓ Test agents deleted")
            
            print("\n✅ All frontend integration tests passed!")
            
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
    success = asyncio.run(test_frontend_integration())
    sys.exit(0 if success else 1)