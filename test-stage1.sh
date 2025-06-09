#!/bin/bash
echo "Testing Stage 1 Implementation..."

echo "1. Testing backend health endpoint..."
cd backend && ./run.sh &
BACKEND_PID=$!
sleep 3

# Test health endpoint
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "✓ Backend health endpoint working"
else
    echo "✗ Backend health endpoint failed"
    echo "Response: $HEALTH_RESPONSE"
fi

echo "2. Testing frontend..."
cd ../frontend && npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Frontend builds successfully"
else
    echo "✗ Frontend build failed"
fi

echo "3. Testing frontend-backend connectivity..."
npm run dev &
FRONTEND_PID=$!
sleep 5

# Test if frontend renders properly
FRONTEND_RESPONSE=$(curl -s http://localhost:3000)
if [[ $FRONTEND_RESPONSE == *"AiGroupchat"* ]]; then
    echo "✓ Frontend renders correctly"
else
    echo "✗ Frontend rendering failed"
fi

# Cleanup
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "Stage 1 testing complete!"