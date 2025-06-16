#!/usr/bin/env python3
"""
Test agent document linking functionality
"""

import asyncio
import httpx
import json
import sys
import tempfile
import os

BASE_URL = "http://localhost:8000"

async def test_agent_document_linking():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("Testing Agent-Document Linking")
            print("=" * 50)
            
            # Step 1: Create a test user and agent
            print("\n1. Creating test user and agent...")
            owner_id = "test_user_123"
            
            # Create custom agent
            new_agent = {
                "name": "DocBot",
                "instructions": "You are DocBot, an agent that only knows about linked documents.",
                "voice_id": "nPczCjzI2devNBz1zQrb",
                "greeting": "Hello! I'm DocBot, ready to help with your documents."
            }
            response = await client.post(
                f"{BASE_URL}/api/agents?owner_id={owner_id}",
                json=new_agent
            )
            assert response.status_code == 200
            agent = response.json()
            agent_id = agent["id"]
            print(f"✓ Created agent: {agent['name']} (ID: {agent_id})")
            
            # Step 2: Upload a test document
            print("\n2. Uploading test document...")
            test_content = """
            AI Agent Personalities Guide
            
            This document describes different AI agent personalities:
            
            1. Study Partner: Friendly and helpful, asks questions to aid learning
            2. Socratic Tutor: Guides through questions rather than direct answers
            3. Debate Partner: Challenges ideas respectfully to explore concepts
            
            Each personality has unique characteristics and interaction styles.
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_content)
                temp_file = f.name
            
            try:
                with open(temp_file, 'rb') as f:
                    files = {'file': ('test_agents.txt', f, 'text/plain')}
                    data = {
                        'title': 'AI Agent Personalities',
                        'owner_id': owner_id
                    }
                    response = await client.post(
                        f"{BASE_URL}/api/documents",
                        files=files,
                        data=data
                    )
                assert response.status_code == 200
                document = response.json()
                document_id = document["document_id"]
                print(f"✓ Uploaded document: {document['title']} ({document['chunk_count']} chunks)")
            finally:
                os.unlink(temp_file)
            
            # Step 3: Link document to agent
            print("\n3. Linking document to agent...")
            link_request = {
                "document_ids": [document_id]
            }
            response = await client.post(
                f"{BASE_URL}/api/agents/{agent_id}/documents",
                json=link_request
            )
            assert response.status_code == 200
            print("✓ Document linked to agent")
            
            # Step 4: Verify agent has access to document
            print("\n4. Verifying agent document access...")
            response = await client.get(f"{BASE_URL}/api/agents/{agent_id}/documents")
            assert response.status_code == 200
            linked_docs = response.json()
            assert len(linked_docs) == 1
            assert linked_docs[0]["id"] == document_id
            print(f"✓ Agent has access to {len(linked_docs)} document(s)")
            
            # Step 5: Test RAG with agent filtering
            print("\n5. Testing RAG with agent filtering...")
            
            # Test with linked agent (should find content)
            context_request = {
                "query": "What are the different AI agent personalities?",
                "owner_id": owner_id,
                "agent_id": agent_id
            }
            response = await client.post(
                f"{BASE_URL}/api/documents/context",
                json=context_request
            )
            assert response.status_code == 200
            result = response.json()
            assert result["has_context"] == True
            assert "Study Partner" in result["context"]
            print("✓ Agent successfully retrieved linked document content")
            
            # Create another agent without document access
            print("\n6. Testing document isolation...")
            other_agent = {
                "name": "IsolatedBot",
                "instructions": "You are IsolatedBot with no document access.",
                "voice_id": "nPczCjzI2devNBz1zQrb",
                "greeting": "Hello from IsolatedBot!"
            }
            response = await client.post(
                f"{BASE_URL}/api/agents?owner_id={owner_id}",
                json=other_agent
            )
            other_agent_id = response.json()["id"]
            
            # Test with unlinked agent (should not find content)
            context_request["agent_id"] = other_agent_id
            response = await client.post(
                f"{BASE_URL}/api/documents/context",
                json=context_request
            )
            assert response.status_code == 200
            result = response.json()
            assert result["has_context"] == False
            print("✓ Document isolation working - unlinked agent has no access")
            
            # Step 7: Test unlinking
            print("\n7. Testing document unlinking...")
            response = await client.delete(
                f"{BASE_URL}/api/agents/{agent_id}/documents/{document_id}"
            )
            assert response.status_code == 200
            
            # Verify document is unlinked
            response = await client.get(f"{BASE_URL}/api/agents/{agent_id}/documents")
            linked_docs = response.json()
            assert len(linked_docs) == 0
            print("✓ Document successfully unlinked")
            
            # Step 8: Cleanup
            print("\n8. Cleaning up...")
            # Delete agents
            await client.delete(f"{BASE_URL}/api/agents/{agent_id}?owner_id={owner_id}")
            await client.delete(f"{BASE_URL}/api/agents/{other_agent_id}?owner_id={owner_id}")
            
            # Delete document
            await client.delete(f"{BASE_URL}/api/documents/{document_id}?owner_id={owner_id}")
            print("✓ Cleanup completed")
            
            print("\n✅ All agent-document linking tests passed!")
            
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
    print("Agent-Document Linking Test")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
    except:
        print("❌ Backend is not running. Please start it first with:")
        print("   cd backend && ./run.sh")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(test_agent_document_linking())
    sys.exit(0 if success else 1)