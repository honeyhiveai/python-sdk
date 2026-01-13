"""Unit tests for HoneyHive OTLP exporter.

This module tests the HoneyHive OTLP exporter functionality including
initialization, span export, error handling, and lifecycle management.

This module follows Agent OS testing standards with proper type annotations,
pylint compliance, and comprehensive coverage targeting 95%+.
"""

# pylint: disable=protected-access,too-many-lines,redefined-outer-name,duplicate-code
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.

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


# Standard fixtures following Agent OS testing standards
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

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.get_default_otlp_config")
    def test_initialization_with_defaults(
        self, mock_get_default_config: Mock, mock_otlp_exporter: Mock
    ) -> None:
        """Test initialization with default parameters.

        Args:
            mock_get_default_config: Mock for get_default_otlp_config function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
        """
        # Arrange
        mock_config = OTLPSessionConfig()
        mock_get_default_config.return_value = mock_config
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter()

        # Assert
        assert exporter.tracer_instance is None
        assert exporter.session_config == mock_config
        assert exporter.use_optimized_session is True
        assert exporter.protocol == "http/protobuf"
        assert exporter._use_json is False
        assert exporter._is_shutdown is False
        mock_get_default_config.assert_called_once_with(None)
        mock_otlp_exporter.assert_called_once()

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.create_optimized_otlp_session")
    def test_initialization_with_optimized_session_success(
        self,
        mock_create_session: Mock,
        mock_otlp_exporter: Mock,
        mock_tracer: Mock,
        mock_otlp_session_config: OTLPSessionConfig,
    ) -> None:
        """Test successful initialization with optimized session.

        Args:
            mock_create_session: Mock for create_optimized_otlp_session function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_otlp_session_config: Mock session configuration
        """
        # Arrange
        mock_session = Mock(spec=requests.Session)
        mock_create_session.return_value = mock_session
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session_config=mock_otlp_session_config,
            use_optimized_session=True,
            endpoint="https://api.honeyhive.ai/opentelemetry/v1/traces",
        )

        # Assert
        assert exporter.tracer_instance == mock_tracer
        assert exporter.session_config == mock_otlp_session_config
        assert exporter._session == mock_session
        assert exporter.protocol == "http/protobuf"
        assert exporter._use_json is False
        mock_create_session.assert_called_once_with(
            config=mock_otlp_session_config, tracer_instance=mock_tracer
        )
        mock_otlp_exporter.assert_called_once_with(
            session=mock_session,
            endpoint="https://api.honeyhive.ai/opentelemetry/v1/traces",
        )

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.create_optimized_otlp_session")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_initialization_with_optimized_session_failure(
        self,
        mock_safe_log: Mock,
        mock_create_session: Mock,
        mock_otlp_exporter: Mock,
        *,
        mock_tracer: Mock,
        mock_otlp_session_config: OTLPSessionConfig,
    ) -> None:
        """Test initialization when optimized session creation fails.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_create_session: Mock for create_optimized_otlp_session function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_otlp_session_config: Mock session configuration
        """
        # Arrange
        test_error = ConnectionError("Network unavailable")
        mock_create_session.side_effect = test_error
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session_config=mock_otlp_session_config,
            use_optimized_session=True,
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
        mock_otlp_exporter.assert_called_once_with()

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_initialization_with_custom_session_provided(
        self, mock_otlp_exporter: Mock, mock_requests_session: Mock
    ) -> None:
        """Test initialization with custom session provided in kwargs.

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            use_optimized_session=True, session=mock_requests_session
        )

        # Assert
        assert exporter._session == mock_requests_session
        mock_otlp_exporter.assert_called_once_with(session=mock_requests_session)

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_initialization_without_optimized_session(
        self, mock_otlp_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test initialization with optimized session disabled.

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, use_optimized_session=False
        )

        # Assert
        assert exporter.use_optimized_session is False
        assert exporter._session is None
        mock_otlp_exporter.assert_called_once_with()


class TestHoneyHiveOTLPExporterExport:
    """Test HoneyHive OTLP exporter export functionality."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_export_success(
        self,
        mock_safe_log: Mock,
        mock_otlp_exporter: Mock,
        mock_tracer: Mock,
        mock_readable_spans: List[ReadableSpan],
    ) -> None:
        """Test successful span export.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_readable_spans: Mock readable spans
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_exporter_instance.export.return_value = SpanExportResult.SUCCESS
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(tracer_instance=mock_tracer)

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

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_export_when_shutdown(
        self,
        mock_safe_log: Mock,
        mock_otlp_exporter: Mock,
        mock_tracer: Mock,
        mock_readable_spans: List[ReadableSpan],
    ) -> None:
        """Test export when exporter is already shutdown.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_readable_spans: Mock readable spans
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(tracer_instance=mock_tracer)
        exporter._is_shutdown = True

        # Act
        result = exporter.export(mock_readable_spans)

        # Assert
        assert result == SpanExportResult.FAILURE
        mock_exporter_instance.export.assert_not_called()
        mock_safe_log.assert_called_with(
            mock_tracer, "debug", "Exporter already shutdown, skipping export"
        )

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_export_with_exception(
        self,
        mock_safe_log: Mock,
        mock_otlp_exporter: Mock,
        mock_tracer: Mock,
        mock_readable_spans: List[ReadableSpan],
    ) -> None:
        """Test export when underlying exporter raises exception.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_readable_spans: Mock readable spans
        """
        # Arrange
        test_error = RuntimeError("Export failed")
        mock_exporter_instance = Mock()
        mock_exporter_instance.export.side_effect = test_error
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(tracer_instance=mock_tracer)

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

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_force_flush_success(
        self, mock_otlp_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test successful force flush.

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_exporter_instance.force_flush.return_value = True
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(tracer_instance=mock_tracer)

        # Act
        result = exporter.force_flush(timeout_millis=15000)

        # Assert
        assert result is True
        mock_exporter_instance.force_flush.assert_called_once_with(15000)

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_force_flush_when_shutdown(
        self, mock_safe_log: Mock, mock_otlp_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test force flush when exporter is shutdown.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(tracer_instance=mock_tracer)
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

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.get_session_stats")
    def test_get_session_stats_with_session(
        self,
        mock_get_session_stats: Mock,
        mock_otlp_exporter: Mock,
        *,
        mock_tracer: Mock,
        mock_requests_session: Mock,
        mock_otlp_session_config: OTLPSessionConfig,
    ) -> None:
        """Test getting session stats when session is available.

        Args:
            mock_get_session_stats: Mock for get_session_stats function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
            mock_otlp_session_config: Mock session configuration
        """
        # Arrange
        expected_stats = {"pools": 2, "connections": 10}
        mock_get_session_stats.return_value = expected_stats
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            session_config=mock_otlp_session_config,
            session=mock_requests_session,
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

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_get_session_stats_without_session(
        self, mock_otlp_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test getting session stats when no session is available.

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, use_optimized_session=False
        )

        # Act
        result = exporter.get_session_stats()

        # Assert
        expected_result = {"error": "No session available", "session_type": "default"}
        assert result == expected_result

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.get_session_stats")
    def test_get_session_stats_with_exception(
        self,
        mock_get_session_stats: Mock,
        mock_otlp_exporter: Mock,
        mock_tracer: Mock,
        mock_requests_session: Mock,
    ) -> None:
        """Test getting session stats when get_session_stats raises exception.

        Args:
            mock_get_session_stats: Mock for get_session_stats function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
        """
        # Arrange
        test_error = AttributeError("Session not configured")
        mock_get_session_stats.side_effect = test_error
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, session=mock_requests_session
        )

        # Act
        result = exporter.get_session_stats()

        # Assert
        expected_result = {
            "error": f"Failed to get session stats: {test_error}",
            "session_type": "optimized",
        }
        assert result == expected_result

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_log_session_stats(
        self,
        mock_safe_log: Mock,
        mock_otlp_exporter: Mock,
        mock_tracer: Mock,
        mock_requests_session: Mock,
    ) -> None:
        """Test logging session statistics.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, session=mock_requests_session
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
            # Verify we got both initialization and session stats calls
            assert mock_safe_log.call_count == 2


class TestHoneyHiveOTLPExporterShutdown:
    """Test HoneyHive OTLP exporter shutdown functionality."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_shutdown_success_with_session_stats(
        self,
        mock_safe_log: Mock,
        mock_otlp_exporter: Mock,
        mock_tracer: Mock,
        mock_requests_session: Mock,
    ) -> None:
        """Test successful shutdown with session statistics logging.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, session=mock_requests_session
        )

        # Mock get_session_stats method
        expected_stats = {"pools": 2, "final_connections": 8}
        with patch.object(exporter, "get_session_stats", return_value=expected_stats):
            # Act
            exporter.shutdown()

            # Assert
            assert exporter._is_shutdown is True
            mock_exporter_instance.shutdown.assert_called_once()

            # Verify logging calls (initialization + session stats + shutdown)
            assert mock_safe_log.call_count == 3
            mock_safe_log.assert_any_call(
                mock_tracer,
                "info",
                "OTLP exporter final session statistics",
                honeyhive_data={"final_session_stats": expected_stats},
            )
            mock_safe_log.assert_any_call(
                mock_tracer, "debug", "HoneyHiveOTLPExporter shutdown completed"
            )

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_shutdown_when_already_shutdown(
        self, mock_safe_log: Mock, mock_otlp_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test shutdown when exporter is already shutdown.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(tracer_instance=mock_tracer)
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
        assert mock_safe_log.call_count == 3

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_shutdown_without_session_or_tracer(
        self, mock_safe_log: Mock, mock_otlp_exporter: Mock
    ) -> None:
        """Test shutdown without session or tracer instance.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=None, use_optimized_session=False
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
        assert mock_safe_log.call_count == 2

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    @patch("honeyhive.tracer.processing.otlp_exporter.safe_log")
    def test_shutdown_with_session_stats_exception(
        self,
        mock_safe_log: Mock,
        mock_otlp_exporter: Mock,
        mock_tracer: Mock,
        mock_requests_session: Mock,
    ) -> None:
        """Test shutdown when getting session stats raises exception.

        Args:
            mock_safe_log: Mock for safe_log function
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
            mock_requests_session: Mock requests session
        """
        # Arrange
        test_error = RuntimeError("Stats unavailable")
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, session=mock_requests_session
        )

        with patch.object(exporter, "get_session_stats", side_effect=test_error):
            # Act
            exporter.shutdown()

            # Assert
            assert exporter._is_shutdown is True
            mock_exporter_instance.shutdown.assert_called_once()

            # Verify error logging and completion logging
            # (initialization + error + completion)
            assert mock_safe_log.call_count == 3
            mock_safe_log.assert_any_call(
                mock_tracer, "debug", f"Could not get final session stats: {test_error}"
            )
            mock_safe_log.assert_any_call(
                mock_tracer, "debug", "HoneyHiveOTLPExporter shutdown completed"
            )


class TestHoneyHiveOTLPExporterEdgeCases:
    """Test edge cases and comprehensive coverage scenarios."""

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_session_type_determination_optimized(
        self, mock_otlp_exporter: Mock, mock_requests_session: Mock
    ) -> None:
        """Test session type determination for optimized session.

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            session=mock_requests_session, use_optimized_session=True
        )

        # Assert
        stats = exporter.get_session_stats()
        assert stats["session_type"] == "optimized"

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_session_type_determination_custom(
        self, mock_otlp_exporter: Mock, mock_requests_session: Mock
    ) -> None:
        """Test session type determination for custom session.

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_requests_session: Mock requests session
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            session=mock_requests_session, use_optimized_session=False
        )

        # Assert
        stats = exporter.get_session_stats()
        assert stats["session_type"] == "custom"

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_empty_spans_export(
        self, mock_otlp_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test export with empty spans sequence.

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_exporter_instance.export.return_value = SpanExportResult.SUCCESS
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(tracer_instance=mock_tracer)
        empty_spans: Sequence[ReadableSpan] = []

        # Act
        result = exporter.export(empty_spans)

        # Assert
        assert result == SpanExportResult.SUCCESS
        mock_exporter_instance.export.assert_called_once_with(empty_spans)

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_session_config_none_handling(
        self, mock_otlp_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test handling when session_config is None in get_session_stats.

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer, session_config=None
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
            "https://api.honeyhive.ai/opentelemetry/v1/traces",
            headers={"Authorization": "Bearer test"},
            timeout=30.0,
        )

        # Assert
        assert exporter.endpoint == "https://api.honeyhive.ai/opentelemetry/v1/traces"
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
            "https://api.honeyhive.ai/opentelemetry/v1/traces",
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
            endpoint="https://api.honeyhive.ai/opentelemetry/v1/traces",
            tracer_instance=mock_tracer,
        )

        # Act
        result = exporter.export([])

        # Assert
        assert result == SpanExportResult.SUCCESS
        mock_session.post.assert_not_called()


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
            endpoint="https://api.honeyhive.ai/opentelemetry/v1/traces",
            headers={"Authorization": "Bearer test"},
        )

        # Assert
        assert exporter.protocol == "http/json"
        assert exporter._use_json is True
        mock_json_exporter.assert_called_once()
        call_kwargs = mock_json_exporter.call_args[1]
        assert (
            call_kwargs["endpoint"]
            == "https://api.honeyhive.ai/opentelemetry/v1/traces"
        )
        assert call_kwargs["headers"]["Authorization"] == "Bearer test"

    @patch("honeyhive.tracer.processing.otlp_exporter.OTLPSpanExporter")
    def test_initialization_with_protobuf_protocol(
        self, mock_otlp_exporter: Mock, mock_tracer: Mock
    ) -> None:
        """Test initialization with Protobuf protocol (default).

        Args:
            mock_otlp_exporter: Mock for OTLPSpanExporter class
            mock_tracer: Mock tracer instance
        """
        # Arrange
        mock_exporter_instance = Mock()
        mock_otlp_exporter.return_value = mock_exporter_instance

        # Act
        exporter = HoneyHiveOTLPExporter(
            tracer_instance=mock_tracer,
            protocol="http/protobuf",
            endpoint="https://api.honeyhive.ai/opentelemetry/v1/traces",
        )

        # Assert
        assert exporter.protocol == "http/protobuf"
        assert exporter._use_json is False
        mock_otlp_exporter.assert_called_once()
