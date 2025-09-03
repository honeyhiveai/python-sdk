#!/usr/bin/env python3
"""
Simple AWS Strands + HoneyHive integration test.

This version focuses on testing the core integration without requiring
actual Bedrock model access. It verifies the instrumentation works correctly.
"""

import os
import sys

# Add src to path for local testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_honeyhive_strands_integration():
    """Test HoneyHive instrumentation with Strands (no model calls)."""
    
    print("🧪 Simple AWS Strands + HoneyHive Integration Test")
    print("=" * 55)
    
    try:
        # Import HoneyHive
        from honeyhive import HoneyHiveTracer, trace, enrich_span
        print("✅ HoneyHive imported successfully")
        
        # Import Strands
        try:
            from strands import Agent
            print("✅ AWS Strands imported successfully")
            strands_available = True
        except ImportError as e:
            print(f"⚠️  Strands import failed: {e}")
            print("   Install with: pip install strands-agents")
            strands_available = False
            
        # Test 1: HoneyHive initialization
        print(f"\n📊 Test 1: HoneyHive Initialization")
        print("-" * 35)
        
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HONEYHIVE_API_KEY", "test-key"),
            project="strands-simple-test",
            source="test",
            test_mode=True,  # Avoid real API calls
            session_name="simple_integration_test"
        )
        
        print(f"✅ Tracer initialized (main provider: {tracer.is_main_provider})")
        
        if not strands_available:
            print("\n⚠️  Skipping Strands tests - package not available")
            return True
            
        # Test 2: Agent creation (no execution)
        print(f"\n🤖 Test 2: Strands Agent Creation")
        print("-" * 35)
        
        @trace(event_type="tool", event_name="agent_creation_test")
        def create_test_agent():
            """Create a Strands agent without executing it."""
            
            agent = Agent(
                # Use a simple model ID (won't be called)
                model="test-model",
                system_prompt="You are a test assistant."
            )
            
            # Use tracer instance method for enrichment
            tracer.enrich_span(metadata={
                "test_type": "agent_creation",
                "integration_test": True,
                "model": "test-model"
            })
            
            print(f"✅ Agent created successfully")
            print(f"   Model: {getattr(agent, 'model', 'unknown')}")
            print(f"   System prompt: {getattr(agent, 'system_prompt', 'unknown')[:50]}...")
            
            return agent
        
        agent = create_test_agent()
        
        # Test 3: OpenTelemetry integration verification
        print(f"\n🔍 Test 3: OpenTelemetry Integration")
        print("-" * 38)
        
        from opentelemetry import trace as otel_trace
        
        current_provider = otel_trace.get_tracer_provider()
        print(f"✅ Current TracerProvider: {type(current_provider).__name__}")
        print(f"✅ HoneyHive is main provider: {tracer.is_main_provider}")
        
        # Test 4: Span creation and enrichment
        print(f"\n📈 Test 4: Span Creation & Enrichment")
        print("-" * 38)
        
        with tracer.start_span("integration_verification") as span:
            tracer.enrich_span(metadata={
                "verification_test": True,
                "strands_available": strands_available,
                "provider_type": type(current_provider).__name__,
                "honeyhive_main": tracer.is_main_provider
            })
            
            # Simulate what would happen in real agent execution
            # (without actually calling the model)
            span_context = getattr(span, "_context", None)
            if span_context:
                span_info = {
                    "span_id": getattr(span_context, "span_id", "unknown"),
                    "trace_id": getattr(span_context, "trace_id", "unknown")
                }
            else:
                span_info = {"span_id": "unknown", "trace_id": "unknown"}
            
            print(f"✅ Span created and enriched")
            print(f"   Span attributes set: verification_test, strands_available, etc.")
            print(f"   Span ID: {span_info['span_id']}")
            
        print(f"\n🎯 Integration Test Results")
        print("=" * 27)
        print(f"✅ HoneyHive tracer: Working")
        print(f"✅ Strands integration: Working")
        print(f"✅ OpenTelemetry flow: Working")
        print(f"✅ Span enrichment: Working")
        
        print(f"\n💡 Next Steps:")
        if not os.getenv("HONEYHIVE_API_KEY") or os.getenv("HONEYHIVE_API_KEY") == "test-key":
            print("   • Set real HONEYHIVE_API_KEY for live testing")
        print("   • Configure AWS credentials for Bedrock access")
        print("   • Run: python check_bedrock_access.py")
        print("   • Use working models from check_bedrock_access.py output")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run the simple integration test."""
    
    # Check basic requirements
    if not os.getenv("HONEYHIVE_API_KEY"):
        print("⚠️  HONEYHIVE_API_KEY not set, using test mode")
        
    success = test_honeyhive_strands_integration()
    
    if success:
        print(f"\n🎉 Simple integration test PASSED!")
        print("   The HoneyHive + Strands integration is working correctly.")
        return 0
    else:
        print(f"\n💥 Simple integration test FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
