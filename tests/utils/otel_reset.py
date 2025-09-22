"""OpenTelemetry state reset utilities for tests."""

import gc
import threading
import time
from typing import Any, Callable, Optional

# OpenTelemetry is a hard dependency - no need for try/except
from opentelemetry import baggage, context
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.trace import NoOpTracerProvider, ProxyTracerProvider

# Import HoneyHive's set_global_provider
from honeyhive.tracer import set_global_provider

# Optional import for registry clearing
clear_registry: Optional[Callable[[], None]]
try:
    from honeyhive.tracer import clear_registry
except ImportError:
    clear_registry = None
from honeyhive.tracer.lifecycle.core import (
    _new_spans_disabled,
)
from honeyhive.utils.logger import (
    reset_logging_state,
)


class OTELStateManager:
    """Manages OpenTelemetry global state for testing."""

    def __init__(self) -> None:
        self._original_provider: Optional[object] = None
        self._lock = threading.Lock()

    def reset_to_provider(
        self, target_provider: object, span_processors: Optional[list] = None
    ) -> None:
        """Reset global TracerProvider to the specified provider.

        Args:
            target_provider: The provider to set as global (NoOp, Proxy, SDK, etc.)
            span_processors: Optional list of span processors to add to the provider
                           (only works with SDK TracerProvider)
        """
        with self._lock:
            # Add span processors if provided and provider supports them
            if span_processors and hasattr(target_provider, "add_span_processor"):
                for processor in span_processors:
                    target_provider.add_span_processor(processor)

            # Use force_override for test utilities to enable clean state modifications
            # This allows test utilities to cleanly reset providers between tests
            set_global_provider(target_provider, force_override=True)

    def reset_to_noop(self) -> None:
        """Reset global TracerProvider to NoOpTracerProvider."""
        noop_provider = NoOpTracerProvider()
        self.reset_to_provider(noop_provider)

    def reset_to_clean_sdk(self) -> TracerProvider:
        """Reset to a clean SDK TracerProvider and return it."""
        with self._lock:
            clean_provider = TracerProvider()
            set_global_provider(clean_provider)
            return clean_provider

    def save_current_state(self) -> None:
        """Save the current TracerProvider state."""
        with self._lock:
            self._original_provider = otel_trace.get_tracer_provider()

    def restore_original_state(self) -> None:
        """Restore the original TracerProvider state."""
        with self._lock:
            if self._original_provider is not None:
                set_global_provider(self._original_provider)
                self._original_provider = None

    def get_current_provider_info(self) -> dict:
        """Get information about the current TracerProvider."""
        current_provider = otel_trace.get_tracer_provider()
        return {
            "provider_type": type(current_provider).__name__,
            "provider_id": id(current_provider),
            "is_noop": isinstance(current_provider, NoOpTracerProvider),
            "is_sdk": isinstance(current_provider, TracerProvider),
        }


# Global instance for test use
_otel_state_manager = OTELStateManager()


def reset_otel_to_provider(
    target_provider: object, span_processors: Optional[list] = None
) -> None:
    """Reset OpenTelemetry to the specified TracerProvider.

    Args:
        target_provider: The provider to set as global (NoOp, Proxy, SDK, etc.)
        span_processors: Optional list of span processors to add to the provider

    Example:
        >>> from opentelemetry.trace import ProxyTracerProvider
        >>> proxy_provider = ProxyTracerProvider()
        >>> reset_otel_to_provider(proxy_provider)

        >>> # With span processors for functioning provider
        >>> from opentelemetry.sdk.trace import TracerProvider
        >>> from opentelemetry.sdk.trace.export import (
        ...     ConsoleSpanExporter, SimpleSpanProcessor
        ... )
        >>> provider = TracerProvider()
        >>> processor = SimpleSpanProcessor(ConsoleSpanExporter())
        >>> reset_otel_to_provider(provider, [processor])
    """
    _otel_state_manager.reset_to_provider(target_provider, span_processors)


def reset_otel_to_noop() -> None:
    """Reset OpenTelemetry to NoOpTracerProvider.

    This is the most common reset needed for tests that expect
    a clean slate with no existing TracerProvider.
    """
    _otel_state_manager.reset_to_noop()


def reset_otel_to_clean_sdk() -> TracerProvider:
    """Reset OpenTelemetry to a clean SDK TracerProvider.

    Returns:
        TracerProvider: The new clean TracerProvider instance
    """
    return _otel_state_manager.reset_to_clean_sdk()


def reset_otel_to_functioning_sdk(exporter: Any = None) -> TracerProvider:
    """Reset OpenTelemetry to a functioning SDK TracerProvider with span processors.

    Args:
        exporter: Optional exporter to use. Defaults to ConsoleSpanExporter.

    Returns:
        TracerProvider: The new functioning TracerProvider instance

    Example:
        >>> # Use default console exporter
        >>> provider = reset_otel_to_functioning_sdk()

        >>> # Use custom exporter
        >>> from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        >>> custom_exporter = ConsoleSpanExporter()
        >>> provider = reset_otel_to_functioning_sdk(custom_exporter)
    """

    # Create provider and exporter
    provider = TracerProvider()
    if exporter is None:
        exporter = ConsoleSpanExporter()

    # Add processor
    processor = SimpleSpanProcessor(exporter)
    reset_otel_to_provider(provider, [processor])

    return provider


def save_otel_state() -> None:
    """Save the current OpenTelemetry state."""
    _otel_state_manager.save_current_state()


def restore_otel_state() -> None:
    """Restore the previously saved OpenTelemetry state."""
    _otel_state_manager.restore_original_state()


def get_otel_provider_info() -> dict:
    """Get information about the current TracerProvider.

    Returns:
        dict: Provider information including type, ID, and flags
    """
    return _otel_state_manager.get_current_provider_info()


def ensure_clean_otel_state() -> None:
    """Ensure OpenTelemetry is in a clean state for testing.

    Enhanced cleanup that:
    1. Gracefully shuts down active HoneyHive tracers
    2. Resets to ProxyTracerProvider to preserve secondary provider behavior
    3. Clears OpenTelemetry context and baggage between tests
    4. Performs garbage collection with small delays for async operations
    """

    try:
        # Step 1: Gracefully shut down any active HoneyHive tracers
        _shutdown_active_honeyhive_tracers()

        # Step 2: Reset HoneyHive-specific global state
        _reset_honeyhive_global_state()

        # Step 3: Clear OpenTelemetry context and baggage
        _clear_otel_context_and_baggage()

        # Step 4: Reset to ProxyTracerProvider (preserves secondary provider behavior)
        proxy_provider = ProxyTracerProvider()
        # Use our set_global_provider with force_override to properly reset SET_ONCE
        # flag
        set_global_provider(proxy_provider, force_override=True)

        # Step 4: Perform garbage collection with small delays for async operations
        gc.collect()
        time.sleep(0.01)  # Small delay for async cleanup
        gc.collect()

        # Verify the reset worked
        current_provider = otel_trace.get_tracer_provider()
        if not isinstance(current_provider, ProxyTracerProvider):
            # Fallback to NoOp if ProxyTracerProvider didn't work
            reset_otel_to_noop()

    except Exception:
        # If enhanced cleanup fails, fall back to basic cleanup
        reset_otel_to_noop()


def _reset_honeyhive_global_state() -> None:
    """Reset HoneyHive-specific global state for test isolation."""
    try:
        # Import the global state variables directly from production code

        # Reset the global events for test isolation
        reset_logging_state()
        _new_spans_disabled.clear()

        # Also try to clear tracer registry if available
        if clear_registry is not None:
            try:
                clear_registry()
            except Exception:
                pass  # Registry clearing is optional

    except Exception:
        pass  # Ignore errors if HoneyHive modules aren't available


def _shutdown_honeyhive_processors(active_processor: Any) -> None:
    """Shutdown HoneyHive span processors."""
    if not hasattr(active_processor, "_span_processors"):
        return
    for (
        processor
    ) in active_processor._span_processors:  # pylint: disable=protected-access
        # Check if this is a HoneyHive span processor
        if (
            hasattr(processor, "shutdown")
            and "honeyhive" in str(type(processor)).lower()
        ):
            try:
                processor.shutdown()
            except Exception:
                pass  # Ignore shutdown errors


def _shutdown_active_honeyhive_tracers() -> None:
    """Gracefully shut down any active HoneyHive tracers."""
    try:
        # Look for HoneyHive tracer instances in the current provider
        current_provider = otel_trace.get_tracer_provider()

        # Check if provider has span processors that might be HoneyHive processors
        if hasattr(current_provider, "_active_span_processor"):
            active_processor = (
                current_provider._active_span_processor  # pylint: disable=protected-access
            )
            _shutdown_honeyhive_processors(active_processor)

        # Also try to shutdown the active processor itself
        if hasattr(current_provider, "_active_span_processor") and hasattr(
            current_provider._active_span_processor,  # pylint: disable=protected-access
            "shutdown",
        ):
            try:
                current_provider._active_span_processor.shutdown()  # pylint: disable=protected-access
            except Exception:
                pass  # Ignore shutdown errors

    except Exception:
        pass  # Ignore all errors in graceful shutdown


def _clear_otel_context_and_baggage() -> None:
    """Clear OpenTelemetry context and baggage between tests."""
    try:

        # Clear baggage items that might persist between tests
        baggage_keys = [
            "event_id",
            "session_id",
            "project",
            "source",
            "parent_id",
            "honeyhive_session_id",
            "honeyhive_project",
            "honeyhive_source",
            "user_id",
            "user_properties",
            "session_properties",
        ]

        current_context = context.get_current()
        for key in baggage_keys:
            try:
                current_context = baggage.set_baggage(key, None, current_context)
            except Exception:
                pass

        # Reset to a clean context
        context.attach(context.Context())

    except Exception:
        pass  # Ignore context clearing errors


def debug_otel_state() -> str:
    """Get debug information about current OpenTelemetry state.

    Returns:
        str: Human-readable debug information
    """
    info = get_otel_provider_info()
    return (
        f"OpenTelemetry State Debug:\n"
        f"  Provider Type: {info['provider_type']}\n"
        f"  Provider ID: {info['provider_id']}\n"
        f"  Is NoOp: {info['is_noop']}\n"
        f"  Is SDK: {info['is_sdk']}\n"
    )
