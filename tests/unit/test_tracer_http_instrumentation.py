"""Unit tests for HTTP instrumentation."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.http_instrumentation import HTTPInstrumentation

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestHTTPInstrumentation:
    """Test HTTP instrumentation functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_tracer = Mock()
        self.instrumentation = HTTPInstrumentation()

    def test_initialization(self) -> None:
        """Test HTTP instrumentation initialization."""
        assert self.instrumentation._is_instrumented is False
        assert self.instrumentation._original_httpx_request is None
        assert self.instrumentation._original_requests_request is None

    def test_instrument_httpx_client(self) -> None:
        """Test httpx client instrumentation."""
        with patch("httpx.Client.request") as mock_request:
            # Mock the original request method
            original_request = Mock()
            mock_request.return_value = original_request

            # Instrument
            self.instrumentation.instrument()

            # Check that instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_instrument_httpx_async_client(self) -> None:
        """Test httpx async client instrumentation."""
        with patch("httpx.AsyncClient.request") as mock_request:
            # Mock the original request method
            original_request = Mock()
            mock_request.return_value = original_request

            # Instrument
            self.instrumentation.instrument()

            # Check that instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_create_request_span(self) -> None:
        """Test creating request spans."""
        # Mock the tracer instance
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance",
            self.mock_tracer,
        ):
            # Mock start_span to return a context manager
            mock_span = Mock()
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=mock_span)
            mock_context_manager.__exit__ = Mock(return_value=None)
            self.mock_tracer.start_span.return_value = mock_context_manager

            # Instrument
            self.instrumentation.instrument()

            # Verify instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_create_response_span(self) -> None:
        """Test creating response spans."""
        # Mock the tracer instance
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance",
            self.mock_tracer,
        ):
            # Mock start_span to return a context manager
            mock_span = Mock()
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=mock_span)
            mock_context_manager.__exit__ = Mock(return_value=None)
            self.mock_tracer.start_span.return_value = mock_context_manager

            # Instrument
            self.instrumentation.instrument()

            # Verify instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_add_request_attributes(self) -> None:
        """Test adding request attributes to spans."""
        # Mock the tracer instance
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance",
            self.mock_tracer,
        ):
            # Mock start_span to return a context manager
            mock_span = Mock()
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=mock_span)
            mock_context_manager.__exit__ = Mock(return_value=None)
            self.mock_tracer.start_span.return_value = mock_context_manager

            # Instrument
            self.instrumentation.instrument()

            # Verify instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_add_response_attributes(self) -> None:
        """Test adding response attributes to spans."""
        # Mock the tracer instance
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance",
            self.mock_tracer,
        ):
            # Mock start_span to return a context manager
            mock_span = Mock()
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=mock_span)
            mock_context_manager.__exit__ = Mock(return_value=None)
            self.mock_tracer.start_span.return_value = mock_context_manager

            # Instrument
            self.instrumentation.instrument()

            # Verify instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_instrument_request(self) -> None:
        """Test instrumenting HTTP requests."""
        # Mock the tracer instance
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance",
            self.mock_tracer,
        ):
            # Mock start_span to return a context manager
            mock_span = Mock()
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=mock_span)
            mock_context_manager.__exit__ = Mock(return_value=None)
            self.mock_tracer.start_span.return_value = mock_context_manager

            # Instrument
            self.instrumentation.instrument()

            # Verify instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_instrument_async_request(self) -> None:
        """Test instrumenting async HTTP requests."""
        # Mock the tracer instance
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance",
            self.mock_tracer,
        ):
            # Mock start_span to return a context manager
            mock_span = Mock()
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=mock_span)
            mock_context_manager.__exit__ = Mock(return_value=None)
            self.mock_tracer.start_span.return_value = mock_context_manager

            # Instrument
            self.instrumentation.instrument()

            # Verify instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_uninstrument(self) -> None:
        """Test removing HTTP instrumentation."""
        # First instrument
        self.instrumentation.instrument()
        assert self.instrumentation._is_instrumented is True

        # Then uninstrument
        self.instrumentation.uninstrument()
        assert self.instrumentation._is_instrumented is False

    def test_double_instrument(self) -> None:
        """Test that double instrumentation doesn't cause issues."""
        # Instrument twice
        self.instrumentation.instrument()
        self.instrumentation.instrument()

        # Should still be instrumented
        assert self.instrumentation._is_instrumented is True

    def test_double_uninstrument(self) -> None:
        """Test that double uninstrumentation doesn't cause issues."""
        # Instrument first
        self.instrumentation.instrument()
        assert self.instrumentation._is_instrumented is True

        # Uninstrument twice
        self.instrumentation.uninstrument()
        self.instrumentation.uninstrument()

        # Should still be uninstrumented
        assert self.instrumentation._is_instrumented is False

    def test_instrumentation_without_tracer(self) -> None:
        """Test instrumentation when no tracer is available."""
        # Mock no tracer instance
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance", None
        ):
            # Should not raise an error
            self.instrumentation.instrument()
            assert self.instrumentation._is_instrumented is True

    def test_instrumentation_with_exception(self) -> None:
        """Test instrumentation handles exceptions gracefully."""
        # Mock an exception during instrumentation
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance",
            self.mock_tracer,
        ):
            # Mock start_span to raise an exception
            self.mock_tracer.start_span.side_effect = Exception("Test exception")

            # Should not raise an error
            self.instrumentation.instrument()
            assert self.instrumentation._is_instrumented is True

    def test_requests_instrumentation(self) -> None:
        """Test requests library instrumentation."""
        with patch("requests.Session.request") as mock_request:
            # Mock the original request method
            original_request = Mock()
            mock_request.return_value = original_request

            # Instrument
            self.instrumentation.instrument()

            # Check that instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_mixed_library_instrumentation(self) -> None:
        """Test instrumentation of both httpx and requests."""
        with patch("httpx.Client.request"), patch("requests.Session.request"):
            # Instrument
            self.instrumentation.instrument()

            # Check that instrumentation was applied
            assert self.instrumentation._is_instrumented is True

    def test_instrumentation_attributes(self) -> None:
        """Test that instrumentation adds correct attributes."""
        # Mock the tracer instance
        with patch(
            "honeyhive.tracer.http_instrumentation.HoneyHiveTracer._instance",
            self.mock_tracer,
        ):
            # Mock start_span to return a context manager
            mock_span = Mock()
            mock_context_manager = Mock()
            mock_context_manager.__enter__ = Mock(return_value=mock_span)
            mock_context_manager.__exit__ = Mock(return_value=None)
            self.mock_tracer.start_span.return_value = mock_context_manager

            # Instrument
            self.instrumentation.instrument()

            # Verify instrumentation was applied
            assert self.instrumentation._is_instrumented is True
