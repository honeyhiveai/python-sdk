#!/usr/bin/env python3
"""
MCP + OpenLLMetry (Traceloop) Integration Example

This example demonstrates how to integrate Model Context Protocol (MCP) with HoneyHive using
OpenLLMetry's MCP instrumentor package, following HoneyHive's
"Bring Your Own Instrumentor" architecture.

Requirements:
- pip install honeyhive[traceloop-mcp]
- Set environment variables: HH_API_KEY, MCP_SERVER_URL (optional)
- Running MCP server (optional for basic demonstration)
"""

import os
from typing import Dict, Any, List

# Import HoneyHive components
from honeyhive import HoneyHiveTracer, trace, enrich_span
from honeyhive.models import EventType

# Import MCP SDK (if available)
try:
    import mcp

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ MCP package not installed. Install with: pip install mcp")

# Import OpenLLMetry MCP instrumentor
from opentelemetry.instrumentation.mcp import MCPInstrumentor


def setup_tracing() -> HoneyHiveTracer:
    """Initialize HoneyHive tracer with OpenLLMetry MCP instrumentor."""

    # Check required environment variables
    if not os.getenv("HH_API_KEY"):
        raise ValueError("HH_API_KEY environment variable is required")

    # Initialize OpenLLMetry MCP instrumentor
    mcp_instrumentor = MCPInstrumentor()

    # Initialize HoneyHive tracer FIRST
    tracer = HoneyHiveTracer.init(
        source="traceloop_mcp_example",
        project=os.getenv("HH_PROJECT", "mcp-traceloop-demo"),
    )
    print("✓ HoneyHive tracer initialized")

    # Initialize instrumentor separately with tracer_provider
    mcp_instrumentor.instrument(tracer_provider=tracer.provider)

    print("✅ Tracing initialized with OpenLLMetry MCP instrumentor")
    return tracer


def basic_mcp_example():
    """Basic MCP usage with automatic tracing via OpenLLMetry."""

    print("\n🔧 Basic MCP Example")
    print("-" * 40)

    if not MCP_AVAILABLE:
        print("⚠️ MCP package not available, showing mock example")
        # Mock MCP functionality for demonstration
        mock_result = {
            "tool": "web_search",
            "query": "OpenLLMetry MCP integration",
            "result": "Mock search results for demonstration",
            "status": "success",
        }
        print(f"✅ Mock MCP tool executed: {mock_result}")
        return mock_result

    # Real MCP usage - automatically traced by OpenLLMetry
    try:
        server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

        # Create MCP client
        client = mcp.Client(server_url=server_url, api_key=os.getenv("MCP_API_KEY"))

        # Execute tool via MCP
        result = client.call_tool(
            name="web_search", arguments={"query": "OpenLLMetry MCP integration"}
        )

        print(f"✅ MCP tool executed: {result}")

        # OpenLLMetry automatically captures:
        # - Tool execution metrics
        # - Request/response content
        # - Latency and timing data
        # - Error handling

        return result

    except Exception as e:
        print(f"❌ MCP Error: {e}")
        print("   This is expected if no MCP server is running")
        return None


@trace(event_type=EventType.chain)
def multi_tool_mcp_workflow(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Advanced workflow using multiple MCP tools with business context tracing."""

    print(f"\n🚀 Multi-Tool MCP Workflow: {len(tasks)} tasks")
    print("-" * 40)

    # Add business context to the trace
    enrich_span(
        {
            "business.workflow": "tool_orchestration",
            "business.task_count": len(tasks),
            "mcp.strategy": "multi_tool_execution",
            "instrumentor.type": "openllmetry",
            "observability.enhanced": True,
        }
    )

    if not MCP_AVAILABLE:
        print("⚠️ MCP package not available, running mock workflow")
        return mock_mcp_workflow(tasks)

    # Real MCP workflow
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

    try:
        client = mcp.Client(server_url=server_url, api_key=os.getenv("MCP_API_KEY"))

        # Available MCP tools
        available_tools = [
            "web_search",
            "file_processor",
            "data_analyzer",
            "content_generator",
        ]

        results = []

        for i, task in enumerate(tasks):
            print(
                f"📝 Processing task {i+1}: {task.get('description', 'Unknown task')}"
            )

            task_results = {}
            tool_name = task.get("tool")
            arguments = task.get("arguments", {})

            if tool_name in available_tools:
                try:
                    # Execute MCP tool
                    result = client.call_tool(name=tool_name, arguments=arguments)

                    task_results[tool_name] = {
                        "success": True,
                        "result": result.content,
                        "metadata": result.metadata,
                    }

                    print(f"✅ {tool_name}: Success")

                except Exception as tool_error:
                    task_results[tool_name] = {
                        "success": False,
                        "error": str(tool_error),
                    }
                    print(f"❌ {tool_name}: {tool_error}")
            else:
                task_results[tool_name] = {
                    "success": False,
                    "error": f"Tool {tool_name} not available",
                }
                print(f"⚠️ {tool_name}: Not available")

            results.append({"task": task, "tool_results": task_results})

        # Add results to span
        enrich_span(
            {
                "business.tasks_processed": len(tasks),
                "business.tools_used": available_tools,
                "mcp.tools_available": available_tools,
                "business.workflow_status": "completed",
            }
        )

        return {
            "tasks_processed": len(tasks),
            "tools_available": available_tools,
            "results": results,
        }

    except Exception as e:
        enrich_span(
            {
                "error.type": "mcp_workflow_error",
                "error.message": str(e),
                "business.workflow_status": "failed",
            }
        )
        print(f"❌ MCP Workflow failed: {e}")
        print("   Falling back to mock workflow")
        return mock_mcp_workflow(tasks)


def mock_mcp_workflow(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mock MCP workflow for demonstration when MCP server is not available."""

    mock_tools = ["web_search", "file_processor", "data_analyzer", "content_generator"]
    results = []

    for i, task in enumerate(tasks):
        print(
            f"📝 Mock processing task {i+1}: {task.get('description', 'Unknown task')}"
        )

        tool_name = task.get("tool")

        # Simulate tool execution
        if tool_name in mock_tools:
            mock_result = {
                tool_name: {
                    "success": True,
                    "result": f"Mock result for {tool_name}",
                    "metadata": {"execution_time": "0.5s", "mock": True},
                }
            }
            print(f"✅ Mock {tool_name}: Success")
        else:
            mock_result = {
                tool_name: {
                    "success": False,
                    "error": f"Mock tool {tool_name} not available",
                }
            }
            print(f"⚠️ Mock {tool_name}: Not available")

        results.append({"task": task, "tool_results": mock_result})

    return {
        "tasks_processed": len(tasks),
        "tools_available": mock_tools,
        "results": results,
        "mock_mode": True,
    }


def demonstrate_tool_orchestration():
    """Demonstrate MCP tool orchestration capabilities."""

    print("\n🔧 Tool Orchestration Demonstration")
    print("-" * 40)

    # Define example tasks
    example_tasks = [
        {
            "tool": "web_search",
            "description": "Search for OpenLLMetry documentation",
            "arguments": {"query": "OpenLLMetry documentation"},
        },
        {
            "tool": "file_processor",
            "description": "Process configuration file",
            "arguments": {"file_path": "/config/settings.json", "action": "validate"},
        },
        {
            "tool": "data_analyzer",
            "description": "Analyze user behavior data",
            "arguments": {
                "dataset": "user_interactions",
                "metrics": ["engagement", "retention"],
            },
        },
    ]

    # Execute workflow
    result = multi_tool_mcp_workflow(example_tasks)

    print(f"\n📊 Orchestration Result:")
    print(f"   • Tasks Processed: {result['tasks_processed']}")
    print(f"   • Tools Available: {len(result['tools_available'])}")
    print(f"   • Mock Mode: {result.get('mock_mode', False)}")


def main():
    """Main example function."""

    print("🧪 MCP + OpenLLMetry (Traceloop) Integration Example")
    print("=" * 60)

    try:
        # Setup tracing
        tracer = setup_tracing()

        # Basic example
        basic_mcp_example()

        # Tool orchestration demonstration
        demonstrate_tool_orchestration()

        # Flush traces
        print("\n📤 Flushing traces to HoneyHive...")
        tracer.force_flush()
        print("✅ Traces sent successfully!")

        print("\n🎉 Example completed successfully!")
        print("\n💡 Key OpenLLMetry Benefits Demonstrated:")
        print("   • Automatic tool execution tracking")
        print("   • Enhanced MCP protocol metrics")
        print("   • Request/response content capture")
        print("   • Performance and latency monitoring")
        print("   • Multi-tool workflow orchestration")
        print("   • Seamless integration with HoneyHive BYOI")

        print("\n🔧 MCP Configuration:")
        print(
            "   • Server URL: " + os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        )
        print("   • Mock Mode: " + ("Enabled" if not MCP_AVAILABLE else "Disabled"))
        print(
            "   • Tools Available: web_search, file_processor, data_analyzer, content_generator"
        )

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
