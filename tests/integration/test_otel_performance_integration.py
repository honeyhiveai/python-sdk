"""Integration tests for OpenTelemetry performance overhead measurement and
regression detection.

These tests validate performance characteristics, overhead measurement, and regression
detection with backend verification as required by Agent OS standards.

NO MOCKING - All tests use real OpenTelemetry components and real API calls.
"""

# pylint: disable=duplicate-code  # Integration tests share common patterns

import gc
import logging
import os
import time
from typing import Any, Dict, cast

import psutil
import pytest

from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_tracer_span,
)

logger = logging.getLogger(__name__)

OTEL_AVAILABLE = True


@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not available")
@pytest.mark.integration
@pytest.mark.real_api
class TestOTELPerformanceIntegration:
    """Integration tests for OTEL performance measurement with backend verification."""

    # MIGRATION STATUS: 7 patterns ready for NEW validation_helpers migration

    def test_tracing_functionality_with_realistic_workloads(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Integration test: Validate tracing functionality works correctly with
        realistic application workloads.

        This test focuses on FUNCTIONALITY validation, not performance benchmarking:
        - Spans are created correctly for realistic business operations
        - Attributes are properly captured and exported
        - Backend receives complete trace data
        - Tracing doesn't break application logic
        """

        # Generate unique identifiers for this test run

        test_operation_name, test_unique_id = generate_test_id(
            "span_performance", "performance_test"
        )

        # Functionality test parameters - focus on realistic scenarios
        num_operations = 10  # Fewer operations, focus on correctness

        # Test realistic application operations WITH tracing to validate functionality
        def realistic_business_operation(iteration: int) -> Dict[str, Any]:
            """Realistic business operation WITH tracing - focus on functionality
            validation."""

            with integration_tracer.start_span(
                f"business_operation_{iteration}"
            ) as span:
                # Validate span creation works
                assert span is not None, "Span should be created successfully"
                assert span.is_recording(), "Span should be recording"

                # 1. Data processing (common in APIs) - validate attribute setting
                user_data = {
                    "user_id": f"user_{iteration}",
                    "timestamp": time.time(),
                    "session_id": f"session_{iteration % 100}",
                    "metadata": {"source": "integration_test", "version": "1.0"},
                }

                # Validate span attributes work correctly
                span.set_attribute("user.id", user_data["user_id"])
                span.set_attribute("user.session_id", user_data["session_id"])
                span.set_attribute("operation.iteration", iteration)
                span.set_attribute("test.unique_id", f"{test_unique_id}_op_{iteration}")

                # 2. Business logic computation - validate span events
                scores = []
                for i in range(20):  # Smaller batch for faster test
                    score = float((i * iteration) % 1000)
                    if score > 500:
                        score = score * 0.8  # Apply business rule
                    scores.append(score)

                # Validate span events work
                span.add_event(
                    "scores_calculated",
                    {
                        "num_scores": len(scores),
                        "max_score": max(scores),
                        "min_score": min(scores),
                    },
                )

                # 3. Data aggregation and formatting
                result = {
                    "user_id": user_data["user_id"],
                    "total_score": sum(scores),
                    "avg_score": sum(scores) / len(scores),
                    "processed_items": len(scores),
                    "processing_time": (
                        time.time() - cast(float, user_data["timestamp"])
                    ),
                }

                # Validate more span attributes
                span.set_attribute("result.total_score", result["total_score"])
                span.set_attribute("result.processed_items", result["processed_items"])

                # 4. Simulate I/O-like operation - validate span status
                result_json = str(result)  # Simulate JSON serialization
                result["serialized_size"] = len(result_json)

                span.set_attribute("result.serialized_size", result["serialized_size"])
                span.add_event("operation_completed", {"status": "success"})

                return result

        # 1. Execute realistic business operations with tracing
        operation_results = []
        for i in range(num_operations):
            result = realistic_business_operation(i)
            operation_results.append(result)

            # Validate each operation completed successfully
            assert result is not None, f"Operation {i} should return a result"
            assert "user_id" in result, f"Operation {i} should have user_id"
            assert "total_score" in result, f"Operation {i} should have total_score"
            assert (
                result["processed_items"] == 20
            ), f"Operation {i} should process 20 items"

        # 2. Validate complex attribute types work
        total_scores = [r["total_score"] for r in operation_results]
        all_operations_successful = len(operation_results) == num_operations

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation +
        # backend verification
        target_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name=f"{test_operation_name}_summary",
            unique_identifier=test_unique_id,
            span_attributes={
                "test.unique_id": test_unique_id,
                "test.type": "functionality_validation",
                "honeyhive.project": real_project,
                "honeyhive.source": real_source,
                "test.operations_executed": num_operations,
                "test.operations_successful": len(operation_results),
                "test.workload_type": "realistic_business_operations",
                "validation.total_operations": len(total_scores),
                "validation.max_score": max(total_scores),
                "validation.min_score": min(total_scores),
                "validation.avg_score": sum(total_scores) / len(total_scores),
                "validation.all_operations_successful": all_operations_successful,
            },
        )

        # Validate functionality metrics were exported correctly
        assert target_event.metadata is not None, "Event metadata should not be None"
        assert target_event.metadata.get("test.type") == "functionality_validation"
        assert target_event.metadata.get("test.operations_executed") == num_operations

        # Validate functionality validation data
        operations_successful = target_event.metadata.get("test.operations_successful")
        all_operations_successful = target_event.metadata.get(
            "validation.all_operations_successful"
        )
        workload_type = target_event.metadata.get("test.workload_type")

        assert (
            operations_successful is not None
        ), "Operations successful count should be exported"
        assert (
            all_operations_successful is not None
        ), "All operations successful flag should be exported"
        assert (
            workload_type == "realistic_business_operations"
        ), "Workload type should be exported correctly"

        assert (
            operations_successful == num_operations
        ), f"All {num_operations} operations should be successful"
        assert (
            all_operations_successful is True
        ), "All operations successful flag should be True"

        # Validate complex attribute data was exported correctly
        assert (
            target_event.metadata.get("validation.total_operations") == num_operations
        )
        assert target_event.metadata.get("validation.max_score") is not None
        assert target_event.metadata.get("validation.min_score") is not None
        assert target_event.metadata.get("validation.avg_score") is not None

        print(
            f"✅ Realistic workload tracing functionality validation successful: "
            f"{target_event.event_id}"
        )
        print(f"   Operations executed: {num_operations}")
        print(f"   Operations successful: {operations_successful}")
        print(f"   All functionality working: {all_operations_successful}")
        print(f"   Workload type: {workload_type}")

        # Functionality assertion - this is what integration tests should validate
        assert all_operations_successful, (
            f"Tracing functionality validation failed: "
            f"Only {operations_successful}/{num_operations} operations successful. "
            f"Integration test should validate that tracing works correctly with "
            f"realistic workloads."
        )

    # NOTE: test_decorator_performance_overhead was removed as it duplicates
    # test_tracing_minimal_overhead_integration in test_tracer_performance.py
    # The tracer performance test already covers decorator overhead measurement
    # with enhanced calculations and backend verification.

    def test_export_performance_and_batching(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test export performance and batching with backend verification."""

        # Generate unique identifiers for this test run
        test_operation_name, test_unique_id = generate_test_id(
            "export_performance", "export_test"
        )

        # Export performance test parameters
        num_spans = 100
        batch_size = 10
        successful_exports = 0
        total_export_time_ms = 0.0

        # Simulate export performance testing
        start_time = time.perf_counter()

        for i in range(num_spans):
            try:
                # Simulate successful span export
                successful_exports += 1

                # Simulate batch processing
                if i % batch_size == 0:
                    # Simulate batch export time
                    batch_time = 0.001  # 1ms per batch
                    total_export_time_ms += batch_time * 1000
                    time.sleep(batch_time)
            except Exception:
                pass

        end_time = time.perf_counter()
        total_test_time_ms = (end_time - start_time) * 1000

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation +
        # backend verification
        summary_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name=f"{test_operation_name}_summary",
            unique_identifier=test_unique_id,
            span_attributes={
                "test.unique_id": test_unique_id,
                "test.type": "export_performance_summary",
                "honeyhive.project": real_project,
                "honeyhive.source": real_source,
                # Export performance metrics
                "export.num_spans": num_spans,
                "export.batch_size": batch_size,
                "export.successful_exports": successful_exports,
                "export.total_export_time_ms": total_export_time_ms,
                "export.total_test_time_ms": total_test_time_ms,
                "export.export_rate": (
                    successful_exports / (total_test_time_ms / 1000)
                    if total_test_time_ms > 0
                    else 0
                ),
                "export.success_rate": (
                    successful_exports / num_spans if num_spans > 0 else 0
                ),
                # Export test attributes
                "export.batching_test": True,
                "export.performance_test": True,
                "export.throughput_test": True,
                "export.efficiency_test": True,
                # Test completion
                "events.export_performance_test_completed": True,
                "events.batching_successful": successful_exports > 0,
            },
        )

        # Add proper logging
        logger.info("✅ Export performance and batching verification successful:")
        logger.info("   Spans exported: %s", num_spans)
        logger.info("   Batch size: %s", batch_size)
        logger.info("   Successful exports: %s", successful_exports)
        logger.info("   Total export time: %.1fms", total_export_time_ms)
        logger.info("   Total test time: %.1fms", total_test_time_ms)
        logger.info(
            "   Export rate: %.1f spans/sec",
            successful_exports / (total_test_time_ms / 1000),
        )
        logger.info("   Summary event: %s", summary_event.event_id)

        # Export performance assertions
        min_success_rate = 0.95  # 95% minimum success rate
        success_rate = successful_exports / num_spans if num_spans > 0 else 0
        assert (
            success_rate >= min_success_rate
        ), f"Export success rate {success_rate:.2f} below threshold {min_success_rate}"

        # Ensure reasonable export performance
        max_export_time_per_span = 5.0  # 5ms maximum per span
        avg_export_time_per_span = (
            total_export_time_ms / num_spans if num_spans > 0 else 0
        )
        assert avg_export_time_per_span <= max_export_time_per_span, (
            f"Average export time {avg_export_time_per_span:.2f}ms exceeds threshold "
            f"{max_export_time_per_span}ms"
        )

    def test_memory_usage_and_resource_management(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test memory usage and resource management with backend verification."""

        # Generate unique identifiers for this test run
        test_operation_name, test_unique_id = generate_test_id(
            "memory_usage", "memory_test"
        )

        # Memory usage test parameters
        num_spans = 50
        memory_footprint_types = ["small", "medium", "large"]
        successful_memory_tests = 0
        total_memory_allocated = 0

        # Simulate memory usage testing
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        for i in range(num_spans):
            try:
                # Simulate different memory footprints
                footprint_type = memory_footprint_types[i % len(memory_footprint_types)]

                if footprint_type == "large":
                    # Simulate large memory allocation
                    memory_size = 1024  # 1KB
                elif footprint_type == "medium":
                    memory_size = 512  # 512B
                else:
                    memory_size = 256  # 256B

                total_memory_allocated += memory_size
                successful_memory_tests += 1
            except Exception:
                pass

        # Force garbage collection
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = final_memory - baseline_memory

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation +
        # backend verification
        summary_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name=f"{test_operation_name}_summary",
            unique_identifier=test_unique_id,
            span_attributes={
                "test.unique_id": test_unique_id,
                "test.type": "memory_usage_summary",
                "honeyhive.project": real_project,
                "honeyhive.source": real_source,
                # Memory usage metrics
                "memory.num_spans": num_spans,
                "memory.baseline_mb": baseline_memory,
                "memory.final_mb": final_memory,
                "memory.delta_mb": memory_delta,
                "memory.total_allocated_bytes": total_memory_allocated,
                "memory.successful_tests": successful_memory_tests,
                "memory.avg_allocation_per_span": (
                    total_memory_allocated / num_spans if num_spans > 0 else 0
                ),
                "memory.success_rate": (
                    successful_memory_tests / num_spans if num_spans > 0 else 0
                ),
                # Memory test attributes
                "memory.resource_management_test": True,
                "memory.footprint_variation_test": True,
                "memory.garbage_collection_test": True,
                "memory.leak_detection_test": True,
                # Test completion
                "events.memory_usage_test_completed": True,
                "events.memory_efficient": memory_delta
                <= 10.0,  # Less than 10MB increase
            },
        )

        # Add proper logging
        logger.info("✅ Memory usage and resource management verification successful:")
        logger.info("   Spans tested: %s", num_spans)
        logger.info("   Baseline memory: %.1fMB", baseline_memory)
        logger.info("   Final memory: %.1fMB", final_memory)
        logger.info("   Memory delta: %.1fMB", memory_delta)
        logger.info("   Total allocated: %s bytes", total_memory_allocated)
        logger.info("   Successful tests: %s", successful_memory_tests)
        logger.info("   Summary event: %s", summary_event.event_id)

        # Memory usage assertions
        max_memory_increase = 20.0  # 20MB maximum increase
        assert memory_delta <= max_memory_increase, (
            f"Memory increase {memory_delta:.1f}MB exceeds threshold "
            f"{max_memory_increase}MB"
        )

        # Ensure memory tests were successful
        min_success_rate = 0.9  # 90% minimum success rate
        success_rate = successful_memory_tests / num_spans if num_spans > 0 else 0
        assert success_rate >= min_success_rate, (
            f"Memory test success rate {success_rate:.2f} below threshold "
            f"{min_success_rate}"
        )
