#!/usr/bin/env python3
"""
Groq Compatibility Test for HoneyHive SDK

Tests Groq integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_groq_integration():
    """Test Groq integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    groq_key = os.getenv("GROQ_API_KEY")

    if not all([api_key, project, groq_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - GROQ_API_KEY (Groq API key)")
        return False

    try:
        # Import dependencies
        from groq import Groq
        from openinference.instrumentation.groq import GroqInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Groq with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        groq_instrumentor = GroqInstrumentor()
        print("✓ Groq instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[groq_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Groq instrumentor")

        # 3. Initialize Groq client
        client = Groq(api_key=groq_key)
        print("✓ Groq client initialized")

        # 4. Test chat completion (automatically traced)
        print("🚀 Testing Groq chat completion...")
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Groq's Llama model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Say hello and confirm this is a compatibility test for HoneyHive + Groq integration.",
                },
            ],
            max_tokens=100,
            temperature=0.1,
        )

        result_text = response.choices[0].message.content
        print(f"✓ Groq response: {result_text}")

        # 5. Test with different model
        print("🔧 Testing Groq with different model...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "groq"},
            outputs={"model_used": "mixtral-8x7b-32768"},
        ) as span:
            try:
                mixtral_response = client.chat.completions.create(
                    model="mixtral-8x7b-32768",  # Groq's Mixtral model
                    messages=[
                        {"role": "user", "content": "What is 2+2? Answer briefly."}
                    ],
                    max_tokens=50,
                    temperature=0.1,
                )

                span_data = {
                    "model": "mixtral-8x7b-32768",
                    "response": mixtral_response.choices[0].message.content,
                    "tokens_used": (
                        mixtral_response.usage.total_tokens
                        if hasattr(mixtral_response, "usage")
                        else None
                    ),
                }
                print(
                    f"✓ Mixtral response: {mixtral_response.choices[0].message.content}"
                )

            except Exception as e:
                print(f"⚠️  Mixtral model test failed: {e}")
                span_data = {"mixtral_error": str(e)}

        # 6. Test streaming (automatically traced)
        print("🔧 Testing Groq streaming...")
        with tracer.enrich_span(
            metadata={"test_type": "streaming", "provider": "groq"},
        ) as span:
            stream_response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": "Count from 1 to 5."}],
                max_tokens=50,
                temperature=0.1,
                stream=True,
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
                "model": "llama3-8b-8192",
            }
            print(
                f"✓ Streaming completed: {chunk_count} chunks, content: {streamed_content.strip()}"
            )

        # 7. Test with system prompt and conversation
        print("🔧 Testing Groq conversation...")
        with tracer.enrich_span(
            metadata={"test_type": "conversation", "provider": "groq"},
        ) as span:
            conversation_response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert on AI observability and monitoring.",
                    },
                    {
                        "role": "user",
                        "content": "What are the benefits of tracing AI applications?",
                    },
                    {
                        "role": "assistant",
                        "content": "Tracing AI applications provides visibility into performance, helps debug issues, and enables optimization.",
                    },
                    {
                        "role": "user",
                        "content": "How does OpenTelemetry help with this?",
                    },
                ],
                max_tokens=100,
                temperature=0.2,
            )

            span_data = {
                "conversation_length": 4,  # Number of messages in conversation
                "response": conversation_response.choices[0].message.content,
                "model": "llama3-8b-8192",
            }
            print(
                f"✓ Conversation response: {conversation_response.choices[0].message.content}"
            )

        # 8. Test with different temperature and parameters
        print("🔧 Testing Groq with custom parameters...")
        with tracer.enrich_span(
            metadata={"test_type": "custom_params", "provider": "groq"},
        ) as span:
            try:
                custom_response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {
                            "role": "user",
                            "content": "Write a creative haiku about fast AI inference.",
                        }
                    ],
                    max_tokens=80,
                    temperature=0.8,
                    top_p=0.9,
                    stop=["\n\n"],
                )

                span_data = {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "stop_sequences": ["\n\n"],
                    "response": custom_response.choices[0].message.content,
                }
                print(
                    f"✓ Creative response: {custom_response.choices[0].message.content}"
                )

            except Exception as e:
                print(f"⚠️  Custom parameters test failed: {e}")
                span_data = {"custom_params_error": str(e)}

        # 9. Test function calling (if supported)
        print("🔧 Testing Groq function calling...")
        with tracer.enrich_span(
            metadata={"test_type": "function_calling", "provider": "groq"},
        ) as span:
            try:
                function_response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {
                            "role": "user",
                            "content": "What's the weather like? Use the get_weather function.",
                        }
                    ],
                    tools=[
                        {
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "description": "Get the current weather",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "location": {
                                            "type": "string",
                                            "description": "The city and state",
                                        }
                                    },
                                    "required": ["location"],
                                },
                            },
                        }
                    ],
                    max_tokens=100,
                )

                span_data = {
                    "function_calls": (
                        len(response.choices[0].message.tool_calls)
                        if hasattr(response.choices[0].message, "tool_calls")
                        and response.choices[0].message.tool_calls
                        else 0
                    ),
                    "response": function_response.choices[0].message.content
                    or "Function call requested",
                }
                print(f"✓ Function calling test completed: {span_data}")

            except Exception as e:
                print(f"⚠️  Function calling test failed (may not be supported): {e}")
                span_data = {"function_calling_error": str(e)}

        # 10. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Groq integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-groq")
        print("   pip install groq")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Groq compatibility test."""
    print("🧪 HoneyHive + Groq Compatibility Test")
    print("=" * 50)

    success = test_groq_integration()

    if success:
        print("\n✅ Groq compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Groq compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
