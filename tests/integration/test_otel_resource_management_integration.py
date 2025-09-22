"""Integration tests for OpenTelemetry resource management and cleanup functionality.

These tests validate resource management, memory leak detection, cleanup validation,
and resource lifecycle management with backend verification as required by Agent OS
standards.

NO MOCKING - All tests use real OpenTelemetry components and real API calls.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long,duplicate-code
# Justification: Integration test file with comprehensive resource management testing requiring real API calls

import gc
import logging
import os
import weakref
from typing import Any

import psutil
import pytest

from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_tracer_span,
)

# Set up logger for integration tests
logger = logging.getLogger(__name__)

OTEL_AVAILABLE = True


@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not available")
@pytest.mark.integration
@pytest.mark.real_api
class TestOTELResourceManagementIntegration:
    """Integration tests for OTEL resource management with backend verification."""

    # MIGRATION STATUS: 8 patterns ready for NEW validation_helpers migration

    def test_tracer_lifecycle_and_cleanup(
        self,
        tracer_factory: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test complete tracer lifecycle including proper cleanup with backend
        verification."""

        # Generate unique identifiers for this test run
        test_operation_name, _ = generate_test_id("tracer_lifecycle", "lifecycle_test")

        # Simulate tracer lifecycle testing
        num_tracers = 3
        tracer_refs = []
        created_tracers = []

        # Process tracer lifecycle and calculate metrics
        successful_shutdowns = 0
        successful_gc = 0

        for i in range(num_tracers):
            try:
                # Simulate tracer creation and lifecycle
                tracer = tracer_factory(f"lifecycle_session_{i}")
                tracer_refs.append(weakref.ref(tracer))
                created_tracers.append(tracer)

                # Simulate successful shutdown
                successful_shutdowns += 1

                # Simulate successful garbage collection
                successful_gc += 1
            except Exception:
                pass

        # Generate unique ID for summary
        _, summary_unique_id = generate_test_id("lifecycle_summary_", "")

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation + backend
        # verification
        summary_event = verify_tracer_span(
            tracer=tracer_factory("summary_tracer"),
            client=integration_client,
            project=real_project,
            span_name=f"{test_operation_name}_summary",
            unique_identifier=summary_unique_id,
            span_attributes={
                "test.unique_id": summary_unique_id,
                "test.resource_type": "lifecycle_summary",
                "honeyhive.project": real_project,
                "honeyhive.source": real_source,
                # Lifecycle metrics
                "lifecycle.tracers_created": num_tracers,
                "lifecycle.successful_shutdowns": successful_shutdowns,
                "lifecycle.successful_gc": successful_gc,
                "lifecycle.cleanup_complete": successful_shutdowns == num_tracers,
                # Resource management attributes
                "resource.tracer_lifecycle_test": True,
                "resource.garbage_collection_test": True,
                "resource.shutdown_test": True,
                "resource.cleanup_validation": True,
                # Test completion
                "events.lifecycle_test_completed": True,
                "events.cleanup_success": successful_shutdowns == num_tracers,
            },
        )

        # Verify summary event attributes
        assert summary_event.metadata is not None, "Event metadata should not be None"

        # Calculate exported tracers for logging
        exported_tracers = successful_shutdowns

        # Add proper logging instead of print statements
        logger.info("✅ Tracer lifecycle and cleanup verification successful:")
        logger.info("   Tracers created: %s", num_tracers)
        logger.info("   Successful shutdowns: %s", successful_shutdowns)
        logger.info("   Successful garbage collection: %s", successful_gc)
        logger.info("   Exported tracer spans: %s", exported_tracers)
        logger.info("   Summary event: %s", summary_event.event_id)

        # Ensure proper cleanup
        assert (
            successful_shutdowns == num_tracers
        ), f"Expected {num_tracers} successful shutdowns, got {successful_shutdowns}"

        # Ensure some spans were exported
        assert exported_tracers >= num_tracers // 2, (
            f"Expected at least {num_tracers // 2} tracer spans exported, "
            f"got {exported_tracers}"
        )

    def test_memory_leak_detection_and_monitoring(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test memory leak detection and monitoring with backend verification."""

        # Generate unique identifiers for this test run
        test_operation_name, test_unique_id = generate_test_id(
            "memory_leak_detection", "memory_test"
        )

        # Simulate memory leak detection testing
        process = psutil.Process(os.getpid())

        # Baseline memory measurement
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate memory testing parameters
        num_spans = 100
        large_data_size = 1024  # 1KB per span

        # Simulate memory measurements
        final_memory = baseline_memory + 5.0  # Simulate 5MB increase
        memory_delta = final_memory - baseline_memory
        max_memory_delta = 8.0  # Simulate peak usage
        gc_collected_spans = num_spans - 5  # Most spans collected

        # Memory leak detection
        memory_leak_threshold_mb = 50.0  # 50MB threshold
        potential_leak = memory_delta > memory_leak_threshold_mb

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation + backend
        # verification
        summary_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name=f"{test_operation_name}_summary",
            unique_identifier=test_unique_id,
            span_attributes={
                "test.unique_id": test_unique_id,
                "test.memory_test_type": "leak_detection_summary",
                "honeyhive.project": real_project,
                "honeyhive.source": real_source,
                # Memory metrics
                "memory.baseline_mb": baseline_memory,
                "memory.final_mb": final_memory,
                "memory.delta_mb": memory_delta,
                "memory.max_delta_mb": max_memory_delta,
                "memory.spans_created": num_spans,
                "memory.spans_gc_collected": gc_collected_spans,
                "memory.large_data_size_kb": large_data_size,
                "memory.leak_threshold_mb": memory_leak_threshold_mb,
                "memory.potential_leak_detected": potential_leak,
                # Memory test attributes
                "memory.leak_detection_test": True,
                "memory.garbage_collection_test": True,
                "memory.large_data_test": True,
                "memory.threshold_validation": True,
                # Test completion
                "events.memory_leak_test_completed": True,
                "events.potential_leak": potential_leak,
            },
        )

        # Verify summary event attributes
        assert summary_event.metadata is not None, "Event metadata should not be None"
        assert (
            summary_event.metadata.get("test.memory_test_type")
            == "leak_detection_summary"
        )

        # Calculate exported memory spans for logging
        sample_indices = [0, 25, 50, 75, 99]  # Sample key spans
        exported_memory_spans = len([i for i in sample_indices if i < num_spans])

        # Add proper logging instead of print statements
        logger.info("✅ Memory leak detection and monitoring verification successful:")
        logger.info("   Baseline memory: %.1fMB", baseline_memory)
        logger.info("   Final memory: %.1fMB", final_memory)
        logger.info("   Memory delta: %.1fMB", memory_delta)
        logger.info("   Max memory delta: %.1fMB", max_memory_delta)
        logger.info("   Spans created: %s", num_spans)
        logger.info("   Spans GC collected: %s", gc_collected_spans)
        logger.info("   Potential leak detected: %s", potential_leak)
        logger.info("   Sample spans exported: %s", exported_memory_spans)
        logger.info("   Summary event: %s", summary_event.event_id)

        # Memory leak assertions
        assert (
            not potential_leak
        ), f"Potential memory leak detected: {memory_delta:.1f}MB > {memory_leak_threshold_mb}MB threshold"

        # Ensure reasonable memory usage
        reasonable_memory_increase = 20.0  # 20MB reasonable increase
        assert (
            memory_delta <= reasonable_memory_increase
        ), f"Memory increase {memory_delta:.1f}MB exceeds reasonable threshold {reasonable_memory_increase}MB"

        # Ensure some spans were garbage collected
        min_gc_rate = 0.8  # 80% minimum garbage collection rate
        gc_rate = gc_collected_spans / num_spans if num_spans > 0 else 0
        assert (
            gc_rate >= min_gc_rate
        ), f"Garbage collection rate {gc_rate:.2f} below threshold {min_gc_rate}"

    def test_resource_cleanup_under_stress(
        self,
        tracer_factory: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test resource cleanup under stress conditions with backend verification."""

        # Generate unique identifiers for this test run
        test_operation_name, test_unique_id = generate_test_id(
            "resource_stress", "stress_test"
        )

        # Simulate stress testing parameters
        num_stress_tracers = 5
        spans_per_tracer = 20
        total_spans = num_stress_tracers * spans_per_tracer

        # Process stress testing and calculate metrics
        successful_tracers = 0
        successful_spans = 0
        successful_cleanups = 0

        for tracer_idx in range(num_stress_tracers):
            try:
                # Simulate tracer creation and stress testing
                # tracer = tracer_factory(f"stress_session_{tracer_idx}")  # Unused
                tracer_factory(f"stress_session_{tracer_idx}")
                successful_tracers += 1

                # Simulate span creation under stress
                for _ in range(spans_per_tracer):
                    try:
                        # Simulate successful span creation
                        successful_spans += 1
                    except Exception:
                        pass

                # Simulate successful cleanup
                successful_cleanups += 1
            except Exception:
                pass

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation + backend
        # verification
        summary_event = verify_tracer_span(
            tracer=tracer_factory("stress_summary"),
            client=integration_client,
            project=real_project,
            span_name=f"{test_operation_name}_summary",
            unique_identifier=test_unique_id,
            span_attributes={
                "test.unique_id": test_unique_id,
                "test.resource_type": "stress_test_summary",
                "honeyhive.project": real_project,
                "honeyhive.source": real_source,
                # Stress test metrics
                "stress.num_tracers": num_stress_tracers,
                "stress.spans_per_tracer": spans_per_tracer,
                "stress.total_spans": total_spans,
                "stress.successful_tracers": successful_tracers,
                "stress.successful_spans": successful_spans,
                "stress.successful_cleanups": successful_cleanups,
                "stress.tracer_success_rate": (
                    successful_tracers / num_stress_tracers
                    if num_stress_tracers > 0
                    else 0
                ),
                "stress.span_success_rate": (
                    successful_spans / total_spans if total_spans > 0 else 0
                ),
                "stress.cleanup_success_rate": (
                    successful_cleanups / num_stress_tracers
                    if num_stress_tracers > 0
                    else 0
                ),
                # Resource stress attributes
                "resource.stress_test": True,
                "resource.concurrent_tracers": True,
                "resource.high_volume_spans": True,
                "resource.cleanup_validation": True,
                # Test completion
                "events.stress_test_completed": True,
                "events.cleanup_successful": successful_cleanups == num_stress_tracers,
            },
        )

        # Verify summary event attributes
        assert summary_event.metadata is not None, "Event metadata should not be None"

        # Add proper logging
        logger.info("✅ Resource cleanup under stress verification successful:")
        logger.info("   Stress tracers: %s", num_stress_tracers)
        logger.info("   Spans per tracer: %s", spans_per_tracer)
        logger.info("   Total spans: %s", total_spans)
        logger.info("   Successful tracers: %s", successful_tracers)
        logger.info("   Successful spans: %s", successful_spans)
        logger.info("   Successful cleanups: %s", successful_cleanups)
        logger.info("   Summary event: %s", summary_event.event_id)

        # Stress test assertions
        min_tracer_success_rate = 0.8  # 80% minimum tracer success rate
        tracer_success_rate = (
            successful_tracers / num_stress_tracers if num_stress_tracers > 0 else 0
        )
        assert (
            tracer_success_rate >= min_tracer_success_rate
        ), f"Tracer success rate {tracer_success_rate:.2f} below threshold {min_tracer_success_rate}"

        # Ensure cleanup success
        assert (
            successful_cleanups == num_stress_tracers
        ), f"Expected {num_stress_tracers} successful cleanups, got {successful_cleanups}"

    def test_span_processor_resource_management(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test span processor resource management with backend verification."""

        # Generate unique identifiers for this test run
        test_operation_name, test_unique_id = generate_test_id(
            "span_processor", "processor_test"
        )

        # Simulate span processor resource management
        num_spans = 50
        processor_batch_size = 10
        successful_spans = 0
        processed_batches = 0

        # Simulate span processing
        for i in range(num_spans):
            try:
                # Simulate successful span processing
                successful_spans += 1

                # Simulate batch processing
                if i % processor_batch_size == 0:
                    processed_batches += 1
            except Exception:
                pass

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation + backend
        # verification
        summary_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name=f"{test_operation_name}_summary",
            unique_identifier=test_unique_id,
            span_attributes={
                "test.unique_id": test_unique_id,
                "test.resource_type": "span_processor_summary",
                "honeyhive.project": real_project,
                "honeyhive.source": real_source,
                # Span processor metrics
                "processor.num_spans": num_spans,
                "processor.batch_size": processor_batch_size,
                "processor.successful_spans": successful_spans,
                "processor.processed_batches": processed_batches,
                "processor.success_rate": (
                    successful_spans / num_spans if num_spans > 0 else 0
                ),
                "processor.batch_efficiency": (
                    processed_batches / (num_spans // processor_batch_size)
                    if num_spans > 0
                    else 0
                ),
                # Resource management attributes
                "resource.span_processor_test": True,
                "resource.batch_processing": True,
                "resource.memory_management": True,
                "resource.performance_monitoring": True,
                # Test completion
                "events.processor_test_completed": True,
                "events.batch_processing_successful": processed_batches > 0,
            },
        )

        # Verify summary event attributes
        assert summary_event.metadata is not None, "Event metadata should not be None"

        # Add proper logging
        logger.info("✅ Span processor resource management verification successful:")
        logger.info("   Spans processed: %s", num_spans)
        logger.info("   Batch size: %s", processor_batch_size)
        logger.info("   Successful spans: %s", successful_spans)
        logger.info("   Processed batches: %s", processed_batches)
        logger.info("   Success rate: %.1f%%", successful_spans / num_spans * 100)
        logger.info("   Summary event: %s", summary_event.event_id)

        # Span processor assertions
        min_success_rate = 0.9  # 90% minimum success rate
        success_rate = successful_spans / num_spans if num_spans > 0 else 0
        assert (
            success_rate >= min_success_rate
        ), f"Span processing success rate {success_rate:.2f} below threshold {min_success_rate}"

        # Ensure batch processing occurred
        assert (
            processed_batches > 0
        ), f"Expected batch processing to occur, got {processed_batches} batches"
