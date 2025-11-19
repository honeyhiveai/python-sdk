"""
HoneyHive Google AI Integration with OpenLLMetry (Traceloop) - WITH WORKAROUND

This example demonstrates how to use Google AI with OpenLLMetry instrumentation
in HoneyHive, including a workaround for the upstream import issue.

WORKAROUND INCLUDED: This example includes a workaround for the upstream bug
in opentelemetry-instrumentation-google-generativeai where the package uses
the wrong import path for Google GenerativeAI types.

Requirements:
- pip install honeyhive[traceloop-google-ai]
- Set GEMINI_API_KEY environment variable
- Set HH_API_KEY and HH_PROJECT environment variables
"""

import os
import sys
import types


def setup_google_genai_workaround():
    """
    Workaround for upstream bug in opentelemetry-instrumentation-google-generativeai

    The package incorrectly imports 'from google.genai.types' instead of
    'from google.generativeai.types'. This function creates a monkey-patch
    to make the import work.
    """
    try:
        import google.generativeai.types as real_types

        # Create fake google.genai module structure
        genai_module = types.ModuleType("google.genai")
        genai_module.types = real_types

        # Create fake google.genai.types module
        genai_types_module = types.ModuleType("google.genai.types")
        for attr in dir(real_types):
            setattr(genai_types_module, attr, getattr(real_types, attr))

        # Register in sys.modules
        sys.modules["google.genai"] = genai_module
        sys.modules["google.genai.types"] = genai_types_module

        print("✅ Google GenAI workaround applied successfully")
        return True

    except ImportError as e:
        print(f"❌ Failed to apply workaround: {e}")
        return False


def main():
    # Check required environment variables
    required_vars = ["GEMINI_API_KEY", "HH_API_KEY", "HH_PROJECT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the example:")
        for var in missing_vars:
            print(f"  export {var}=your_key_here")
        return

    print("🔧 Setting up Google AI with OpenLLMetry integration...")

    # Apply the workaround BEFORE importing the instrumentor
    if not setup_google_genai_workaround():
        print("❌ Workaround failed, cannot proceed")
        return

    try:
        # Import HoneyHive tracer
        from honeyhive import HoneyHiveTracer

        # Import the instrumentor (note: GoogleGenerativeAiInstrumentor, not GoogleGenerativeAIInstrumentor)
        from opentelemetry.instrumentation.google_generativeai import (
            GoogleGenerativeAiInstrumentor,
        )

        # Import Google AI
        import google.generativeai as genai

        print("✅ All imports successful!")

        # Initialize instrumentor
        print("🔧 Initializing Google AI instrumentor...")
        google_ai_instrumentor = GoogleGenerativeAiInstrumentor()
        google_ai_instrumentor.instrument()
        print("✅ Google AI instrumentation active")

        # Initialize HoneyHive tracer with the instrumentor
        print("🔧 Initializing HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY"),
            project=os.getenv("HH_PROJECT"),
            source="traceloop_example_with_workaround",
        )
        print("✓ HoneyHive tracer initialized")

        # Initialize instrumentor separately with tracer_provider
        google_ai_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✅ HoneyHive tracer initialized")

        # Configure Google AI
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Test with a simple generation
        print("🤖 Testing Google AI generation...")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            "Hello from OpenLLMetry Google AI with workaround!"
        )

        print(f"✅ Response received: {response.text}")

        # Test span enrichment
        print("🔧 Testing span enrichment...")
        try:
            with tracer.enrich_span(
                metadata={
                    "test_type": "traceloop_compatibility_with_workaround",
                    "provider": "google_ai",
                    "instrumentor": "opentelemetry_google_generativeai",
                    "workaround_applied": True,
                },
                outputs={"model_used": "gemini-1.5-flash"},
            ) as span:
                response2 = model.generate_content("What is 2+2? Answer briefly.")
                span_data = {
                    "response_length": len(response2.text),
                    "prompt": "What is 2+2? Answer briefly.",
                }
                print(f"✅ Enriched span created: {span_data}")
        except Exception as enrich_error:
            print(f"⚠️ Span enrichment test skipped: {enrich_error}")

        # Flush traces
        print("📤 Flushing traces...")
        tracer.force_flush()
        print("✅ Traces flushed successfully")

        print("\n🎉 Google AI + OpenLLMetry integration test completed successfully!")
        print("📝 Check your HoneyHive project dashboard for the traces")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
