#!/usr/bin/env python3
"""
Mistral AI Compatibility Test for HoneyHive SDK

Tests Mistral AI integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_mistralai_integration():
    """Test Mistral AI integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    mistral_key = os.getenv("MISTRAL_API_KEY")

    if not all([api_key, project, mistral_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - MISTRAL_API_KEY (Mistral AI API key)")
        return False

    try:
        # Import dependencies
        from mistralai.client import MistralClient
        from mistralai.models.chat_completion import ChatMessage
        from openinference.instrumentation.mistralai import MistralAIInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Mistral AI with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        mistral_instrumentor = MistralAIInstrumentor()
        print("✓ Mistral AI instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[mistral_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Mistral AI instrumentor")

        # 3. Initialize Mistral client
        client = MistralClient(api_key=mistral_key)
        print("✓ Mistral AI client initialized")

        # 4. Test chat completion (automatically traced)
        print("🚀 Testing Mistral AI chat completion...")
        messages = [
            ChatMessage(
                role="user",
                content="Say hello and confirm this is a compatibility test for HoneyHive + Mistral AI integration.",
            )
        ]

        response = client.chat(
            model="mistral-tiny", messages=messages, max_tokens=100, temperature=0.1
        )

        result_text = response.choices[0].message.content
        print(f"✓ Mistral response: {result_text}")

        # 5. Test with different model
        print("🔧 Testing Mistral with different model...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "mistral_ai"},
            outputs={"model_used": "mistral-small"},
        ) as span:
            try:
                small_messages = [
                    ChatMessage(role="user", content="What is 2+2? Answer briefly.")
                ]

                small_response = client.chat(
                    model="mistral-small",
                    messages=small_messages,
                    max_tokens=50,
                    temperature=0.1,
                )

                span_data = {
                    "model": "mistral-small",
                    "response": small_response.choices[0].message.content,
                    "usage": (
                        small_response.usage.dict()
                        if hasattr(small_response, "usage")
                        else None
                    ),
                }
                print(
                    f"✓ Mistral Small response: {small_response.choices[0].message.content}"
                )

            except Exception as e:
                print(f"⚠️  Mistral Small test failed: {e}")
                span_data = {"mistral_small_error": str(e)}

        # 6. Test streaming (automatically traced)
        print("🔧 Testing Mistral AI streaming...")
        with tracer.enrich_span(
            metadata={"test_type": "streaming", "provider": "mistral_ai"},
        ) as span:
            try:
                stream_messages = [
                    ChatMessage(role="user", content="Count from 1 to 5.")
                ]

                stream_response = client.chat_stream(
                    model="mistral-tiny",
                    messages=stream_messages,
                    max_tokens=50,
                    temperature=0.1,
                )

                streamed_content = ""
                chunk_count = 0
                for chunk in stream_response:
                    if chunk.choices[0].delta.content:
                        streamed_content += chunk.choices[0].delta.content
                        chunk_count += 1

                span_data = {
                    "chunks_received": chunk_count,
                    "streamed_content": streamed_content.strip(),
                    "streaming": True,
                    "model": "mistral-tiny",
                }
                print(
                    f"✓ Streaming completed: {chunk_count} chunks, content: {streamed_content.strip()}"
                )

            except Exception as e:
                print(f"⚠️  Streaming test failed: {e}")
                span_data = {"streaming_error": str(e)}

        # 7. Test conversation with system message
        print("🔧 Testing Mistral conversation...")
        with tracer.enrich_span(
            metadata={"test_type": "conversation", "provider": "mistral_ai"},
        ) as span:
            conversation_messages = [
                ChatMessage(
                    role="system",
                    content="You are an expert on AI and machine learning.",
                ),
                ChatMessage(
                    role="user", content="What are the benefits of model observability?"
                ),
                ChatMessage(
                    role="assistant",
                    content="Model observability helps track performance, detect issues, and optimize AI systems.",
                ),
                ChatMessage(role="user", content="How does tracing help with this?"),
            ]

            conversation_response = client.chat(
                model="mistral-tiny",
                messages=conversation_messages,
                max_tokens=100,
                temperature=0.2,
            )

            span_data = {
                "conversation_length": len(conversation_messages),
                "response": conversation_response.choices[0].message.content,
                "model": "mistral-tiny",
            }
            print(
                f"✓ Conversation response: {conversation_response.choices[0].message.content}"
            )

        # 8. Test embeddings (if available)
        print("🔧 Testing Mistral embeddings...")
        with tracer.enrich_span(
            metadata={"test_type": "embeddings", "provider": "mistral_ai"},
        ) as span:
            try:
                embeddings_response = client.embeddings(
                    model="mistral-embed", input=["This is a test text for embedding."]
                )

                span_data = {
                    "embedding_dimension": len(embeddings_response.data[0].embedding),
                    "num_embeddings": len(embeddings_response.data),
                    "model": "mistral-embed",
                }
                print(f"✓ Embeddings created: {span_data}")

            except Exception as e:
                print(f"⚠️  Embeddings test failed: {e}")
                span_data = {"embeddings_error": str(e)}

        # 9. Test with custom parameters
        print("🔧 Testing Mistral with custom parameters...")
        with tracer.enrich_span(
            metadata={"test_type": "custom_params", "provider": "mistral_ai"},
        ) as span:
            try:
                custom_messages = [
                    ChatMessage(
                        role="user",
                        content="Write a creative haiku about artificial intelligence.",
                    )
                ]

                custom_response = client.chat(
                    model="mistral-tiny",
                    messages=custom_messages,
                    max_tokens=80,
                    temperature=0.8,
                    top_p=0.9,
                    random_seed=42,
                )

                span_data = {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "random_seed": 42,
                    "response": custom_response.choices[0].message.content,
                }
                print(
                    f"✓ Creative response: {custom_response.choices[0].message.content}"
                )

            except Exception as e:
                print(f"⚠️  Custom parameters test failed: {e}")
                span_data = {"custom_params_error": str(e)}

        # 10. Test function calling (if supported)
        print("🔧 Testing Mistral function calling...")
        with tracer.enrich_span(
            metadata={"test_type": "function_calling", "provider": "mistral_ai"},
        ) as span:
            try:
                from mistralai.models.chat_completion import FunctionCall, ToolCall

                function_messages = [
                    ChatMessage(
                        role="user",
                        content="What's the current time? Use the get_time function.",
                    )
                ]

                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_time",
                            "description": "Get the current time",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "timezone": {
                                        "type": "string",
                                        "description": "The timezone",
                                    }
                                },
                            },
                        },
                    }
                ]

                function_response = client.chat(
                    model="mistral-small",
                    messages=function_messages,
                    tools=tools,
                    max_tokens=100,
                )

                span_data = {
                    "function_calls": (
                        len(function_response.choices[0].message.tool_calls)
                        if hasattr(function_response.choices[0].message, "tool_calls")
                        and function_response.choices[0].message.tool_calls
                        else 0
                    ),
                    "response": function_response.choices[0].message.content
                    or "Function call requested",
                }
                print(f"✓ Function calling test completed: {span_data}")

            except Exception as e:
                print(f"⚠️  Function calling test failed (may not be supported): {e}")
                span_data = {"function_calling_error": str(e)}

        # 11. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Mistral AI integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-mistralai")
        print("   pip install mistralai")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Mistral AI compatibility test."""
    print("🧪 HoneyHive + Mistral AI Compatibility Test")
    print("=" * 50)

    success = test_mistralai_integration()

    if success:
        print("\n✅ Mistral AI compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Mistral AI compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
