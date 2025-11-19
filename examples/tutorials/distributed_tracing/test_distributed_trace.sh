#!/bin/bash
# Test script for distributed tracing tutorial

set -e

echo "🧪 Testing Distributed Tracing Example"
echo "======================================"
echo ""

# Check if services are running
echo "1️⃣  Checking if services are running..."
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "❌ API Gateway not running on port 5000"
    exit 1
fi

if ! curl -s http://localhost:5001/health > /dev/null; then
    echo "❌ User Service not running on port 5001"
    exit 1
fi

if ! curl -s http://localhost:5002/health > /dev/null; then
    echo "❌ LLM Service not running on port 5002"
    exit 1
fi

echo "✅ All services are running"
echo ""

# Test with valid user
echo "2️⃣  Testing with valid user (user_123)..."
response=$(curl -s -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "query": "Explain distributed tracing in one sentence"}')

if echo "$response" | grep -q "response"; then
    echo "✅ Valid user request succeeded"
    echo "Response: $response" | head -c 100
    echo "..."
else
    echo "❌ Valid user request failed"
    echo "Response: $response"
    exit 1
fi
echo ""

# Test with invalid user
echo "3️⃣  Testing with invalid user (invalid_123)..."
response=$(curl -s -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": "invalid_123", "query": "This should fail"}')

if echo "$response" | grep -q "Invalid user"; then
    echo "✅ Invalid user request correctly rejected"
else
    echo "❌ Invalid user should have been rejected"
    echo "Response: $response"
    exit 1
fi
echo ""

echo "======================================"
echo "✅ All tests passed!"
echo ""
echo "📊 View your distributed traces at:"
echo "   https://app.honeyhive.ai/projects/distributed-tracing-tutorial/traces"
echo ""

