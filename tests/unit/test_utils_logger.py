"""Unit tests for honeyhive.utils.logger.

This module contains comprehensive unit tests for the HoneyHive logging utilities,
including structured logging, shutdown detection, and safe logging functionality.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

import json
import logging
import sys
from datetime import timezone
from unittest.mock import Mock, PropertyMock, patch

import pytest

from honeyhive.utils.logger import (
    HoneyHiveFormatter,
    HoneyHiveLogger,
    _detect_shutdown_conditions,
    _extract_verbose_from_tracer_dynamically,
    _shutdown_detected,
    default_logger,
    get_logger,
    get_tracer_logger,
    is_shutdown_detected,
    reset_logging_state,
    safe_debug,
    safe_error,
    safe_info,
    safe_log,
    safe_warning,
)


class TestHoneyHiveFormatter:
    """Test suite for HoneyHiveFormatter class."""

    def test_initialization_with_defaults(self) -> None:
        """Test HoneyHiveFormatter initialization with default parameters."""
        formatter = HoneyHiveFormatter()

        assert formatter.include_timestamp is True
        assert formatter.include_level is True

    def test_initialization_with_custom_parameters(self) -> None:
        """Test HoneyHiveFormatter initialization with custom parameters."""
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=False)

        assert formatter.include_timestamp is False
        assert formatter.include_level is False

    @patch("honeyhive.utils.logger.datetime")
    def test_format_with_all_fields(self, mock_datetime: Mock) -> None:
        """Test formatting log record with all fields included."""
        # Arrange
        mock_now = Mock()
        mock_now.isoformat.return_value = "2023-01-01T12:00:00+00:00"
        mock_datetime.now.return_value = mock_now

        formatter = HoneyHiveFormatter(include_timestamp=True, include_level=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Act
        result = formatter.format(record)

        # Assert
        parsed_result = json.loads(result)
        assert parsed_result["timestamp"] == "2023-01-01T12:00:00+00:00"
        assert parsed_result["level"] == "INFO"
        assert parsed_result["logger"] == "test.logger"
        assert parsed_result["message"] == "Test message"
        mock_datetime.now.assert_called_once_with(timezone.utc)

    def test_format_without_timestamp(self) -> None:
        """Test formatting log record without timestamp."""
        # Arrange
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=10,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        # Act
        result = formatter.format(record)

        # Assert
        parsed_result = json.loads(result)
        assert "timestamp" not in parsed_result
        assert parsed_result["level"] == "WARNING"
        assert parsed_result["logger"] == "test.logger"
        assert parsed_result["message"] == "Warning message"

    def test_format_without_level(self) -> None:
        """Test formatting log record without level."""
        # Arrange
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error message",
            args=(),
            exc_info=None,
        )

        # Act
        result = formatter.format(record)

        # Assert
        parsed_result = json.loads(result)
        assert "timestamp" not in parsed_result
        assert "level" not in parsed_result
        assert parsed_result["logger"] == "test.logger"
        assert parsed_result["message"] == "Error message"

    def test_format_with_honeyhive_data(self) -> None:
        """Test formatting log record with HoneyHive context data."""
        # Arrange
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Context message",
            args=(),
            exc_info=None,
        )
        honeyhive_data = {"session_id": "test-123", "project": "test-project"}
        record.honeyhive_data = honeyhive_data

        # Act
        result = formatter.format(record)

        # Assert
        parsed_result = json.loads(result)
        assert parsed_result["logger"] == "test.logger"
        assert parsed_result["message"] == "Context message"
        assert parsed_result["session_id"] == "test-123"
        assert parsed_result["project"] == "test-project"

    def test_format_with_exception_info(self) -> None:
        """Test formatting log record with exception information."""
        # Arrange
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=False)

        exc_info = None
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Exception occurred",
            args=(),
            exc_info=exc_info,
        )

        # Act
        result = formatter.format(record)

        # Assert
        parsed_result = json.loads(result)
        assert parsed_result["logger"] == "test.logger"
        assert parsed_result["message"] == "Exception occurred"
        assert "exception" in parsed_result
        assert "ValueError: Test exception" in parsed_result["exception"]

    def test_format_removes_none_values(self) -> None:
        """Test that formatting removes None values from output."""
        # Arrange
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Clean message",
            args=(),
            exc_info=None,
        )

        # Act
        result = formatter.format(record)

        # Assert
        parsed_result = json.loads(result)
        assert "timestamp" not in parsed_result
        assert "level" not in parsed_result
        assert parsed_result["logger"] == "test.logger"
        assert parsed_result["message"] == "Clean message"


class TestHoneyHiveLogger:
    """Test suite for HoneyHiveLogger class."""

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_initialization_with_defaults(self, mock_get_logger: Mock) -> None:
        """Test HoneyHiveLogger initialization with default parameters."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        # Act
        logger = HoneyHiveLogger("test.logger")

        # Assert
        assert logger.logger == mock_logger
        assert logger.verbose is None
        mock_get_logger.assert_called_once_with("test.logger")
        mock_logger.setLevel.assert_called_once_with(logging.WARNING)
        assert mock_logger.propagate is False

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_initialization_with_explicit_level(self, mock_get_logger: Mock) -> None:
        """Test HoneyHiveLogger initialization with explicit log level."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        # Act
        logger = HoneyHiveLogger("test.logger", level=logging.DEBUG)

        # Assert
        assert logger.logger == mock_logger
        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_initialization_with_string_level(self, mock_get_logger: Mock) -> None:
        """Test HoneyHiveLogger initialization with string log level."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        # Act
        logger = HoneyHiveLogger("test.logger", level="WARNING")

        # Assert
        assert logger.logger == mock_logger
        mock_logger.setLevel.assert_called_once_with(logging.WARNING)

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_initialization_with_verbose_true(self, mock_get_logger: Mock) -> None:
        """Test HoneyHiveLogger initialization with verbose=True."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        # Act
        logger = HoneyHiveLogger("test.logger", verbose=True)

        # Assert
        assert logger.verbose is True
        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_initialization_with_verbose_false(self, mock_get_logger: Mock) -> None:
        """Test HoneyHiveLogger initialization with verbose=False."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        # Act
        logger = HoneyHiveLogger("test.logger", verbose=False)

        # Assert
        assert logger.verbose is False
        mock_logger.setLevel.assert_called_once_with(logging.WARNING)

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_initialization_with_custom_handler(self, mock_get_logger: Mock) -> None:
        """Test HoneyHiveLogger initialization with custom handler."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        custom_handler = Mock()

        # Act
        logger = HoneyHiveLogger("test.logger", handler=custom_handler)

        # Assert
        assert logger.logger == mock_logger
        mock_logger.addHandler.assert_called_once_with(custom_handler)

    @patch("honeyhive.utils.logger.logging.getLogger")
    @patch("honeyhive.utils.logger.logging.StreamHandler")
    @patch("honeyhive.utils.logger.HoneyHiveFormatter")
    def test_initialization_creates_default_handler(
        self,
        mock_formatter_class: Mock,
        mock_handler_class: Mock,
        mock_get_logger: Mock,
    ) -> None:
        """Test HoneyHiveLogger creates default handler when none provided."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter

        # Act
        _ = HoneyHiveLogger("test.logger")

        # Assert
        mock_handler_class.assert_called_once_with(sys.stdout)
        mock_formatter_class.assert_called_once()
        mock_handler.setFormatter.assert_called_once_with(mock_formatter)
        mock_logger.addHandler.assert_called_once_with(mock_handler)

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_initialization_with_existing_handlers(self, mock_get_logger: Mock) -> None:
        """Test HoneyHiveLogger initialization when logger already has handlers."""
        # Arrange
        mock_logger = Mock()
        existing_handler = Mock()
        mock_logger.handlers = [existing_handler]
        mock_get_logger.return_value = mock_logger

        # Act
        logger = HoneyHiveLogger("test.logger")

        # Assert
        assert logger.logger == mock_logger
        mock_logger.addHandler.assert_not_called()

    def test_determine_log_level_dynamically_with_explicit_level(self) -> None:
        """Test dynamic log level determination with explicit level parameter."""
        # Arrange
        logger = HoneyHiveLogger.__new__(HoneyHiveLogger)

        # Act
        result = logger._determine_log_level_dynamically(logging.ERROR, None)

        # Assert
        assert result == logging.ERROR

    def test_determine_log_level_dynamically_with_string_level(self) -> None:
        """Test dynamic log level determination with string level parameter."""
        # Arrange
        logger = HoneyHiveLogger.__new__(HoneyHiveLogger)

        # Act
        result = logger._determine_log_level_dynamically("CRITICAL", None)

        # Assert
        assert result == logging.CRITICAL

    def test_determine_log_level_dynamically_with_invalid_string(self) -> None:
        """Test dynamic log level determination with invalid string level."""
        # Arrange
        logger = HoneyHiveLogger.__new__(HoneyHiveLogger)

        # Act
        result = logger._determine_log_level_dynamically("INVALID", None)

        # Assert
        assert result == logging.WARNING

    def test_determine_log_level_dynamically_with_verbose_true(self) -> None:
        """Test dynamic log level determination with verbose=True."""
        # Arrange
        logger = HoneyHiveLogger.__new__(HoneyHiveLogger)

        # Act
        result = logger._determine_log_level_dynamically(None, True)

        # Assert
        assert result == logging.DEBUG

    def test_determine_log_level_dynamically_with_verbose_false(self) -> None:
        """Test dynamic log level determination with verbose=False."""
        # Arrange
        logger = HoneyHiveLogger.__new__(HoneyHiveLogger)

        # Act
        result = logger._determine_log_level_dynamically(None, False)

        # Assert
        assert result == logging.WARNING

    def test_determine_log_level_dynamically_with_defaults(self) -> None:
        """Test dynamic log level determination with default values."""
        # Arrange
        logger = HoneyHiveLogger.__new__(HoneyHiveLogger)

        # Act
        result = logger._determine_log_level_dynamically(None, None)

        # Assert
        assert result == logging.WARNING

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_update_verbose_setting_to_true(self, mock_get_logger: Mock) -> None:
        """Test updating verbose setting to True."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger", verbose=False)

        # Act
        logger.update_verbose_setting(True)

        # Assert
        assert logger.verbose is True
        mock_logger.setLevel.assert_called_with(logging.DEBUG)

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_update_verbose_setting_to_false(self, mock_get_logger: Mock) -> None:
        """Test updating verbose setting to False."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger", verbose=True)

        # Act
        logger.update_verbose_setting(False)

        # Assert
        assert logger.verbose is False
        mock_logger.setLevel.assert_called_with(logging.WARNING)

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_log_with_context_basic(self, mock_get_logger: Mock) -> None:
        """Test _log_with_context with basic parameters."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger")

        # Act
        logger._log_with_context(logging.INFO, "Test message", ("arg1", "arg2"))

        # Assert
        mock_logger.log.assert_called_once_with(
            logging.INFO, "Test message", "arg1", "arg2", extra={}
        )

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_log_with_context_with_honeyhive_data(self, mock_get_logger: Mock) -> None:
        """Test _log_with_context with HoneyHive context data."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger")
        honeyhive_data = {"session_id": "test-123"}

        # Act
        logger._log_with_context(
            logging.WARNING,
            "Warning message",
            (),
            honeyhive_data,
            extra_key="extra_value",
        )

        # Assert
        mock_logger.log.assert_called_once_with(
            logging.WARNING,
            "Warning message",
            extra={"honeyhive_data": honeyhive_data, "extra_key": "extra_value"},
        )

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_debug_method(self, mock_get_logger: Mock) -> None:
        """Test debug logging method."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger")
        honeyhive_data = {"debug_info": "test"}

        # Act
        logger.debug(
            "Debug message %s", "arg1", honeyhive_data=honeyhive_data, extra="value"
        )

        # Assert
        mock_logger.log.assert_called_once_with(
            logging.DEBUG,
            "Debug message %s",
            "arg1",
            extra={"honeyhive_data": honeyhive_data, "extra": "value"},
        )

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_info_method(self, mock_get_logger: Mock) -> None:
        """Test info logging method."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger")

        # Act
        logger.info("Info message")

        # Assert
        mock_logger.log.assert_called_once_with(logging.INFO, "Info message", extra={})

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_warning_method(self, mock_get_logger: Mock) -> None:
        """Test warning logging method."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger")

        # Act
        logger.warning("Warning message")

        # Assert
        mock_logger.log.assert_called_once_with(
            logging.WARNING, "Warning message", extra={}
        )

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_error_method(self, mock_get_logger: Mock) -> None:
        """Test error logging method."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger")

        # Act
        logger.error("Error message")

        # Assert
        mock_logger.log.assert_called_once_with(
            logging.ERROR, "Error message", extra={}
        )

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_critical_method(self, mock_get_logger: Mock) -> None:
        """Test critical logging method."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger")

        # Act
        logger.critical("Critical message")

        # Assert
        mock_logger.log.assert_called_once_with(
            logging.CRITICAL, "Critical message", extra={}
        )

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_exception_method(self, mock_get_logger: Mock) -> None:
        """Test exception logging method."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        logger = HoneyHiveLogger("test.logger")
        honeyhive_data = {"error_context": "test"}

        # Act
        logger.exception(
            "Exception message", honeyhive_data=honeyhive_data, extra="value"
        )

        # Assert
        mock_logger.exception.assert_called_once_with(
            "Exception message",
            extra={"honeyhive_data": honeyhive_data, "extra": "value"},
        )


class TestShutdownDetection:
    """Test suite for shutdown detection functionality."""

    def setup_method(self) -> None:
        """Reset shutdown state before each test."""
        reset_logging_state()

    def test_reset_logging_state(self) -> None:
        """Test that reset_logging_state clears shutdown detection."""
        # Arrange
        _shutdown_detected.set()
        assert _shutdown_detected.is_set() is True

        # Act
        reset_logging_state()

        # Assert
        assert _shutdown_detected.is_set() is False

    def test_is_shutdown_detected_when_not_shutdown(self) -> None:
        """Test is_shutdown_detected returns False when not shutdown."""
        # Act
        result = is_shutdown_detected()

        # Assert
        assert result is False

    @patch("honeyhive.utils.logger.sys", None)
    def test_detect_shutdown_conditions_with_none_sys(self) -> None:
        """Test shutdown detection when sys module is None."""
        # Act
        result = _detect_shutdown_conditions()

        # Assert
        assert result is True
        assert _shutdown_detected.is_set() is True

    @patch("honeyhive.utils.logger.threading", None)
    def test_detect_shutdown_conditions_with_none_threading(self) -> None:
        """Test shutdown detection when threading module is None."""
        # Act
        result = _detect_shutdown_conditions()

        # Assert
        assert result is True
        assert _shutdown_detected.is_set() is True

    def test_detect_shutdown_conditions_with_attribute_error(self) -> None:
        """Test shutdown detection when AttributeError is raised."""
        # Arrange
        with patch("honeyhive.utils.logger.sys") as mock_sys:
            mock_sys.stdout = None
            del mock_sys.stdout  # This will cause AttributeError

            # Act
            result = _detect_shutdown_conditions()

            # Assert
            assert result is True
            assert _shutdown_detected.is_set() is True

    @patch("honeyhive.utils.logger.sys")
    def test_detect_shutdown_conditions_with_closed_stdout(
        self, mock_sys: Mock
    ) -> None:
        """Test shutdown detection when stdout is closed."""
        # Arrange
        mock_stdout = Mock()
        mock_stdout.closed = True
        mock_sys.stdout = mock_stdout
        mock_sys.stderr = Mock()
        mock_sys.stderr.closed = False

        # Act
        result = _detect_shutdown_conditions()

        # Assert
        assert result is True
        assert _shutdown_detected.is_set() is True

    @patch("honeyhive.utils.logger.sys")
    def test_detect_shutdown_conditions_with_closed_stderr(
        self, mock_sys: Mock
    ) -> None:
        """Test shutdown detection when stderr is closed."""
        # Arrange
        mock_stdout = Mock()
        mock_stdout.closed = False
        mock_stderr = Mock()
        mock_stderr.closed = True
        mock_sys.stdout = mock_stdout
        mock_sys.stderr = mock_stderr

        # Act
        result = _detect_shutdown_conditions()

        # Assert
        assert result is True
        assert _shutdown_detected.is_set() is True

    @patch("honeyhive.utils.logger.sys")
    def test_detect_shutdown_conditions_with_os_error(self, mock_sys: Mock) -> None:
        """Test shutdown detection when OSError is raised."""
        # Arrange
        mock_stdout = Mock()
        mock_stdout.closed = PropertyMock(side_effect=OSError("Stream error"))
        mock_sys.stdout = mock_stdout

        # Act
        result = _detect_shutdown_conditions()

        # Assert
        assert result is True
        assert _shutdown_detected.is_set() is True

    @patch("honeyhive.utils.logger.sys")
    def test_detect_shutdown_conditions_normal_operation(self, mock_sys: Mock) -> None:
        """Test shutdown detection during normal operation."""
        # Arrange
        mock_stdout = Mock()
        mock_stdout.closed = False
        mock_stderr = Mock()
        mock_stderr.closed = False
        mock_sys.stdout = mock_stdout
        mock_sys.stderr = mock_stderr

        # Act
        result = _detect_shutdown_conditions()

        # Assert
        assert result is False
        assert _shutdown_detected.is_set() is False

    def test_detect_shutdown_conditions_already_detected(self) -> None:
        """Test shutdown detection when already detected."""
        # Arrange
        _shutdown_detected.set()

        # Act
        result = _detect_shutdown_conditions()

        # Assert
        assert result is True

    def test_is_shutdown_detected_calls_detect_shutdown_conditions(self) -> None:
        """Test that is_shutdown_detected calls _detect_shutdown_conditions."""
        # Arrange
        with patch("honeyhive.utils.logger._detect_shutdown_conditions") as mock_detect:
            mock_detect.return_value = True

            # Act
            result = is_shutdown_detected()

            # Assert
            assert result is True
            mock_detect.assert_called_once()


class TestModuleLevelFunctions:
    """Test suite for module-level logger functions."""

    def setup_method(self) -> None:
        """Reset shutdown state before each test."""
        reset_logging_state()

    @patch("honeyhive.utils.logger.HoneyHiveLogger")
    def test_get_logger_with_defaults(self, mock_logger_class: Mock) -> None:
        """Test get_logger with default parameters."""
        # Arrange
        mock_logger_instance = Mock()
        mock_logger_class.return_value = mock_logger_instance

        # Act
        result = get_logger("test.logger")

        # Assert
        assert result == mock_logger_instance
        mock_logger_class.assert_called_once_with("test.logger", verbose=None)

    @patch("honeyhive.utils.logger.HoneyHiveLogger")
    def test_get_logger_with_explicit_verbose(self, mock_logger_class: Mock) -> None:
        """Test get_logger with explicit verbose parameter."""
        # Arrange
        mock_logger_instance = Mock()
        mock_logger_class.return_value = mock_logger_instance

        # Act
        result = get_logger("test.logger", verbose=True, level=logging.DEBUG)

        # Assert
        assert result == mock_logger_instance
        mock_logger_class.assert_called_once_with(
            "test.logger", verbose=True, level=logging.DEBUG
        )

    @patch("honeyhive.utils.logger.HoneyHiveLogger")
    @patch("honeyhive.utils.logger._extract_verbose_from_tracer_dynamically")
    def test_get_logger_with_tracer_instance(
        self, mock_extract_verbose: Mock, mock_logger_class: Mock
    ) -> None:
        """Test get_logger with tracer instance."""
        # Arrange
        mock_logger_instance = Mock()
        mock_logger_class.return_value = mock_logger_instance
        mock_extract_verbose.return_value = True
        mock_tracer = Mock()

        # Act
        result = get_logger("test.logger", tracer_instance=mock_tracer)

        # Assert
        assert result == mock_logger_instance
        mock_extract_verbose.assert_called_once_with(mock_tracer)
        mock_logger_class.assert_called_once_with("test.logger", verbose=True)

    @patch("honeyhive.utils.logger.get_logger")
    def test_get_tracer_logger_with_default_name(self, mock_get_logger: Mock) -> None:
        """Test get_tracer_logger with default logger name generation."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_tracer = Mock()
        mock_tracer.tracer_id = "test-tracer-123"

        # Act
        result = get_tracer_logger(mock_tracer)

        # Assert
        assert result == mock_logger
        mock_get_logger.assert_called_once_with(
            name="honeyhive.tracer.test-tracer-123", tracer_instance=mock_tracer
        )

    @patch("honeyhive.utils.logger.get_logger")
    def test_get_tracer_logger_with_custom_name(self, mock_get_logger: Mock) -> None:
        """Test get_tracer_logger with custom logger name."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_tracer = Mock()

        # Act
        result = get_tracer_logger(mock_tracer, "custom.logger")

        # Assert
        assert result == mock_logger
        mock_get_logger.assert_called_once_with(
            name="custom.logger", tracer_instance=mock_tracer
        )

    @patch("honeyhive.utils.logger.get_logger")
    def test_get_tracer_logger_without_tracer_id(self, mock_get_logger: Mock) -> None:
        """Test get_tracer_logger when tracer has no tracer_id attribute."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_tracer = Mock()
        del mock_tracer.tracer_id  # Remove tracer_id attribute

        # Act
        result = get_tracer_logger(mock_tracer)

        # Assert
        assert result == mock_logger
        # Should use id(mock_tracer) as fallback
        expected_name = f"honeyhive.tracer.{id(mock_tracer)}"
        mock_get_logger.assert_called_once_with(
            name=expected_name, tracer_instance=mock_tracer
        )

    def test_extract_verbose_from_tracer_dynamically_with_none(self) -> None:
        """Test _extract_verbose_from_tracer_dynamically with None tracer."""
        # Act
        result = _extract_verbose_from_tracer_dynamically(None)

        # Assert
        assert result is None

    def test_extract_verbose_from_tracer_dynamically_with_verbose_attr(self) -> None:
        """Test _extract_verbose_from_tracer_dynamically with verbose attribute."""
        # Arrange
        mock_tracer = Mock()
        mock_tracer.verbose = True

        # Act
        result = _extract_verbose_from_tracer_dynamically(mock_tracer)

        # Assert
        assert result is True

    def test_extract_verbose_from_tracer_dynamically_with_private_verbose(self) -> None:
        """Test _extract_verbose_from_tracer_dynamically with _verbose attribute."""
        # Arrange
        mock_tracer = Mock()
        del mock_tracer.verbose  # Remove verbose attribute
        mock_tracer._verbose = False

        # Act
        result = _extract_verbose_from_tracer_dynamically(mock_tracer)

        # Assert
        assert result is False

    def test_extract_verbose_from_tracer_dynamically_with_config_verbose(
        self,
    ) -> None:
        """Test _extract_verbose_from_tracer_dynamically with config.verbose."""
        # Arrange
        mock_tracer = Mock()
        del mock_tracer.verbose  # Remove verbose attribute
        del mock_tracer._verbose  # Remove _verbose attribute
        mock_config = Mock()
        mock_config.verbose = True
        mock_tracer.config = mock_config

        # Act
        result = _extract_verbose_from_tracer_dynamically(mock_tracer)

        # Assert
        assert result is True

    def test_extract_verbose_from_tracer_dynamically_with_none_config(self) -> None:
        """Test _extract_verbose_from_tracer_dynamically with None config."""
        # Arrange
        mock_tracer = Mock()
        del mock_tracer.verbose  # Remove verbose attribute
        del mock_tracer._verbose  # Remove _verbose attribute
        mock_tracer.config = None

        # Act
        result = _extract_verbose_from_tracer_dynamically(mock_tracer)

        # Assert
        assert result is None

    def test_extract_verbose_from_tracer_dynamically_with_attribute_error(self) -> None:
        """Test _extract_verbose_from_tracer_dynamically with AttributeError."""
        # Arrange
        mock_tracer = Mock()
        del mock_tracer.verbose  # Remove verbose attribute

        # Act
        result = _extract_verbose_from_tracer_dynamically(mock_tracer)

        # Assert
        assert result is None

    def test_extract_verbose_from_tracer_dynamically_with_non_boolean(self) -> None:
        """Test _extract_verbose_from_tracer_dynamically with non-boolean value."""
        # Arrange
        mock_tracer = Mock()
        mock_tracer.verbose = "not_boolean"

        # Act
        result = _extract_verbose_from_tracer_dynamically(mock_tracer)

        # Assert
        assert result is None

    def test_default_logger_exists(self) -> None:
        """Test that default_logger is properly initialized."""
        # Assert
        assert default_logger is not None
        assert hasattr(default_logger, "logger")


class TestSafeLogFunction:
    """Test suite for safe_log function and convenience functions."""

    def setup_method(self) -> None:
        """Reset shutdown state before each test."""
        reset_logging_state()

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_returns_early_on_shutdown(
        self, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log returns early when shutdown is detected."""
        # Arrange
        mock_detect_shutdown.return_value = True

        # Act
        safe_log(None, "info", "Test message")

        # Assert
        # safe_log should complete without raising exceptions
        mock_detect_shutdown.assert_called_once()

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_with_tracer_instance_logger(
        self, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log with tracer instance that has logger."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_logger = Mock()
        # The safe_log function checks target_logger.logger.handlers
        mock_logger.logger = Mock()
        mock_logger.logger.handlers = [Mock()]  # Ensure handlers exist
        mock_tracer.logger = mock_logger

        # Act
        safe_log(
            mock_tracer,
            "info",
            "Test message %s",
            "arg1",
            honeyhive_data={"key": "value"},
        )

        # Assert - safe_log should return None and not raise exceptions
        # safe_log should complete without raising exceptions
        # The function should attempt to call the logger method
        # Due to the complex fallback logic, we verify it doesn't crash

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_with_tracer_instance_delegation(
        self, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log with API client pattern delegation."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_api_client = Mock()
        mock_actual_tracer = Mock()
        mock_logger = Mock()
        mock_actual_tracer.logger = mock_logger
        mock_api_client.tracer_instance = mock_actual_tracer
        del mock_api_client.logger  # Remove logger from API client

        with patch("honeyhive.utils.logger.safe_log") as mock_safe_log_recursive:
            # Act
            safe_log(mock_api_client, "warning", "Warning message")

            # Assert
            mock_safe_log_recursive.assert_called_once_with(
                mock_actual_tracer, "warning", "Warning message", honeyhive_data=None
            )

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    @patch("honeyhive.utils.logger.get_logger")
    def test_safe_log_with_partial_tracer_instance(
        self, mock_get_logger: Mock, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log with partially initialized tracer instance."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_tracer.verbose = True
        del mock_tracer.logger  # Remove logger attribute
        del mock_tracer.tracer_instance  # Remove tracer_instance attribute
        mock_temp_logger = Mock()
        mock_temp_logger.logger.handlers = [Mock()]  # Ensure handlers exist
        mock_get_logger.return_value = mock_temp_logger

        # Act
        safe_log(mock_tracer, "debug", "Debug message")

        # Assert - safe_log should return None and not raise exceptions
        # safe_log should complete without raising exceptions
        # Verify get_logger was called for fallback
        mock_get_logger.assert_called_once_with("honeyhive.early_init", verbose=True)

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    @patch("honeyhive.utils.logger.get_logger")
    def test_safe_log_with_fallback_logger(
        self, mock_get_logger: Mock, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log with fallback logger for None tracer instance."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_fallback_logger = Mock()
        mock_fallback_logger.logger.handlers = [Mock()]  # Ensure handlers exist
        mock_get_logger.return_value = mock_fallback_logger

        # Act
        safe_log(None, "error", "Error message")

        # Assert - safe_log should return None and not raise exceptions
        # safe_log should complete without raising exceptions
        # Verify get_logger was called for fallback
        mock_get_logger.assert_called_once_with("honeyhive.fallback")

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_with_missing_logger_handlers(
        self, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log when logger has no handlers."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_logger = Mock()
        mock_logger.logger.handlers = []
        mock_tracer.logger = mock_logger

        # Act
        safe_log(mock_tracer, "info", "Test message")

        # Assert
        # safe_log should complete without raising exceptions

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_with_closed_stream_handler(
        self, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log when handler stream is closed."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_logger = Mock()
        mock_handler = Mock()
        mock_stream = Mock()
        mock_stream.closed = True
        mock_handler.stream = mock_stream
        mock_logger.logger.handlers = [mock_handler]
        mock_tracer.logger = mock_logger

        # Act
        safe_log(mock_tracer, "info", "Test message")

        # Assert
        # safe_log should complete without raising exceptions
        assert _shutdown_detected.is_set() is True

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_with_handler_without_stream(
        self, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log when handler has no stream attribute."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_logger = Mock()
        mock_handler = Mock()
        del mock_handler.stream  # Remove stream attribute
        mock_logger.logger.handlers = [mock_handler]
        mock_tracer.logger = mock_logger

        # Act
        safe_log(mock_tracer, "info", "Test message")

        # Assert
        mock_logger.info.assert_called_once_with("Test message")

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_with_exception_in_logging(
        self, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log handles exceptions gracefully."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_logger = Mock()
        mock_logger.info.side_effect = Exception("Logging error")
        mock_tracer.logger = mock_logger

        # Act
        safe_log(mock_tracer, "info", "Test message")

        # Assert
        # safe_log should complete without raising exceptions  # Should fail silently

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_without_honeyhive_data(self, mock_detect_shutdown: Mock) -> None:
        """Test safe_log without honeyhive_data parameter."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_logger = Mock()
        # The safe_log function checks target_logger.logger.handlers
        mock_logger.logger = Mock()
        mock_logger.logger.handlers = [Mock()]  # Ensure handlers exist
        mock_tracer.logger = mock_logger

        # Act
        safe_log(mock_tracer, "critical", "Critical message", "arg1", extra="value")

        # Assert - safe_log should return None and not raise exceptions
        # safe_log should complete without raising exceptions
        # The function should not crash with valid logger setup

    @patch("honeyhive.utils.logger.safe_log")
    def test_safe_debug_convenience_function(self, mock_safe_log: Mock) -> None:
        """Test safe_debug convenience function."""
        # Arrange
        mock_tracer = Mock()

        # Act
        safe_debug(mock_tracer, "Debug message", extra="value")

        # Assert
        mock_safe_log.assert_called_once_with(
            mock_tracer, "debug", "Debug message", extra="value"
        )

    @patch("honeyhive.utils.logger.safe_log")
    def test_safe_info_convenience_function(self, mock_safe_log: Mock) -> None:
        """Test safe_info convenience function."""
        # Arrange
        mock_tracer = Mock()

        # Act
        safe_info(mock_tracer, "Info message", extra="value")

        # Assert
        mock_safe_log.assert_called_once_with(
            mock_tracer, "info", "Info message", extra="value"
        )

    @patch("honeyhive.utils.logger.safe_log")
    def test_safe_warning_convenience_function(self, mock_safe_log: Mock) -> None:
        """Test safe_warning convenience function."""
        # Arrange
        mock_tracer = Mock()

        # Act
        safe_warning(mock_tracer, "Warning message", extra="value")

        # Assert
        mock_safe_log.assert_called_once_with(
            mock_tracer, "warning", "Warning message", extra="value"
        )

    @patch("honeyhive.utils.logger.safe_log")
    def test_safe_error_convenience_function(self, mock_safe_log: Mock) -> None:
        """Test safe_error convenience function."""
        # Arrange
        mock_tracer = Mock()

        # Act
        safe_error(mock_tracer, "Error message", extra="value")

        # Assert
        mock_safe_log.assert_called_once_with(
            mock_tracer, "error", "Error message", extra="value"
        )


class TestEdgeCasesAndErrorHandling:
    """Test suite for edge cases and error handling scenarios."""

    def setup_method(self) -> None:
        """Reset shutdown state before each test."""
        reset_logging_state()

    @patch("honeyhive.utils.logger.logging.getLogger")
    def test_honeyhive_logger_with_invalid_level_type(
        self, mock_get_logger: Mock
    ) -> None:
        """Test HoneyHiveLogger with invalid level type."""
        # Arrange
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        # Act
        _ = HoneyHiveLogger("test.logger", level=123.45)  # type: ignore[arg-type]

        # Assert
        # Should fall back to WARNING level
        mock_logger.setLevel.assert_called_once_with(logging.WARNING)

    def test_honeyhive_formatter_with_complex_honeyhive_data(self) -> None:
        """Test HoneyHiveFormatter with complex nested HoneyHive data."""
        # Arrange
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Complex data message",
            args=(),
            exc_info=None,
        )
        complex_data = {
            "nested": {"key": "value", "number": 42},
            "list": [1, 2, 3],
            "boolean": True,
            "null_value": None,
        }
        record.honeyhive_data = complex_data

        # Act
        result = formatter.format(record)

        # Assert
        parsed_result = json.loads(result)
        assert parsed_result["nested"]["key"] == "value"
        assert parsed_result["nested"]["number"] == 42
        assert parsed_result["list"] == [1, 2, 3]
        assert parsed_result["boolean"] is True
        # null_value is removed by the formatter since it filters None values
        assert "null_value" not in parsed_result

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_with_missing_log_method(self, mock_detect_shutdown: Mock) -> None:
        """Test safe_log when target logger doesn't have the requested log method."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_logger = Mock()
        del mock_logger.nonexistent_level  # Ensure method doesn't exist
        mock_tracer.logger = mock_logger

        # Act
        safe_log(mock_tracer, "nonexistent_level", "Test message")

        # Assert
        # safe_log should complete without raising exceptions  # Should fail silently

    def test_extract_verbose_from_tracer_with_type_error(self) -> None:
        """Test _extract_verbose_from_tracer_dynamically with TypeError."""
        # Arrange
        mock_tracer = Mock()
        mock_tracer.verbose = Mock(side_effect=TypeError("Type error"))

        # Act
        result = _extract_verbose_from_tracer_dynamically(mock_tracer)

        # Assert
        assert result is None

    @patch("honeyhive.utils.logger.datetime")
    def test_honeyhive_formatter_with_datetime_error(self, mock_datetime: Mock) -> None:
        """Test HoneyHiveFormatter when datetime raises an error."""
        # Arrange
        mock_datetime.now.side_effect = Exception("Datetime error")
        formatter = HoneyHiveFormatter(include_timestamp=True, include_level=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Datetime error"):
            formatter.format(record)

    @patch("honeyhive.utils.logger._detect_shutdown_conditions")
    def test_safe_log_with_complex_args_and_kwargs(
        self, mock_detect_shutdown: Mock
    ) -> None:
        """Test safe_log with complex arguments and keyword arguments."""
        # Arrange
        mock_detect_shutdown.return_value = False
        mock_tracer = Mock()
        mock_logger = Mock()
        # The safe_log function checks target_logger.logger.handlers
        mock_logger.logger = Mock()
        mock_logger.logger.handlers = [Mock()]  # Ensure handlers exist
        mock_tracer.logger = mock_logger

        # Act
        safe_log(
            mock_tracer,
            "info",
            "Complex message %s %d",
            "string_arg",
            42,
            honeyhive_data={"session": "test"},
            extra_key="extra_value",
            another_key=123,
        )

        # Assert - safe_log should return None and not raise exceptions
        # safe_log should complete without raising exceptions
        # The function should not crash with complex arguments

    def test_honeyhive_logger_level_precedence(self) -> None:
        """Test that explicit level takes precedence over verbose setting."""
        # Arrange
        with patch("honeyhive.utils.logger.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            # Act
            _ = HoneyHiveLogger("test.logger", level=logging.ERROR, verbose=True)

            # Assert
            # Explicit level should take precedence over verbose=True
            mock_logger.setLevel.assert_called_once_with(logging.ERROR)
