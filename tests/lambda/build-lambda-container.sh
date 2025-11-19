#!/bin/bash
set -e

echo "🏗️  Building HoneyHive Lambda Test Container"
echo "==========================================="

# Build from the project root to include the full context
cd ../../

echo "📦 Building container with full SDK context..."
docker build -f tests/lambda/Dockerfile.lambda-complete \
  -t honeyhive-lambda:latest \
  -t honeyhive-lambda:test \
  .

echo "✅ Container built successfully!"
echo ""
echo "🧪 Available test commands:"
echo "  docker run --rm -p 9000:8080 honeyhive-lambda:test basic_tracing.lambda_handler"
echo "  docker run --rm -p 9001:8080 honeyhive-lambda:test cold_start_test.lambda_handler"
echo "  docker run --rm -p 9002:8080 honeyhive-lambda:test simple_test.lambda_handler"
echo ""
echo "📋 To test:"
echo "  curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"test\": \"container_build\", \"message\": \"hello from custom container\"}'"
