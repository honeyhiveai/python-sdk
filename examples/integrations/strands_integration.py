"""
AWS Strands Integration Example

This example demonstrates how to integrate HoneyHive with AWS Strands,
a framework that uses OpenTelemetry directly for tracing.

AWS Strands is a non-instrumentor framework, meaning it doesn't rely on
auto-instrumentation libraries and sets up its own OpenTelemetry configuration.
"""

import os
import asyncio
from honeyhive import HoneyHiveTracer

# Optional: Only import if strands is available
try:
    from strands import Agent
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    print("⚠️  AWS Strands not available. Install with: pip install strands-agents")


def main():
    """Main integration example."""
    print("🚀 AWS Strands + HoneyHive Integration Example")
    print("=" * 50)
    
    if not STRANDS_AVAILABLE:
        print("❌ AWS Strands is not installed. Exiting.")
        return
    
    # Step 1: Initialize HoneyHive tracer first
    # This ensures HoneyHive becomes the main TracerProvider
    print("1. Initializing HoneyHive tracer...")
    
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project=os.getenv("HH_PROJECT", "strands-integration-demo"),
        source="strands-example",
        test_mode=True,  # Set to False for production
        verbose=True     # Enable debug logging
    )
    
    print(f"✅ HoneyHive tracer initialized")
    print(f"   Session ID: {tracer.session_id}")
    print(f"   Project: {tracer.project}")
    print()
    
    # Step 2: Initialize AWS Strands
    # Strands will use HoneyHive's TracerProvider
    print("2. Initializing AWS Strands agent...")
    
    agent = Agent(
        system_prompt="You are a helpful AI assistant that provides clear, concise answers.",
        model="gpt-4o-mini",  # Use a cost-effective model for demo
        temperature=0.7
    )
    
    print("✅ AWS Strands agent initialized")
    print()
    
    # Step 3: Execute traced operations
    print("3. Executing traced operations...")
    
    # Example 1: Simple query
    print("   Example 1: Simple math query")
    try:
        result1 = asyncio.run(agent.invoke_async("What is 15 * 23?"))
        print(f"   Result: {result1}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Example 2: Complex reasoning
    print("   Example 2: Complex reasoning task")
    try:
        result2 = asyncio.run(agent.invoke_async(
            "Explain the concept of machine learning in simple terms, "
            "including its main types and applications."
        ))
        print(f"   Result: {result2[:100]}...")  # Truncate for display
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Step 4: Demonstrate context propagation
    print("4. Demonstrating context propagation...")
    
    from opentelemetry import trace
    
    # Get the tracer (should be HoneyHive's tracer)
    otel_tracer = trace.get_tracer("strands-example")
    
    with otel_tracer.start_as_current_span("multi-step-workflow") as parent_span:
        parent_span.set_attribute("workflow.type", "multi-step")
        parent_span.set_attribute("workflow.steps", 3)
        
        # Step 1: Information gathering
        with otel_tracer.start_as_current_span("step-1-gather-info") as step1_span:
            step1_span.set_attribute("step.name", "gather_info")
            try:
                info_result = asyncio.run(agent.invoke_async(
                    "What are the key components of a neural network?"
                ))
                step1_span.set_attribute("step.result", "success")
                print(f"   Step 1 result: {info_result[:50]}...")
            except Exception as e:
                step1_span.set_attribute("step.result", "error")
                step1_span.set_attribute("step.error", str(e))
                print(f"   Step 1 error: {e}")
        
        # Step 2: Analysis
        with otel_tracer.start_as_current_span("step-2-analyze") as step2_span:
            step2_span.set_attribute("step.name", "analyze")
            try:
                analysis_result = asyncio.run(agent.invoke_async(
                    "How do neural networks learn from data?"
                ))
                step2_span.set_attribute("step.result", "success")
                print(f"   Step 2 result: {analysis_result[:50]}...")
            except Exception as e:
                step2_span.set_attribute("step.result", "error")
                step2_span.set_attribute("step.error", str(e))
                print(f"   Step 2 error: {e}")
        
        # Step 3: Summary
        with otel_tracer.start_as_current_span("step-3-summarize") as step3_span:
            step3_span.set_attribute("step.name", "summarize")
            try:
                summary_result = asyncio.run(agent.invoke_async(
                    "Summarize the key points about neural networks in 2 sentences."
                ))
                step3_span.set_attribute("step.result", "success")
                print(f"   Step 3 result: {summary_result}")
            except Exception as e:
                step3_span.set_attribute("step.result", "error")
                step3_span.set_attribute("step.error", str(e))
                print(f"   Step 3 error: {e}")
        
        parent_span.set_attribute("workflow.status", "completed")
    
    print()
    print("✅ Integration example completed!")
    print()
    print("📊 Check your HoneyHive dashboard to see the traced operations:")
    print(f"   Session ID: {tracer.session_id}")
    print(f"   Project: {tracer.project}")


def demonstrate_error_handling():
    """Demonstrate error handling in integration."""
    print("🔧 Error Handling Example")
    print("=" * 30)
    
    # Example 1: Missing API key
    print("1. Testing missing API key...")
    try:
        tracer = HoneyHiveTracer.init(
            api_key=None,  # Missing API key
            project="error-demo",
            test_mode=False
        )
        print("   Unexpected: No error raised")
    except Exception as e:
        print(f"   Expected error: {e}")
    
    print()
    
    # Example 2: Invalid configuration
    print("2. Testing invalid configuration...")
    try:
        tracer = HoneyHiveTracer.init(
            api_key="invalid-key",
            project="",  # Empty project
            test_mode=True  # Use test mode to avoid API calls
        )
        print("   ✅ Tracer initialized with test mode")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("⚡ Performance Monitoring Example")
    print("=" * 35)
    
    if not STRANDS_AVAILABLE:
        print("❌ AWS Strands not available for performance demo")
        return
    
    import time
    
    # Initialize with performance monitoring
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-key"),
        project="performance-demo",
        source="performance-test",
        test_mode=True,
        verbose=False  # Reduce noise for performance testing
    )
    
    agent = Agent(
        system_prompt="Provide very brief answers.",
        model="gpt-4o-mini",
        temperature=0.1
    )
    
    # Measure performance
    operations = [
        "What is 2+2?",
        "Name a color.",
        "What day is it?",
        "Count to 3.",
        "Say hello."
    ]
    
    print(f"Running {len(operations)} operations...")
    start_time = time.perf_counter()
    
    for i, operation in enumerate(operations, 1):
        op_start = time.perf_counter()
        try:
            result = asyncio.run(agent.invoke_async(operation))
            op_end = time.perf_counter()
            op_time = op_end - op_start
            print(f"   Operation {i}: {op_time:.3f}s - {operation}")
        except Exception as e:
            op_end = time.perf_counter()
            op_time = op_end - op_start
            print(f"   Operation {i}: {op_time:.3f}s - ERROR: {e}")
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = total_time / len(operations)
    
    print()
    print(f"📊 Performance Results:")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Average per operation: {avg_time:.3f}s")
    print(f"   Operations per second: {len(operations) / total_time:.1f}")


if __name__ == "__main__":
    """Run the integration examples."""
    
    # Check for required environment variables
    if not os.getenv("HH_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Environment Setup:")
        print("   Set HH_API_KEY for HoneyHive integration")
        print("   Set OPENAI_API_KEY for AWS Strands (if using real API)")
        print("   Or run in test mode (demo will use test mode)")
        print()
    
    # Run examples
    try:
        main()
        print()
        demonstrate_error_handling()
        print()
        demonstrate_performance_monitoring()
        
    except KeyboardInterrupt:
        print("\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 AWS Strands integration examples completed!")
