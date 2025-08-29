#!/usr/bin/env python3
"""
HoneyHiveTracer.init Method Compatibility Demo

This example demonstrates that the HoneyHiveTracer.init method is now
fully compatible with the base HoneyHiveTracer constructor, supporting
all the same parameters and functionality.
"""

import os
from honeyhive.tracer import HoneyHiveTracer


def demonstrate_full_compatibility():
    """Demonstrate that init method supports all constructor parameters."""
    print("🔧 HoneyHiveTracer.init Full Compatibility Demo")
    print("=" * 60)
    
    # Test 1: Basic parameters (existing functionality)
    print("\n1. Basic Parameters (Existing)")
    print("-" * 30)
    
    tracer1 = HoneyHiveTracer.init(
        api_key="your-api-key",
        project="my-project",
        source="production"
    )
    
    print(f"✓ Basic init: Project={tracer1.project}, Source={tracer1.source}")
    
    # Test 2: Test mode parameter (newly added)
    print("\n2. Test Mode Parameter (Newly Added)")
    print("-" * 30)
    
    tracer2 = HoneyHiveTracer.init(
        api_key="your-api-key",
        project="my-project",
        source="production",
        test_mode=True  # This was missing before!
    )
    
    print(f"✓ Test mode init: Test Mode={tracer2.test_mode}")
    
    # Test 3: Instrumentors parameter (newly added)
    print("\n3. Instrumentors Parameter (Newly Added)")
    print("-" * 30)
    
    # Create a mock instrumentor for demonstration
    class MockInstrumentor:
        def __init__(self, name: str):
            self.name = name
        
        def instrument(self):
            print(f"🔗 Mock {self.name} instrumented")
    
    mock_instrumentor = MockInstrumentor("OpenAI")
    
    tracer3 = HoneyHiveTracer.init(
        api_key="your-api-key",
        project="my-project",
        source="production",
        instrumentors=[mock_instrumentor]  # This was missing before!
    )
    
    print(f"✓ Instrumentors init: Instrumentors supported")
    
    # Test 4: All parameters together
    print("\n4. All Parameters Together")
    print("-" * 30)
    
    tracer4 = HoneyHiveTracer.init(
        api_key="your-api-key",
        project="my-project",
        source="production",
        test_mode=True,
        session_name="compatibility_demo",
        server_url="https://custom-server.com",
        instrumentors=[mock_instrumentor],
        disable_http_tracing=True
    )
    
    print(f"✓ Full compatibility: All parameters supported")
    print(f"  - Project: {tracer4.project}")
    print(f"  - Source: {tracer4.source}")
    print(f"  - Test Mode: {tracer4.test_mode}")
    print(f"  - Session Name: {tracer4.session_name}")
    print(f"  - HTTP Tracing Disabled: {tracer4.disable_http_tracing}")
    
    print("\n🎉 HoneyHiveTracer.init is now fully compatible!")
    print("   All constructor parameters are supported in the init method.")
    print("   Use HoneyHiveTracer.init() as your primary initialization method!")


if __name__ == "__main__":
    demonstrate_full_compatibility()
