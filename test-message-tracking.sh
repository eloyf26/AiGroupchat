#!/bin/bash

# Test conversation message storage

echo "=== Testing Conversation Message Storage ==="
echo ""

ROOM_NAME="test-room-$(date +%s)"
OWNER_ID="test-user"
BASE_URL="http://localhost:8000"

echo "Room: $ROOM_NAME"
echo "Owner: $OWNER_ID"
echo ""

# Test 1: Store human message
echo "1. Storing human message..."
curl -s -X POST "$BASE_URL/api/conversation/message" \
  -H "Content-Type: application/json" \
  -d "{
    \"room_name\": \"$ROOM_NAME\",
    \"participant_name\": \"TestUser\",
    \"participant_type\": \"human\",
    \"message\": \"Hello from human\",
    \"owner_id\": \"$OWNER_ID\"
  }" | jq .

# Test 2: Store agent message with owner_id
echo -e "\n2. Storing agent message (with owner_id)..."
curl -s -X POST "$BASE_URL/api/conversation/message" \
  -H "Content-Type: application/json" \
  -d "{
    \"room_name\": \"$ROOM_NAME\",
    \"participant_name\": \"Alex\",
    \"participant_type\": \"agent\",
    \"message\": \"Hello from Alex\",
    \"owner_id\": \"$OWNER_ID\"
  }" | jq .

# Test 3: Store agent message without owner_id
echo -e "\n3. Storing agent message (without owner_id)..."
curl -s -X POST "$BASE_URL/api/conversation/message" \
  -H "Content-Type: application/json" \
  -d "{
    \"room_name\": \"$ROOM_NAME\",
    \"participant_name\": \"Sophie\",
    \"participant_type\": \"agent\",
    \"message\": \"Hello from Sophie\"
  }" | jq .

# Test 4: Retrieve messages
echo -e "\n4. Retrieving conversation history..."
curl -s "$BASE_URL/api/conversation/$ROOM_NAME?limit=10" | jq '.messages[] | {participant_type, participant_name, message, owner_id}'

echo -e "\n=== Test Complete ==="