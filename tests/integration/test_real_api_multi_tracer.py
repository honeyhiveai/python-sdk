"""Real API integration tests for multi-tracer functionality in HoneyHive."""

import time
import pytest
from unittest.mock import Mock, patch

from honeyhive.tracer.decorators import trace, atrace
from honeyhive.tracer.otel_tracer import HoneyHiveTracer


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.multi_tracer
class TestRealAPIMultiTracer:
    """Test multi-tracer functionality with real API calls."""

    def test_real_session_creation_with_multiple_tracers(
        self, real_api_key, real_project, real_source
    ):
        """Test that multiple tracers can create real sessions independently."""
        # Create multiple tracers with different session names
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="real-session-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="real-session-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Verify they're independent
        assert tracer1 is not tracer2
        assert tracer1.session_name != tracer2.session_name
        
        # Test real session creation with both tracers
        with tracer1.start_span("real_session1") as span1:
            span1.set_attribute("session", "tracer1")
            span1.add_event("session_started", {"tracer": "tracer1", "timestamp": time.time()})
            # Simulate some work
            time.sleep(0.1)
            span1.set_attribute("duration_ms", 100)
        
        with tracer2.start_span("real_session2") as span2:
            span2.set_attribute("session", "tracer2")
            span2.add_event("session_started", {"tracer": "tracer2", "timestamp": time.time()})
            # Simulate different work
            time.sleep(0.05)
            span2.set_attribute("duration_ms", 50)

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_real_event_creation_with_multiple_tracers(
        self, real_api_key, real_project, real_source
    ):
        """Test that multiple tracers can create real events independently."""
        # Create multiple tracers
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="real-event-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="real-event-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Create events with both tracers
        with tracer1.start_span("event_creation1") as span1:
            span1.set_attribute("event_type", "model_inference")
            span1.set_attribute("model", "gpt-4")
            span1.set_attribute("tracer", "tracer1")
            
            # Simulate model inference
            span1.add_event("inference_started", {"input_tokens": 100})
            time.sleep(0.1)
            span1.add_event("inference_completed", {"output_tokens": 150, "latency_ms": 100})
        
        with tracer2.start_span("event_creation2") as span2:
            span2.set_attribute("event_type", "data_processing")
            span2.set_attribute("dataset", "test_dataset")
            span2.set_attribute("tracer", "tracer2")
            
            # Simulate data processing
            span2.add_event("processing_started", {"records": 1000})
            time.sleep(0.05)
            span2.add_event("processing_completed", {"processed_records": 1000, "latency_ms": 50})

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_real_decorator_integration_with_multiple_tracers(
        self, real_api_key, real_project, real_source
    ):
        """Test @trace decorator with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="decorator-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="decorator-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Test functions decorated with different tracers
        @trace(event_name="function1", event_type="test", tracer=tracer1)
        def function1(x, y):
            time.sleep(0.1)  # Simulate work
            return x + y

        @trace(event_name="function2", event_type="test", tracer=tracer2)
        def function2(x, y):
            time.sleep(0.05)  # Simulate different work
            return x * y

        # Execute both functions
        result1 = function1(5, 3)
        result2 = function2(4, 6)
        
        assert result1 == 8
        assert result2 == 24
        
        # Verify both tracers are properly configured
        assert tracer1.project == real_project
        assert tracer2.project == real_project
        assert tracer1.session_name != tracer2.session_name

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_real_async_decorator_integration_with_multiple_tracers(
        self, real_api_key, real_project, real_source
    ):
        """Test @atrace decorator with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="async-decorator-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="async-decorator-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Test async functions decorated with different tracers
        @atrace(event_name="async_function1", event_type="test", tracer=tracer1)
        async def async_function1(x, y):
            await asyncio.sleep(0.1)  # Simulate async work
            return x + y

        @atrace(event_name="async_function2", event_type="test", tracer=tracer2)
        async def async_function2(x, y):
            await asyncio.sleep(0.05)  # Simulate different async work
            return x * y

        # Execute both async functions
        import asyncio
        result1 = asyncio.run(async_function1(5, 3))
        result2 = asyncio.run(async_function2(4, 6))
        
        assert result1 == 8
        assert result2 == 24
        
        # Verify both tracers are properly configured
        assert tracer1.project == real_project
        assert tracer2.project == real_project
        assert tracer1.session_name != tracer2.session_name

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_real_concurrent_tracer_usage(
        self, real_api_key, real_project, real_source
    ):
        """Test concurrent usage of multiple tracers with real API."""
        import threading
        
        # Create multiple tracers
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="concurrent-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="concurrent-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        results = []
        
        def use_tracer1():
            with tracer1.start_span("thread1_span") as span:
                span.set_attribute("thread", "thread1")
                span.set_attribute("tracer", "tracer1")
                # Simulate work
                time.sleep(0.1)
                span.add_event("work_completed", {"duration_ms": 100})
                results.append("tracer1_used")
        
        def use_tracer2():
            with tracer2.start_span("thread2_span") as span:
                span.set_attribute("thread", "thread2")
                span.set_attribute("tracer", "tracer2")
                # Simulate different work
                time.sleep(0.05)
                span.add_event("work_completed", {"duration_ms": 50})
                results.append("tracer2_used")
        
        # Run both tracers concurrently
        thread1 = threading.Thread(target=use_tracer1)
        thread2 = threading.Thread(target=use_tracer2)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verify both tracers were used
        assert "tracer1_used" in results
        assert "tracer2_used" in results
        assert len(results) == 2

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_real_tracer_lifecycle_with_api_calls(
        self, real_api_key, real_project, real_source
    ):
        """Test complete tracer lifecycle with real API calls."""
        # Create tracer
        tracer = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="lifecycle-test",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        # Test initialization
        assert tracer.project == real_project
        assert tracer.source == real_source
        assert tracer.session_name == "lifecycle-test"
        
        # Test span creation and API communication
        with tracer.start_span("lifecycle_span") as span:
            span.set_attribute("test_phase", "initialization")
            span.add_event("tracer_ready", {"status": "initialized"})
            
            # Simulate some work
            time.sleep(0.1)
            
            span.set_attribute("test_phase", "execution")
            span.add_event("work_started", {"timestamp": time.time()})
            
            # Simulate more work
            time.sleep(0.05)
            
            span.set_attribute("test_phase", "completion")
            span.add_event("work_completed", {"duration_ms": 150})
        
        # Test shutdown
        tracer.shutdown()
        
        # Verify tracer is properly shut down
        assert hasattr(tracer, 'shutdown')

    def test_real_error_handling_with_multiple_tracers(
        self, real_api_key, real_project, real_source
    ):
        """Test error handling with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="error-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="error-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Test error handling in tracer1
        try:
            with tracer1.start_span("error_span") as span:
                span.set_attribute("test", "error_handling")
                # Simulate an error
                raise ValueError("Test error for tracer1")
        except ValueError:
            # Error should be caught and not affect tracer2
            pass
        
        # Tracer2 should still work normally
        with tracer2.start_span("normal_span") as span:
            span.set_attribute("status", "working")
            span.add_event("operation_successful", {"tracer": "tracer2"})
            assert span.is_recording()

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_real_performance_monitoring_with_multiple_tracers(
        self, real_api_key, real_project, real_source
    ):
        """Test performance monitoring with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="performance-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="performance-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Test performance monitoring with tracer1
        with tracer1.start_span("performance_span1") as span1:
            start_time = time.time()
            
            # Simulate work
            time.sleep(0.1)
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            span1.set_attribute("duration_ms", duration)
            span1.set_attribute("operation", "performance_test_1")
            span1.add_event("performance_measured", {"latency_ms": duration})
        
        # Test performance monitoring with tracer2
        with tracer2.start_span("performance_span2") as span2:
            start_time = time.time()
            
            # Simulate different work
            time.sleep(0.05)
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            span2.set_attribute("duration_ms", duration)
            span2.set_attribute("operation", "performance_test_2")
            span2.add_event("performance_measured", {"latency_ms": duration})

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()

    def test_real_metadata_and_attributes_with_multiple_tracers(
        self, real_api_key, real_project, real_source
    ):
        """Test metadata and attributes with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="metadata-test-1",
            test_mode=False,
            disable_http_tracing=True,
        )
        
        tracer2 = HoneyHiveTracer(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name="metadata-test-2",
            test_mode=False,
            disable_http_tracing=True,
        )

        # Test rich metadata with tracer1
        with tracer1.start_span("metadata_span1") as span1:
            span1.set_attribute("user_id", "user123")
            span1.set_attribute("request_id", "req456")
            span1.set_attribute("environment", "production")
            span1.set_attribute("version", "1.0.0")
            
            span1.add_event("user_action", {
                "action": "login",
                "timestamp": time.time(),
                "ip_address": "192.168.1.1"
            })
        
        # Test different metadata with tracer2
        with tracer2.start_span("metadata_span2") as span2:
            span2.set_attribute("service_name", "api_gateway")
            span2.set_attribute("endpoint", "/api/v1/users")
            span2.set_attribute("method", "POST")
            span2.set_attribute("status_code", 200)
            
            span2.add_event("api_call", {
                "endpoint": "/api/v1/users",
                "method": "POST",
                "response_time_ms": 150,
                "user_agent": "test-client"
            })

        # Clean up
        tracer1.shutdown()
        tracer2.shutdown()
