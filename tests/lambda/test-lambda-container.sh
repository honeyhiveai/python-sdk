#!/bin/bash
set -e

echo "🧪 Testing HoneyHive Lambda Container"
echo "==================================="

# Function to test a Lambda handler
test_lambda_handler() {
    local handler=$1
    local port=$2
    local test_name=$3
    local test_payload=$4
    
    echo "🚀 Testing $test_name..."
    
    # Start container in background
    docker run --rm -p $port:8080 \
        -e AWS_LAMBDA_FUNCTION_NAME=honeyhive-$test_name \
        -e HH_API_KEY=test-key \
        -e HH_PROJECT=lambda-container-test \
        honeyhive-lambda:test $handler &
    
    local container_pid=$!
    
    # Wait for container to start
    sleep 8
    
    # Test the Lambda function
    local response=$(curl -s -X POST http://localhost:$port/2015-03-31/functions/function/invocations \
        -H "Content-Type: application/json" \
        -d "$test_payload" \
        --max-time 20)
    
    # Stop container
    docker ps -q --filter "publish=$port" | xargs -r docker stop > /dev/null 2>&1
    
    # Check response
    if echo "$response" | grep -q '"statusCode": 200'; then
        echo "✅ $test_name: SUCCESS"
        echo "   Response: $(echo "$response" | jq -r '.body | fromjson | .message // .error' 2>/dev/null || echo "$response")"
    else
        echo "❌ $test_name: FAILED"
        echo "   Response: $response"
    fi
    
    echo ""
}

# Test different Lambda handlers
test_lambda_handler "simple_test.lambda_handler" 9010 "simple-test" \
    '{"test": "container", "message": "simple test"}'

test_lambda_handler "basic_tracing.lambda_handler" 9011 "basic-tracing" \
    '{"test": "container", "data": {"message": "tracing test"}}'

test_lambda_handler "cold_start_test.lambda_handler" 9012 "cold-start" \
    '{"test": "container", "iteration": 1}'

echo "🎯 Container testing completed!"
