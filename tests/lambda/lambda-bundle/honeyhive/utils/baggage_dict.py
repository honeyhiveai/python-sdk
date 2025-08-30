"""Baggage dictionary for OpenTelemetry context management."""

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Iterator, KeysView, Optional, ValuesView

if TYPE_CHECKING:
    from opentelemetry import baggage, context
    from opentelemetry.context import Context

try:
    from opentelemetry import baggage, context
    from opentelemetry.context import Context

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


class BaggageDict:
    """Dictionary-like interface for OpenTelemetry baggage.

    This class provides a convenient way to work with OpenTelemetry baggage
    as if it were a regular dictionary, while maintaining proper context
    propagation.
    """

    def __init__(self, ctx: Optional[Context] = None):
        """Initialize BaggageDict with optional context.

        Args:
            ctx: OpenTelemetry context. If None, uses current context.
        """
        if not OTEL_AVAILABLE:
            raise ImportError("OpenTelemetry is required for BaggageDict")

        self._context = ctx or context.get_current()

    @property
    def context(self) -> Context:
        """Get the current context."""
        return self._context

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from baggage.

        Args:
            key: Baggage key
            default: Default value if key not found

        Returns:
            Value from baggage or default
        """
        if not OTEL_AVAILABLE:
            return default

        value = baggage.get_baggage(key, self._context)
        return value if value is not None else default

    def set(self, key: str, value: Any) -> "BaggageDict":
        """Set a value in baggage.

        Args:
            key: Baggage key
            value: Value to set

        Returns:
            New BaggageDict with updated context
        """
        if not OTEL_AVAILABLE:
            return self

        new_context = baggage.set_baggage(key, str(value), self._context)
        return BaggageDict(new_context)

    def delete(self, key: str) -> "BaggageDict":
        """Delete a key from baggage.

        Args:
            key: Baggage key to delete

        Returns:
            New BaggageDict with updated context
        """
        if not OTEL_AVAILABLE:
            return self

        new_context = baggage.set_baggage(key, None, self._context)
        return BaggageDict(new_context)

    def update(self, **kwargs: Any) -> "BaggageDict":
        """Update multiple baggage values.

        Args:
            **kwargs: Key-value pairs to set

        Returns:
            New BaggageDict with updated context
        """
        if not OTEL_AVAILABLE:
            return self

        new_context = self._context
        for key, value in kwargs.items():
            new_context = baggage.set_baggage(key, str(value), new_context)

        return BaggageDict(new_context)

    def clear(self) -> "BaggageDict":
        """Clear all baggage.

        Returns:
            New BaggageDict with empty baggage
        """
        if not OTEL_AVAILABLE:
            return self

        # Create new context without baggage
        new_context = context.get_current()
        return BaggageDict(new_context)

    def items(self) -> Dict[str, str]:
        """Get all baggage items as a dictionary.

        Returns:
            Dictionary of baggage key-value pairs
        """
        if not OTEL_AVAILABLE:
            return {}

        try:
            # Get current baggage context
            current_baggage = baggage.get_all()
            if current_baggage:
                # Convert to string values to match the expected return type
                return {k: str(v) for k, v in current_baggage.items()}
            return {}
        except Exception:
            return {}

    def keys(self) -> KeysView[str]:
        """Get all baggage keys."""
        return self.items().keys()

    def values(self) -> ValuesView[str]:
        """Get all baggage values."""
        return self.items().values()

    def __getitem__(self, key: str) -> str:
        """Get baggage value using bracket notation."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return str(value)  # Ensure we return a string

    def __setitem__(self, key: str, value: Any) -> None:
        """Set baggage value using bracket notation."""
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """Delete baggage key using bracket notation."""
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in baggage."""
        return self.get(key) is not None

    def __len__(self) -> int:
        """Get number of baggage items."""
        return len(self.items())

    def __iter__(self) -> Iterator[str]:
        """Iterate over baggage keys."""
        return iter(self.keys())

    def __repr__(self) -> str:
        """String representation."""
        items = self.items()
        return f"BaggageDict({items})"

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], context: Optional[Context] = None
    ) -> "BaggageDict":
        """Create BaggageDict from dictionary.

        Args:
            data: Dictionary of key-value pairs
            context: Optional OpenTelemetry context

        Returns:
            New BaggageDict with baggage from dictionary
        """
        baggage_dict = cls(context)
        return baggage_dict.update(**data)

    @contextmanager
    def as_context(self) -> Iterator[None]:
        """Context manager to temporarily set baggage in current context.

        Example:
            with BaggageDict().set("user_id", "123").as_context():
                # baggage is available in this context
                pass
        """
        if not OTEL_AVAILABLE:
            yield
            return

        token = context.attach(self._context)
        try:
            yield
        finally:
            context.detach(token)
