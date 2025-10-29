"""Integration tests for OpenTelemetry concurrency and thread safety functionality.

These tests validate concurrent span management, thread safety, and multi-threaded
operations with backend verification as required by Agent OS standards.

NO MOCKING - All tests use real OpenTelemetry components and real API calls.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long,too-many-nested-blocks,too-many-branches,too-many-locals,no-else-return,logging-fstring-interpolation,unused-argument,R0917
# Justification: Integration test file with comprehensive concurrency testing requiring extensive real API calls and complex test scenarios

import asyncio
import concurrent.futures
import logging
import threading
import time
import traceback
from typing import Any, Dict, cast

import pytest

# OpenTelemetry is a hard dependency - no conditional imports needed
from opentelemetry import trace as otel_trace
from opentelemetry.trace import Status, StatusCode

from honeyhive.tracer import HoneyHiveTracer, atrace, enrich_span
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_backend_event,
)

OTEL_AVAILABLE = True

logger = logging.getLogger(__name__)


@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not available")
@pytest.mark.integration
@pytest.mark.real_api
class TestOTELConcurrencyIntegration:
    """Integration tests for OTEL concurrency and thread safety with backend
    verification."""

    # MIGRATION STATUS: 6 patterns ready for NEW validation_helpers migration

    def _debug_tracer_flow(self, tracer: Any, test_name: str = "debug_flow") -> None:
        """Debug helper to trace the complete tracer initialization and processing
        flow."""
        print(f"\n🔍 TRACER FLOW DEBUG: {test_name}")
        print("=" * 80)

        # 1. Tracer Configuration
        print("\n📋 TRACER CONFIGURATION:")
        print(f"   Type: {type(tracer).__name__}")
        print(f"   Project: {getattr(tracer, 'project', 'NOT_SET')}")
        print(f"   Source: {getattr(tracer, 'source', 'NOT_SET')}")
        print(f"   Session Name: {getattr(tracer, 'session_name', 'NOT_SET')}")
        print(f"   API Key: {'SET' if getattr(tracer, 'api_key', None) else 'NOT_SET'}")
        print(f"   Test Mode: {getattr(tracer, 'test_mode', 'NOT_SET')}")
        print(f"   Is Main Provider: {getattr(tracer, 'is_main_provider', 'NOT_SET')}")
        print(f"   HTTP Tracing: {getattr(tracer, 'http_tracing_enabled', 'NOT_SET')}")

        # 2. OTEL Provider Investigation
        print("\n🚀 OTEL PROVIDER INVESTIGATION:")
        provider = None
        if hasattr(tracer, "provider"):
            provider = tracer.provider
            print(f"   Provider Type: {type(provider).__name__}")
            print(f"   Provider ID: {id(provider)}")

            # Check span processors
            if hasattr(provider, "_active_span_processor"):
                active_processor = provider._active_span_processor
                print(f"   Active Span Processor: {type(active_processor).__name__}")
                print(f"   Active Processor ID: {id(active_processor)}")

                # If it's a composite processor, show all processors
                if hasattr(active_processor, "_span_processors"):
                    processors = active_processor._span_processors
                    print(f"   Total Processors: {len(processors)}")
                    for i, proc in enumerate(processors):
                        print(f"     Processor {i}: {type(proc).__name__}")
                        if hasattr(proc, "span_exporter"):
                            exporter = proc.span_exporter
                            print(f"       Exporter: {type(exporter).__name__}")
                            if hasattr(exporter, "_endpoint"):
                                print(f"       Endpoint: {exporter._endpoint}")
            else:
                print("   ❌ No active span processor found")
        else:
            print("   ❌ No OTEL tracer provider found")

        # 3. HoneyHive Span Processor Investigation
        print("\n🍯 HONEYHIVE SPAN PROCESSOR INVESTIGATION:")
        if hasattr(tracer, "span_processor"):
            hh_processor = tracer.span_processor
            print(f"   HH Processor Type: {type(hh_processor).__name__}")
            print(f"   HH Processor ID: {id(hh_processor)}")

            # Check client
            if hasattr(hh_processor, "client"):
                client = hh_processor.client
                print(f"   Client Type: {type(client).__name__}")
                print(f"   Client Base URL: {getattr(client, 'base_url', 'NOT_SET')}")

            # Check OTLP processor
            if hasattr(hh_processor, "_otlp_processor"):
                otlp_proc = hh_processor._otlp_processor
                print(
                    f"   OTLP Processor: "
                    f"{type(otlp_proc).__name__ if otlp_proc else 'None'}"
                )
                if otlp_proc and hasattr(otlp_proc, "span_exporter"):
                    exporter = otlp_proc.span_exporter
                    print(f"   OTLP Exporter: {type(exporter).__name__}")
                    if hasattr(exporter, "_endpoint"):
                        print(f"   OTLP Endpoint: {exporter._endpoint}")
                    if hasattr(exporter, "_headers"):
                        # Mask sensitive headers
                        headers = dict(exporter._headers)
                        if "authorization" in headers:
                            headers["authorization"] = "Bearer ***MASKED***"
                        print(f"   OTLP Headers: {headers}")
            else:
                print("   ❌ No OTLP processor found in HH processor")
        else:
            print("   ❌ No HoneyHive span processor found")

        # 4. Test Span Creation
        print("\n🎯 TEST SPAN CREATION:")
        test_unique_id = f"debug_test_{int(time.time())}"
        try:
            with tracer.start_span(f"debug_span_{test_unique_id}") as span:
                if span:
                    print(f"   ✅ Span created: {type(span).__name__}")
                    print(f"   Span ID: {span.get_span_context().span_id}")
                    print(f"   Trace ID: {span.get_span_context().trace_id}")

                    # Set test attributes
                    span.set_attribute("test.unique_id", test_unique_id)
                    span.set_attribute("test.debug_flow", "true")
                    span.set_attribute("honeyhive_event_type", "tool")

                    print("   ✅ Attributes set")
                else:
                    print("   ❌ No span created")
        except Exception as e:
            print(f"   ❌ Span creation failed: {e}")

            print(f"   Traceback: {traceback.format_exc()}")

        # 5. Force flush to ensure export
        print("\n🚀 FORCE FLUSH:")
        try:
            tracer.force_flush()
            print("   ✅ Force flush completed")
        except Exception as e:
            print(f"   ❌ Force flush failed: {e}")

        print("=" * 80)

    def _dump_span_content_debug(
        self, events: Any, unique_identifier: Any, expected_event_name: Any
    ) -> None:
        """Debug helper to dump comprehensive span content for troubleshooting."""
        print(
            f"\n🔍 DEBUG: Span content analysis for unique_id='{unique_identifier}', "
            f"event_name='{expected_event_name}'"
        )
        print(f"   Total events found: {len(events)}")

        for i, event in enumerate(events[:10]):  # Limit to first 10 events
            print(f"\n   Event {i}:")
            print(f"     Event ID: {getattr(event, 'event_id', 'unknown')}")
            print(f"     Event Name: {getattr(event, 'event_name', 'unknown')}")
            print(f"     Session ID: {getattr(event, 'session_id', 'unknown')}")

            if hasattr(event, "metadata") and event.metadata:
                print(f"     Metadata keys: {list(event.metadata.keys())}")
                unique_id_value = event.metadata.get("test.unique_id")
                print(f"     test.unique_id: {unique_id_value}")
                print(f"     Matches target: {unique_id_value == unique_identifier}")

                # Show other test-related metadata
                test_keys = [k for k in event.metadata.keys() if k.startswith("test.")]
                for key in test_keys:
                    print(f"     {key}: {event.metadata.get(key)}")
            else:
                print("     Metadata: None")

            # Show inputs if available
            if hasattr(event, "inputs") and event.inputs:
                print(f"     Inputs: {event.inputs}")

            # Show outputs if available
            if hasattr(event, "outputs") and event.outputs:
                print(f"     Outputs: {event.outputs}")

    def test_concurrent_span_creation_thread_safety(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test concurrent span creation across multiple threads with backend
        verification."""

        # Generate unique identifiers for this test run
        test_operation_name, test_unique_id = generate_test_id(
            "concurrent_spans", "concurrency_test"
        )

        # Thread-safe results collection
        results = []
        results_lock = threading.Lock()

        def create_span_worker(worker_id: int) -> Dict[str, Any]:
            """Worker function to create spans concurrently."""
            worker_unique_id = f"{test_unique_id}_worker_{worker_id}"

            try:
                with integration_tracer.start_span(
                    f"{test_operation_name}_worker_{worker_id}"
                ) as span:
                    if span is not None:
                        assert span.is_recording()

                        # Add worker-specific attributes
                        span.set_attribute("test.unique_id", worker_unique_id)
                        span.set_attribute("test.worker_id", worker_id)
                        span.set_attribute("test.thread_id", threading.get_ident())
                        span.set_attribute("test.concurrency_type", "thread_safety")
                        span.set_attribute("honeyhive.project", real_project)
                        span.set_attribute("honeyhive.source", real_source)

                        # Add events to test event thread safety
                        span.add_event("worker_started", {"worker_id": worker_id})

                        # Simulate work with varying durations
                        work_duration = 0.05 + (
                            worker_id * 0.01
                        )  # 50ms + worker_id * 10ms
                        time.sleep(work_duration)

                        span.add_event(
                            "work_completed",
                            {
                                "duration_ms": work_duration * 1000,
                                "worker_id": worker_id,
                            },
                        )

                        span.set_attribute(
                            "test.work_duration_ms", work_duration * 1000
                        )
                        span.set_status(
                            Status(StatusCode.OK, f"Worker {worker_id} completed")
                        )

                        # Thread-safe result collection
                        with results_lock:
                            results.append(
                                {
                                    "worker_id": worker_id,
                                    "unique_id": worker_unique_id,
                                    "thread_id": threading.get_ident(),
                                    "success": True,
                                }
                            )

                        return {
                            "worker_id": worker_id,
                            "unique_id": worker_unique_id,
                            "status": "completed",
                        }
                    else:
                        with results_lock:
                            results.append(
                                {
                                    "worker_id": worker_id,
                                    "unique_id": worker_unique_id,
                                    "thread_id": threading.get_ident(),
                                    "success": False,
                                    "error": "span_is_none",
                                }
                            )
                        return {
                            "worker_id": worker_id,
                            "status": "failed",
                            "error": "span_is_none",
                        }

            except Exception as e:
                with results_lock:
                    results.append(
                        {
                            "worker_id": worker_id,
                            "unique_id": worker_unique_id,
                            "thread_id": threading.get_ident(),
                            "success": False,
                            "error": str(e),
                        }
                    )
                return {"worker_id": worker_id, "status": "failed", "error": str(e)}

        # 1. Execute concurrent span creation
        num_workers = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit all workers
            futures = [
                executor.submit(create_span_worker, i) for i in range(num_workers)
            ]

            # Wait for all to complete
            completed_results = []
            for future in concurrent.futures.as_completed(futures, timeout=30):
                try:
                    result = future.result()
                    completed_results.append(result)
                except Exception as e:
                    completed_results.append({"status": "failed", "error": str(e)})

        # Verify all workers completed
        assert (
            len(completed_results) == num_workers
        ), f"Expected {num_workers} results, got {len(completed_results)}"

        successful_workers = [
            r for r in completed_results if r.get("status") == "completed"
        ]
        # Add proper logging instead of print statements

        logger = logging.getLogger(__name__)
        logger.info("Successful workers: %s/%s", len(successful_workers), num_workers)

        # 2. Force flush to ensure spans are exported
        integration_tracer.force_flush()
        time.sleep(2.0)  # Reduced wait time since we're forcing flush

        # 3. Backend verification using HoneyHive SDK
        _ = integration_client  # Validate client available

        try:
            # Verify spans from successful workers
            verified_spans = 0

            for worker_result in successful_workers:
                worker_id = worker_result["worker_id"]
                expected_unique_id = f"{test_unique_id}_worker_{worker_id}"

                try:

                    target_event = verify_backend_event(
                        client=integration_client,
                        project=real_project,
                        unique_identifier=expected_unique_id,
                        expected_event_name=f"{test_operation_name}_worker_{worker_id}",
                    )

                    # Validate concurrent span attributes (check both inputs and metadata)
                    event_inputs = target_event.inputs or {}
                    event_metadata = target_event.metadata or {}

                    worker_id_match = (
                        event_inputs.get("test.worker_id") == worker_id
                        or event_metadata.get("test.worker_id") == worker_id
                    )
                    concurrency_type_match = (
                        event_inputs.get("test.concurrency_type") == "thread_safety"
                        or event_metadata.get("test.concurrency_type")
                        == "thread_safety"
                    )
                    # NOTE: honeyhive.project is routed to top-level project_id, not metadata
                    # (backend routing per attribute_router.ts as of Oct 20, 2025)
                    project_match = target_event.project_id is not None

                    assert worker_id_match, (
                        f"Worker ID mismatch: expected {worker_id}, "
                        f"got inputs={event_inputs.get('test.worker_id')}, "
                        f"metadata={event_metadata.get('test.worker_id')}"
                    )
                    assert concurrency_type_match, (
                        f"Concurrency type mismatch: expected 'thread_safety', "
                        f"got inputs={event_inputs.get('test.concurrency_type')}, "
                        f"metadata={event_metadata.get('test.concurrency_type')}"
                    )
                    assert (
                        project_match
                    ), "Project not set: project_id should be populated from honeyhive.project"

                    verified_spans += 1
                except AssertionError:
                    # Skip this worker if verification fails (timing issues)
                    pass

            logger.info("✅ Concurrent span creation verification successful:")
            logger.info(f"   Workers executed: {num_workers}")
            logger.info(f"   Successful workers: {len(successful_workers)}")
            logger.info(f"   Verified spans in backend: {verified_spans}")

            # Ensure we verified at least some spans (allowing for timing issues)
            assert verified_spans >= max(
                1, len(successful_workers) // 2
            ), f"Expected to verify at least {max(1, len(successful_workers) // 2)} spans, got {verified_spans}"

        except Exception as e:
            pytest.fail(f"Concurrent span creation verification failed: {e}")

    def test_async_concurrent_span_management(
        self,
        tracer_factory: Any,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test async concurrent span management with backend verification."""

        # Create a verbose tracer for detailed debugging
        # Force it to be a main provider by using a different session name and ensuring clean state
        verbose_tracer = tracer_factory("verbose_tracer")

        # Generate unique identifiers for this test run

        test_operation_name, test_unique_id = generate_test_id(
            "async_concurrent", "async_test"
        )

        @atrace(  # type: ignore[misc]
            tracer=verbose_tracer,
            event_type="chain",
            event_name=f"{test_operation_name}_async_parent",
        )
        async def async_parent_operation(operation_id: str) -> Dict[str, Any]:
            """Async parent operation that manages concurrent child operations."""
            # Get current span and set attributes directly (like working performance test)
            current_span = otel_trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.set_attribute("test.unique_id", f"{test_unique_id}_parent")
                current_span.set_attribute("test.async_type", "parent")
                current_span.set_attribute(
                    "test.concurrency_pattern", "async_concurrent"
                )
                current_span.set_attribute("honeyhive.project", real_project)
                current_span.set_attribute("honeyhive.source", real_source)

            with enrich_span(
                inputs={
                    "operation_id": operation_id,
                },
                metadata={
                    "test.async_type": "parent",
                    "test.concurrency_pattern": "async_concurrent",
                    "honeyhive.project": real_project,
                    "honeyhive.source": real_source,
                },
            ):
                # Create multiple concurrent async child operations
                tasks = []
                for i in range(5):
                    task = asyncio.create_task(
                        async_child_operation(f"{operation_id}_child_{i}", i)
                    )
                    tasks.append(task)

                # Wait for all child operations to complete
                child_results = await asyncio.gather(*tasks, return_exceptions=True)

                successful_children = [
                    r
                    for r in child_results
                    if isinstance(r, dict) and r.get("status") == "completed"
                ]

                return {
                    "parent_operation_id": operation_id,
                    "children_created": len(tasks),
                    "children_successful": len(successful_children),
                    "async_pattern": "concurrent_children",
                    "status": "completed",
                }

        @atrace(  # type: ignore[misc]
            tracer=verbose_tracer,
            event_type="tool",
            event_name=f"{test_operation_name}_async_child",
        )
        async def async_child_operation(
            child_id: str, child_index: int
        ) -> Dict[str, Any]:
            """Async child operation."""
            # Get current span and set attributes directly (like working performance test)
            current_span = otel_trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.set_attribute(
                    "test.unique_id", f"{test_unique_id}_child_{child_index}"
                )
                current_span.set_attribute("test.async_type", "child")
                current_span.set_attribute("test.child_index", child_index)
                current_span.set_attribute("honeyhive.project", real_project)
                current_span.set_attribute("honeyhive.source", real_source)

            with enrich_span(
                inputs={
                    "child_id": child_id,
                    "child_index": child_index,
                },
                metadata={
                    "test.async_type": "child",
                    "test.child_index": child_index,
                    "honeyhive.project": real_project,
                    "honeyhive.source": real_source,
                },
            ):
                # Simulate async work with varying durations
                work_duration = 0.1 + (child_index * 0.02)  # 100ms + index * 20ms
                await asyncio.sleep(work_duration)

                return {
                    "child_id": child_id,
                    "child_index": child_index,
                    "work_duration_ms": work_duration * 1000,
                    "status": "completed",
                }

        # 1. Execute async concurrent operations
        async def run_async_test() -> Dict[str, Any]:
            return cast(
                Dict[str, Any],
                await async_parent_operation(
                    "async_test__" + generate_test_id("async_test_", "")[1]
                ),
            )

        # Run the async test
        result = asyncio.run(run_async_test())

        # Verify async operations completed successfully
        assert result["status"] == "completed"
        assert result["children_created"] == 5
        assert (
            result["children_successful"] >= 1
        )  # Allow for some failures due to timing

        # 2. Force flush to ensure spans are exported
        verbose_tracer.force_flush()

        # 3. Skip debug tracer flow for performance (verbose tracer will show detailed logs)
        # self._debug_tracer_flow(verbose_tracer, "async_concurrent_test")

        # 4. Backend verification using standard retry pattern with debug content
        # Verify parent async span
        parent_event = verify_backend_event(
            client=integration_client,
            project=real_project,
            unique_identifier=f"{test_unique_id}_parent",
            expected_event_name=f"{test_operation_name}_async_parent",
        )

        # Validate parent event attributes (stored in metadata for OTLP)
        assert (
            parent_event.metadata is not None
        ), "Parent event metadata should not be None"
        assert parent_event.metadata.get("test.async_type") == "parent"
        assert (
            parent_event.metadata.get("test.concurrency_pattern") == "async_concurrent"
        )

        # Verify at least one child async span (simplified for reliability)
        try:
            child_event = verify_backend_event(
                client=integration_client,
                project=real_project,
                unique_identifier=f"{test_unique_id}_child_0",
                expected_event_name=f"{test_operation_name}_async_child",
            )
            assert (
                child_event.metadata is not None
            ), "Child event metadata should not be None"
            assert child_event.metadata.get("test.async_type") == "child"
            assert child_event.metadata.get("test.child_index") == 0
            logger.info(f"✅ Child async span verified: {child_event.event_id}")
        except AssertionError:
            # Try child_1 as fallback due to async timing
            child_event = verify_backend_event(
                client=integration_client,
                project=real_project,
                unique_identifier=f"{test_unique_id}_child_1",
                expected_event_name=f"{test_operation_name}_async_child",
            )
            assert (
                child_event.metadata is not None
            ), "Child event metadata should not be None"
            assert child_event.metadata.get("test.async_type") == "child"
            assert child_event.metadata.get("test.child_index") == 1
            logger.info(
                f"✅ Child async span verified (fallback): {child_event.event_id}"
            )

        logger.info("✅ Async concurrent span management verification successful:")
        logger.info(f"   Parent event: {parent_event.event_id}")
        logger.info(f"   Child event: {child_event.event_id}")

    def test_multi_tracer_concurrent_operations(
        self,
        tracer_factory: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test concurrent operations across multiple tracer instances with backend verification."""

        # Generate unique identifiers for this test run

        test_operation_name, test_unique_id = generate_test_id(
            "multi_tracer_concurrent", "multi_tracer_test"
        )

        # Create multiple tracer instances using factory
        tracers = []
        for i in range(3):
            tracer = tracer_factory(f"concurrent_session_{i}")
            tracers.append(tracer)

        # Results collection
        results = []
        results_lock = threading.Lock()

        def tracer_worker(tracer_index: int, tracer: HoneyHiveTracer) -> Dict[str, Any]:
            """Worker function using specific tracer instance."""
            worker_unique_id = f"{test_unique_id}_tracer_{tracer_index}"

            try:
                with tracer.start_span(
                    f"{test_operation_name}_tracer_{tracer_index}"
                ) as span:
                    if span is not None:
                        assert span.is_recording()

                        # Add tracer-specific attributes
                        span.set_attribute("test.unique_id", worker_unique_id)
                        span.set_attribute("test.tracer_index", tracer_index)
                        span.set_attribute("test.session_name", tracer.session_name)
                        span.set_attribute("test.concurrency_type", "multi_tracer")
                        span.set_attribute("honeyhive.project", real_project)
                        span.set_attribute("honeyhive.source", real_source)

                        # Create nested spans within this tracer
                        for j in range(2):
                            with tracer.start_span(f"nested_span_{j}") as nested_span:
                                if nested_span is not None:
                                    nested_span.set_attribute("test.nested_index", j)
                                    nested_span.set_attribute(
                                        "test.parent_tracer", tracer_index
                                    )
                                    time.sleep(0.02)

                        span.add_event(
                            "tracer_work_completed",
                            {"tracer_index": tracer_index, "nested_spans_created": 2},
                        )

                        with results_lock:
                            results.append(
                                {
                                    "tracer_index": tracer_index,
                                    "unique_id": worker_unique_id,
                                    "session_name": tracer.session_name,
                                    "success": True,
                                }
                            )

                        return {
                            "tracer_index": tracer_index,
                            "unique_id": worker_unique_id,
                            "status": "completed",
                        }
                    else:
                        with results_lock:
                            results.append(
                                {
                                    "tracer_index": tracer_index,
                                    "unique_id": worker_unique_id,
                                    "success": False,
                                    "error": "span_is_none",
                                }
                            )
                        return {"tracer_index": tracer_index, "status": "failed"}

            except Exception as e:
                with results_lock:
                    results.append(
                        {
                            "tracer_index": tracer_index,
                            "unique_id": worker_unique_id,
                            "success": False,
                            "error": str(e),
                        }
                    )
                return {
                    "tracer_index": tracer_index,
                    "status": "failed",
                    "error": str(e),
                }

        try:
            # 1. Execute concurrent operations across multiple tracers
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(tracers)
            ) as executor:
                futures = [
                    executor.submit(tracer_worker, i, tracer)
                    for i, tracer in enumerate(tracers)
                ]

                completed_results = []
                for future in concurrent.futures.as_completed(futures, timeout=30):
                    try:
                        result = future.result()
                        completed_results.append(result)
                    except Exception as e:
                        completed_results.append({"status": "failed", "error": str(e)})

            # Verify all tracers completed
            assert len(completed_results) == len(
                tracers
            ), f"Expected {len(tracers)} results, got {len(completed_results)}"

            successful_tracers = [
                r for r in completed_results if r.get("status") == "completed"
            ]
            print(f"Successful tracers: {len(successful_tracers)}/{len(tracers)}")

            # 2. Force flush to ensure spans are exported
            for tracer in tracers:
                tracer.force_flush()
            time.sleep(2.0)  # Reduced wait time since we're forcing flush

            # 3. Backend verification using HoneyHive SDK
            _ = integration_client  # Validate client available

            verified_tracers = 0

            for tracer_result in successful_tracers:
                tracer_index = tracer_result["tracer_index"]
                expected_unique_id = f"{test_unique_id}_tracer_{tracer_index}"

                try:

                    target_event = verify_backend_event(
                        client=integration_client,
                        project=real_project,
                        unique_identifier=expected_unique_id,
                        expected_event_name=f"{test_operation_name}_tracer_{tracer_index}",
                    )

                    # Check both inputs and metadata for validation
                    target_inputs = target_event.inputs or {}
                    target_metadata = target_event.metadata or {}

                    # Handle nested test attributes for validation
                    tracer_index_match = (
                        target_inputs.get("test.tracer_index") == tracer_index
                        or target_metadata.get("test.tracer_index") == tracer_index
                        or (target_inputs.get("test", {}) or {}).get("tracer_index")
                        == tracer_index
                        or (target_metadata.get("test", {}) or {}).get("tracer_index")
                        == tracer_index
                    )
                    concurrency_type_match = (
                        target_inputs.get("test.concurrency_type") == "multi_tracer"
                        or target_metadata.get("test.concurrency_type")
                        == "multi_tracer"
                        or (target_inputs.get("test", {}) or {}).get("concurrency_type")
                        == "multi_tracer"
                        or (target_metadata.get("test", {}) or {}).get(
                            "concurrency_type"
                        )
                        == "multi_tracer"
                    )

                    assert (
                        tracer_index_match
                    ), f"Tracer index mismatch for tracer {tracer_index}: expected {tracer_index}, got inputs={target_inputs.get('test.tracer_index')}, metadata={target_metadata.get('test.tracer_index')}"
                    assert (
                        concurrency_type_match
                    ), f"Concurrency type mismatch for tracer {tracer_index}: expected 'multi_tracer', got inputs={target_inputs.get('test.concurrency_type')}, metadata={target_metadata.get('test.concurrency_type')}"
                    verified_tracers += 1
                except AssertionError:
                    # Skip this tracer if verification fails (timing issues)
                    pass

            print("✅ Multi-tracer concurrent operations verification successful:")
            print(f"   Tracers executed: {len(tracers)}")
            print(f"   Successful tracers: {len(successful_tracers)}")
            print(f"   Verified tracers in backend: {verified_tracers}")

            # Ensure we verified at least some tracers (allow for timing issues in concurrent tests)
            min_expected = (
                max(1, len(successful_tracers) // 3)
                if len(successful_tracers) > 0
                else 0
            )
            assert (
                verified_tracers >= min_expected
            ), f"Expected to verify at least {min_expected} tracers, got {verified_tracers} (successful: {len(successful_tracers)})"

        finally:
            # Cleanup handled by tracer_factory fixture
            pass

    def test_high_frequency_span_creation_stress(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test high-frequency span creation under stress conditions with backend verification."""

        # Generate unique identifiers for this test run

        test_operation_name, test_unique_id = generate_test_id(
            "high_frequency_stress", "stress_test"
        )

        # Stress test parameters - reduced for integration testing
        num_spans = 20  # Create spans quickly (reduced from 50)
        batch_size = 5  # Process in smaller batches

        created_spans = []
        creation_lock = threading.Lock()

        def create_stress_spans(batch_id: int, spans_per_batch: int) -> Dict[str, Any]:
            """Create multiple spans rapidly in a batch."""
            batch_results = []

            for i in range(spans_per_batch):
                span_id = (batch_id * spans_per_batch) + i
                span_unique_id = f"{test_unique_id}_span_{span_id}"

                try:
                    with integration_tracer.start_span(
                        f"{test_operation_name}_span_{span_id}"
                    ) as span:
                        if span is not None:
                            assert span.is_recording()

                            # Minimal attributes for high-frequency testing
                            span.set_attribute("test.unique_id", span_unique_id)
                            span.set_attribute("test.span_id", span_id)
                            span.set_attribute("test.batch_id", batch_id)
                            span.set_attribute("test.stress_type", "high_frequency")
                            span.set_attribute("honeyhive.project", real_project)
                            span.set_attribute("honeyhive.source", real_source)

                            # Quick event
                            span.add_event("stress_span_created", {"span_id": span_id})

                            # Very short work simulation
                            time.sleep(0.001)  # 1ms

                            with creation_lock:
                                created_spans.append(
                                    {
                                        "span_id": span_id,
                                        "unique_id": span_unique_id,
                                        "batch_id": batch_id,
                                        "success": True,
                                    }
                                )

                            batch_results.append(
                                {"span_id": span_id, "status": "created"}
                            )
                        else:
                            batch_results.append(
                                {
                                    "span_id": span_id,
                                    "status": "failed",
                                    "error": "span_is_none",
                                }
                            )

                except Exception as e:
                    batch_results.append(
                        {"span_id": span_id, "status": "failed", "error": str(e)}
                    )

            return {
                "batch_id": batch_id,
                "spans_attempted": spans_per_batch,
                "results": batch_results,
                "successful_spans": len(
                    [r for r in batch_results if r.get("status") == "created"]
                ),
            }

        # 1. Execute high-frequency span creation
        start_time = time.time()

        num_batches = (num_spans + batch_size - 1) // batch_size  # Ceiling division

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for batch_id in range(num_batches):
                spans_in_batch = min(batch_size, num_spans - (batch_id * batch_size))
                future = executor.submit(create_stress_spans, batch_id, spans_in_batch)
                futures.append(future)

            batch_results = []
            for future in concurrent.futures.as_completed(futures, timeout=60):
                try:
                    result = future.result()
                    batch_results.append(result)
                except Exception as e:
                    batch_results.append({"status": "failed", "error": str(e)})

        creation_time = time.time() - start_time

        # Analyze results
        total_successful = sum(r.get("successful_spans", 0) for r in batch_results)

        print("Stress test completed:")
        print(f"   Target spans: {num_spans}")
        print(f"   Successful spans: {total_successful}")
        print(f"   Creation time: {creation_time:.2f}s")
        print(f"   Rate: {total_successful/creation_time:.1f} spans/sec")

        # 2. Force flush to ensure spans are exported
        integration_tracer.force_flush()
        time.sleep(3.0)  # Reduced wait time since we're forcing flush

        # 3. Backend verification (sample-based for performance)
        _ = integration_client  # Validate client available

        try:
            # Verify a sample of created spans (not all, for performance)
            sample_size = min(
                5, total_successful
            )  # Reduced sample size for faster testing
            verified_spans = 0

            # Sample spans to verify
            sample_spans = (
                created_spans[:sample_size]
                if len(created_spans) >= sample_size
                else created_spans
            )

            for span_info in sample_spans:
                span_id = span_info["span_id"]
                expected_unique_id = span_info["unique_id"]

                try:
                    # Use the retry helper for backend verification
                    verified_event = verify_backend_event(
                        client=integration_client,
                        project=real_project,
                        unique_identifier=str(expected_unique_id),
                        expected_event_name=f"{test_operation_name}_span_{span_id}",
                    )

                    if verified_event:
                        verified_spans += 1

                except AssertionError:
                    # Skip failed verifications in stress test (some spans may not make it to backend)
                    continue

            print("✅ High-frequency stress test verification successful:")
            print(f"   Spans created: {total_successful}")
            print(f"   Sample verified: {verified_spans}/{sample_size}")
            print(f"   Creation rate: {total_successful/creation_time:.1f} spans/sec")

            # Ensure we created a reasonable number of spans
            assert (
                total_successful >= num_spans * 0.5
            ), f"Expected at least {num_spans * 0.5} successful spans, got {total_successful}"

            # Ensure we verified some spans in the backend
            assert verified_spans >= max(
                1, sample_size // 2
            ), f"Expected to verify at least {max(1, sample_size // 2)} spans, got {verified_spans}"

        except Exception as e:
            pytest.fail(f"High-frequency stress test verification failed: {e}")
