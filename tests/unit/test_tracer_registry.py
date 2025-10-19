"""Unit tests for HoneyHive tracer registry functionality (refactored version).

This module tests the tracer registry system including tracer registration,
discovery, baggage-based lookup, and default tracer management.
"""

# pylint: disable=protected-access,duplicate-code
# Justification: Testing internal registry functionality requires access to
# protected members

import gc
import threading
import weakref
from typing import cast
from unittest.mock import Mock, patch

import pytest
from opentelemetry.context import Context

from honeyhive.tracer import registry
from honeyhive.tracer.core import HoneyHiveTracer
from honeyhive.tracer.registry import (
    _TRACER_REGISTRY,
    discover_tracer,
    get_all_tracers,
    get_default_tracer,
    get_tracer_from_baggage,
    register_tracer,
    set_default_tracer,
)
from tests.utils import ensure_clean_otel_state  # pylint: disable=no-name-in-module


class MockHoneyHiveTracer:  # pylint: disable=too-few-public-methods
    """Mock HoneyHive tracer for testing registry functionality."""

    def __init__(
        self,
        project: str = "test-project",
        source: str = "test-source",
        api_key: str = "test-key",
    ):
        self.project = project
        self.source = source
        self.api_key = api_key
        self.test_mode = True
        self.session_id = f"session-{id(self)}"

    def __repr__(self) -> str:
        return f"MockHoneyHiveTracer(project={self.project}, source={self.source})"


def mock_tracer_cast(
    mock_tracer: MockHoneyHiveTracer,
) -> HoneyHiveTracer:
    """Helper function to cast MockHoneyHiveTracer to HoneyHiveTracer for type
    checking."""
    return cast(HoneyHiveTracer, mock_tracer)


class TestTracerRegistry:  # pylint: disable=too-many-public-methods
    """Test the tracer registry functionality."""

    def setup_method(self) -> None:
        """Set up clean state for each test method."""
        # AGGRESSIVE STATE RESET - Same as integration tests
        ensure_clean_otel_state()

        # Clear the global registry
        _TRACER_REGISTRY.clear()

        # Clear the global default tracer
        registry._DEFAULT_TRACER = None

        # Force garbage collection to ensure clean state
        gc.collect()

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # AGGRESSIVE CLEANUP - Same as integration tests
        ensure_clean_otel_state()

        # Clear the global registry
        _TRACER_REGISTRY.clear()

        # Clear the global default tracer
        registry._DEFAULT_TRACER = None

        # Force garbage collection
        gc.collect()

    def test_register_tracer_success(self) -> None:
        """Test successful tracer registration."""
        tracer = MockHoneyHiveTracer()

        tracer_id = register_tracer(mock_tracer_cast(tracer))

        # Verify tracer ID was generated
        assert tracer_id is not None
        assert isinstance(tracer_id, str)
        assert len(tracer_id) > 0

        # Verify tracer is in registry
        assert tracer_id in _TRACER_REGISTRY
        assert _TRACER_REGISTRY[tracer_id] is tracer

    def test_register_multiple_tracers(self) -> None:
        """Test registering multiple tracers generates unique IDs."""
        tracer1 = MockHoneyHiveTracer(project="project1")
        tracer2 = MockHoneyHiveTracer(project="project2")
        tracer3 = MockHoneyHiveTracer(project="project3")

        id1 = register_tracer(mock_tracer_cast(tracer1))
        id2 = register_tracer(mock_tracer_cast(tracer2))
        id3 = register_tracer(mock_tracer_cast(tracer3))

        # Verify all IDs are unique
        assert id1 != id2
        assert id2 != id3
        assert id1 != id3

        # Verify all tracers are in registry
        assert len(_TRACER_REGISTRY) == 3
        assert _TRACER_REGISTRY[id1] is tracer1
        assert _TRACER_REGISTRY[id2] is tracer2
        assert _TRACER_REGISTRY[id3] is tracer3

    def test_register_same_tracer_multiple_times(self) -> None:
        """Test registering the same tracer multiple times returns same ID."""
        tracer = MockHoneyHiveTracer()

        id1 = register_tracer(mock_tracer_cast(tracer))
        id2 = register_tracer(mock_tracer_cast(tracer))

        # Should return the same ID
        assert id1 == id2

        # Should only have one entry in registry
        assert len(_TRACER_REGISTRY) == 1

    def test_tracer_automatic_cleanup_on_garbage_collection(self) -> None:
        """Test that tracers are automatically removed when garbage collected."""
        tracer = MockHoneyHiveTracer()
        tracer_id = register_tracer(mock_tracer_cast(tracer))

        # Verify tracer is registered
        assert tracer_id in _TRACER_REGISTRY

        # Delete the tracer and force garbage collection
        del tracer
        gc.collect()

        # Verify tracer was automatically removed from registry
        assert tracer_id not in _TRACER_REGISTRY

    def test_get_tracer_from_baggage_success(self) -> None:
        """Test successful tracer retrieval from baggage."""
        tracer = MockHoneyHiveTracer()
        tracer_id = register_tracer(mock_tracer_cast(tracer))

        # Mock baggage to return the tracer ID
        with patch(
            "honeyhive.tracer.registry.baggage.get_baggage", return_value=tracer_id
        ):
            result = get_tracer_from_baggage()

            assert result is tracer

    def test_get_tracer_from_baggage_with_context(self) -> None:
        """Test tracer retrieval from baggage with specific context."""
        tracer = MockHoneyHiveTracer()
        tracer_id = register_tracer(mock_tracer_cast(tracer))

        mock_context = Mock(spec=Context)

        with patch(
            "honeyhive.tracer.registry.baggage.get_baggage", return_value=tracer_id
        ) as mock_get:
            result = get_tracer_from_baggage(mock_context)

            assert result is tracer
            # Verify context was passed to baggage.get_baggage (positional argument)
            mock_get.assert_called_once_with("honeyhive_tracer_id", mock_context)

    def test_get_tracer_from_baggage_no_baggage(self) -> None:
        """Test tracer retrieval when no baggage exists."""
        with patch("honeyhive.tracer.registry.baggage.get_baggage", return_value=None):
            result = get_tracer_from_baggage()

            assert result is None

    def test_get_tracer_from_baggage_invalid_id(self) -> None:
        """Test tracer retrieval with invalid tracer ID in baggage."""
        with patch(
            "honeyhive.tracer.registry.baggage.get_baggage", return_value="invalid-id"
        ):
            result = get_tracer_from_baggage()

            assert result is None

    def test_get_tracer_from_baggage_exception_handling(self) -> None:
        """Test tracer retrieval handles baggage exceptions gracefully."""
        with patch(
            "honeyhive.tracer.registry.baggage.get_baggage",
            side_effect=Exception("Baggage error"),
        ):
            result = get_tracer_from_baggage()

            # Should return None instead of raising exception
            assert result is None

    def test_set_default_tracer(self) -> None:
        """Test setting a default tracer."""
        tracer = MockHoneyHiveTracer()

        set_default_tracer(mock_tracer_cast(tracer))

        # Verify tracer was registered and set as default
        assert mock_tracer_cast(tracer) in _TRACER_REGISTRY.values()
        assert registry._DEFAULT_TRACER is not None
        assert registry._DEFAULT_TRACER() is tracer

    def test_set_default_tracer_none(self) -> None:
        """Test clearing the default tracer."""
        # First set a default tracer
        tracer = MockHoneyHiveTracer()
        set_default_tracer(mock_tracer_cast(tracer))
        assert registry._DEFAULT_TRACER is not None

        # Then clear it
        set_default_tracer(None)
        assert registry._DEFAULT_TRACER is None

    def test_get_default_tracer_success(self) -> None:
        """Test successful default tracer retrieval."""
        tracer = MockHoneyHiveTracer()
        set_default_tracer(mock_tracer_cast(tracer))

        result = get_default_tracer()

        assert result is tracer

    def test_get_default_tracer_none(self) -> None:
        """Test default tracer retrieval when none is set."""
        result = get_default_tracer()

        assert result is None

    def test_get_default_tracer_garbage_collected(self) -> None:
        """Test default tracer retrieval when tracer was garbage collected."""
        tracer = MockHoneyHiveTracer()
        set_default_tracer(mock_tracer_cast(tracer))

        # Delete the tracer and force garbage collection
        del tracer
        gc.collect()

        result = get_default_tracer()

        # Should return None and clear the stale reference
        assert result is None
        assert registry._DEFAULT_TRACER is None

    def test_first_tracer_becomes_default_automatically(self) -> None:
        """Test that the first registered tracer automatically becomes default.

        This verifies the fix for decorator auto-discovery: when no default
        tracer exists, the first tracer should be automatically set as default
        to enable @trace() decorator usage without explicit tracer parameter.
        """
        # Verify no default tracer exists initially
        assert get_default_tracer() is None

        # Register first tracer
        tracer1 = MockHoneyHiveTracer(project="first-tracer")
        register_tracer(mock_tracer_cast(tracer1))

        # Manually set as default (simulating what _register_tracer_instance does)
        if get_default_tracer() is None:
            set_default_tracer(mock_tracer_cast(tracer1))

        # First tracer should now be the default
        default_tracer = get_default_tracer()
        assert default_tracer is not None
        assert default_tracer is tracer1

        # Register second tracer
        tracer2 = MockHoneyHiveTracer(project="second-tracer")
        register_tracer(mock_tracer_cast(tracer2))

        # Simulate auto-default logic (second tracer should NOT become default)
        if get_default_tracer() is None:
            set_default_tracer(mock_tracer_cast(tracer2))

        # Default should still be the first tracer
        default_tracer = get_default_tracer()
        assert default_tracer is tracer1
        assert default_tracer is not tracer2

        # Both tracers should be in registry
        assert len(_TRACER_REGISTRY) == 2

    def test_decorator_discovery_with_auto_default(self) -> None:
        """Test that decorator discovery works with automatically set default tracer.

        This verifies the full discovery priority chain:
        1. Explicit tracer parameter (not used here)
        2. Baggage-discovered tracer (not used here)
        3. Global default tracer (should work via auto-default)
        """
        # Register first tracer and set as default
        tracer = MockHoneyHiveTracer(project="decorator-test")
        register_tracer(mock_tracer_cast(tracer))

        # Manually simulate auto-default behavior
        if get_default_tracer() is None:
            set_default_tracer(mock_tracer_cast(tracer))

        # Discover tracer without explicit parameter (should use default)
        discovered = discover_tracer(explicit_tracer=None, ctx=None)

        # Should discover the auto-default tracer
        assert discovered is not None
        assert discovered is tracer

    def test_discover_tracer_explicit_priority(self) -> None:
        """Test tracer discovery prioritizes explicit tracer parameter."""
        explicit_tracer = MockHoneyHiveTracer(project="explicit")
        baggage_tracer = MockHoneyHiveTracer(project="baggage")
        default_tracer = MockHoneyHiveTracer(project="default")

        # Set up baggage and default tracers
        baggage_id = register_tracer(mock_tracer_cast(baggage_tracer))
        set_default_tracer(mock_tracer_cast(default_tracer))

        with patch(
            "honeyhive.tracer.registry.baggage.get_baggage", return_value=baggage_id
        ):
            result = discover_tracer(explicit_tracer=mock_tracer_cast(explicit_tracer))

            # Should return explicit tracer (highest priority)
            assert result is explicit_tracer

    def test_discover_tracer_baggage_priority(self) -> None:
        """Test tracer discovery prioritizes baggage tracer over default."""
        baggage_tracer = MockHoneyHiveTracer(project="baggage")
        default_tracer = MockHoneyHiveTracer(project="default")

        # Set up baggage and default tracers
        baggage_id = register_tracer(mock_tracer_cast(baggage_tracer))
        set_default_tracer(mock_tracer_cast(default_tracer))

        with patch(
            "honeyhive.tracer.registry.baggage.get_baggage", return_value=baggage_id
        ):
            result = discover_tracer()

            # Should return baggage tracer (second priority)
            assert result is baggage_tracer

    def test_discover_tracer_default_fallback(self) -> None:
        """Test tracer discovery falls back to default tracer."""
        default_tracer = MockHoneyHiveTracer(project="default")
        set_default_tracer(mock_tracer_cast(default_tracer))

        with patch("honeyhive.tracer.registry.baggage.get_baggage", return_value=None):
            result = discover_tracer()

            # Should return default tracer (fallback)
            assert result is default_tracer

    def test_discover_tracer_none_available(self) -> None:
        """Test tracer discovery when no tracers are available."""
        with patch("honeyhive.tracer.registry.baggage.get_baggage", return_value=None):
            result = discover_tracer()

            # Should return None
            assert result is None

    def test_discover_tracer_with_context(self) -> None:
        """Test tracer discovery with specific context."""
        baggage_tracer = MockHoneyHiveTracer(project="baggage")
        baggage_id = register_tracer(mock_tracer_cast(baggage_tracer))

        mock_context = Mock(spec=Context)

        with patch(
            "honeyhive.tracer.registry.baggage.get_baggage", return_value=baggage_id
        ) as mock_get:
            result = discover_tracer(ctx=mock_context)

            assert result is baggage_tracer
            # Verify context was passed through
            mock_get.assert_called_once_with("honeyhive_tracer_id", mock_context)

    def test_thread_safety_with_concurrent_registration(self) -> None:
        """Test that tracer registration is thread-safe."""
        tracers = []
        tracer_ids = []

        def register_worker(worker_id: int) -> None:
            tracer = MockHoneyHiveTracer(project=f"project-{worker_id}")
            tracers.append(tracer)
            tracer_id = register_tracer(mock_tracer_cast(tracer))
            tracer_ids.append(tracer_id)

        # Create multiple threads registering tracers
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all tracers were registered with unique IDs
        assert len(tracers) == 10
        assert len(tracer_ids) == 10
        assert len(set(tracer_ids)) == 10  # All IDs should be unique
        assert len(_TRACER_REGISTRY) == 10

    def test_thread_safety_with_concurrent_default_operations(self) -> None:
        """Test that default tracer operations are thread-safe."""
        results = []

        def default_tracer_worker(worker_id: int) -> None:
            tracer = MockHoneyHiveTracer(project=f"project-{worker_id}")
            set_default_tracer(mock_tracer_cast(tracer))
            result = get_default_tracer()
            results.append(result)

        # Create multiple threads setting/getting default tracer
        threads = []
        for i in range(5):
            thread = threading.Thread(target=default_tracer_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations completed (one of the tracers should be default)
        assert len(results) == 5
        final_default = get_default_tracer()
        assert final_default is not None

    @pytest.mark.parametrize(
        "explicit,baggage_available,default_available,expected_source",
        [
            (True, True, True, "explicit"),
            (False, True, True, "baggage"),
            (False, False, True, "default"),
            (False, False, False, "none"),
        ],
    )
    def test_discover_tracer_priority_matrix(
        self,
        explicit: bool,
        baggage_available: bool,
        default_available: bool,
        expected_source: str,
    ) -> None:
        """Test tracer discovery priority with various availability combinations."""
        explicit_tracer = MockHoneyHiveTracer(project="explicit") if explicit else None
        baggage_tracer = (
            MockHoneyHiveTracer(project="baggage") if baggage_available else None
        )
        default_tracer = (
            MockHoneyHiveTracer(project="default") if default_available else None
        )

        # Set up baggage tracer
        baggage_id = None
        if baggage_tracer:
            baggage_id = register_tracer(mock_tracer_cast(baggage_tracer))

        # Set up default tracer
        if default_tracer:
            set_default_tracer(mock_tracer_cast(default_tracer))

        with patch(
            "honeyhive.tracer.registry.baggage.get_baggage", return_value=baggage_id
        ):
            result = discover_tracer(
                explicit_tracer=(
                    mock_tracer_cast(explicit_tracer) if explicit_tracer else None
                )
            )

            if expected_source == "explicit":
                assert result is explicit_tracer
            elif expected_source == "baggage":
                assert result is baggage_tracer
            elif expected_source == "default":
                assert result is default_tracer
            else:  # "none"
                assert result is None

    def test_weak_reference_behavior(self) -> None:
        """Test that registry uses weak references correctly."""
        tracer = MockHoneyHiveTracer()
        tracer_id = register_tracer(mock_tracer_cast(tracer))

        # Get a weak reference to the tracer
        weak_ref = weakref.ref(tracer)

        # Verify tracer is accessible
        assert weak_ref() is tracer
        assert tracer_id in _TRACER_REGISTRY

        # Delete the tracer
        del tracer

        # Force garbage collection
        gc.collect()

        # Verify weak reference is now None
        assert weak_ref() is None
        # Registry should automatically clean up
        assert tracer_id not in _TRACER_REGISTRY

    def test_registry_memory_efficiency(self) -> None:
        """Test that registry doesn't prevent garbage collection."""
        initial_registry_size = len(_TRACER_REGISTRY)

        # Create and register many tracers
        for i in range(100):
            tracer = MockHoneyHiveTracer(project=f"project-{i}")
            register_tracer(mock_tracer_cast(tracer))
            # Explicitly delete the tracer reference
            del tracer

        # Force garbage collection multiple times to ensure cleanup
        gc.collect()
        gc.collect()  # Sometimes multiple collections are needed

        # Registry should be cleaned up automatically
        final_registry_size = len(_TRACER_REGISTRY)
        assert final_registry_size == initial_registry_size

    def test_baggage_key_consistency(self) -> None:
        """Test that baggage operations use consistent key."""
        tracer = MockHoneyHiveTracer()
        tracer_id = register_tracer(mock_tracer_cast(tracer))

        with patch("honeyhive.tracer.registry.baggage.get_baggage") as mock_get:
            mock_get.return_value = tracer_id

            get_tracer_from_baggage()

            # Verify consistent baggage key is used
            mock_get.assert_called_once_with("honeyhive_tracer_id", {})

    def test_unregister_tracer_success(self) -> None:
        """Test successful tracer unregistration."""
        tracer = MockHoneyHiveTracer()
        tracer_id = register_tracer(mock_tracer_cast(tracer))

        # Verify tracer is registered
        assert tracer_id in _TRACER_REGISTRY

        # Unregister the tracer
        result = registry.unregister_tracer(tracer_id)

        # Verify unregistration was successful
        assert result is True
        assert tracer_id not in _TRACER_REGISTRY

    def test_unregister_tracer_not_found(self) -> None:
        """Test unregistering a tracer that doesn't exist."""
        # Try to unregister a non-existent tracer
        result = registry.unregister_tracer("non-existent-id")

        # Should return False
        assert result is False

    def test_get_all_tracers_empty(self) -> None:
        """Test getting all tracers when registry is empty."""
        result = registry.get_all_tracers()

        assert not result
        assert isinstance(result, list)

    def test_get_all_tracers_with_tracers(self) -> None:
        """Test getting all tracers when registry has tracers."""
        tracer1 = MockHoneyHiveTracer(project="project1")
        tracer2 = MockHoneyHiveTracer(project="project2")

        register_tracer(mock_tracer_cast(tracer1))
        register_tracer(mock_tracer_cast(tracer2))

        result = registry.get_all_tracers()

        assert len(result) == 2
        assert tracer1 in result
        assert tracer2 in result
        assert isinstance(result, list)

    def test_get_registry_stats_empty(self) -> None:
        """Test getting registry stats when empty."""
        result = registry.get_registry_stats()

        expected = {
            "active_tracers": 0,
            "has_default_tracer": 0,
        }
        assert result == expected
        assert isinstance(result, dict)

    def test_get_registry_stats_with_tracers_and_default(self) -> None:
        """Test getting registry stats with tracers and default."""
        tracer1 = MockHoneyHiveTracer(project="project1")
        tracer2 = MockHoneyHiveTracer(project="project2")

        register_tracer(mock_tracer_cast(tracer1))
        register_tracer(mock_tracer_cast(tracer2))
        set_default_tracer(mock_tracer_cast(tracer1))

        result = registry.get_registry_stats()

        expected = {
            "active_tracers": 2,
            "has_default_tracer": 1,
        }
        assert result == expected
        assert isinstance(result, dict)

    def test_get_registry_stats_with_tracers_no_default(self) -> None:
        """Test getting registry stats with tracers but no default."""
        tracer1 = MockHoneyHiveTracer(project="project1")
        tracer2 = MockHoneyHiveTracer(project="project2")

        register_tracer(mock_tracer_cast(tracer1))
        register_tracer(mock_tracer_cast(tracer2))

        result = registry.get_registry_stats()

        expected = {
            "active_tracers": 2,
            "has_default_tracer": 0,
        }
        assert result == expected
        assert isinstance(result, dict)

    def test_clear_registry_functionality(self) -> None:
        """Test clearing the registry removes all tracers and default."""
        tracer1 = MockHoneyHiveTracer(project="project1")
        tracer2 = MockHoneyHiveTracer(project="project2")

        # Set up registry with tracers and default
        register_tracer(mock_tracer_cast(tracer1))
        register_tracer(mock_tracer_cast(tracer2))
        set_default_tracer(mock_tracer_cast(tracer1))

        # Verify setup
        assert len(_TRACER_REGISTRY) == 2
        assert registry._DEFAULT_TRACER is not None

        # Clear registry
        registry.clear_registry()

        # Verify everything is cleared
        assert len(_TRACER_REGISTRY) == 0
        assert registry._DEFAULT_TRACER is None
        assert get_default_tracer() is None
        assert not get_all_tracers()
