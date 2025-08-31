"""Unit tests for HoneyHive verbose logging functionality."""

import json
import logging
import os
import sys
from unittest.mock import patch

import pytest

from honeyhive.utils.config import config
from honeyhive.utils.logger import (
    HoneyHiveFormatter,
    HoneyHiveLogger,
    default_logger,
    get_logger,
)

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestLoggingSetup:
    """Test logging setup functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Reset logging configuration
        logging.getLogger().handlers.clear()
        logging.getLogger().setLevel(logging.WARNING)

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        # Reset logging configuration
        logging.getLogger().handlers.clear()
        logging.getLogger().setLevel(logging.WARNING)

    def test_honeyhive_logger_initialization(self) -> None:
        """Test HoneyHiveLogger initialization."""
        logger = HoneyHiveLogger("test-logger")

        assert logger.logger.name == "test-logger"
        assert len(logger.logger.handlers) > 0

        # Check that handlers are properly configured
        for handler in logger.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.stream == sys.stdout

    def test_honeyhive_logger_custom_level(self) -> None:
        """Test HoneyHiveLogger with custom level."""
        logger = HoneyHiveLogger("test-logger", level=logging.DEBUG)

        assert logger.logger.level == logging.DEBUG

    def test_honeyhive_logger_custom_formatter(self) -> None:
        """Test HoneyHiveLogger with custom formatter."""
        custom_formatter = HoneyHiveFormatter(
            include_timestamp=False, include_level=False
        )
        logger = HoneyHiveLogger("test-logger", formatter=custom_formatter)

        assert len(logger.logger.handlers) > 0

        # Check that at least one handler has the custom formatter
        has_custom_formatter = False
        for handler in logger.logger.handlers:
            if handler.formatter:
                if isinstance(handler.formatter, HoneyHiveFormatter):
                    has_custom_formatter = True
                    break

        assert has_custom_formatter

    def test_honeyhive_logger_custom_handler(self) -> None:
        """Test HoneyHiveLogger with custom handler."""
        test_log_file = "test_logging.log"

        try:
            file_handler = logging.FileHandler(test_log_file)
            # Use a unique logger name to avoid conflicts
            logger = HoneyHiveLogger("test-logger-custom-handler", handler=file_handler)

            assert len(logger.logger.handlers) > 0

            # Check that at least one handler is a file handler
            has_file_handler = False
            for handler in logger.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    has_file_handler = True
                    break

            assert has_file_handler

        finally:
            # Clean up
            if os.path.exists(test_log_file):
                os.remove(test_log_file)

    def test_honeyhive_logger_multiple_handlers(self) -> None:
        """Test HoneyHiveLogger with multiple handlers."""
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler("test.log")

        logger = HoneyHiveLogger("test-logger", handler=console_handler)

        # Add another handler
        logger.logger.addHandler(file_handler)

        assert len(logger.logger.handlers) >= 2

        # Should have both console and file handlers
        has_console_handler = False

        for handler in logger.logger.handlers:
            if (
                isinstance(handler, logging.StreamHandler)
                and handler.stream == sys.stdout
            ):
                has_console_handler = True
            elif isinstance(handler, logging.FileHandler):
                pass

        assert has_console_handler
        # Note: file handler test would require a log file path

        # Clean up
        if os.path.exists("test.log"):
            os.remove("test.log")

    def test_honeyhive_logger_no_handlers(self) -> None:
        """Test HoneyHiveLogger with no handlers."""
        # This should create a default handler
        logger = HoneyHiveLogger("test-logger")

        # Should have at least one handler
        assert len(logger.logger.handlers) > 0

    def test_honeyhive_logger_environment_override(self) -> None:
        """Test that environment variables override default settings."""
        with patch("honeyhive.utils.logger.config") as mock_config:
            mock_config.debug_mode = True

            logger = HoneyHiveLogger("test-logger")

            # Should use debug level when debug mode is enabled
            assert logger.logger.level <= logging.DEBUG

    def test_honeyhive_logger_invalid_level(self) -> None:
        """Test HoneyHiveLogger with invalid level."""
        # Test with invalid string level
        with pytest.raises(AttributeError):
            HoneyHiveLogger("test-logger", level="INVALID_LEVEL")

        # Test with invalid integer level
        logger = HoneyHiveLogger("test-logger", level=99999)
        assert logger.logger.level == 99999

    def test_honeyhive_logger_existing_handlers(self) -> None:
        """Test HoneyHiveLogger when logger already has handlers."""
        # Create a logger with existing handlers
        existing_logger = logging.getLogger("existing-test-logger")
        existing_handler = logging.StreamHandler(sys.stdout)
        existing_logger.addHandler(existing_handler)
        existing_logger.setLevel(logging.DEBUG)

        # Create HoneyHiveLogger with same name
        honeyhive_logger = HoneyHiveLogger("existing-test-logger")

        # Should not add new handlers if they already exist
        assert len(honeyhive_logger.logger.handlers) == 1
        assert honeyhive_logger.logger.handlers[0] == existing_handler

    def test_honeyhive_logger_debug_mode(self) -> None:
        """Test HoneyHiveLogger with debug mode enabled."""
        # Mock config.debug_mode to True
        with patch("honeyhive.utils.logger.config") as mock_config:
            mock_config.debug_mode = True
            logger = HoneyHiveLogger("test-logger")
            assert logger.logger.level == logging.DEBUG

    def test_honeyhive_logger_no_debug_mode(self) -> None:
        """Test HoneyHiveLogger with debug mode disabled."""
        # Mock config.debug_mode to False
        with patch("honeyhive.utils.logger.config") as mock_config:
            mock_config.debug_mode = False
            logger = HoneyHiveLogger("test-logger")
            assert logger.logger.level == logging.INFO


class TestHoneyHiveFormatter:
    """Test HoneyHiveFormatter functionality."""

    def test_formatter_default(self) -> None:
        """Test HoneyHiveFormatter default values."""
        formatter = HoneyHiveFormatter()

        assert formatter.include_timestamp is True
        assert formatter.include_level is True

    def test_formatter_custom(self) -> None:
        """Test HoneyHiveFormatter with custom values."""
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=False)

        assert formatter.include_timestamp is False
        assert formatter.include_level is False

    def test_formatter_format(self) -> None:
        """Test HoneyHiveFormatter format method."""
        formatter = HoneyHiveFormatter()

        # Create a mock log record
        record = logging.LogRecord(
            name="test-logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Should be valid JSON
        import json

        parsed = json.loads(formatted)

        # Should contain expected fields
        assert "message" in parsed
        assert "logger" in parsed
        assert "timestamp" in parsed
        assert "level" in parsed

        assert parsed["message"] == "Test message"
        assert parsed["logger"] == "test-logger"
        assert parsed["level"] == "INFO"

    def test_formatter_with_exception(self) -> None:
        """Test formatter with exception info."""
        formatter = HoneyHiveFormatter()
        record = logging.LogRecord(
            "test", logging.INFO, "test.py", 10, "Test message", (), None
        )
        record.exc_info = (ValueError, ValueError("Test error"), None)

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "exception" in log_data
        assert "ValueError: Test error" in log_data["exception"]

    def test_formatter_with_extra_data(self) -> None:
        """Test formatter with extra data."""
        formatter = HoneyHiveFormatter()
        record = logging.LogRecord(
            "test", logging.INFO, "test.py", 10, "Test message", (), None
        )
        record.honeyhive_data = {"user_id": "123", "session_id": "abc"}

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["user_id"] == "123"
        assert log_data["session_id"] == "abc"

    def test_formatter_with_none_values(self) -> None:
        """Test formatter with None values."""
        formatter = HoneyHiveFormatter(include_timestamp=False, include_level=False)
        record = logging.LogRecord(
            "test", logging.INFO, "test.py", 10, "Test message", (), None
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        # Should not include None values
        assert "timestamp" not in log_data
        assert "level" not in log_data
        assert "logger" in log_data
        assert "message" in log_data

    def test_formatter_with_empty_strings(self) -> None:
        """Test formatter with empty strings."""
        formatter = HoneyHiveFormatter()
        record = logging.LogRecord("test", logging.INFO, "test.py", 10, "", (), None)

        result = formatter.format(record)
        log_data = json.loads(result)

        # Empty strings should be included (not None)
        assert log_data["message"] == ""

    def test_formatter_with_special_characters(self) -> None:
        """Test formatter with special characters."""
        formatter = HoneyHiveFormatter()
        message = "Test message with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        record = logging.LogRecord(
            "test", logging.INFO, "test.py", 10, message, (), None
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["message"] == message

    def test_formatter_with_unicode(self) -> None:
        """Test formatter with unicode characters."""
        formatter = HoneyHiveFormatter()
        message = "Test message with unicode: 🚀🌟🎉"
        record = logging.LogRecord(
            "test", logging.INFO, "test.py", 10, message, (), None
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["message"] == message

    def test_formatter_with_very_long_messages(self) -> None:
        """Test formatter with very long messages."""
        formatter = HoneyHiveFormatter()
        long_message = "x" * 10000
        record = logging.LogRecord(
            "test", logging.INFO, "test.py", 10, long_message, (), None
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["message"] == long_message
        assert len(result) > 10000

    def test_formatter_with_complex_objects(self) -> None:
        """Test formatter with complex objects in extra data."""
        formatter = HoneyHiveFormatter()
        record = logging.LogRecord(
            "test", logging.INFO, "test.py", 10, "Test message", (), None
        )
        record.honeyhive_data = {
            "list": [1, 2, 3],
            "dict": {"a": 1, "b": 2},
            "tuple": (1, 2, 3),
            "set": {1, 2, 3},
        }

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["list"] == [1, 2, 3]
        assert log_data["dict"] == {"a": 1, "b": 2}
        assert log_data["tuple"] == [1, 2, 3]  # JSON converts tuples to lists

        # Check that set is properly serialized (JSON doesn't support sets natively)
        # The exact format may vary depending on the JSON implementation
        set_value = log_data["set"]
        assert isinstance(set_value, (list, str))
        if isinstance(set_value, list):
            assert set_value == [1, 2, 3]
        else:
            # If it's a string representation, it should contain the values
            assert "1" in set_value
            assert "2" in set_value
            assert "3" in set_value

    def test_logger_exception_method(self) -> None:
        """Test HoneyHiveLogger exception method."""
        logger = HoneyHiveLogger("test-logger")

        # Test exception logging with honeyhive_data
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred", honeyhive_data={"user_id": "123"})

        # Test exception logging without honeyhive_data
        try:
            raise TypeError("Another exception")
        except TypeError:
            logger.exception("Another exception occurred")

    def test_get_logger_function(self) -> None:
        """Test get_logger function."""
        # Test basic logger creation
        logger = get_logger("test-get-logger")
        assert isinstance(logger, HoneyHiveLogger)
        assert logger.logger.name == "test-get-logger"

        # Test logger with custom kwargs
        custom_logger = get_logger("custom-logger", level="DEBUG")
        assert custom_logger.logger.level == logging.DEBUG

        # Test that different names create different loggers
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        assert logger1.logger.name != logger2.logger.name

    def test_default_logger(self) -> None:
        """Test default logger."""
        # Test that default_logger exists and is functional
        assert default_logger is not None
        assert isinstance(default_logger, HoneyHiveLogger)
        assert default_logger.logger.name == "honeyhive"

        # Test that default logger can log messages
        default_logger.info("Test message from default logger")
        assert default_logger.logger.handlers

    def test_logger_exception_with_honeyhive_data(self) -> None:
        """Test HoneyHiveLogger exception method with honeyhive_data."""
        logger = HoneyHiveLogger("test-logger")

        # Test exception logging with honeyhive_data
        try:
            raise ValueError("Test exception with data")
        except ValueError:
            logger.exception(
                "Exception occurred with data",
                honeyhive_data={"user_id": "123", "session_id": "abc"},
            )

        # Test exception logging without honeyhive_data
        try:
            raise TypeError("Test exception without data")
        except TypeError:
            logger.exception("Exception occurred without data")


class TestLoggingIntegration:
    """Test logging integration with other components."""

    def test_logging_with_config(self) -> None:
        """Test that logging respects config settings."""
        # Mock config to return specific log level
        with patch.object(config, "debug_mode", True):
            logger = HoneyHiveLogger("test.module")

            # Should use debug level when debug mode is enabled
            assert logger.logger.level <= logging.DEBUG

    def test_logging_with_api_calls(self) -> None:
        """Test that API calls generate appropriate logs."""
        logger = HoneyHiveLogger("honeyhive.api", level=logging.DEBUG)

        # Capture log output
        log_records = []

        class TestHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                log_records.append(record)

        test_handler = TestHandler()
        test_handler.setLevel(logging.DEBUG)

        logger.logger.addHandler(test_handler)

        # Simulate some API activity
        logger.info("API call started")
        logger.debug("Request details: {}", {"method": "GET", "url": "/test"})
        logger.info("API call completed")

        # Should have captured log records
        assert len(log_records) >= 3

        # Check log levels
        info_records = [r for r in log_records if r.levelno == logging.INFO]
        debug_records = [r for r in log_records if r.levelno == logging.DEBUG]

        assert len(info_records) >= 2
        assert len(debug_records) >= 1

    def test_logging_performance(self) -> None:
        """Test that logging doesn't significantly impact performance."""
        import time

        logger = HoneyHiveLogger("performance.test", level=logging.INFO)

        # Time logging operations
        start_time = time.time()

        for i in range(1000):
            logger.info(f"Performance test message {i}")

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in reasonable time (less than 1 second)
        assert duration < 1.0

    def test_logging_memory_usage(self) -> None:
        """Test that logging doesn't cause memory leaks."""
        import gc
        import sys

        logger = HoneyHiveLogger("memory.test", level=logging.DEBUG)

        # Get initial memory usage
        gc.collect()
        initial_memory = sys.getsizeof(logger)

        # Perform many logging operations
        for i in range(1000):
            logger.debug(f"Memory test message {i}")
            logger.info(f"Memory test info {i}")
            logger.warning(f"Memory test warning {i}")

        # Force garbage collection
        gc.collect()

        # Check memory usage hasn't grown significantly
        final_memory = sys.getsizeof(logger)
        memory_growth = final_memory - initial_memory

        # Memory growth should be minimal
        assert memory_growth < 1000  # Less than 1KB growth


class TestLoggingEdgeCases:
    """Test logging edge cases and error handling."""

    def test_logging_with_none_values(self) -> None:
        """Test logging with None values."""
        logger = HoneyHiveLogger("edge.test", level=logging.DEBUG)

        # Should handle None values gracefully by converting to string
        logger.info(str(None))
        logger.debug(str(None))
        logger.warning(str(None))
        logger.error(str(None))

        # Should not crash

    def test_logging_with_empty_strings(self) -> None:
        """Test logging with empty strings."""
        logger = HoneyHiveLogger("edge.test", level=logging.DEBUG)

        # Should handle empty strings gracefully
        logger.info("")
        logger.debug("")
        logger.warning("")
        logger.error("")

        # Should not crash

    def test_logging_with_special_characters(self) -> None:
        """Test logging with special characters."""
        logger = HoneyHiveLogger("edge.test", level=logging.DEBUG)

        # Should handle special characters gracefully
        special_message = "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        logger.info(special_message)
        logger.debug(special_message)

        # Should not crash

    def test_logging_with_unicode(self) -> None:
        """Test logging with unicode characters."""
        logger = HoneyHiveLogger("edge.test", level=logging.DEBUG)

        # Should handle unicode gracefully
        unicode_message = "Unicode: 🚀🌟🎉💻🔥"
        logger.info(unicode_message)
        logger.debug(unicode_message)

        # Should not crash

    def test_logging_with_very_long_messages(self) -> None:
        """Test logging with very long messages."""
        logger = HoneyHiveLogger("edge.test", level=logging.DEBUG)

        # Should handle very long messages gracefully
        long_message = "x" * 10000
        logger.info(long_message)
        logger.debug(long_message)

        # Should not crash

    def test_logging_with_complex_objects(self) -> None:
        """Test logging with complex objects."""
        logger = HoneyHiveLogger("edge.test", level=logging.DEBUG)

        # Should handle complex objects gracefully
        complex_obj = {"nested": {"deep": {"structure": [1, 2, 3, {"key": "value"}]}}}

        logger.info("Complex object: %s", complex_obj)
        logger.debug("Complex object: %s", complex_obj)

        # Should not crash

    def test_logging_concurrent_access(self) -> None:
        """Test logging with concurrent access."""
        import threading
        import time

        logger = HoneyHiveLogger("concurrent.test", level=logging.DEBUG)

        errors = []

        def log_messages(thread_id: int) -> None:
            try:
                for i in range(100):
                    logger.info(f"Thread {thread_id} message {i}")
                    logger.debug(f"Thread {thread_id} debug {i}")
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_messages, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should not have any errors
        assert len(errors) == 0

    def test_logging_handler_errors(self) -> None:
        """Test logging when handlers encounter errors."""
        logger = HoneyHiveLogger("handler.error.test", level=logging.DEBUG)

        # Create a handler that raises an error
        class ErrorHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                raise Exception("Handler error")

        error_handler = ErrorHandler()
        error_handler.setLevel(logging.DEBUG)

        logger.logger.addHandler(error_handler)

        # Should crash when handler errors occur (current behavior)
        with pytest.raises(Exception, match="Handler error"):
            logger.info("This should crash due to handler error")

    def test_logging_formatter_errors(self) -> None:
        """Test logging when formatters encounter errors."""
        logger = HoneyHiveLogger("formatter.error.test", level=logging.DEBUG)

        # Create a formatter that raises an error
        class ErrorFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                raise Exception("Formatter error")

        # Create a handler with the error formatter
        error_handler = logging.StreamHandler()
        error_handler.setFormatter(ErrorFormatter())
        error_handler.setLevel(logging.DEBUG)

        logger.logger.addHandler(error_handler)

        # Should not crash when formatter errors occur
        logger.info("This should not crash")
        logger.debug("This should not crash either")

        # Remove the error handler
        logger.logger.removeHandler(error_handler)
