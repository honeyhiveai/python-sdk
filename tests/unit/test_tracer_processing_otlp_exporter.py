"""Unit tests for HoneyHive OTLP exporter.

This module tests the HoneyHive OTLP exporter functionality including
initialization, span export, error handling, and lifecycle management.

This module follows testing standards with proper type annotations,
pylint compliance, and comprehensive coverage targeting 95%+.

NOTE: Tests temporarily skipped - test expectations don't match current implementation.
TODO: Update tests to match current OTLP exporter implementation.
"""

from typing import List, Sequence
from unittest.mock import Mock, patch

import pytest
import requests
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult

from honeyhive.tracer.processing.otlp_exporter import (
    HoneyHiveOTLPExporter,
    OTLPJSONExporter,
)
from honeyhive.tracer.processing.otlp_session import OTLPSessionConfig

# Tests updated to match current OTLP exporter implementation (endpoint required)

# pylint: disable=protected-access,too-many-lines,redefined-outer-name,duplicate-code
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.


# Use a clearly-fake URL for unit tests (all HTTP calls are mocked)
TEST_OTLP_ENDPOINT = "https://test.example.com/opentelemetry/v1/traces"


# Standard fixtures
@pytest.fixture
def mock_tracer() -> Mock:
    """Create a fresh mock tracer for each test.

    Returns:
        Mock tracer instance with basic configuration
    """
    tracer = Mock()
    tracer.config = Mock()
    return tracer


@pytest.fixture
def mock_otlp_session_config() -> OTLPSessionConfig:
    """Create mock OTLP session configuration.

    Returns:
        OTLPSessionConfig instance with test values
    """
    return OTLPSessionConfig(
        pool_connections=5,
        pool_maxsize=10,
        max_retries=2,
        timeout=15.0,
        backoff_factor=0.3,
    )


@pytest.fixture
def mock_readable_spans() -> List[ReadableSpan]:
    """Create mock readable spans for testing.

    Returns:
        List of mock ReadableSpan objects
    """
    spans: List[ReadableSpan] = []
    for i in range(3):
        span = Mock(spec=ReadableSpan)
        span.name = f"test_span_{i}"
        span.context = Mock()
        spans.append(span)
    return spans


@pytest.fixture
def mock_requests_session() -> Mock:
    """Create mock requests session.

    Returns:
        Mock requests.Session with adapter configuration
    """
    session = Mock(spec=requests.Session)
    session.adapters = {"http://": Mock(), "https://": Mock()}
    session.timeout = 30.0
    return session


class TestHoneyHiveOTLPExporterInitialization:
    """Test HoneyHive OTLP exporter initialization scenarios."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.get_default_otlp_config")
    def test_initialization_with_defaults(
        self, mock_get_default_config: Mock, mock_json_exporter: Mock
    ) -> None:
        """Test initialization with default parameters.

        Args:
            mock_get_default_config: Mock for get_default_otlp_config function
            mock_json_exporter: Mock for OTLPJSONExporter class
        """
        # Arrange
        mock_config = OTLPSessionConfig()
        mock_get_default_config.return_value = mock_config
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        # Act - endpoint is required for JSON protocol (default)
        exporter = HoneyHiveOTLPExporter(endpoint=TEST_OTLP_ENDPOINT)

        # Assert
        assert exporter.tracer_instance is None
        assert exporter.session_config == mock_config
        assert exporter.use_optimized_session is True
        assert exporter.protocol == "http/json"
        assert exporter._use_json is True
        assert exporter._is_shutdown is False
        mock_get_default_config.assert_called_once_with(None)

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.create_optimized_otlp_session")
    def test_initialization_with_optimized_session_success(
        self,
        mock_create_session: Mock,
        mock_json_exporter: Mock,
        mock_tracer: Mock,
        mock_otlp_session_config: OTLPSessionConfig,
    ) -> None:
        """Test successful initialization with optimized session.

        Args:
            mock_create_session: Mock for create_optimized_otlp_session function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_otlp_session_config: Mock session configuration
        """
        # Arrange
        mock_session = Mock(spec=requests.Session)
        mock_create_session.return_value = mock_session
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session_config=mock_otlp_session_config,
            use_optimized_session=True,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Assert
        assert exporter.tracer_instance == mock_tracer
        assert exporter.session_config == mock_otlp_session_config
        assert exporter._session == mock_session
        assert exporter.protocol == "http/json"
        assert exporter._use_json is True
        mock_create_session.assert_called_once_with(
            config=mock_otlp_session_config, tracer_instance=mock_tracer
        )

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.create_optimized_otlp_session")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_initialization_with_optimized_session_failure(
        self,
        mock_safe_log: Mock,
        mock_create_session: Mock,
        mock_json_exporter: Mock,
        *,
        mock_tracer: Mock,
        mock_otlp_session_config: OTLPSessionConfig,
    ) -> None:
        """Test initialization when optimized session creation fails.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_create_session: Mock for create_optimized_otlp_session function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_otlp_session_config: Mock session configuration
        """
        # Arrange
        test_error = ConnectionError("Network unavailable")
        mock_create_session.side_effect = test_error
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session_config=mock_otlp_session_config,
            use_optimized_session=True,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Assert
        assert exporter._session is None
        mock_safe_log.assert_called_with(
            mock_tracer,
            "debug",
            "HoneyHiveOTLPExporter initialized with default session",
            honeyhive_data={
                "session_type": "default",
                "use_optimized_session": True,
                "has_custom_session": False,
            },
        )
        mock_json_exporter.assert_called_once()

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_initialization_with_custom_session_provided(
        self, mock_json_exporter: Mock, mock_requests_session: Mock
    ) -> None:
        """Test initialization with custom session provided in kwargs.

        Args:
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            use_optimized_session=True,
            session=mock_requests_session,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Assert
        assert exporter._session == mock_requests_session
        mock_json_exporter.assert_called_once()

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_initialization_without_optimized_session(
        self, mock_json_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test initialization with optimized session disabled.

        Args:
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            use_optimized_session=False,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Assert
        assert exporter.use_optimized_session is False
        assert exporter._session is None
        mock_json_exporter.assert_called_once()


class TestHoneyHiveOTLPExporterExport:
    """Test HoneyHive OTLP exporter export functionality."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_export_success(
        self,
        mock_safe_log: Mock,
        mock_json_exporter: Mock,
        mock_tracer: Mock,
        mock_readable_spans: List[ReadableSpan],
    ) -> None:
        """Test successful span export.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_readable_spans: Mock readable spans
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_exporter_instance.export.return_value = SpanExportResult.SUCCESS
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, endpoint=TEST_OTLP_ENDPOINT
        )

        # Act
        result = exporter.export(mock_readable_spans)

        # Assert
        assert result == SpanExportResult.SUCCESS
        mock_exporter_instance.export.assert_called_once_with(mock_readable_spans)
        mock_safe_log.assert_called_with(
            mock_tracer,
            "debug",
            f"Exporting {len(mock_readable_spans)} processed spans to HoneyHive",
            honeyhive_data={"span_count": len(mock_readable_spans)},
        )

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_export_when_shutdown(
        self,
        mock_safe_log: Mock,
        mock_json_exporter: Mock,
        mock_tracer: Mock,
        mock_readable_spans: List[ReadableSpan],
    ) -> None:
        """Test export when exporter is already shutdown.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_readable_spans: Mock readable spans
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, endpoint=TEST_OTLP_ENDPOINT
        )
        exporter._is_shutdown = True

        # Act
        result = exporter.export(mock_readable_spans)

        # Assert
        assert result == SpanExportResult.FAILURE
        mock_exporter_instance.export.assert_not_called()
        mock_safe_log.assert_called_with(
            mock_tracer, "debug", "Exporter already shutdown, skipping export"
        )

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_export_with_exception(
        self,
        mock_safe_log: Mock,
        mock_json_exporter: Mock,
        mock_tracer: Mock,
        mock_readable_spans: List[ReadableSpan],
    ) -> None:
        """Test export when underlying exporter raises exception.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_readable_spans: Mock readable spans
        """
        # Arrange
        test_error = RuntimeError("Export failed")
        mock_exporter_instance = Mock()
        mock_exporter_instance.export.side_effect = test_error
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, endpoint=TEST_OTLP_ENDPOINT
        )

        # Act
        result = exporter.export(mock_readable_spans)

        # Assert
        assert result == SpanExportResult.FAILURE
        mock_safe_log.assert_called_with(
            mock_tracer,
            "error",
            f"Error in OTLP export: {test_error}",
            honeyhive_data={"error_type": "RuntimeError"},
        )


class TestHoneyHiveOTLPExporterForceFlush:
    """Test HoneyHive OTLP exporter force flush functionality."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_force_flush_success(
        self, mock_json_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test successful force flush.

        Args:
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_exporter_instance.force_flush.return_value = True
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, endpoint=TEST_OTLP_ENDPOINT
        )

        # Act
        result = exporter.force_flush(timeout_millis=15000)

        # Assert
        assert result is True
        mock_exporter_instance.force_flush.assert_called_once_with(15000)

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_force_flush_when_shutdown(
        self, mock_safe_log: Mock, mock_json_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test force flush when exporter is shutdown.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, endpoint=TEST_OTLP_ENDPOINT
        )
        exporter._is_shutdown = True

        # Act
        result = exporter.force_flush()

        # Assert
        assert result is True
        mock_exporter_instance.force_flush.assert_not_called()
        mock_safe_log.assert_called_with(
            mock_tracer, "debug", "Exporter already shutdown, skipping force_flush"
        )


class TestHoneyHiveOTLPExporterSessionStats:
    """Test HoneyHive OTLP exporter session statistics functionality."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.get_session_stats")
    def test_get_session_stats_with_session(
        self,
        mock_get_session_stats: Mock,
        mock_json_exporter: Mock,
        *,
        mock_tracer: Mock,
        mock_requests_session: Mock,
        mock_otlp_session_config: OTLPSessionConfig,
    ) -> None:
        """Test getting session stats when session is available.

        Args:
            mock_get_session_stats: Mock for get_session_stats function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
            mock_otlp_session_config: Mock session configuration
        """
        # Arrange
        expected_stats = {"pools": 2, "connections": 10}
        mock_get_session_stats.return_value = expected_stats
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session_config=mock_otlp_session_config,
            session=mock_requests_session,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Act
        result = exporter.get_session_stats()

        # Assert
        expected_result = {
            **expected_stats,
            "session_type": "optimized",
            "session_config": mock_otlp_session_config.to_dict(),
        }
        assert result == expected_result
        mock_get_session_stats.assert_called_once_with(mock_requests_session)

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_get_session_stats_without_session(
        self, mock_json_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test getting session stats when no session is available.

        Args:
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            use_optimized_session=False,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Act
        result = exporter.get_session_stats()

        # Assert
        expected_result = {"error": "No session available", "session_type": "default"}
        assert result == expected_result

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.get_session_stats")
    def test_get_session_stats_with_exception(
        self,
        mock_get_session_stats: Mock,
        mock_json_exporter: Mock,
        mock_tracer: Mock,
        mock_requests_session: Mock,
    ) -> None:
        """Test getting session stats when get_session_stats raises exception.

        Args:
            mock_get_session_stats: Mock for get_session_stats function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
        """
        # Arrange
        test_error = AttributeError("Session not configured")
        mock_get_session_stats.side_effect = test_error
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session=mock_requests_session,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Act
        result = exporter.get_session_stats()

        # Assert
        expected_result = {
            "error": f"Failed to get session stats: {test_error}",
            "session_type": "optimized",
        }
        assert result == expected_result

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_log_session_stats(
        self,
        mock_safe_log: Mock,
        mock_json_exporter: Mock,
        mock_tracer: Mock,
        mock_requests_session: Mock,
    ) -> None:
        """Test logging session statistics.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session=mock_requests_session,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Mock get_session_stats method
        expected_stats = {"pools": 1, "connections": 5}
        with patch.object(exporter, "get_session_stats", return_value=expected_stats):
            # Act
            exporter.log_session_stats()

            # Assert - Check for the specific session stats call
            # (initialization also logs)
            mock_safe_log.assert_any_call(
                mock_tracer,
                "debug",
                "OTLP exporter session statistics",
                honeyhive_data={"session_stats": expected_stats},
            )
            # Verify we got initialization, JSON exporter init, and session stats calls
            assert mock_safe_log.call_count >= 2


class TestHoneyHiveOTLPExporterShutdown:
    """Test HoneyHive OTLP exporter shutdown functionality."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_shutdown_success_with_session_stats(
        self,
        mock_safe_log: Mock,
        mock_json_exporter: Mock,
        mock_tracer: Mock,
        mock_requests_session: Mock,
    ) -> None:
        """Test successful shutdown with session statistics logging.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session=mock_requests_session,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Mock get_session_stats method
        expected_stats = {"pools": 2, "final_connections": 8}
        with patch.object(exporter, "get_session_stats", return_value=expected_stats):
            # Act
            exporter.shutdown()

            # Assert
            assert exporter._is_shutdown is True
            mock_exporter_instance.shutdown.assert_called_once()

            # Verify logging calls (initialization + JSON init + session stats + shutdown)
            assert mock_safe_log.call_count >= 3
            mock_safe_log.assert_any_call(
                mock_tracer,
                "info",
                "OTLP exporter final session statistics",
                honeyhive_data={"final_session_stats": expected_stats},
            )
            mock_safe_log.assert_any_call(
                mock_tracer, "debug", "HoneyHiveOTLPExporter shutdown completed"
            )

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_shutdown_when_already_shutdown(
        self, mock_safe_log: Mock, mock_json_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test shutdown when exporter is already shutdown.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, endpoint=TEST_OTLP_ENDPOINT
        )
        exporter._is_shutdown = True

        # Act
        exporter.shutdown()

        # Assert
        mock_exporter_instance.shutdown.assert_not_called()
        # Check for the specific "already shutdown" call (initialization also logs)
        mock_safe_log.assert_any_call(
            mock_tracer, "debug", "Exporter already shutdown, ignoring call"
        )
        # Verify we got initialization logs plus the shutdown message
        assert mock_safe_log.call_count >= 3

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_shutdown_without_session_or_tracer(
        self, mock_safe_log: Mock, mock_json_exporter: Mock
    ) -> None:
        """Test shutdown without session or tracer instance.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=None,
            use_optimized_session=False,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Act
        exporter.shutdown()

        # Assert
        assert exporter._is_shutdown is True
        mock_exporter_instance.shutdown.assert_called_once()
        # Check for the specific shutdown completion call (initialization also logs)
        mock_safe_log.assert_any_call(
            None, "debug", "HoneyHiveOTLPExporter shutdown completed"
        )
        # Verify we got initialization and shutdown completion calls
        assert mock_safe_log.call_count >= 2

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_shutdown_with_session_stats_exception(
        self,
        mock_safe_log: Mock,
        mock_json_exporter: Mock,
        mock_tracer: Mock,
        mock_requests_session: Mock,
    ) -> None:
        """Test shutdown when getting session stats raises exception.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
        """
        # Arrange
        test_error = RuntimeError("Stats unavailable")
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session=mock_requests_session,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        with patch.object(exporter, "get_session_stats", side_effect=test_error):
            # Act
            exporter.shutdown()

            # Assert
            assert exporter._is_shutdown is True
            mock_exporter_instance.shutdown.assert_called_once()

            # Verify error logging and completion logging
            # (initialization + JSON init + error + completion)
            assert mock_safe_log.call_count >= 3
            mock_safe_log.assert_any_call(
                mock_tracer, "debug", f"Could not get final session stats: {test_error}"
            )
            mock_safe_log.assert_any_call(
                mock_tracer, "debug", "HoneyHiveOTLPExporter shutdown completed"
            )


class TestHoneyHiveOTLPExporterEdgeCases:
    """Test edge cases and comprehensive coverage scenarios."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_session_type_determination_optimized(
        self, mock_json_exporter: Mock, mock_requests_session: Mock
    ) -> None:
        """Test session type determination for optimized session.

        Args:
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            session=mock_requests_session,
            use_optimized_session=True,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Assert
        stats = exporter.get_session_stats()
        assert stats["session_type"] == "optimized"

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_session_type_determination_custom(
        self, mock_json_exporter: Mock, mock_requests_session: Mock
    ) -> None:
        """Test session type determination for custom session.

        Args:
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            session=mock_requests_session,
            use_optimized_session=False,
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Assert
        stats = exporter.get_session_stats()
        assert stats["session_type"] == "custom"

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_empty_spans_export(
        self, mock_json_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test export with empty spans sequence.

        Args:
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_exporter_instance.export.return_value = SpanExportResult.SUCCESS
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, endpoint=TEST_OTLP_ENDPOINT
        )
        empty_spans: Sequence[ReadableSpan] = []

        # Act
        result = exporter.export(empty_spans)

        # Assert
        assert result == SpanExportResult.SUCCESS
        mock_exporter_instance.export.assert_called_once_with(empty_spans)

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_session_config_none_handling(
        self, mock_json_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test handling when session_config is None in get_session_stats.

        Args:
            mock_json_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session_config=None,
            endpoint=TEST_OTLP_ENDPOINT,
        )
        exporter._session = Mock(spec=requests.Session)

        # Mock get_session_stats to return basic stats
        with patch(
            "honeyhive.tracer.processing.otlp_exporter.get_session_stats"
        ) as mock_get_stats:
            mock_get_stats.return_value = {"pools": 1}

            # Act
            result = exporter.get_session_stats()

            # Assert - Production code returns actual config even when
            # initialized with None
            assert "session_config" in result
            assert (
                result["session_config"] is not None
            )  # Production provides default config
            assert "pools" in result


class TestOTLPJSONExporter:
    """Test OTLP JSON exporter functionality."""

    @patch("honeyhive.tracer.processing.otlp_exporter.requests.Session")
    def test_json_exporter_initialization(self, mock_session_class: Mock) -> None:
        """Test JSON exporter initialization.

        Args:
            mock_session_class: Mock for requests.Session class
        """
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Act
        exporter = OTLPJSONExporter(
            TEST_OTLP_ENDPOINT,
            headers={"Authorization": "Bearer test"},
            timeout=30.0,
        )

        # Assert
        assert exporter.endpoint == TEST_OTLP_ENDPOINT
        assert exporter.headers["Content-Type"] == "application/json"
        assert exporter.headers["Authorization"] == "Bearer test"
        assert exporter.timeout == 30.0
        assert exporter._is_shutdown is False

    @patch("honeyhive.tracer.processing.otlp_exporter.requests.Session")
    def test_json_exporter_export_success(
        self,
        mock_session_class: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test successful JSON export.

        Args:
            mock_session_class: Mock for requests.Session
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Create properly structured mock spans
        span = Mock(spec=ReadableSpan)
        span.name = "test_span"
        span.context = Mock()
        span.context.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        span.context.span_id = 0x1234567890ABCDEF
        span.parent = None
        span.kind = Mock()
        span.kind.name = "INTERNAL"
        span.start_time = 1000000000
        span.end_time = 2000000000
        span.status = Mock()
        span.status.status_code = Mock()
        span.status.status_code.name = "OK"
        span.status.description = None
        span.attributes = {}
        span.events = []
        span.resource = Mock()
        span.resource.attributes = {}
        span.instrumentation_scope = None

        exporter = OTLPJSONExporter(
            TEST_OTLP_ENDPOINT,
            tracer_instance=mock_tracer,
        )

        # Act
        result = exporter.export([span])

        # Assert
        assert result == SpanExportResult.SUCCESS
        mock_session.post.assert_called_once()
        assert (
            mock_session.post.call_args[1]["headers"]["Content-Type"]
            == "application/json"
        )

    @patch("honeyhive.tracer.processing.otlp_exporter.requests.Session")
    def test_json_exporter_export_empty_spans(
        self, mock_session_class: Mock, mock_tracer: Mock
    ) -> None:
        """Test JSON export with empty spans.

        Args:
            mock_session_class: Mock for requests.Session
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        exporter = OTLPJSONExporter(
            endpoint=TEST_OTLP_ENDPOINT,
            tracer_instance=mock_tracer,
        )

        # Act
        result = exporter.export([])

        # Assert
        assert result == SpanExportResult.SUCCESS
        mock_session.post.assert_not_called()


class TestOTLPJSONExporterAnyValueMapping:
    """Verify native-type preservation in OTLP AnyValue encoding (HHAI-4935)."""

    def test_string_attribute_preserved_as_string(self) -> None:
        assert OTLPJSONExporter._to_otlp_any_value("hello") == {"stringValue": "hello"}

    def test_int_attribute_serialized_as_string(self) -> None:
        # Integers must serialize as intValue JSON strings per protobuf JSON
        # mapping spec. Raw JSON numbers lose precision above 2^53 through the
        # server's float64 decode path (HHAI-5004).
        assert OTLPJSONExporter._to_otlp_any_value(42) == {"intValue": "42"}

    def test_large_int_preserved_exactly_as_string(self) -> None:
        # int64 max — must round-trip exactly; a raw JSON number would be fine
        # here but values just above 2^53 would not.
        assert OTLPJSONExporter._to_otlp_any_value(9223372036854775807) == {
            "intValue": "9223372036854775807"
        }

    def test_int_above_float64_precision_round_trips_exactly(self) -> None:
        # 2^53 + 1 = 9007199254740993 cannot be represented exactly as float64.
        # Emitting it as a JSON string ensures the server recovers the exact value.
        import json as _json

        large = 2**53 + 1  # 9007199254740993
        result = OTLPJSONExporter._to_otlp_any_value(large)
        assert result == {"intValue": "9007199254740993"}
        # Prove the wire JSON encodes the value as a quoted string, not a bare
        # number. json.loads returns str for JSON strings and int for JSON numbers,
        # so this assertion fails if str() is ever dropped from the helper.
        wire = _json.dumps(result)
        recovered = _json.loads(wire)
        assert isinstance(recovered["intValue"], str), (
            "intValue must be a JSON string on the wire, not a number"
        )
        assert int(recovered["intValue"]) == large

    def test_float_attribute_preserved_as_double(self) -> None:
        assert OTLPJSONExporter._to_otlp_any_value(3.14) == {"doubleValue": 3.14}

    def test_non_finite_floats_fall_back_to_string(self) -> None:
        # NaN/Inf serialize to non-standard JSON tokens that the Go backend
        # rejects outright, failing the whole batch. Stringify them instead
        # so they land (matching the pre-fix behavior for this one case).
        assert OTLPJSONExporter._to_otlp_any_value(float("nan")) == {
            "stringValue": "nan"
        }
        assert OTLPJSONExporter._to_otlp_any_value(float("inf")) == {
            "stringValue": "inf"
        }
        assert OTLPJSONExporter._to_otlp_any_value(float("-inf")) == {
            "stringValue": "-inf"
        }

    def test_non_finite_float_payload_is_valid_json(self) -> None:
        # Guard against regressing into NaN/Infinity tokens in the wire JSON.
        import json as _json

        payload = OTLPJSONExporter._to_otlp_any_value(float("nan"))
        serialized = _json.dumps(payload, allow_nan=False)
        assert "NaN" not in serialized and "Infinity" not in serialized

    def test_bool_attribute_preserved_as_bool(self) -> None:
        # bool is a subclass of int in Python; the bool check must come first
        # or True would erroneously serialize as intValue 1.
        assert OTLPJSONExporter._to_otlp_any_value(True) == {"boolValue": True}
        assert OTLPJSONExporter._to_otlp_any_value(False) == {"boolValue": False}

    def test_bytes_attribute_falls_back_to_string(self) -> None:
        # OTel Python attribute spec doesn't include bytes; if one sneaks
        # through, we stringify rather than crash.
        assert OTLPJSONExporter._to_otlp_any_value(b"abc") == {"stringValue": "b'abc'"}

    def test_list_attribute_recurses(self) -> None:
        assert OTLPJSONExporter._to_otlp_any_value([1, 2, 3]) == {
            "arrayValue": {
                "values": [
                    {"intValue": "1"},
                    {"intValue": "2"},
                    {"intValue": "3"},
                ]
            }
        }

    def test_tuple_attribute_treated_as_array(self) -> None:
        assert OTLPJSONExporter._to_otlp_any_value(("a", "b")) == {
            "arrayValue": {
                "values": [
                    {"stringValue": "a"},
                    {"stringValue": "b"},
                ]
            }
        }

    def test_unknown_type_falls_back_to_string(self) -> None:
        class Custom:
            def __str__(self) -> str:
                return "custom"

        assert OTLPJSONExporter._to_otlp_any_value(Custom()) == {
            "stringValue": "custom"
        }

    def test_key_values_builder_returns_empty_for_none(self) -> None:
        assert OTLPJSONExporter._to_otlp_key_values(None) == []
        assert OTLPJSONExporter._to_otlp_key_values({}) == []

    def test_key_values_builder_preserves_types(self) -> None:
        result = OTLPJSONExporter._to_otlp_key_values(
            {"count": 42, "name": "foo", "ok": True, "ratio": 0.5}
        )
        by_key = {kv["key"]: kv["value"] for kv in result}
        assert by_key == {
            "count": {"intValue": "42"},
            "name": {"stringValue": "foo"},
            "ok": {"boolValue": True},
            "ratio": {"doubleValue": 0.5},
        }

    @patch("honeyhive.tracer.processing.otlp_exporter.requests.Session")
    def test_span_attributes_emit_typed_any_values(
        self, mock_session_class: Mock, mock_tracer: Mock
    ) -> None:
        """End-to-end: a span with mixed-type attributes must serialize with
        the correct AnyValue variants in the outgoing payload."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        span = Mock(spec=ReadableSpan)
        span.name = "typed_attrs_span"
        span.context = Mock()
        span.context.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        span.context.span_id = 0x1234567890ABCDEF
        span.parent = None
        span.kind = Mock()
        span.kind.name = "INTERNAL"
        span.start_time = 1_000_000_000
        span.end_time = 2_000_000_000
        span.status = Mock()
        span.status.status_code = Mock()
        span.status.status_code.name = "OK"
        span.status.description = None
        span.attributes = {
            "attr.int": 42,
            "attr.float": 3.14,
            "attr.bool": True,
            "attr.string": "hello",
        }
        span.events = []
        span.resource = Mock()
        span.resource.attributes = {"service.name": "svc", "replicas": 3}
        span.instrumentation_scope = None

        exporter = OTLPJSONExporter(TEST_OTLP_ENDPOINT, tracer_instance=mock_tracer)

        result = exporter.export([span])

        assert result == SpanExportResult.SUCCESS
        posted_body = mock_session.post.call_args[1]["data"]
        import json as _json

        payload = _json.loads(posted_body)
        resource_span = payload["resourceSpans"][0]

        # Resource attributes preserve native types.
        resource_attrs = {
            kv["key"]: kv["value"] for kv in resource_span["resource"]["attributes"]
        }
        assert resource_attrs == {
            "service.name": {"stringValue": "svc"},
            "replicas": {"intValue": "3"},
        }

        # Span attributes preserve native types (the HHAI-4935 regression).
        span_payload = resource_span["scopeSpans"][0]["spans"][0]
        span_attrs = {kv["key"]: kv["value"] for kv in span_payload["attributes"]}
        assert span_attrs == {
            "attr.int": {"intValue": "42"},
            "attr.float": {"doubleValue": 3.14},
            "attr.bool": {"boolValue": True},
            "attr.string": {"stringValue": "hello"},
        }


class TestOTLPJSONExporterTimestamps:
    """Verify uint64 timestamp fields are serialized as JSON strings (HHAI-5004)."""

    @patch("honeyhive.tracer.processing.otlp_exporter.requests.Session")
    def test_span_timestamps_are_strings(
        self, mock_session_class: Mock, mock_tracer: Mock
    ) -> None:
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        span = Mock(spec=ReadableSpan)
        span.name = "ts_test"
        span.context = Mock()
        span.context.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        span.context.span_id = 0x1234567890ABCDEF
        span.parent = None
        span.kind = Mock()
        span.kind.name = "INTERNAL"
        span.start_time = 1_000_000_000
        span.end_time = 2_000_000_000
        span.status = Mock()
        span.status.status_code = Mock()
        span.status.status_code.name = "UNSET"
        span.status.description = None
        span.attributes = {}
        span.resource = Mock()
        span.resource.attributes = {}
        span.instrumentation_scope = None

        event = Mock()
        event.timestamp = 1_500_000_000
        event.name = "evt"
        event.attributes = {}
        span.events = [event]

        exporter = OTLPJSONExporter(TEST_OTLP_ENDPOINT, tracer_instance=mock_tracer)
        exporter.export([span])

        import json as _json

        payload = _json.loads(mock_session.post.call_args[1]["data"])
        span_json = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]

        # protobuf JSON mapping requires uint64 fields to be JSON strings
        assert span_json["startTimeUnixNano"] == "1000000000"
        assert span_json["endTimeUnixNano"] == "2000000000"
        assert span_json["events"][0]["timeUnixNano"] == "1500000000"


class TestHoneyHiveOTLPExporterProtocol:
    """Test HoneyHive OTLP exporter protocol selection."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter")
    def test_initialization_with_json_protocol(
        self, mock_json_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test initialization with JSON protocol.

        Args:
            mock_json_exporter: Mock for OTLPJSONExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_json_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            protocol="http/json",
            endpoint=TEST_OTLP_ENDPOINT,
            headers={"Authorization": "Bearer test"},
        )

        # Assert
        assert exporter.protocol == "http/json"
        assert exporter._use_json is True
        mock_json_exporter.assert_called_once()
        call_kwargs = mock_json_exporter.call_args[1]
        assert call_kwargs["endpoint"] == TEST_OTLP_ENDPOINT
        assert call_kwargs["headers"]["Authorization"] == "Bearer test"

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_initialization_with_protobuf_protocol(
        self, mock_span_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test initialization with Protobuf protocol (uses OTLPSpanExporter).

        Args:
            mock_span_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_span_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            protocol="http/protobuf",
            endpoint=TEST_OTLP_ENDPOINT,
        )

        # Assert
        assert exporter.protocol == "http/protobuf"
        assert exporter._use_json is False
        mock_span_exporter.assert_called_once()
