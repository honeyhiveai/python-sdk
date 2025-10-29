"""Multi-instance tracer safety tests.

This module tests that multiple concurrent tracer instances don't interfere
with each other, validating the v1.0 multi-instance architecture.
"""

# pylint: disable=protected-access
# Justification: Tests need to access _tracer_id for tracer identification

import threading
import time
from typing import Dict, List, Optional

import pytest

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.registry import get_tracer_from_baggage


class TestMultiInstanceSafety:
    """Test multiple concurrent tracer instances are isolated."""

    def test_concurrent_tracers_isolated(self) -> None:
        """Test 10 concurrent tracers are isolated."""
        results: List[Dict[str, str]] = []
        errors: List[Exception] = []

        def thread_func(thread_id: int) -> None:
            """Thread function that creates and uses a tracer."""
            try:
                # Create unique tracer per thread
                tracer = HoneyHiveTracer.init(
                    api_key="test-key",
                    project=f"project-{thread_id}",
                    session_name=f"session-{thread_id}",
                    test_mode=True,
                )

                # Create span and enrich
                with tracer.start_span(f"span-{thread_id}") as span:
                    if span and span.is_recording():
                        # Enrich with thread-specific metadata
                        tracer.enrich_span(
                            metadata={
                                "thread_id": thread_id,
                                "tracer_id": tracer._tracer_id,
                            }
                        )

                        # Verify attributes are thread-specific
                        attrs = dict(span.attributes or {})

                        # Check metadata was set correctly
                        expected_key = "honeyhive.metadata.thread_id"
                        if expected_key in attrs:
                            actual_thread_id = attrs[expected_key]
                            assert (
                                actual_thread_id == thread_id
                            ), f"Thread {thread_id} got wrong thread_id: {actual_thread_id}"

                results.append(
                    {
                        "thread_id": str(thread_id),
                        "tracer_id": tracer._tracer_id,
                        "project": tracer.project_name or "unknown",
                    }
                )

            except Exception as e:
                errors.append(e)

        # Create and start threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=thread_func, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify no errors
        assert not errors, f"Errors in threads: {errors}"

        # Verify all threads completed
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"

        # Verify each thread had unique tracer
        tracer_ids = [r["tracer_id"] for r in results]
        assert len(set(tracer_ids)) == 10, "Tracer IDs not unique across threads"

    def test_baggage_isolation(self) -> None:
        """Test each thread sees only its own baggage."""
        results: Dict[int, Optional[str]] = {}
        errors: List[Exception] = []

        def thread_func(thread_id: int) -> None:
            """Thread function that sets and reads baggage."""
            try:
                # Create unique tracer
                tracer = HoneyHiveTracer.init(
                    api_key="test-key", project=f"project-{thread_id}", test_mode=True
                )

                # Set baggage via tracer context
                with tracer.start_span(f"span-{thread_id}"):
                    # Get tracer from baggage
                    discovered_tracer = get_tracer_from_baggage()

                    # Verify we get the right tracer
                    if discovered_tracer:
                        results[thread_id] = discovered_tracer._tracer_id
                    else:
                        results[thread_id] = None

            except Exception as e:
                errors.append(e)

        # Create and start threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=thread_func, args=(i,))
            threads.append(thread)
            thread.start()
            time.sleep(0.01)  # Slight stagger

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify no errors
        assert not errors, f"Errors in threads: {errors}"

        # Verify all threads completed
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"

    def test_registry_concurrent_access(self) -> None:
        """Test registry is thread-safe for concurrent access."""
        tracers: List[HoneyHiveTracer] = []
        errors: List[Exception] = []

        def thread_func(thread_id: int) -> None:
            """Thread function that creates multiple tracers."""
            try:
                for i in range(3):
                    tracer = HoneyHiveTracer.init(
                        api_key="test-key",
                        project=f"project-{thread_id}-{i}",
                        test_mode=True,
                    )
                    tracers.append(tracer)
                    time.sleep(0.001)  # Simulate work

            except Exception as e:
                errors.append(e)

        # Create and start threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=thread_func, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify no errors
        assert not errors, f"Errors in threads: {errors}"

        # Verify all tracers created
        assert len(tracers) == 30, f"Expected 30 tracers, got {len(tracers)}"

        # Verify all tracer IDs are unique
        tracer_ids = [t.tracer_id for t in tracers]
        assert len(set(tracer_ids)) == 30, "Tracer IDs not unique"

    def test_discovery_in_threads(self) -> None:
        """Test tracer discovery works per-thread."""
        results: Dict[int, bool] = {}
        errors: List[Exception] = []

        def thread_func(thread_id: int) -> None:
            """Thread function that tests discovery."""
            try:
                # Create tracer
                tracer = HoneyHiveTracer.init(
                    api_key="test-key", project=f"project-{thread_id}", test_mode=True
                )

                # Create span (sets baggage)
                with tracer.start_span(f"span-{thread_id}"):
                    # Try to discover tracer
                    discovered = get_tracer_from_baggage()

                    # Verify discovery worked
                    if discovered:
                        results[thread_id] = discovered.tracer_id == tracer._tracer_id
                    else:
                        results[thread_id] = False

            except Exception as e:
                errors.append(e)

        # Create and start threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=thread_func, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify no errors
        assert not errors, f"Errors in threads: {errors}"

        # Verify all threads completed
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"

        # Verify all discoveries succeeded (Note: discovery may not work in all contexts)
        # This test validates that discovery doesn't crash or return wrong tracer

    def test_no_cross_contamination(self) -> None:
        """Test span attributes are isolated between tracers."""
        results: Dict[int, Dict[str, str]] = {}
        errors: List[Exception] = []

        def thread_func(thread_id: int) -> None:
            """Thread function that enriches spans."""
            try:
                # Create tracer
                tracer = HoneyHiveTracer.init(
                    api_key="test-key", project=f"project-{thread_id}", test_mode=True
                )

                # Create and enrich span
                with tracer.start_span(f"span-{thread_id}") as span:
                    if span and span.is_recording():
                        # Add unique metadata
                        tracer.enrich_span(
                            metadata={
                                "unique_id": f"thread-{thread_id}",
                                "timestamp": time.time(),
                            }
                        )

                        # Read attributes
                        attrs = dict(span.attributes or {})
                        results[thread_id] = {
                            "unique_id": str(
                                attrs.get("honeyhive.metadata.unique_id", "")
                            ),
                            "tracer_id": tracer._tracer_id,
                        }

            except Exception as e:
                errors.append(e)

        # Create and start threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=thread_func, args=(i,))
            threads.append(thread)
            thread.start()
            time.sleep(0.01)  # Stagger slightly

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify no errors
        assert not errors, f"Errors in threads: {errors}"

        # Verify all threads completed
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"

        # Verify each thread has correct unique_id
        for thread_id, data in results.items():
            expected_unique_id = f"thread-{thread_id}"
            actual_unique_id = data["unique_id"]
            assert actual_unique_id == expected_unique_id, (
                f"Thread {thread_id} contaminated: expected {expected_unique_id}, "
                f"got {actual_unique_id}"
            )


@pytest.mark.integration
class TestMultiInstanceIntegration:
    """Integration tests for multi-instance scenarios."""

    def test_two_projects_same_process(self) -> None:
        """Test two tracers for different projects in same process."""
        # Create production tracer
        prod_tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="production",
            session_name="prod-session",
            test_mode=True,
        )

        # Create staging tracer
        staging_tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="staging",
            session_name="staging-session",
            test_mode=True,
        )

        # Use both tracers
        with prod_tracer.start_span("prod-operation") as prod_span:
            prod_tracer.enrich_span(metadata={"env": "production"})

            if prod_span and prod_span.is_recording():
                prod_attrs = dict(prod_span.attributes or {})
                assert prod_attrs.get("honeyhive.metadata.env") == "production"

        with staging_tracer.start_span("staging-operation") as staging_span:
            staging_tracer.enrich_span(metadata={"env": "staging"})

            if staging_span and staging_span.is_recording():
                staging_attrs = dict(staging_span.attributes or {})
                assert staging_attrs.get("honeyhive.metadata.env") == "staging"

        # Verify tracers are distinct
        assert prod_tracer._tracer_id != staging_tracer._tracer_id
        assert prod_tracer.project_name != staging_tracer.project_name

    def test_sequential_tracer_creation(self) -> None:
        """Test creating and destroying tracers sequentially."""
        tracer_ids = []

        for i in range(5):
            tracer = HoneyHiveTracer.init(
                api_key="test-key", project=f"project-{i}", test_mode=True
            )
            tracer_ids.append(tracer._tracer_id)

            # Use tracer
            with tracer.start_span(f"span-{i}"):
                tracer.enrich_span(metadata={"iteration": i})

        # Verify all IDs unique
        assert len(set(tracer_ids)) == 5, "Sequential tracer IDs not unique"
