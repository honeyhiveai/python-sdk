.PHONY: help test test-lambda test-cold-start clean setup build

# Default target
help:
	@echo "HoneyHive SDK Lambda Testing"
	@echo ""
	@echo "Available targets:"
	@echo "  setup           - Install dependencies for Lambda testing"
	@echo "  build           - Build Lambda test containers"
	@echo "  test            - Run all Lambda compatibility tests"
	@echo "  test-lambda     - Run basic Lambda tests"
	@echo "  test-cold-start - Run cold start specific tests"
	@echo "  test-performance- Run performance tests"
	@echo "  validate        - Validate all Lambda containers and functions"
	@echo "  start-containers- Start Lambda containers for testing"
	@echo "  stop-containers - Stop Lambda containers"
	@echo "  clean           - Clean up containers and images"

# Setup dependencies
setup:
	@echo "📦 Installing Lambda testing dependencies..."
	pip install docker requests pytest pytest-asyncio

# Build containers
build:
	@echo "🐳 Building Lambda test containers..."
	@echo "Building native bundle container..."
	cd ../../ && docker build -f tests/lambda/Dockerfile.bundle-builder -t honeyhive-lambda:bundle-native .

# Run all Lambda tests
test: build test-lambda test-cold-start test-performance

# Run basic Lambda compatibility tests
test-lambda:
	@echo "🧪 Running Lambda compatibility tests..."
	python -m pytest test_lambda_compatibility.py::TestLambdaCompatibility -v --override-ini="addopts="

# Run cold start tests
test-cold-start:
	@echo "❄️ Running cold start tests..."
	python -m pytest test_lambda_compatibility.py::TestLambdaColdStarts -v --override-ini="addopts="

# Run performance tests
test-performance:
	@echo "⚡ Running Lambda performance tests..."
	python -m pytest test_lambda_performance.py -v --override-ini="addopts="

# Start containers for manual testing
start-containers:
	@echo "🚀 Starting Lambda containers..."
	docker-compose -f docker-compose.lambda.yml up -d
	@echo "Containers started. Access them at:"
	@echo "  Python 3.11: http://localhost:9000"
	@echo "  Python 3.12: http://localhost:9001"
	@echo "  Cold Start:  http://localhost:9002"
	@echo "  Memory Test: http://localhost:9003"

# Stop containers
stop-containers:
	@echo "🛑 Stopping Lambda containers..."
	docker-compose -f docker-compose.lambda.yml down

# Clean up
clean:
	@echo "🧹 Cleaning up Lambda test environment..."
	docker-compose -f docker-compose.lambda.yml down --rmi all --volumes
	docker system prune -f

# Test with real AWS Lambda (requires AWS credentials)
test-real-lambda:
	@echo "☁️ Testing with real AWS Lambda..."
	@echo "Note: This requires AWS credentials and will deploy actual Lambda functions"
	@echo "Run: make deploy-lambda && make test-deployed-lambda && make cleanup-lambda"

# Quick test - start containers and run basic test
quick-test:
	@echo "⚡ Running quick Lambda test..."
	docker-compose -f docker-compose.lambda.yml up -d lambda-python311
	sleep 5
	curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
		-H "Content-Type: application/json" \
		-d '{"test_type": "quick", "data": {"message": "hello"}}'
	docker-compose -f docker-compose.lambda.yml down

# Interactive shell for debugging
debug-shell:
	@echo "🐛 Starting debug shell in Lambda container..."
	docker run -it --rm \
		-v $(PWD)/lambda_functions:/var/task \
		-v $(PWD)/../../src:/var/task/honeyhive \
		public.ecr.aws/lambda/python:3.11 \
		/bin/bash

# Custom Container Build Targets
build-container:
	@echo "🏗️  Building custom Lambda container..."
	./build-lambda-container.sh

test-container: build-container
	@echo "🧪 Testing custom Lambda container..."
	./test-lambda-container.sh

# Quick container test
quick-container-test:
	@echo "⚡ Quick container test..."
	docker run --rm -p 9020:8080 \
		-e AWS_LAMBDA_FUNCTION_NAME=honeyhive-quick-test \
		-e HH_API_KEY=test-key \
		honeyhive-lambda:test simple_test.lambda_handler &
	sleep 8
	curl -X POST http://localhost:9020/2015-03-31/functions/function/invocations \
		-H "Content-Type: application/json" \
		-d '{"test": "quick", "message": "container works!"}' \
		--max-time 10
	docker ps -q --filter "publish=9020" | xargs -r docker stop

# Validate containers and functions
validate:
	@echo "🔍 Validating Lambda containers and functions..."
	python validate-containers.py

# Clean up containers
clean-containers:
	@echo "🧹 Cleaning up Lambda containers..."
	docker images | grep honeyhive-lambda | awk '{print $$3}' | xargs -r docker rmi
	docker system prune -f

# Production-like build (would use PyPI in real production)
build-production-container:
	@echo "🚀 Building production-like container..."
	docker build -f Dockerfile.lambda-production -t honeyhive-lambda:production .
