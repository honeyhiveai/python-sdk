"""Unit tests for tracing models."""

from honeyhive.models.tracing import TracingParams


class TestTracingModels:
    """Test tracing-related model functionality."""

    def test_tracing_params_creation(self) -> None:
        """Test creating a TracingParams model."""
        params = TracingParams(
            event_type="model",
            event_name="test_event",
            inputs={"query": "test query"},
            outputs={"response": "test response"},
            metadata={"version": "1.0"},
        )

        assert params.event_type == "model"
        assert params.event_name == "test_event"
        assert params.inputs == {"query": "test query"}
        assert params.outputs == {"response": "test response"}
        assert params.metadata == {"version": "1.0"}

    def test_tracing_params_optional_fields(self) -> None:
        """Test TracingParams with optional fields."""
        params = TracingParams()

        assert params.event_type is None
        assert params.event_name is None
        assert params.inputs is None
        assert params.outputs is None

    def test_tracing_params_validation(self) -> None:
        """Test TracingParams validation."""
        # Test that TracingParams can be created with minimal fields
        params = TracingParams(event_type="tool")  # Use valid event_type

        assert params is not None
        assert hasattr(params, "event_type")
        assert hasattr(params, "event_name")
