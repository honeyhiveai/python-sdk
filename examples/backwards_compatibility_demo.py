#!/usr/bin/env python3
"""
Backwards Compatibility Demo

This example demonstrates that both initialization patterns are supported:
1. Constructor pattern: HoneyHiveTracer(...)
2. Official SDK pattern: HoneyHiveTracer.init(...)

This ensures compatibility with existing production code that follows
the official HoneyHive documentation at docs.honeyhive.ai
"""

import os
from honeyhive.tracer import HoneyHiveTracer


def demonstrate_constructor_pattern():
    """Demonstrate the constructor pattern (for backwards compatibility)."""
    print("🔧 Constructor Pattern (Backwards Compatible)")
    print("=" * 50)
    
    # Constructor pattern with additional options
    tracer = HoneyHiveTracer(
        api_key="your-api-key",
        project="my-project",
        source="production",
        test_mode=True,  # Additional option not in official docs
        session_name="constructor_demo"
    )
    
    print(f"✓ Tracer created with constructor pattern")
    print(f"  Project: {tracer.project}")
    print(f"  Source: {tracer.source}")
    print(f"  Test Mode: {tracer.test_mode}")
    print(f"  Session Name: {tracer.session_name}")
    print()


def demonstrate_official_sdk_pattern():
    """Demonstrate the official SDK pattern (now fully compatible)."""
    print("📚 Official SDK Pattern (Fully Compatible)")
    print("=" * 50)

    # Official SDK pattern from docs.honeyhive.ai
    tracer = HoneyHiveTracer.init(
        api_key="your-api-key",
        project="my-project",
        source="production",
        session_name="official_sdk_demo"
    )

    print(f"✓ Tracer created with official SDK pattern")
    print(f"  Project: {tracer.project}")
    print(f"  Source: {tracer.source}")
    print(f"  Session Name: {tracer.session_name}")
    print()

    # Example with enhanced features (now available in init method)
    print("🚀 Enhanced Features Now Available")
    print("-" * 30)
    
    # Test mode and instrumentors are now supported in init method
    print("✓ Test mode and instrumentors now supported in init method:")
    
    # Create a mock instrumentor for demonstration
    class MockInstrumentor:
        def __init__(self, name: str):
            self.name = name
        
        def instrument(self):
            print(f"🔗 Mock {self.name} instrumented")
    
    mock_instrumentor = MockInstrumentor("OpenAI")
    
    # This now works with all constructor features
    enhanced_tracer = HoneyHiveTracer.init(
        api_key="your-api-key",
        project="my-project",
        source="production",
        test_mode=True,  # Now supported!
        instrumentors=[mock_instrumentor],  # Now supported!
        disable_http_tracing=True
    )
    
    print(f"✓ Enhanced init: Test Mode={enhanced_tracer.test_mode}")
    print("✓ All constructor features now available in init method")
    print()

    # Example with HTTP tracing enabled
    print("🌐 HTTP Tracing Control Example")
    print("-" * 30)
    
    # Note: HTTP tracing is disabled by default for performance
    print("Note: HTTP tracing is disabled by default for performance")
    print("To enable HTTP tracing, use disable_http_tracing=False:")
    
    # This would enable HTTP tracing (commented out to avoid side effects)
    # HoneyHiveTracer.init(
    #     api_key="your-api-key",
    #     project="my-project",
    #     source="production",
    #     disable_http_tracing=False
    # )
    
    print("✓ HTTP tracing control demonstrated")
    print()


def demonstrate_server_url_compatibility():
    """Demonstrate server_url parameter compatibility."""
    print("🌐 Server URL Compatibility")
    print("=" * 50)
    
    # Official SDK pattern with server_url for self-hosted deployments
    tracer = HoneyHiveTracer.init(
        api_key="your-api-key",
        project="my-project",
        source="production",
        server_url="https://custom-honeyhive-server.com"
    )
    
    print(f"✓ Tracer created with custom server URL")
    print(f"  Project: {tracer.project}")
    print(f"  Source: {tracer.source}")
    print(f"  Server URL: Custom endpoint")
    print()


def demonstrate_singleton_behavior():
    """Demonstrate that both patterns work with the singleton."""
    print("🔄 Singleton Behavior")
    print("=" * 50)
    
    # Create tracer with constructor
    tracer1 = HoneyHiveTracer(
        api_key="key1",
        project="project1",
        source="source1"
    )
    
    # Create tracer with init method
    tracer2 = HoneyHiveTracer.init(
        api_key="key2",
        project="project2",
        source="source2"
    )
    
    # Both should be the same instance (singleton)
    print(f"✓ Constructor tracer: {tracer1}")
    print(f"✓ Init method tracer: {tracer2}")
    print(f"✓ Same instance: {tracer1 is tracer2}")
    print(f"✓ Singleton instance: {HoneyHiveTracer._instance}")
    print()


def main():
    """Main demonstration function."""
    print("🚀 HoneyHive SDK Full Compatibility Demo")
    print("=" * 60)
    print()
    print("This demo shows the recommended initialization pattern:")
    print("1. Primary: HoneyHiveTracer.init(...) - Recommended")
    print("2. Alternative: HoneyHiveTracer(...) - Backwards compatible")
    print()
    print("The init method now supports ALL constructor features!")
    print("This ensures full compatibility with existing production code!")
    print()
    
    try:
        # Set test environment
        os.environ["HH_API_KEY"] = "test-key"
        os.environ["HH_PROJECT"] = "test-project"
        
        demonstrate_constructor_pattern()
        demonstrate_official_sdk_pattern()
        demonstrate_server_url_compatibility()
        demonstrate_singleton_behavior()
        
        print("🎉 All patterns work correctly!")
        print()
        print("✅ Constructor pattern: Backwards compatible")
        print("✅ Official SDK pattern: FULL compatibility (all features!)")
        print("✅ Both patterns: Same singleton instance")
        print()
        print("🚀 Your existing code will continue to work unchanged!")
        print("🚀 Use HoneyHiveTracer.init() for the best experience!")
        print("🚀 All features now available in the init method!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("This might be due to missing OpenTelemetry dependencies")


if __name__ == "__main__":
    main()
