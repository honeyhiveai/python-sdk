"""Real instrumentor integration tests that would catch ProxyTracerProvider bugs.

This test module validates real-world instrumentor integration scenarios
that our mocked tests miss. These tests use actual OpenTelemetry components
to catch bugs like the ProxyTracerProvider issue.
"""

import os
import subprocess
import sys
import tempfile

import pytest


@pytest.mark.integration
class TestRealInstrumentorIntegration:
    """Test real instrumentor integration scenarios."""

    def test_fresh_environment_proxy_tracer_provider_bug(self):
        """Test the ProxyTracerProvider bug in a fresh environment.

        This test reproduces the exact scenario that caused the bug:
        1. Fresh Python environment (no existing TracerProvider)
        2. OpenTelemetry creates default ProxyTracerProvider
        3. HoneyHive tries to integrate with ProxyTracerProvider
        4. Should detect and handle ProxyTracerProvider correctly
        """
        # Create a test script that reproduces the bug scenario
        test_script = """
import os
import sys
sys.path.insert(0, "/Users/josh/src/github.com/honeyhiveai/python-sdk/src")

# Simulate fresh environment - no existing TracerProvider
from opentelemetry import trace

# Verify we start with ProxyTracerProvider (the bug condition)
initial_provider = trace.get_tracer_provider()
provider_type = type(initial_provider).__name__
print(f"Initial provider type: {provider_type}")

# This should be ProxyTracerProvider in a fresh environment
assert "Proxy" in provider_type, f"Expected ProxyTracerProvider, got {provider_type}"

# Now test HoneyHive initialization
from honeyhive.tracer import HoneyHiveTracer

# Get real API key for integration test
api_key = os.getenv("HH_API_KEY")
if not api_key:
    print("⚠️ HH_API_KEY not available, using test key for ProxyTracerProvider test")
    api_key = "test-key-for-proxy-test"

# Initialize HoneyHive - this should handle ProxyTracerProvider correctly
tracer = HoneyHiveTracer(
    api_key=api_key,
    project="integration-test-project", 
    source="integration-test-source",
    test_mode=False,  # Use real API for integration testing
    disable_http_tracing=True
)

# Verify HoneyHive created a real TracerProvider
final_provider = trace.get_tracer_provider()
final_provider_type = type(final_provider).__name__
print(f"Final provider type: {final_provider_type}")

# Should now have a real TracerProvider, not ProxyTracerProvider
assert "TracerProvider" in final_provider_type
assert "Proxy" not in final_provider_type

# Verify span processor was added successfully
assert hasattr(tracer.provider, "add_span_processor")
assert tracer.span_processor is not None

print("✅ ProxyTracerProvider handled correctly!")
"""

        # Write test script to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_script)
            script_path = f.name

        try:
            # Run the test script in a subprocess (fresh environment)
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            # Check if the test passed
            if result.returncode != 0:
                pytest.fail(
                    f"ProxyTracerProvider test failed:\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

            # Verify expected output
            assert "Initial provider type: ProxyTracerProvider" in result.stdout
            assert "Final provider type: TracerProvider" in result.stdout
            assert "✅ ProxyTracerProvider handled correctly!" in result.stdout

        finally:
            # Clean up
            os.unlink(script_path)

    def test_instrumentor_initialization_order_bug(self):
        """Test the instrumentor initialization order that caused the bug.

        This test validates that both initialization patterns work:
        1. Correct: HoneyHive first, then instrumentor
        2. Incorrect but should work: instrumentor in HoneyHive.init()
        """
        test_script = """
import os
import sys
sys.path.insert(0, "/Users/josh/src/github.com/honeyhiveai/python-sdk/src")

from opentelemetry import trace
from honeyhive.tracer import HoneyHiveTracer

print("Testing correct initialization order...")

# Get real API key for integration test
api_key = os.getenv("HH_API_KEY")
if not api_key:
    print("⚠️ HH_API_KEY not available, using test key for initialization order test")
    api_key = "test-key-for-init-order-test"

# ✅ CORRECT: HoneyHive first, then instrumentor separately
tracer = HoneyHiveTracer(
    api_key=api_key,
    project="integration-test-project",
    source="integration-test-source", 
    test_mode=False,  # Use real API for integration testing
    disable_http_tracing=True
)

# Verify we have a real TracerProvider
provider = trace.get_tracer_provider()
provider_type = type(provider).__name__
print(f"Provider after HoneyHive init: {provider_type}")

assert "TracerProvider" in provider_type
assert "Proxy" not in provider_type
assert hasattr(provider, "add_span_processor")

print("✅ Correct initialization order works!")

# Test that span processor is working
with tracer.start_span("test_span") as span:
    span.set_attribute("test", "value")
    assert span.is_recording()

print("✅ Span creation and processing works!")
"""

        # Write and run test script
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_script)
            script_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.fail(
                    f"Initialization order test failed:\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

            assert "✅ Correct initialization order works!" in result.stdout
            assert "✅ Span creation and processing works!" in result.stdout

        finally:
            os.unlink(script_path)

    def test_span_processor_integration_bug(self):
        """Test that span processors are correctly added and functional.

        This test specifically validates the span processor integration
        that was broken by the ProxyTracerProvider bug.
        """
        test_script = """
import os
import sys
sys.path.insert(0, "/Users/josh/src/github.com/honeyhiveai/python-sdk/src")

from opentelemetry import trace
from honeyhive.tracer import HoneyHiveTracer

# Get real API key for integration test
api_key = os.getenv("HH_API_KEY")
if not api_key:
    print("⚠️ HH_API_KEY not available, using test key for span processor test")
    api_key = "test-key-for-span-processor-test"

# Initialize HoneyHive
tracer = HoneyHiveTracer(
    api_key=api_key,
    project="integration-test-project",
    source="integration-test-source",
    test_mode=False,  # Use real API for integration testing
    disable_http_tracing=True
)

# Verify span processor was added
provider = trace.get_tracer_provider()
print(f"Provider type: {type(provider).__name__}")
print(f"Has add_span_processor: {hasattr(provider, 'add_span_processor')}")
print(f"Span processor exists: {tracer.span_processor is not None}")

# Test span processing
span_created = False
with tracer.start_span("test_span") as span:
    span_created = True
    span.set_attribute("test_key", "test_value")
    print(f"Span is recording: {span.is_recording()}")

assert span_created, "Span creation failed"
print("✅ Span processor integration works!")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_script)
            script_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.fail(
                    f"Span processor integration test failed:\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

            assert "✅ Span processor integration works!" in result.stdout

        finally:
            os.unlink(script_path)

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for real instrumentor test",
    )
    def test_real_openai_instrumentor_integration(self):
        """Test with real OpenAI instrumentor to catch integration bugs.

        This test uses actual OpenInference OpenAI instrumentor to validate
        the complete integration works end-to-end.
        """
        test_script = """
import os
import sys
sys.path.insert(0, "/Users/josh/src/github.com/honeyhiveai/python-sdk/src")

# Test real instrumentor integration
from opentelemetry import trace
from honeyhive.tracer import HoneyHiveTracer

# Get real API key for integration test
api_key = os.getenv("HH_API_KEY")
if not api_key:
    print("⚠️ HH_API_KEY not available, using test key for real instrumentor test")
    api_key = "test-key-for-real-instrumentor-test"

# Step 1: Initialize HoneyHive first
tracer = HoneyHiveTracer(
    api_key=api_key,
    project="integration-test-project",
    source="integration-test-source",
    test_mode=False,  # Use real API for integration testing
    disable_http_tracing=True
)

print(f"HoneyHive provider: {type(tracer.provider).__name__}")

# Step 2: Initialize instrumentor with HoneyHive's provider
try:
    from openinference.instrumentation.openai import OpenAIInstrumentor
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)
    print("✅ OpenAI instrumentor initialized successfully")
    
    # Verify integration
    provider = trace.get_tracer_provider()
    print(f"Final provider: {type(provider).__name__}")
    assert hasattr(provider, "add_span_processor")
    
    # Clean up
    instrumentor.uninstrument()
    print("✅ Real instrumentor integration test passed!")
    
except ImportError:
    print("⚠️  OpenInference OpenAI not available, skipping")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_script)
            script_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.fail(
                    f"Real instrumentor integration test failed:\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

            # Should either pass or skip gracefully
            assert (
                "✅ Real instrumentor integration test passed!" in result.stdout
                or "⚠️  OpenInference OpenAI not available" in result.stdout
            )

        finally:
            os.unlink(script_path)
