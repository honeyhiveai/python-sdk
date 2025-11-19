"""HoneyHive tracer class implementation.

This module provides the main HoneyHiveTracer class composed from multiple
mixins using dynamic inheritance patterns. It maintains full backward
compatibility while providing a clean, modular architecture.
"""

from typing import Optional

from .base import HoneyHiveTracerBase
from .context import TracerContextMixin
from .operations import TracerOperationsMixin


class HoneyHiveTracer(HoneyHiveTracerBase, TracerOperationsMixin, TracerContextMixin):
    """HoneyHive OpenTelemetry tracer with dynamic multi-instance architecture.

    This tracer class is composed from multiple mixins using dynamic inheritance,
    providing a comprehensive tracing solution with flexible configuration,
    robust error handling, and multi-instance support.

    The class combines:
    - HoneyHiveTracerBase: Core initialization and configuration
    - TracerOperationsMixin: Span creation and event management
    - TracerContextMixin: Context and baggage management

    All operations use dynamic logic for flexible parameter handling,
    automatic error recovery, and graceful degradation.

    Example:
        >>> # New Pydantic config approach (recommended)
        >>> config = TracerConfig(api_key="...", project="...", verbose=True)
        >>> tracer = HoneyHiveTracer(config=config)
        >>>
        >>> # Backwards compatible approach
        >>> tracer = HoneyHiveTracer(api_key="...", project="...", verbose=True)

        >>> # Dynamic span creation
        >>> with tracer.start_span("operation") as span:
        ...     span.set_attribute("key", "value")

        >>> # Dynamic event creation
        >>> event_id = tracer.create_event(
        ...     event_name="my_event",
        ...     event_type="tool",
        ...     inputs={"input": "data"},
        ...     outputs={"output": "result"}
        ... )
    """

    # Explicit implementation to satisfy ABC requirements
    # The TracerContextMixin provides the actual implementation
    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage value by key.

        Delegates to TracerContextMixin implementation.

        Args:
            key: The baggage key to retrieve

        Returns:
            Baggage value or None if not found
        """
        return TracerContextMixin.get_baggage(self, key)

    def __repr__(self) -> str:
        """Dynamic string representation of tracer instance."""
        return (
            f"HoneyHiveTracer("
            f"project={self.project_name!r}, "
            f"source={self.source_environment!r}, "
            f"initialized={self.is_initialized}, "
            f"test_mode={self.is_test_mode})"
        )
