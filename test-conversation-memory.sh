#!/bin/bash

# Test script for conversation memory and multi-agent features
echo "=== Testing Conversation Memory and Multi-Agent Features ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -n "Testing $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓${NC} ($http_code)"
        if [ -n "$body" ]; then
            echo "  Response: $(echo $body | jq -c . 2>/dev/null || echo $body)"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} ($http_code)"
        echo "  Error: $body"
        return 1
    fi
}

# Check if backend is running
echo "Checking backend health..."
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${RED}Backend is not running at $BASE_URL${NC}"
    echo "Please start the backend with: cd backend && ./run.sh"
    exit 1
fi
echo -e "${GREEN}Backend is running${NC}"

echo ""
echo "=== Testing Conversation Memory Endpoints ==="

# Test adding a conversation message
test_endpoint "POST" "/api/conversation/message" \
    '{"room_name":"test-room","participant_name":"User","participant_type":"human","message":"Hello, this is a test message","owner_id":"User"}' \
    "POST /api/conversation/message (human)"

# Test adding an agent message
test_endpoint "POST" "/api/conversation/message" \
    '{"room_name":"test-room","participant_name":"Alex","participant_type":"agent","message":"Hi! I am Alex, your AI study partner.","owner_id":"User"}' \
    "POST /api/conversation/message (agent)"

# Test retrieving conversation history
test_endpoint "GET" "/api/conversation/test-room?limit=10" "" \
    "GET /api/conversation/{room_name}"

echo ""
echo "=== Testing Multi-Agent Token Generation ==="

# Test single agent token
test_endpoint "POST" "/api/token" \
    '{"room_name":"single-agent-room","participant_name":"TestUser","enable_ai_agent":true,"agent_type":"study_partner"}' \
    "POST /api/token (single agent)"

# Test multi-agent token
test_endpoint "POST" "/api/token" \
    '{"room_name":"multi-agent-room","participant_name":"TestUser","enable_ai_agent":true,"agent_type":"study_partner","agent_types":["study_partner","socratic_tutor"]}' \
    "POST /api/token (multi-agent)"

echo ""
echo "=== Testing Agent Templates ==="

# Test getting all templates
test_endpoint "GET" "/api/agent-templates" "" \
    "GET /api/agent-templates"

echo ""
echo -e "${GREEN}Test complete!${NC}"