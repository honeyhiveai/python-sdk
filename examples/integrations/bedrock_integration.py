#!/usr/bin/env python3
"""
AWS Bedrock Integration Example with HoneyHive

This example demonstrates how to integrate AWS Bedrock (Nova, Titan, Claude) with
HoneyHive using the OpenInference Bedrock instrumentor for comprehensive observability.

Requirements:
    pip install honeyhive boto3 openinference-instrumentation-bedrock

Environment Variables:
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    AWS_ACCESS_KEY_ID: Your AWS access key
    AWS_SECRET_ACCESS_KEY: Your AWS secret key
    AWS_SESSION_TOKEN: Your AWS session token (optional, for temporary credentials)
    AWS_REGION: AWS region (default: us-east-1)
    
Alternative: Use AWS CLI default profile or IAM role (credentials auto-detected)
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any


async def main():
    """Main example demonstrating AWS Bedrock integration with HoneyHive."""

    # Check required environment variables
    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # Optional for temporary credentials
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not all([hh_api_key, hh_project]):
        print("❌ Missing required HoneyHive environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("\nSet these environment variables and try again.")
        return False
    
    # Check AWS credentials (will fall back to boto3 default credential chain)
    if not aws_access_key or not aws_secret_key:
        print("⚠️  AWS credentials not found in environment variables.")
        print("   Will use boto3 default credential chain (AWS CLI profile, IAM role, etc.)")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to use explicit credentials.")
        print()
    
    if aws_session_token:
        print("✓ AWS session token detected - using temporary credentials")

    try:
        # Import required packages
        import boto3
        from openinference.instrumentation.bedrock import BedrockInstrumentor
        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.instrumentation.decorators import trace

        print("🚀 AWS Bedrock + HoneyHive Integration Example")
        print("=" * 50)

        # 1. Initialize the Bedrock instrumentor
        print("🔧 Setting up Bedrock instrumentor...")
        bedrock_instrumentor = BedrockInstrumentor()
        print("✓ Bedrock instrumentor initialized")

        # 2. Initialize HoneyHive tracer
        print("🔧 Setting up HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=hh_api_key,
            project=hh_project,
            session_name=Path(__file__).stem,  # Use filename as session name
            source="bedrock_example"
        )
        print("✓ HoneyHive tracer initialized")

        # Instrument Bedrock with tracer provider
        bedrock_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ HoneyHive tracer initialized with Bedrock instrumentor")

        # 3. Create Bedrock Runtime client
        print(f"✓ AWS region configured: {aws_region}")
        
        # Build client kwargs based on available credentials
        client_kwargs = {"region_name": aws_region}
        
        # If explicit credentials are provided, use them
        if aws_access_key and aws_secret_key:
            client_kwargs["aws_access_key_id"] = aws_access_key
            client_kwargs["aws_secret_access_key"] = aws_secret_key
            
            # Add session token if provided (for temporary credentials)
            if aws_session_token:
                client_kwargs["aws_session_token"] = aws_session_token
                print("✓ Using temporary credentials with session token")
            else:
                print("✓ Using long-term credentials")
        else:
            # Fall back to boto3's default credential chain
            print("✓ Using boto3 default credential chain")
        
        bedrock_client = boto3.client("bedrock-runtime", **client_kwargs)

        # 4. Test Amazon Nova models
        print("\n🌟 Testing Amazon Nova Lite...")
        result1 = await test_amazon_nova(tracer, bedrock_client)
        print(f"✓ Nova test completed: {result1[:100]}...")

        # 5. Test Amazon Titan models
        print("\n📝 Testing Amazon Titan Text...")
        result2 = await test_amazon_titan(tracer, bedrock_client)
        print(f"✓ Titan test completed: {result2[:100]}...")

        # 6. Test Anthropic Claude models
        print("\n🤖 Testing Anthropic Claude...")
        result3 = await test_anthropic_claude(tracer, bedrock_client)
        print(f"✓ Claude test completed: {result3[:100]}...")

        # 7. Test Converse API (unified interface)
        print("\n💬 Testing Converse API...")
        result4 = await test_converse_api(tracer, bedrock_client)
        print(f"✓ Converse API test completed: {result4[:100]}...")

        # 8. Test streaming responses
        print("\n🌊 Testing streaming responses...")
        chunk_count = await test_streaming_response(tracer, bedrock_client)
        print(f"✓ Streaming test completed: {chunk_count} chunks received")

        # 9. Test multi-turn conversation
        print("\n🔄 Testing multi-turn conversation...")
        result6 = await test_multi_turn_conversation(tracer, bedrock_client)
        print(f"✓ Multi-turn test completed: {len(result6)} messages")

        # 10. Test document understanding
        print("\n📄 Testing document understanding...")
        result7 = await test_document_understanding(tracer, bedrock_client)
        print(f"✓ Document understanding completed: {result7[:100]}...")

        # 11. Test native API with streaming
        print("\n⚡ Testing native API with streaming...")
        chunk_count2 = await test_native_streaming(tracer, bedrock_client)
        print(f"✓ Native streaming completed: {chunk_count2} chunks received")

        # 12. Clean up instrumentor
        print("\n🧹 Cleaning up...")
        bedrock_instrumentor.uninstrument()
        print("✓ Instrumentor cleaned up")

        print("\n🎉 AWS Bedrock integration example completed successfully!")
        print(f"📊 Check your HoneyHive project '{hh_project}' for trace data")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install honeyhive boto3 openinference-instrumentation-bedrock")
        return False

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_amazon_nova(tracer: "HoneyHiveTracer", client) -> str:
    """Test 1: Amazon Nova Lite model for text generation."""

    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_amazon_nova", tracer=tracer)
    def _test():
        # Use Amazon Nova Lite model
        model_id = "amazon.nova-lite-v1:0"

        # Create the request using the Converse API
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Explain quantum computing in one sentence."}]
                }
            ],
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        )

        # Extract response text
        return response["output"]["message"]["content"][0]["text"]
    
    # Run synchronously in async context
    return await asyncio.to_thread(_test)


async def test_amazon_titan(tracer: "HoneyHiveTracer", client) -> str:
    """Test 2: Amazon Titan Text model for text generation."""

    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_amazon_titan", tracer=tracer)
    def _test():
        # Use Amazon Titan Text model
        model_id = "amazon.titan-text-express-v1"

        # Format the request using Titan's native structure
        native_request = {
            "inputText": "What is the purpose of a 'hello world' program?",
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.7,
                "topP": 0.9,
            }
        }

        # Convert to JSON and invoke
        request = json.dumps(native_request)
        response = client.invoke_model(modelId=model_id, body=request)

        # Decode and extract response
        model_response = json.loads(response["body"].read())
        return model_response["results"][0]["outputText"]
    
    return await asyncio.to_thread(_test)


async def test_anthropic_claude(tracer: "HoneyHiveTracer", client) -> str:
    """Test 3: Anthropic Claude model for text generation."""

    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_anthropic_claude", tracer=tracer)
    def _test():
        # Use Claude 3 Haiku model
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        # Use the Converse API for Claude
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Explain machine learning in simple terms."}]
                }
            ],
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.5,
                "topP": 0.9
            }
        )

        # Extract response text
        return response["output"]["message"]["content"][0]["text"]
    
    return await asyncio.to_thread(_test)


async def test_converse_api(tracer: "HoneyHiveTracer", client) -> str:
    """Test 4: Converse API - unified interface for all models."""

    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_converse_api", tracer=tracer)
    def _test():
        # Using Claude with Converse API
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

        # Create conversation with system prompt
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Write a haiku about artificial intelligence."}]
                }
            ],
            system=[{"text": "You are a creative poet who writes concise, meaningful poetry."}],
            inferenceConfig={
                "maxTokens": 200,
                "temperature": 0.8
            }
        )

        return response["output"]["message"]["content"][0]["text"]
    
    return await asyncio.to_thread(_test)


async def test_streaming_response(tracer: "HoneyHiveTracer", client) -> int:
    """Test 5: Streaming responses with Converse Stream API."""

    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_streaming_response", tracer=tracer)
    def _test():
        # Use Claude with streaming
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        # Create streaming response
        streaming_response = client.converse_stream(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Tell me a short story about a robot."}]
                }
            ],
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.7
            }
        )

        # Process stream and count chunks
        chunk_count = 0
        full_text = ""
        
        for chunk in streaming_response["stream"]:
            if "contentBlockDelta" in chunk:
                text = chunk["contentBlockDelta"]["delta"]["text"]
                full_text += text
                chunk_count += 1
                print(text, end="", flush=True)
        
        print()  # New line after streaming
        return chunk_count
    
    return await asyncio.to_thread(_test)


async def test_multi_turn_conversation(tracer: "HoneyHiveTracer", client) -> list:
    """Test 6: Multi-turn conversation maintaining context."""

    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_multi_turn_conversation", tracer=tracer)
    def _test():
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        # Build conversation history
        conversation = []
        
        # Turn 1: Initial question
        conversation.append({
            "role": "user",
            "content": [{"text": "What are the three primary colors?"}]
        })
        
        response1 = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 300, "temperature": 0.5}
        )
        
        assistant_response1 = response1["output"]["message"]["content"][0]["text"]
        conversation.append({
            "role": "assistant",
            "content": [{"text": assistant_response1}]
        })
        
        # Turn 2: Follow-up question
        conversation.append({
            "role": "user",
            "content": [{"text": "Can you mix them to create other colors?"}]
        })
        
        response2 = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 300, "temperature": 0.5}
        )
        
        assistant_response2 = response2["output"]["message"]["content"][0]["text"]
        conversation.append({
            "role": "assistant",
            "content": [{"text": assistant_response2}]
        })
        
        # Turn 3: Final question
        conversation.append({
            "role": "user",
            "content": [{"text": "Give me an example."}]
        })
        
        response3 = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 300, "temperature": 0.5}
        )
        
        assistant_response3 = response3["output"]["message"]["content"][0]["text"]
        
        print(f"\n  Turn 1 Response: {assistant_response1[:50]}...")
        print(f"  Turn 2 Response: {assistant_response2[:50]}...")
        print(f"  Turn 3 Response: {assistant_response3[:50]}...")
        
        return conversation
    
    return await asyncio.to_thread(_test)


async def test_document_understanding(tracer: "HoneyHiveTracer", client) -> str:
    """Test 7: Document understanding with Converse API."""

    from honeyhive.tracer.instrumentation.decorators import trace
    import base64

    @trace(event_type="chain", event_name="test_document_understanding", tracer=tracer)
    def _test():
        # Use Claude for document understanding
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        # Create a simple text document (in a real scenario, you'd load a PDF/DOC)
        # For this example, we'll use inline text to avoid file dependencies
        document_text = """
# Amazon Nova Service Overview

Amazon Nova is a new generation of foundation models that deliver frontier intelligence and industry-leading price performance.

## Key Features:
- High-quality text understanding and generation
- Multi-modal capabilities (text, images, video)
- Optimized for cost-effectiveness
- Available in multiple sizes: Micro, Lite, Pro, and Premier

## Use Cases:
- Content generation
- Document analysis
- Code generation
- Conversational AI
"""

        # Create conversation with document
        conversation = [
            {
                "role": "user",
                "content": [
                    {"text": "Briefly summarize the key features of Amazon Nova described in this document."},
                    {
                        "document": {
                            "format": "txt",
                            "name": "Amazon Nova Overview",
                            "source": {"bytes": document_text.encode('utf-8')},
                        }
                    },
                ],
            }
        ]

        # Send the message with document
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 500, "temperature": 0.3},
        )

        # Extract response text
        return response["output"]["message"]["content"][0]["text"]
    
    return await asyncio.to_thread(_test)


async def test_native_streaming(tracer: "HoneyHiveTracer", client) -> int:
    """Test 8: Native invoke model API with streaming (not Converse API)."""

    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_native_streaming", tracer=tracer)
    def _test():
        # Use Claude with native API for streaming
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        # Define the prompt
        prompt = "Write a short poem about technology in 4 lines."

        # Format the request using Claude's native structure
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }

        # Convert to JSON and invoke with streaming
        request = json.dumps(native_request)
        streaming_response = client.invoke_model_with_response_stream(
            modelId=model_id, body=request
        )

        # Extract and print the response text in real-time
        chunk_count = 0
        full_text = ""
        
        print("   Streaming response: ", end="", flush=True)
        for event in streaming_response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                text = chunk["delta"].get("text", "")
                if text:
                    full_text += text
                    chunk_count += 1
                    print(text, end="", flush=True)
        
        print()  # New line after streaming
        return chunk_count
    
    return await asyncio.to_thread(_test)


if __name__ == "__main__":
    """Run the AWS Bedrock integration example."""
    success = asyncio.run(main())

    if success:
        print("\n✅ Example completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Example failed!")
        sys.exit(1)

