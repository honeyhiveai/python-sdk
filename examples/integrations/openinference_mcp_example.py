#!/usr/bin/env python3
"""Simple MCP (Model Context Protocol) integration example with HoneyHive.

This example demonstrates the basic integration pattern for MCP instrumentor
following the established simple integration format used by other providers.

Prerequisites:
- Install MCP support: pip install honeyhive[openinference-mcp]
- Set HH_API_KEY environment variable
- Optional: Set up actual MCP server for real testing

Usage:
    python examples/openinference_mcp_example.py
"""

import asyncio
import os
import sys
from typing import Any, Dict

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from honeyhive import HoneyHiveTracer, trace
from honeyhive.models import EventType


def main():
    """Simple MCP integration example following established pattern."""
    print("🚀 Simple MCP Integration Example")
    print("=" * 40)

    # Check for MCP instrumentor availability
    try:
        from openinference.instrumentation.mcp import MCPInstrumentor

        print("✅ MCP instrumentor available")
        mcp_available = True
    except ImportError:
        print("⚠️  MCP instrumentor not available")
        print("   Install with: pip install honeyhive[openinference-mcp]")
        mcp_available = False

    # Initialize HoneyHive tracer FIRST
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "demo-api-key"),
        project="simple-mcp-demo",
        source="example-script",
        test_mode=os.getenv("HH_API_KEY") is None,  # Use test mode if no real API key
    )
    print("✅ HoneyHive tracer initialized")

    # Initialize MCP instrumentor separately if available
    if mcp_available:
        mcp_instrumentor = MCPInstrumentor()
        mcp_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✅ MCP instrumentor initialized with HoneyHive tracer_provider")
    else:
        print("⚠️ MCP instrumentor not available, continuing without MCP tracing")

    # Example MCP-style tool function with tracing
    @trace(event_type=EventType.tool)
    def simple_mcp_tool(query: str) -> Dict[str, Any]:
        """Simple MCP tool example with automatic tracing.

        In a real MCP setup, this would be called by an MCP client
        and the instrumentor would automatically trace the communication.
        """
        print(f"🔧 Processing MCP tool request: {query}")

        # Simulate tool processing
        result = {
            "query": query,
            "result": f"Processed: {query}",
            "tool_name": "simple_analyzer",
            "status": "success",
        }

        print(f"✅ Tool processing complete")
        return result

    # Example MCP workflow with tracing
    @trace(event_type=EventType.chain)
    def simple_mcp_workflow() -> Dict[str, Any]:
        """Simple MCP workflow demonstrating chain of operations."""
        print("🔄 Starting MCP workflow")

        # Step 1: Tool call
        tool_result = simple_mcp_tool("analyze user data")

        # Step 2: Process result
        workflow_result = {
            "workflow_id": "simple-mcp-workflow",
            "steps_completed": 1,
            "tool_results": [tool_result],
            "final_status": "completed",
        }

        print("✅ MCP workflow complete")
        return workflow_result

    # Run the example
    try:
        print("\n" + "=" * 40)
        print("📊 Running Simple MCP Example")
        print("=" * 40)

        # Execute the workflow
        result = simple_mcp_workflow()

        print(f"\n📋 Workflow Result:")
        print(f"   Status: {result['final_status']}")
        print(f"   Steps: {result['steps_completed']}")

        # Force flush traces
        if hasattr(tracer, "force_flush"):
            print("\n📤 Flushing traces...")
            tracer.force_flush()

        print("\n✅ Simple MCP integration example complete!")

        if os.getenv("HH_API_KEY") is None:
            print("\n💡 To see traces in HoneyHive dashboard:")
            print("   export HH_API_KEY='your-api-key'")
            print("   python examples/openinference_mcp_example.py")

        return 0

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        return 1


async def async_mcp_example():
    """Simple async MCP example demonstrating async tool execution."""
    print("\n🔄 Async MCP Example")

    @trace(event_type=EventType.tool)
    async def async_mcp_tool(data: str) -> Dict[str, Any]:
        """Async MCP tool example."""
        print(f"⚡ Processing async MCP tool: {data}")

        # Simulate async processing
        await asyncio.sleep(0.1)

        result = {
            "input": data,
            "processed_async": True,
            "result": f"Async result for: {data}",
        }

        print("✅ Async tool complete")
        return result

    # Execute async tool
    result = await async_mcp_tool("async test data")
    print(f"📋 Async Result: {result['result']}")


if __name__ == "__main__":
    """Entry point for simple MCP integration example."""
    try:
        # Run synchronous example
        exit_code = main()

        # Run async example if successful
        if exit_code == 0:
            asyncio.run(async_mcp_example())

        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n⚠️  Example interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
