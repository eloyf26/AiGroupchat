#!/usr/bin/env python3
"""
Test script for custom agent functionality
"""

import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:8000"

async def test_custom_agents():
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("1. Testing backend health...")
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            print("✓ Backend is healthy")
            
            # Test 2: List agents for a user
            print("\n2. Testing agent list...")
            response = await client.get(f"{BASE_URL}/api/agents?owner_id=testuser")
            assert response.status_code == 200
            agents = response.json()
            print(f"✓ Found {len(agents)} agents")
            for agent in agents:
                print(f"  - {agent['name']} ({'Default' if agent['is_default'] else 'Custom'})")
            
            # Test 3: Create a custom agent
            print("\n3. Creating custom agent...")
            new_agent = {
                "name": "TestBot",
                "instructions": "You are a helpful test assistant",
                "voice_id": "nPczCjzI2devNBz1zQrb",
                "greeting": "Hello! I'm TestBot."
            }
            response = await client.post(
                f"{BASE_URL}/api/agents?owner_id=testuser",
                json=new_agent
            )
            assert response.status_code == 200
            created_agent = response.json()
            agent_id = created_agent["id"]
            print(f"✓ Created agent: {created_agent['name']} (ID: {agent_id})")
            
            # Test 4: Get specific agent
            print("\n4. Getting agent details...")
            response = await client.get(f"{BASE_URL}/api/agents/{agent_id}")
            assert response.status_code == 200
            agent_details = response.json()
            print(f"✓ Retrieved agent: {agent_details['name']}")
            
            # Test 5: Test document context with agent filtering
            print("\n5. Testing document context retrieval...")
            context_request = {
                "query": "Tell me about AI agents",
                "owner_id": "testuser",
                "agent_id": agent_id
            }
            response = await client.post(
                f"{BASE_URL}/api/documents/context",
                json=context_request
            )
            assert response.status_code == 200
            context_data = response.json()
            print(f"✓ Context retrieval working (has_context: {context_data['has_context']})")
            
            # Test 6: Delete the test agent
            print("\n6. Deleting test agent...")
            response = await client.delete(
                f"{BASE_URL}/api/agents/{agent_id}?owner_id=testuser"
            )
            assert response.status_code == 200
            print("✓ Agent deleted successfully")
            
            print("\n✅ All tests passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("Custom Agent Feature Test")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
    except:
        print("❌ Backend is not running. Please start it first with:")
        print("   cd backend && ./run.sh")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(test_custom_agents())
    sys.exit(0 if success else 1)