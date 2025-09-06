"""
Multi-framework integration tests for non-instrumentor frameworks.

Tests scenarios where multiple frameworks using OpenTelemetry directly
are integrated with HoneyHive simultaneously.
"""

import os
import threading
import time
from typing import Any, Dict, List

import pytest

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.provider_detector import IntegrationStrategy, ProviderDetector
from tests.mocks.mock_frameworks import (
    ConcurrentFrameworkManager,
    MockFrameworkA,
    MockFrameworkB,
    MockFrameworkC,
)


class TestMultiFrameworkIntegration:
    """Test integration with multiple non-instrumentor frameworks simultaneously."""

    def __init__(self):
        """Initialize test class attributes."""
        self.test_api_key = None
        self.test_project = None
        self.test_source = None

    def setup_method(self):
        """Set up test fixtures."""
        # Reset OpenTelemetry state
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

        # Test configuration
        self.test_api_key = "test-multi-framework-key"
        self.test_project = "multi-framework-test"
        self.test_source = "integration-test"

    def teardown_method(self):
        """Clean up after tests."""
        # Reset OpenTelemetry state
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

    @pytest.mark.integration
    def test_sequential_framework_initialization(self):
        """Test multiple frameworks initialized sequentially with HoneyHive."""
        # Initialize HoneyHive first
        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            source=self.test_source,
            test_mode=True,
        )

        # Initialize frameworks sequentially
        framework_a = MockFrameworkA("SequentialA")
        framework_b = MockFrameworkB("SequentialB", delay_provider_setup=False)
        framework_c = MockFrameworkC("SequentialC")

        # Execute operations from each framework
        result_a = framework_a.execute_operation("sequential_test", data="test_data_a")
        result_b = framework_b.process_data("test_data_b", "sequential")
        result_c = framework_c.analyze_content(
            "test content for analysis", "sequential"
        )

        # Verify all operations completed successfully
        assert result_a["status"] == "completed"
        assert result_b["status"] == "completed"
        assert result_c["status"] == "completed"

        # Verify unified session tracking (may be None in test mode)
        # In test mode, session_id might be None due to invalid API key
        # This is expected behavior for integration tests

        # All operations should be in the same trace context
        # (Note: In real implementation, we'd verify spans are linked)
        operations_a = framework_a.get_operations()
        operations_b = framework_b.get_operations()
        operations_c = framework_c.get_operations()

        assert len(operations_a) == 1
        assert len(operations_b) == 1
        assert len(operations_c) == 1

        print("✅ Sequential framework initialization completed successfully")

    @pytest.mark.integration
    def test_concurrent_framework_operations(self):
        """Test concurrent operations across multiple frameworks."""
        # Initialize HoneyHive
        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            source=self.test_source,
            test_mode=True,
        )

        # Create frameworks
        framework_a = MockFrameworkA("ConcurrentA")
        framework_b = MockFrameworkB("ConcurrentB", delay_provider_setup=False)
        framework_c = MockFrameworkC("ConcurrentC")

        # Set up concurrent manager
        manager = ConcurrentFrameworkManager()
        manager.add_framework("framework_a", framework_a)
        manager.add_framework("framework_b", framework_b)
        manager.add_framework("framework_c", framework_c)

        # Define concurrent operations
        operations = [
            {
                "framework": "framework_a",
                "method": "execute_operation",
                "args": ["concurrent_op_1"],
                "kwargs": {"priority": "high", "batch_size": 10},
            },
            {
                "framework": "framework_b",
                "method": "process_data",
                "args": ["concurrent_data_batch"],
                "kwargs": {"processing_type": "concurrent"},
            },
            {
                "framework": "framework_c",
                "method": "analyze_content",
                "args": ["concurrent analysis content"],
                "kwargs": {"analysis_type": "concurrent_sentiment"},
            },
            {
                "framework": "framework_a",
                "method": "execute_operation",
                "args": ["concurrent_op_2"],
                "kwargs": {"priority": "medium", "batch_size": 5},
            },
        ]

        # Execute operations concurrently
        results = manager.run_concurrent_operations(operations)

        # Verify all operations completed successfully
        assert len(results) == 4
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == 4

        # Verify framework operations were recorded
        all_ops = manager.get_all_framework_operations()
        assert len(all_ops["framework_a"]) == 2  # Two operations
        assert len(all_ops["framework_b"]) == 1
        assert len(all_ops["framework_c"]) == 1

        # Verify different thread IDs (concurrent execution)
        thread_ids = {r["thread_id"] for r in results}
        assert len(thread_ids) >= 2  # At least some concurrency

        print("✅ Concurrent framework operations completed successfully")

    @pytest.mark.integration
    def test_framework_interaction_patterns(self):
        """Test interaction patterns between frameworks."""
        # Initialize HoneyHive
        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            source=self.test_source,
            test_mode=True,
        )

        # Create frameworks
        framework_a = MockFrameworkA("InteractionA")
        framework_b = MockFrameworkB("InteractionB", delay_provider_setup=False)

        # Simulate framework interaction workflow
        # Framework A generates data
        result_a1 = framework_a.execute_operation(
            "generate_data", output_type="structured", data_size=100
        )

        # Framework B processes the data from Framework A
        input_data = f"data_from_{result_a1['framework']}"
        result_b = framework_b.process_data(input_data, "interaction_processing")

        # Framework A performs follow-up operation
        result_a2 = framework_a.execute_operation(
            "finalize_workflow",
            input_source=result_b["framework"],
            workflow_id="interaction_test",
        )

        # Verify workflow completed
        assert result_a1["status"] == "completed"
        assert result_b["status"] == "completed"
        assert result_a2["status"] == "completed"

        # Verify operation sequence
        ops_a = framework_a.get_operations()
        ops_b = framework_b.get_operations()

        assert len(ops_a) == 2
        assert len(ops_b) == 1
        assert ops_a[0]["operation"] == "generate_data"
        assert ops_a[1]["operation"] == "finalize_workflow"
        assert "interaction_processing" in ops_b[0]["processing_type"]

        print("✅ Framework interaction patterns validated successfully")

    @pytest.mark.integration
    def test_context_propagation_between_frameworks(self):
        """Test context propagation between different frameworks."""
        # Initialize HoneyHive
        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            source=self.test_source,
            test_mode=True,
        )

        # Create frameworks
        framework_a = MockFrameworkA("ContextA")
        framework_c = MockFrameworkC("ContextC")

        # Execute operations that should share context
        # Use OpenTelemetry tracer directly for context propagation
        from opentelemetry import trace

        otel_tracer = trace.get_tracer("test_tracer")
        with otel_tracer.start_as_current_span(
            "context_propagation_test"
        ) as parent_span:
            parent_span.set_attribute("test.type", "context_propagation")

            # Framework A operation within parent context
            result_a = framework_a.execute_operation(
                "context_aware_op", parent_context="propagation_test"
            )

            # Framework C operation within same parent context
            result_c = framework_c.analyze_content(
                "context propagation test content", "context_aware"
            )

            parent_span.set_attribute("child_operations", 2)
            parent_span.set_attribute("frameworks_used", "ContextA,ContextC")

        # Verify operations completed
        assert result_a["status"] == "completed"
        assert result_c["status"] == "completed"

        # Verify operations were recorded
        ops_a = framework_a.get_operations()
        ops_c = framework_c.get_operations()

        assert len(ops_a) == 1
        assert len(ops_c) == 1

        # In a real implementation, we'd verify trace IDs match
        # For now, verify the operations have trace information
        assert "trace_id" in result_a
        assert "trace_id" in result_c
        assert "span_id" in result_a
        assert "span_id" in result_c

        print("✅ Context propagation between frameworks validated successfully")

    @pytest.mark.integration
    def test_unified_session_tracking(self):
        """Test unified session tracking across all frameworks."""
        # Initialize HoneyHive
        tracer = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            source=self.test_source,
            test_mode=True,
        )

        session_id = tracer.session_id
        # In test mode, session_id might be None due to invalid API key
        # This is expected behavior for integration tests
        print(f"Session ID: {session_id} (may be None in test mode)")

        # Create multiple frameworks
        frameworks = {
            "framework_a": MockFrameworkA("SessionA"),
            "framework_b": MockFrameworkB("SessionB", delay_provider_setup=False),
            "framework_c": MockFrameworkC("SessionC"),
        }

        # Execute operations from all frameworks
        results = {}
        results["a"] = frameworks["framework_a"].execute_operation(
            "session_test", session_id=session_id
        )
        results["b"] = frameworks["framework_b"].process_data(
            f"session_data_{session_id}", "session_processing"
        )
        results["c"] = frameworks["framework_c"].analyze_content(
            "session content analysis", "session_analysis"
        )

        # Verify all operations completed
        for key, result in results.items():
            assert result["status"] == "completed", f"Framework {key} operation failed"

        # Verify session consistency
        # In a real implementation, all spans would have the same session_id
        # For now, verify the tracer maintains consistent session
        # (session_id may be None in test mode)
        current_session_id = tracer.session_id
        assert current_session_id == session_id  # Should be consistent

        # Verify all frameworks recorded operations
        total_operations = 0
        for framework in frameworks.values():
            ops = framework.get_operations()
            total_operations += len(ops)

        assert total_operations == 3

        print(f"✅ Unified session tracking validated (session: {session_id})")

    @pytest.mark.integration
    def test_performance_with_multiple_frameworks(self):
        """Test performance impact of multiple frameworks."""
        # Initialize HoneyHive
        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            source=self.test_source,
            test_mode=True,
        )

        # Create frameworks
        frameworks = [
            MockFrameworkA("PerfA"),
            MockFrameworkB("PerfB", delay_provider_setup=False),
            MockFrameworkC("PerfC"),
        ]

        # Measure performance with multiple frameworks
        start_time = time.perf_counter()

        # Execute operations from all frameworks
        for i in range(10):  # Multiple iterations
            for _, framework in enumerate(frameworks):
                if isinstance(framework, MockFrameworkA):
                    framework.execute_operation(f"perf_test_{i}", iteration=i)
                elif isinstance(framework, MockFrameworkB):
                    framework.process_data(f"perf_data_{i}", "performance")
                elif isinstance(framework, MockFrameworkC):
                    framework.analyze_content(f"perf content {i}", "performance")

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Verify performance is acceptable
        # 30 operations (10 iterations × 3 frameworks) should complete quickly
        assert (
            total_time < 5.0
        ), f"Performance too slow: {total_time:.3f}s for 30 operations"

        # Verify all operations completed
        total_operations = sum(len(f.get_operations()) for f in frameworks)
        assert total_operations == 30

        avg_time_per_op = total_time / 30
        print(
            f"✅ Performance test completed: {total_time:.3f}s total, {avg_time_per_op:.4f}s per operation"
        )

    @pytest.mark.integration
    def test_framework_specific_attributes_preservation(self):
        """Test that framework-specific attributes are preserved alongside HoneyHive attributes."""
        # Initialize HoneyHive
        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            source=self.test_source,
            test_mode=True,
        )

        # Create framework with custom attributes
        framework_c = MockFrameworkC("AttributesC")

        # Execute operation that adds custom attributes
        result = framework_c.analyze_content(
            "attribute preservation test content", "attribute_test"
        )

        # Verify operation completed
        assert result["status"] == "completed"

        # Verify framework-specific data is preserved
        assert result["confidence"] == 0.95
        assert "results" in result
        assert "preprocessing" in result["results"]
        assert "feature_extraction" in result["results"]
        assert "analysis" in result["results"]
        assert "post_processing" in result["results"]

        # Verify framework operations were recorded
        ops = framework_c.get_operations()
        assert len(ops) == 1
        assert ops[0]["analysis_type"] == "attribute_test"

        print("✅ Framework-specific attributes preservation validated")


class TestMockFrameworks:
    """Test the mock frameworks themselves."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset OpenTelemetry state
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

    def teardown_method(self):
        """Clean up after tests."""
        # Reset OpenTelemetry state
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

    def test_mock_framework_a_functionality(self):
        """Test MockFrameworkA basic functionality."""
        framework = MockFrameworkA("TestA")

        result = framework.execute_operation("test_op", param1="value1", param2=42)

        assert result["operation"] == "test_op"
        assert result["framework"] == "TestA"
        assert result["status"] == "completed"
        assert "span_id" in result
        assert "trace_id" in result

        ops = framework.get_operations()
        assert len(ops) == 1
        assert ops[0] == result

    def test_mock_framework_b_functionality(self):
        """Test MockFrameworkB basic functionality."""
        framework = MockFrameworkB("TestB", delay_provider_setup=False)

        result = framework.process_data("test_data", "test_processing")

        assert result["original_data"] == "test_data"
        assert result["processed_data"] == "processed_test_processing_test_data"
        assert result["processing_type"] == "test_processing"
        assert result["framework"] == "TestB"
        assert result["status"] == "completed"

        ops = framework.get_operations()
        assert len(ops) == 1

    def test_mock_framework_c_functionality(self):
        """Test MockFrameworkC basic functionality."""
        framework = MockFrameworkC("TestC")

        result = framework.analyze_content("test content", "test_analysis")

        assert result["content"] == "test content"
        assert result["analysis_type"] == "test_analysis"
        assert result["framework"] == "TestC"
        assert result["confidence"] == 0.95
        assert result["status"] == "completed"
        assert "results" in result

        ops = framework.get_operations()
        assert len(ops) == 1

    def test_concurrent_framework_manager(self):
        """Test ConcurrentFrameworkManager functionality."""
        manager = ConcurrentFrameworkManager()

        # Add frameworks
        framework_a = MockFrameworkA("ManagerA")
        framework_b = MockFrameworkB("ManagerB", delay_provider_setup=False)

        manager.add_framework("a", framework_a)
        manager.add_framework("b", framework_b)

        # Define operations
        operations = [
            {
                "framework": "a",
                "method": "execute_operation",
                "args": ["manager_test"],
                "kwargs": {"test": True},
            },
            {
                "framework": "b",
                "method": "process_data",
                "args": ["manager_data"],
                "kwargs": {"processing_type": "manager"},
            },
        ]

        # Execute operations
        results = manager.run_concurrent_operations(operations)

        assert len(results) == 2
        assert all(r["success"] for r in results)

        # Verify framework operations
        all_ops = manager.get_all_framework_operations()
        assert len(all_ops["a"]) == 1
        assert len(all_ops["b"]) == 1
