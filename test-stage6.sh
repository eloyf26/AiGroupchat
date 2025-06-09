#!/bin/bash

# Stage 6 Test Script - Supabase Vector Database Setup
# Tests document upload and storage functionality

echo "======================================="
echo "Testing Stage 6: Supabase Vector Database Setup"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
check_backend() {
    echo -n "Checking if backend is running... "
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        echo -e "${YELLOW}Please start the backend first: cd backend && ./run.sh${NC}"
        return 1
    fi
}

# Test document upload
test_document_upload() {
    echo -e "\n${YELLOW}Testing document upload...${NC}"
    
    # Create a test text file
    echo "This is a test document for Stage 6 RAG implementation." > test_document.txt
    
    # Upload document
    response=$(curl -s -X POST http://localhost:8000/api/documents \
        -F "file=@test_document.txt" \
        -F "title=Test Document" \
        -F "owner_id=test-user-123" \
        -F "doc_type=text")
    
    if echo "$response" | grep -q "document_id"; then
        echo -e "${GREEN}✓ Document upload successful${NC}"
        echo "Response: $response"
        
        # Extract document_id for further tests
        export DOCUMENT_ID=$(echo "$response" | grep -o '"document_id":"[^"]*' | cut -d'"' -f4)
        echo "Document ID: $DOCUMENT_ID"
        return 0
    else
        echo -e "${RED}✗ Document upload failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Test document listing
test_document_list() {
    echo -e "\n${YELLOW}Testing document listing...${NC}"
    
    response=$(curl -s "http://localhost:8000/api/documents?owner_id=test-user-123")
    
    if echo "$response" | grep -q "Test Document"; then
        echo -e "${GREEN}✓ Document listing successful${NC}"
        echo "Found documents: $(echo "$response" | grep -o '"title":"[^"]*' | wc -l)"
        return 0
    else
        echo -e "${RED}✗ Document listing failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Test document retrieval
test_document_get() {
    echo -e "\n${YELLOW}Testing document retrieval...${NC}"
    
    if [ -z "$DOCUMENT_ID" ]; then
        echo -e "${YELLOW}Skipping - no document ID available${NC}"
        return 1
    fi
    
    response=$(curl -s "http://localhost:8000/api/documents/$DOCUMENT_ID?owner_id=test-user-123")
    
    if echo "$response" | grep -q "document"; then
        echo -e "${GREEN}✓ Document retrieval successful${NC}"
        echo "Document has $(echo "$response" | grep -o '"sections":\[' | wc -l) section(s)"
        return 0
    else
        echo -e "${RED}✗ Document retrieval failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Test document deletion
test_document_delete() {
    echo -e "\n${YELLOW}Testing document deletion...${NC}"
    
    if [ -z "$DOCUMENT_ID" ]; then
        echo -e "${YELLOW}Skipping - no document ID available${NC}"
        return 1
    fi
    
    response=$(curl -s -X DELETE "http://localhost:8000/api/documents/$DOCUMENT_ID?owner_id=test-user-123")
    
    if echo "$response" | grep -q "deleted successfully"; then
        echo -e "${GREEN}✓ Document deletion successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Document deletion failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Clean up test file
cleanup() {
    rm -f test_document.txt
}

# Run tests
echo "Starting Stage 6 tests..."

if ! check_backend; then
    exit 1
fi

# Run document tests
test_document_upload
test_document_list
test_document_get
test_document_delete

# Cleanup
cleanup

echo -e "\n======================================="
echo "Stage 6 Testing Complete!"
echo "======================================="
echo ""
echo "Note: Make sure you have:"
echo "1. Set SUPABASE_URL and SUPABASE_KEY in backend/.env"
echo "2. Run the schema.sql script in your Supabase database"
echo "3. Enabled the pgvector extension in Supabase"
echo ""
echo "Next steps:"
echo "- Stage 7: Implement document chunking and embeddings"
echo "- Stage 8: Add hybrid search functionality"