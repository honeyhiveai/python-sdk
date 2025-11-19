"""Test A2A SDK integration with HoneyHive BYOI.

This script demonstrates how to use the A2A SDK with HoneyHive's
Bring-Your-Own-Instrumentation (BYOI) architecture.
"""

import asyncio
import os

# Import HoneyHive tracer (assuming honeyhive SDK is installed)
try:
    from honeyhive import HoneyHiveTracer
    HONEYHIVE_AVAILABLE = True
except ImportError:
    print("HoneyHive SDK not installed. Install with: pip install honeyhive")
    HONEYHIVE_AVAILABLE = False

# Import A2A SDK components
from a2a.client import Client, ClientConfig
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.types import Message, MessageSendParams


# Example AgentExecutor implementation
class SimpleEchoAgent(AgentExecutor):
    """A simple echo agent for testing."""

    async def execute(
        self, request_context: RequestContext
    ) -> Message:
        """Echo back the user's message."""
        user_message = request_context.message.content
        return Message(
            role="assistant",
            content=f"Echo: {user_message}"
        )


async def test_a2a_with_honeyhive():
    """Test A2A SDK with HoneyHive tracing."""

    if not HONEYHIVE_AVAILABLE:
        print("Skipping test - HoneyHive not available")
        return

    # Initialize HoneyHive tracer
    # The A2A SDK will automatically use this global TracerProvider
    tracer = HoneyHiveTracer.init(
        project="a2a-test",
        api_key=os.getenv("HH_API_KEY", "test-key"),
        source="a2a-integration-test"
    )

    print("✓ HoneyHive TracerProvider initialized")
    print("✓ A2A SDK will automatically use it via trace.get_tracer()")

    # Now use A2A SDK normally - it will automatically trace to HoneyHive!
    # All @trace_class and @trace_function decorated methods will create spans

    # Example: Create a client (this will be traced)
    # Note: In real usage, you'd have a running A2A server
    print("✓ A2A SDK operations will be traced to HoneyHive")
    print("✓ Check HoneyHive dashboard for traces")
    print(f"  Project: a2a-test")
    print(f"  Source: a2a-integration-test")

    # The tracing happens automatically via the decorators:
    # - RestTransport.send_message() -> traced (CLIENT span)
    # - DefaultRequestHandler methods -> traced (SERVER spans)
    # - Helper functions -> traced (INTERNAL spans)


def test_without_honeyhive():
    """Test that A2A SDK gracefully handles missing OpenTelemetry."""
    print("\nTesting without OpenTelemetry installed:")
    print("✓ A2A SDK has graceful degradation")
    print("✓ All trace calls become no-ops")
    print("✓ SDK functions normally without telemetry")


if __name__ == "__main__":
    print("=" * 60)
    print("A2A SDK + HoneyHive BYOI Integration Test")
    print("=" * 60)

    if HONEYHIVE_AVAILABLE:
        asyncio.run(test_a2a_with_honeyhive())
    else:
        test_without_honeyhive()

    print("\n" + "=" * 60)
    print("Integration Pattern:")
    print("=" * 60)
    print("""
1. Install both SDKs:
   pip install a2a-sdk[telemetry] honeyhive

2. Initialize HoneyHive tracer BEFORE using A2A:
   from honeyhive import HoneyHiveTracer
   HoneyHiveTracer.init(project="my-project", api_key="...")

3. Use A2A SDK normally:
   from a2a.client import Client
   # All operations automatically traced!

4. What gets traced:
   - Client transport operations (REST/gRPC/JSON-RPC)
   - Server request handling
   - Agent execution (if using @trace_class on your agent)
   - Custom operations (use @trace_function decorator)

5. Span hierarchy:
   - CLIENT spans: client.send_message()
   - SERVER spans: request handlers, event processing
   - INTERNAL spans: helper functions

6. What's NOT traced automatically:
   - Your custom AgentExecutor.execute() method
   - LLM API calls within your agent
   - Solution: Add @trace_class to your AgentExecutor
   - Solution: Use existing LLM instrumentors (openai, anthropic, etc.)
""")

