#!/usr/bin/env python3
"""
OpenInference Integration Example

This example demonstrates how to integrate OpenInference with HoneyHive
using the modern HoneyHiveTracer.init() initialization pattern.

The HoneyHiveTracer provides seamless integration with OpenInference instrumentors
for automatic tracing of complex LLM workflows.
"""

import os
import asyncio
from typing import Any, Optional
from honeyhive.tracer import HoneyHiveTracer

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_PROJECT"] = "openinference-demo"
os.environ["HH_SOURCE"] = "development"

def setup_openinference_integration(tracer: HoneyHiveTracer) -> Optional[Any]:
    """Set up OpenInference integration with the tracer."""
    try:
        # Try to import OpenInference instrumentors
        from openinference.instrumentation.openai import OpenAIInstrumentor
        
        # Set up OpenAI instrumentation
        OpenAIInstrumentor().instrument()
        print("✓ OpenAI instrumentation set up successfully")
        return OpenAIInstrumentor
        
    except ImportError:
        print("⚠️  OpenInference not available, skipping instrumentation")
        return None


def demonstrate_basic_integration(tracer: HoneyHiveTracer):
    """Demonstrate basic integration without any SDK code changes."""
    # Check if OpenAI is available
    try:
        import openai
        OPENAI_AVAILABLE = True
    except ImportError:
        OPENAI_AVAILABLE = False
        print("⚠️  OpenAI not available, skipping OpenAI examples")
        return

    if not OPENAI_AVAILABLE:
        return

    instrumentor = setup_openinference_integration(tracer)
    if not instrumentor:
        return

    try:
        print("✓ HoneyHive tracer loaded")
        print(f"✓ Project: {tracer.project}")
        print(f"✓ Source: {tracer.source}")

        # Create a custom span using our tracer
        with tracer.start_span("ai_operation") as span:
            # Add custom attributes to our span
            span.set_attribute("honeyhive.project", tracer.project)
            span.set_attribute("honeyhive.source", tracer.source)
            span.set_attribute("operation.type", "openai_chat_completion")
            span.set_attribute("integration.method", "modern_tracer")

            print("✓ Custom span created with enhanced attributes")

            # This would make an actual OpenAI call if API key is configured
            if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your-openai-key-here":
                try:
                    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": "Hello from HoneyHive + OpenInference!"}
                        ],
                        max_tokens=50
                    )
                    
                    span.set_attribute("openai.response.content", response.choices[0].message.content)
                    span.set_attribute("openai.response.tokens", response.usage.total_tokens if response.usage else 0)
                    
                    print(f"✓ OpenAI response received and traced")
                    
                except Exception as e:
                    print(f"⚠️  OpenAI call failed: {e}")
                    span.set_attribute("error.occurred", True)
                    span.set_attribute("error.message", str(e))
            else:
                print("⚠️  OpenAI API key not configured - skipping actual API call")

        print("✓ Basic integration demo completed")

    except Exception as e:
        print(f"❌ Error in basic integration: {e}")


def demonstrate_complex_workflow(tracer: HoneyHiveTracer):
    """Demonstrate a complex multi-step AI workflow with detailed tracing."""
    # Check if OpenAI is available
    try:
        import openai
        OPENAI_AVAILABLE = True
    except ImportError:
        OPENAI_AVAILABLE = False
        print("⚠️  OpenAI not available, skipping complex workflow demo")
        return

    instrumentor = setup_openinference_integration(tracer)
    if not instrumentor:
        return

    try:
        # Create a parent span for a complex operation
        with tracer.start_span("complex_ai_workflow") as parent_span:
            parent_span.set_attribute("workflow.type", "multi_step_ai_processing")
            parent_span.set_attribute("honeyhive.project", tracer.project)
            parent_span.set_attribute("honeyhive.source", tracer.source)

            print("✓ Parent span created for complex workflow")

            # Step 1: Data preprocessing
            with tracer.start_span("data_preprocessing") as prep_span:
                prep_span.set_attribute("step.number", 1)
                prep_span.set_attribute("step.type", "preprocessing")
                
                # Simulate preprocessing work
                import time
                time.sleep(0.1)
                
                prep_span.set_attribute("preprocessing.status", "completed")
                print("✓ Step 1: Data preprocessing completed")

            # Step 2: LLM calls
            if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your-openai-key-here":
                with tracer.start_span("llm_processing") as llm_span:
                    llm_span.set_attribute("step.number", 2)
                    llm_span.set_attribute("step.type", "llm_processing")
                    
                    try:
                        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                        
                        # Multiple LLM calls in sequence
                        for i in range(3):
                            with tracer.start_span(f"llm_call_{i+1}") as call_span:
                                call_span.set_attribute("call.index", i+1)
                                call_span.set_attribute("call.type", "chat_completion")
                                
                                response = client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "user", "content": f"Processing step {i+1} of 3"}
                                    ],
                                    max_tokens=30
                                )
                                
                                call_span.set_attribute("openai.response.tokens", response.usage.total_tokens if response.usage else 0)
                                print(f"✓ LLM call {i+1} completed")
                        
                        llm_span.set_attribute("llm_processing.status", "completed")
                        print("✓ Step 2: LLM processing completed")
                        
                    except Exception as e:
                        llm_span.set_attribute("error.occurred", True)
                        llm_span.set_attribute("error.message", str(e))
                        print(f"⚠️  LLM processing failed: {e}")
            else:
                print("⚠️  Step 2: LLM processing skipped (no API key)")

            # Step 3: Post-processing
            with tracer.start_span("post_processing") as post_span:
                post_span.set_attribute("step.number", 3)
                post_span.set_attribute("step.type", "post_processing")
                
                # Simulate post-processing work
                time.sleep(0.1)
                
                post_span.set_attribute("post_processing.status", "completed")
                print("✓ Step 3: Post-processing completed")

            parent_span.set_attribute("workflow.status", "completed")
            parent_span.set_attribute("workflow.steps_completed", 3)
            print("✓ Complex workflow demo completed")

    except Exception as e:
        print(f"❌ Error in complex workflow: {e}")


async def demonstrate_async_operations(tracer: HoneyHiveTracer):
    """Demonstrate async operations with OpenInference integration."""
    try:
        import openai
        OPENAI_AVAILABLE = True
    except ImportError:
        OPENAI_AVAILABLE = False
        print("⚠️  OpenAI not available, skipping async demo")
        return

    async def async_ai_operation():
        """Make an async OpenAI call that will be automatically traced."""
        try:
            # Create a span for the async operation
            with tracer.start_span("async_ai_operation") as span:
                span.set_attribute("operation.type", "async_openai_call")
                span.set_attribute("honeyhive.project", tracer.project)
                span.set_attribute("honeyhive.source", tracer.source)

                if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your-openai-key-here":
                    client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    response = await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": "Async hello from HoneyHive!"}
                        ],
                        max_tokens=30
                    )
                    
                    span.set_attribute("openai.response.tokens", response.usage.total_tokens if response.usage else 0)
                    span.set_attribute("operation.success", True)
                    print("✓ Async OpenAI call completed")
                    return response.choices[0].message.content
                else:
                    print("⚠️  Async OpenAI call skipped (no API key)")
                    span.set_attribute("operation.skipped", True)
                    return "Simulated async response"
                    
        except Exception as e:
            print(f"❌ Async operation failed: {e}")
            return None

    # Run multiple async operations concurrently
    print("🚀 Running async operations demo...")
    
    tasks = [async_ai_operation() for _ in range(3)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful_results = [r for r in results if not isinstance(r, Exception)]
    print(f"✓ Async demo completed: {len(successful_results)}/{len(results)} operations successful")


def demonstrate_error_handling(tracer: HoneyHiveTracer):
    """Demonstrate error handling and retry scenarios."""
    try:
        import openai
        OPENAI_AVAILABLE = True
    except ImportError:
        OPENAI_AVAILABLE = False
        print("⚠️  OpenAI not available, skipping error handling demo")
        return

    instrumentor = setup_openinference_integration(tracer)
    if not instrumentor:
        return

    try:
        # Simulate a retry scenario
        max_retries = 3
        current_retry = 0

        with tracer.start_span("retry_operation") as retry_span:
            retry_span.set_attribute("operation.type", "retry_with_error_handling")
            retry_span.set_attribute("max_retries", max_retries)
            retry_span.set_attribute("honeyhive.project", tracer.project)

            while current_retry < max_retries:
                with tracer.start_span(f"retry_attempt_{current_retry + 1}") as attempt_span:
                    attempt_span.set_attribute("attempt.number", current_retry + 1)
                    attempt_span.set_attribute("attempt.max_retries", max_retries)
                    
                    try:
                        # Simulate an operation that might fail
                        if current_retry < 2:  # Fail first 2 attempts
                            raise Exception(f"Simulated failure on attempt {current_retry + 1}")
                        
                        # Success on 3rd attempt
                        attempt_span.set_attribute("attempt.status", "success")
                        retry_span.set_attribute("operation.final_status", "success")
                        retry_span.set_attribute("operation.attempts_needed", current_retry + 1)
                        print(f"✓ Operation succeeded on attempt {current_retry + 1}")
                        break
                        
                    except Exception as e:
                        attempt_span.set_attribute("attempt.status", "failed")
                        attempt_span.set_attribute("error.message", str(e))
                        
                        current_retry += 1
                        if current_retry >= max_retries:
                            retry_span.set_attribute("operation.final_status", "failed")
                            retry_span.set_attribute("operation.attempts_needed", max_retries)
                            print(f"❌ Operation failed after {max_retries} attempts")
                        else:
                            print(f"⚠️  Attempt {current_retry} failed, retrying...")

        print("✓ Error handling demo completed")

    except Exception as e:
        print(f"❌ Error in error handling demo: {e}")


def main():
    """Main function demonstrating comprehensive OpenInference integration."""
    print("OpenInference Integration Example")
    print("=" * 40)
    
    # Initialize HoneyHive tracer using the modern pattern
    print("🔍 Initializing HoneyHive tracer...")
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT", "openinference-demo"),
        source=os.getenv("HH_SOURCE", "development"),
        test_mode=True  # Enable test mode for this demo
    )
    
    print(f"✓ HoneyHive tracer initialized")
    print(f"  - Project: {tracer.project}")
    print(f"  - Source: {tracer.source}")
    print(f"  - Session: {tracer.session_id}")

    # Check dependencies
    try:
        import openai
        print("✓ OpenAI library is available")
    except ImportError:
        print("⚠️  OpenAI library not available")
        print("   Install with: pip install openai")

    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your-openai-key-here":
        print("⚠️  OpenAI API key not configured")
        print("   Set OPENAI_API_KEY environment variable to enable actual API calls")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        print()

    # Check HoneyHive configuration
    print(f"✓ HoneyHive configuration loaded")
    print(f"  - Project: {tracer.project}")
    print(f"  - Source: {tracer.source}")
    print()

    # Run demos
    print("\n🚀 Running Integration Demos")
    print("=" * 30)

    print("\n1. Basic Integration Demo")
    print("-" * 25)
    demonstrate_basic_integration(tracer)

    print("\n2. Complex Workflow Demo")
    print("-" * 25)
    demonstrate_complex_workflow(tracer)

    print("\n3. Async Operations Demo")
    print("-" * 25)
    asyncio.run(demonstrate_async_operations(tracer))

    print("\n4. Error Handling Demo")
    print("-" * 22)
    demonstrate_error_handling(tracer)

    print("\n🎉 All demos completed!")
    print("Check your HoneyHive dashboard to see the traced operations")


if __name__ == "__main__":
    main()