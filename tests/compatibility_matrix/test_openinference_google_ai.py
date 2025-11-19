#!/usr/bin/env python3
"""
Google Generative AI Compatibility Test for HoneyHive SDK

Tests Google Generative AI (Gemini) integration using OpenInference instrumentation
with HoneyHive's "Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_google_genai_integration():
    """Test Google Generative AI integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not all([api_key, project, google_api_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - GOOGLE_API_KEY (Google AI Studio API key)")
        return False

    try:
        # Import dependencies
        import google.generativeai as genai
        from openinference.instrumentation.google_generativeai import (
            GoogleGenerativeAIInstrumentor,
        )

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Google Generative AI with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        google_instrumentor = GoogleGenerativeAIInstrumentor()
        print("✓ Google Generative AI instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[google_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Google Generative AI instrumentor")

        # 3. Configure Google Generative AI
        genai.configure(api_key=google_api_key)
        print("✓ Google Generative AI configured")

        # 4. Test Gemini Pro model (automatically traced)
        print("🚀 Testing Google Gemini Pro model...")
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(
            "Say hello and confirm this is a compatibility test for HoneyHive + Google Generative AI integration.",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=100, temperature=0.1
            ),
        )

        result_text = response.text
        print(f"✓ Gemini Pro response: {result_text}")

        # 5. Test with chat session
        print("🔧 Testing Gemini chat session...")

        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "google_genai"},
            outputs={"model_used": "gemini-pro"},
        ) as span:
            chat = model.start_chat(history=[])

            chat_response = chat.send_message(
                "What is 2+2? Answer briefly.",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=50, temperature=0.1
                ),
            )

            span_data = {
                "chat_history_length": len(chat.history),
                "response": chat_response.text,
                "model": "gemini-pro",
            }
            print(f"✓ Chat response: {chat_response.text}")

        # 6. Test Gemini Vision (if available)
        print("🔧 Testing Gemini Vision capabilities...")

        try:
            vision_model = genai.GenerativeModel("gemini-pro-vision")

            with tracer.enrich_span(
                metadata={"test_type": "vision", "provider": "google_genai"},
            ) as span:
                # Test with text-only prompt (vision model can handle text)
                vision_response = vision_model.generate_content(
                    "Describe the concept of artificial intelligence in one sentence.",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=50, temperature=0.1
                    ),
                )

                span_data = {
                    "model": "gemini-pro-vision",
                    "response": vision_response.text,
                    "input_type": "text_only",
                }
                print(f"✓ Vision model response: {vision_response.text}")

        except Exception as e:
            print(f"⚠️  Vision model not available or error: {e}")

        # 7. Test with safety settings
        print("🔧 Testing with safety settings...")

        with tracer.enrich_span(
            metadata={"test_type": "safety", "provider": "google_genai"},
        ) as span:
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ]

            safe_response = model.generate_content(
                "Write a positive message about technology.",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=50, temperature=0.1
                ),
                safety_settings=safety_settings,
            )

            span_data = {
                "safety_settings_count": len(safety_settings),
                "response": safe_response.text,
            }
            print(f"✓ Safe response: {safe_response.text}")

        # 8. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Google Generative AI integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-google-generativeai")
        print("   pip install google-generativeai")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Google Generative AI compatibility test."""
    print("🧪 HoneyHive + Google Generative AI Compatibility Test")
    print("=" * 50)

    success = test_google_genai_integration()

    if success:
        print("\n✅ Google Generative AI compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Google Generative AI compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
