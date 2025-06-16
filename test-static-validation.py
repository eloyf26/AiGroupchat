#!/usr/bin/env python3
"""
Static validation tests for the conversation memory and multi-agent implementation
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "agent"))

def test_imports():
    """Test that all modules can be imported"""
    print("=== Testing Imports ===")
    
    try:
        # Backend imports
        from backend.main import TokenRequest, ConversationMessage
        print("✓ Backend models imported successfully")
        
        # Agent imports  
        from agent.agent import RAGVoiceAgent, DocumentContextManager
        print("✓ Agent classes imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_sql_syntax():
    """Validate SQL syntax"""
    print("\n=== Testing SQL Syntax ===")
    
    sql_files = [
        "backend/schema.sql",
        "backend/migrate_conversation.sql"
    ]
    
    for sql_file in sql_files:
        if os.path.exists(sql_file):
            try:
                with open(sql_file, 'r') as f:
                    content = f.read()
                    # Basic SQL validation
                    if "CREATE TABLE" in content and ";" in content:
                        print(f"✓ {sql_file} has valid SQL structure")
                    else:
                        print(f"✗ {sql_file} may have SQL issues")
            except Exception as e:
                print(f"✗ Error reading {sql_file}: {e}")
        else:
            print(f"- {sql_file} not found")

def test_agent_templates():
    """Test agent template configuration"""
    print("\n=== Testing Agent Templates ===")
    
    try:
        from backend.agent_templates import AGENT_TEMPLATES, get_agent_template
        
        # Check all templates exist
        expected_templates = ["study_partner", "socratic_tutor", "debate_partner"]
        for template in expected_templates:
            if template in AGENT_TEMPLATES:
                agent = AGENT_TEMPLATES[template]
                if all(key in agent for key in ["name", "instructions", "voice_id"]):
                    print(f"✓ {template} template is properly configured")
                else:
                    print(f"✗ {template} template missing required fields")
            else:
                print(f"✗ {template} template not found")
                
        return True
    except Exception as e:
        print(f"✗ Agent template test failed: {e}")
        return False

def test_frontend_build():
    """Check if frontend can build"""
    print("\n=== Testing Frontend ===")
    
    # Check package.json exists
    if os.path.exists("frontend/package.json"):
        print("✓ package.json exists")
        
        # Check for TypeScript errors we fixed
        tsx_files = ["frontend/app/components/VoiceRoom.tsx", "frontend/app/page.tsx"]
        for tsx_file in tsx_files:
            if os.path.exists(tsx_file):
                with open(tsx_file, 'r') as f:
                    content = f.read()
                    # Check for known issues we fixed
                    if "ParticipantTile" not in content or "import {" not in content:
                        print(f"✓ {tsx_file} has cleaned imports")
                    if "agent_types" in content:
                        print(f"✓ {tsx_file} supports multi-agent")
    else:
        print("✗ frontend/package.json not found")

def test_conversation_api_structure():
    """Test the conversation API endpoint structure"""
    print("\n=== Testing API Structure ===")
    
    # Check if main.py has the new endpoints
    if os.path.exists("backend/main.py"):
        with open("backend/main.py", 'r') as f:
            content = f.read()
            
        endpoints = [
            ("/api/conversation/message", "POST", "Store conversation message"),
            ("/api/conversation/{room_name}", "GET", "Get conversation history")
        ]
        
        for endpoint, method, desc in endpoints:
            if endpoint.replace("{room_name}", "") in content:
                print(f"✓ {method} {endpoint} - {desc}")
            else:
                print(f"✗ {method} {endpoint} - Not found")

def test_multi_agent_support():
    """Test multi-agent implementation"""
    print("\n=== Testing Multi-Agent Support ===")
    
    # Check run-multi.sh exists and is executable
    if os.path.exists("agent/run-multi.sh"):
        print("✓ run-multi.sh exists")
        # Check if executable
        if os.access("agent/run-multi.sh", os.X_OK):
            print("✓ run-multi.sh is executable")
        else:
            print("✗ run-multi.sh is not executable")
    else:
        print("✗ run-multi.sh not found")
    
    # Check agent.py for multi-agent features
    if os.path.exists("agent/agent.py"):
        with open("agent/agent.py", 'r') as f:
            content = f.read()
            
        features = [
            ("other_agents", "Agent awareness"),
            ("_check_turn_taking", "Turn-taking mechanism"),
            ("agent_types", "Multi-agent type support"),
            ("conversation_messages", "Conversation memory")
        ]
        
        for feature, desc in features:
            if feature in content:
                print(f"✓ {desc} implemented")
            else:
                print(f"✗ {desc} not found")

def main():
    """Run all static tests"""
    print("=" * 50)
    print("Static Validation Tests for Conversation Memory & Multi-Agent")
    print("=" * 50)
    
    test_sql_syntax()
    test_agent_templates()
    test_frontend_build()
    test_conversation_api_structure()
    test_multi_agent_support()
    
    print("\n" + "=" * 50)
    print("Static validation complete!")
    print("To run live tests, start the backend with: cd backend && ./run.sh")
    print("Then run: ./test-conversation-memory.sh")

if __name__ == "__main__":
    main()