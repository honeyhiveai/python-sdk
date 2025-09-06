"""Comprehensive real instrumentor integration tests.

These tests use real OpenTelemetry components and real API calls to catch
bugs that mocked tests miss, such as the ProxyTracerProvider issue.
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict

import pytest

from honeyhive import HoneyHiveTracer

# Real API fixtures are now in the main conftest.py
# No need for special imports - pytest will discover them automatically


@pytest.mark.real_api
@pytest.mark.real_instrumentor
class TestRealInstrumentorIntegration:
    """Test real instrumentor integration with no mocking."""

    def test_proxy_tracer_provider_bug_detection(self, fresh_tracer_environment):
        """Test that we properly handle ProxyTracerProvider in fresh environments.

        This test reproduces the exact bug scenario:
        1. Fresh Python environment starts with ProxyTracerProvider
        2. HoneyHive should detect and replace it with real TracerProvider
        3. Span processor should be added successfully
        """
        tracer = fresh_tracer_environment

        # Verify we have a real TracerProvider, not ProxyTracerProvider
        provider_type = type(tracer.provider).__name__
        assert "TracerProvider" in provider_type
        assert (
            "Proxy" not in provider_type
        ), f"Still using ProxyTracerProvider: {provider_type}"

        # Verify span processor was added successfully
        assert tracer.span_processor is not None
        assert hasattr(tracer.provider, "add_span_processor")

        # Test that spans can be created and recorded
        with tracer.start_span("test_span") as span:
            assert span.is_recording()
            span.set_attribute("test", "proxy_provider_bug")

    def test_subprocess_fresh_environment_integration(self, real_api_credentials):
        """Test instrumentor integration in a completely fresh subprocess.

        This catches issues that persist even with fixture cleanup.
        """
        # Create test script that runs in fresh environment
        test_script = f"""
import sys
sys.path.insert(0, "{Path(__file__).parent.parent.parent / 'src'}")

# Test the exact scenario that caused the bug
from opentelemetry import trace

# Verify we start with ProxyTracerProvider
initial_provider = trace.get_tracer_provider()
initial_type = type(initial_provider).__name__
print(f"Initial provider: {{initial_type}}")

# Initialize HoneyHive
from honeyhive.tracer.otel_tracer import HoneyHiveTracer

tracer = HoneyHiveTracer(
    api_key="{real_api_credentials['api_key']}",
    source="subprocess-test",
    test_mode=False,
    disable_http_tracing=True
)

# Verify we now have a real TracerProvider
final_provider = trace.get_tracer_provider()
final_type = type(final_provider).__name__
print(f"Final provider: {{final_type}}")

# Verify span processor was added
assert tracer.span_processor is not None
assert hasattr(tracer.provider, "add_span_processor")

# Test span creation
with tracer.start_span("subprocess_test") as span:
    assert span.is_recording()
    span.set_attribute("test", "subprocess_integration")

print("✅ Subprocess integration test passed")
"""

        # Write and execute test script
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
                    f"Subprocess integration test failed:\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

            # Verify expected behavior
            assert "Initial provider: ProxyTracerProvider" in result.stdout
            assert "Final provider: TracerProvider" in result.stdout
            assert "✅ Subprocess integration test passed" in result.stdout

        finally:
            os.unlink(script_path)

    @pytest.mark.openai_required
    def test_real_openai_instrumentor_integration(
        self,
        fresh_tracer_environment,
        provider_api_keys,
    ):
        """Test real OpenAI instrumentor integration with actual API calls."""
        tracer = fresh_tracer_environment

        try:
            # Import OpenAI and instrumentor
            import openai
            from openinference.instrumentation.openai import OpenAIInstrumentor

            # Initialize OpenAI client
            client = openai.OpenAI(api_key=provider_api_keys["openai"])

            # Initialize instrumentor with HoneyHive's tracer_provider
            instrumentor = OpenAIInstrumentor()
            instrumentor.instrument(tracer_provider=tracer.provider)

            # Make a real OpenAI API call (this should be traced)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'Hello from HoneyHive integration test'",
                    }
                ],
                max_tokens=20,
            )

            # Verify response
            assert response.choices[0].message.content
            assert "Hello" in response.choices[0].message.content

            # Force flush traces
            tracer.force_flush()

            # Cleanup
            instrumentor.uninstrument()

        except ImportError:
            pytest.skip("OpenAI or OpenInference instrumentor not available")

    @pytest.mark.anthropic_required
    def test_real_anthropic_instrumentor_integration(
        self,
        fresh_tracer_environment,
        provider_api_keys,
    ):
        """Test real Anthropic instrumentor integration with actual API calls."""
        tracer = fresh_tracer_environment

        try:
            # Import Anthropic and instrumentor
            import anthropic
            from openinference.instrumentation.anthropic import AnthropicInstrumentor

            # Initialize Anthropic client
            client = anthropic.Anthropic(api_key=provider_api_keys["anthropic"])

            # Initialize instrumentor with HoneyHive's tracer_provider
            instrumentor = AnthropicInstrumentor()
            instrumentor.instrument(tracer_provider=tracer.provider)

            # Make a real Anthropic API call (this should be traced)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=20,
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'Hello from HoneyHive Anthropic test'",
                    }
                ],
            )

            # Verify response
            assert response.content[0].text
            assert "Hello" in response.content[0].text

            # Force flush traces
            tracer.force_flush()

            # Cleanup
            instrumentor.uninstrument()

        except ImportError:
            pytest.skip("Anthropic or OpenInference instrumentor not available")

    def test_multiple_instrumentor_coexistence(
        self,
        fresh_tracer_environment,
        provider_api_keys,
    ):
        """Test that multiple instrumentors can coexist with real TracerProvider."""
        tracer = fresh_tracer_environment
        instrumentors = []

        try:
            # Try to initialize multiple instrumentors
            available_instrumentors = []

            # OpenAI
            if provider_api_keys["openai"]:
                try:
                    import openai
                    from openinference.instrumentation.openai import OpenAIInstrumentor

                    openai_instrumentor = OpenAIInstrumentor()
                    openai_instrumentor.instrument(tracer_provider=tracer.provider)
                    instrumentors.append(openai_instrumentor)
                    available_instrumentors.append("OpenAI")
                except ImportError:
                    pass

            # Anthropic
            if provider_api_keys["anthropic"]:
                try:
                    import anthropic
                    from openinference.instrumentation.anthropic import (
                        AnthropicInstrumentor,
                    )

                    anthropic_instrumentor = AnthropicInstrumentor()
                    anthropic_instrumentor.instrument(tracer_provider=tracer.provider)
                    instrumentors.append(anthropic_instrumentor)
                    available_instrumentors.append("Anthropic")
                except ImportError:
                    pass

            # Verify at least one instrumentor was initialized
            if not available_instrumentors:
                pytest.skip("No instrumentors available for testing")

            # Test that tracer still works with multiple instrumentors
            with tracer.start_span("multi_instrumentor_test") as span:
                assert span.is_recording()
                span.set_attribute("instrumentors", ",".join(available_instrumentors))
                span.set_attribute("count", len(available_instrumentors))

            # Force flush
            tracer.force_flush()

        finally:
            # Cleanup all instrumentors
            for instrumentor in instrumentors:
                try:
                    instrumentor.uninstrument()
                except Exception:
                    pass

    def test_tracer_provider_transition_monitoring(self, real_api_credentials):
        """Test monitoring of TracerProvider transitions during initialization."""
        # Import OpenTelemetry
        from opentelemetry import trace

        # Record initial state
        initial_provider = trace.get_tracer_provider()
        initial_type = type(initial_provider).__name__

        # Should start with ProxyTracerProvider in fresh environment
        assert (
            "Proxy" in initial_type
        ), f"Expected ProxyTracerProvider, got {initial_type}"

        # Initialize HoneyHive tracer (project derived from API key)
        tracer = HoneyHiveTracer(
            api_key=real_api_credentials["api_key"],
            source="transition-monitoring",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Record final state
        final_provider = trace.get_tracer_provider()
        final_type = type(final_provider).__name__

        # Should now have real TracerProvider
        assert "TracerProvider" in final_type
        assert "Proxy" not in final_type

        # Verify the transition worked
        assert initial_provider != final_provider
        assert tracer.provider == final_provider

        # Test functionality
        with tracer.start_span("transition_test") as span:
            assert span.is_recording()
            span.set_attribute("initial_provider", initial_type)
            span.set_attribute("final_provider", final_type)

        # Cleanup
        tracer.force_flush()
        tracer.shutdown()

    def test_span_processor_integration_real_api(self, real_honeyhive_tracer):
        """Test that span processor correctly processes spans with real API."""
        tracer = real_honeyhive_tracer

        # Create a span with rich attributes
        with tracer.start_span("real_api_test") as span:
            assert span.is_recording()

            # Add various types of attributes
            span.set_attribute("test.type", "real_api_integration")
            span.set_attribute("test.timestamp", int(time.time()))
            span.set_attribute("test.boolean", True)
            span.set_attribute("test.number", 42)

            # Test nested span
            with tracer.start_span("nested_span") as nested_span:
                assert nested_span.is_recording()
                nested_span.set_attribute("nested", True)
                nested_span.set_attribute("parent_test", "real_api_integration")

        # Force flush to ensure spans are processed
        tracer.force_flush()

    def test_error_handling_real_environment(self, fresh_tracer_environment):
        """Test error handling in real OpenTelemetry environment."""
        tracer = fresh_tracer_environment

        # Test span creation with errors
        try:
            with tracer.start_span("error_test") as span:
                assert span.is_recording()
                span.set_attribute("test", "error_handling")

                # Simulate an error
                raise ValueError("Test error for span recording")

        except ValueError:
            # Error should be handled gracefully
            pass

        # Tracer should still be functional after error
        with tracer.start_span("post_error_test") as span:
            assert span.is_recording()
            span.set_attribute("after_error", True)

        tracer.force_flush()


@pytest.mark.real_api
class TestRealAPIWorkflows:
    """Test complete workflows with real API integration."""

    def test_end_to_end_tracing_workflow(self, real_honeyhive_tracer):
        """Test complete end-to-end tracing workflow with real API."""
        tracer = real_honeyhive_tracer

        # Simulate a complete AI application workflow
        with tracer.start_span("ai_application_workflow") as main_span:
            assert main_span.is_recording()
            main_span.set_attribute("workflow.type", "ai_application")
            main_span.set_attribute("workflow.version", "1.0")

            # Step 1: Input processing
            with tracer.start_span("input_processing") as input_span:
                input_span.set_attribute("step", 1)
                input_span.set_attribute("input.type", "user_query")
                time.sleep(0.01)  # Simulate processing time

            # Step 2: Model inference (simulated)
            with tracer.start_span("model_inference") as model_span:
                model_span.set_attribute("step", 2)
                model_span.set_attribute("model.name", "test_model")
                model_span.set_attribute("model.temperature", 0.7)
                time.sleep(0.02)  # Simulate inference time

            # Step 3: Output processing
            with tracer.start_span("output_processing") as output_span:
                output_span.set_attribute("step", 3)
                output_span.set_attribute("output.format", "json")
                time.sleep(0.01)  # Simulate processing time

        # Force flush to ensure all spans are sent
        tracer.force_flush()

    def test_concurrent_span_creation_real_api(self, real_honeyhive_tracer):
        """Test concurrent span creation with real API."""
        import queue
        import threading

        tracer = real_honeyhive_tracer
        results = queue.Queue()

        def create_spans(thread_id: int):
            """Create spans in a separate thread."""
            try:
                with tracer.start_span(f"thread_{thread_id}_main") as main_span:
                    main_span.set_attribute("thread.id", thread_id)
                    main_span.set_attribute("test.type", "concurrent")

                    # Create nested spans
                    for i in range(3):
                        with tracer.start_span(
                            f"thread_{thread_id}_nested_{i}"
                        ) as nested_span:
                            nested_span.set_attribute("nested.index", i)
                            nested_span.set_attribute("thread.id", thread_id)
                            time.sleep(0.001)  # Small delay

                results.put(f"thread_{thread_id}_success")

            except Exception as e:
                results.put(f"thread_{thread_id}_error: {e}")

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_spans, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)

        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if "success" in result:
                success_count += 1
            else:
                pytest.fail(f"Thread failed: {result}")

        assert success_count == 3, f"Expected 3 successful threads, got {success_count}"

        # Force flush
        tracer.force_flush()
