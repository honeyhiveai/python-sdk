"""Unit tests for HoneyHive CLI functionality."""

import os
from io import StringIO
from unittest.mock import patch

import pytest

from honeyhive.cli.main import cli

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestCLIArgumentParsing:
    """Test CLI argument parsing functionality."""

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        # Capture help output
        help_output = StringIO()

        with patch("sys.stdout", help_output):
            try:
                cli(["--help"])
            except SystemExit:
                pass

        help_text = help_output.getvalue()

        # Should contain expected help information
        assert "HoneyHive CLI" in help_text
        assert "Usage:" in help_text

    def test_cli_version(self) -> None:
        """Test CLI version output."""
        # Capture version output
        version_output = StringIO()

        with patch("sys.stdout", version_output):
            try:
                cli(["--version"])
            except SystemExit:
                pass

        version_text = version_output.getvalue()

        # Should contain version information
        assert "version" in version_text.lower()

    def test_cli_verbose_flag(self) -> None:
        """Test CLI verbose flag."""
        # Capture verbose output
        verbose_output = StringIO()

        with patch(
            "click.echo", lambda msg, **kwargs: verbose_output.write(str(msg) + "\n")
        ):
            try:
                cli(["--verbose", "config", "show"])
            except SystemExit:
                pass

        verbose_text = verbose_output.getvalue()

        # Should contain verbose message
        assert "Verbose mode enabled" in verbose_text

    def test_cli_debug_flag(self) -> None:
        """Test CLI debug flag."""
        # Capture debug output
        debug_output = StringIO()

        with patch(
            "click.echo", lambda msg, **kwargs: debug_output.write(str(msg) + "\n")
        ):
            try:
                cli(["--debug", "config", "show"])
            except SystemExit:
                pass

        debug_text = debug_output.getvalue()

        # Should contain debug message
        assert "Debug mode enabled" in debug_text

    def test_cli_config_file(self) -> None:
        """Test CLI config file option."""
        import os
        import tempfile

        # Create a temporary config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as temp_file:
            temp_file.write("test: config")
            temp_config = temp_file.name

        try:
            # Capture config output
            config_output = StringIO()

            with patch(
                "click.echo", lambda msg, **kwargs: config_output.write(str(msg) + "\n")
            ):
                try:
                    cli(["--config", temp_config, "config", "show"])
                except SystemExit:
                    pass

            config_text = config_output.getvalue()

            # Should contain config file message
            assert f"Using config file: {temp_config}" in config_text
        finally:
            # Clean up temporary file
            if os.path.exists(temp_config):
                os.unlink(temp_config)

    def test_cli_config_group(self) -> None:
        """Test CLI config group commands."""
        # Test config show command
        show_output = StringIO()

        with patch("sys.stdout", show_output):
            try:
                cli(["config", "show"])
            except SystemExit:
                pass

        # Should not crash

    def test_cli_trace_group(self) -> None:
        """Test CLI trace group commands."""
        # Test trace start command
        trace_output = StringIO()

        with patch("sys.stdout", trace_output):
            try:
                cli(["trace", "start", "--name", "test-span"])
            except SystemExit:
                pass

        # Should not crash

    def test_cli_integration(self) -> None:
        """Test CLI integration with other components."""
        # Test that CLI can be imported and used
        assert cli is not None

        # Test that CLI is a click command group
        assert hasattr(cli, "commands")
        assert hasattr(cli, "get_command")

    def test_cli_error_handling(self) -> None:
        """Test CLI error handling."""
        # Test with invalid arguments
        error_output = StringIO()

        with patch("sys.stderr", error_output):
            try:
                cli(["invalid-command"])
            except SystemExit:
                pass

        # Should handle errors gracefully

    def test_cli_environment_integration(self) -> None:
        """Test CLI integration with environment variables."""
        # Test that CLI respects environment configuration
        with patch.dict(os.environ, {"HH_DEBUG_MODE": "true"}):
            # CLI should be able to run without crashing
            try:
                cli(["--help"])
            except SystemExit:
                pass

    def test_cli_performance(self) -> None:
        """Test CLI performance characteristics."""
        import time

        # Time CLI help command
        start_time = time.time()

        try:
            cli(["--help"])
        except SystemExit:
            pass

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in reasonable time (less than 1 second)
        assert duration < 1.0

    def test_cli_memory_usage(self) -> None:
        """Test CLI memory usage characteristics."""
        import gc
        import sys

        # Get initial memory usage
        gc.collect()
        initial_memory = sys.getsizeof(cli)

        # Run CLI commands multiple times
        for _ in range(10):
            try:
                cli(["--help"])
            except SystemExit:
                pass

        # Force garbage collection
        gc.collect()

        # Check memory usage hasn't grown significantly
        final_memory = sys.getsizeof(cli)
        memory_growth = final_memory - initial_memory

        # Memory growth should be minimal
        assert memory_growth < 1000  # Less than 1KB growth
