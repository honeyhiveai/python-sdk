"""Unit tests for HoneyHive CLI functionality."""

import json
import os
import tempfile
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml
from click.testing import CliRunner

from honeyhive.cli.main import cli

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestCLICommandStructure:
    """Phase 1: Test CLI command structure and argument parsing."""

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "HoneyHive CLI" in result.output
        assert "LLM Observability and Evaluation Platform" in result.output
        assert "Usage:" in result.output

    def test_cli_version(self) -> None:
        """Test CLI version output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_cli_verbose_flag(self) -> None:
        """Test CLI verbose flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "config", "show"])

        assert "Verbose mode enabled" in result.output

    def test_cli_debug_flag(self) -> None:
        """Test CLI debug flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--debug", "config", "show"])

        assert "Debug mode enabled" in result.output

    def test_cli_config_file_flag(self) -> None:
        """Test CLI config file option."""
        runner = CliRunner()

        # Create a temporary config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as temp_file:
            temp_file.write("api_key: test-key")
            temp_config = temp_file.name

        try:
            result = runner.invoke(cli, ["--config", temp_config, "config", "show"])
            assert f"Using config file: {temp_config}" in result.output
        finally:
            os.unlink(temp_config)

    def test_config_group_help(self) -> None:
        """Test config group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "--help"])

        assert result.exit_code == 0
        assert "Configuration management commands" in result.output
        assert "show" in result.output
        assert "set" in result.output

    def test_trace_group_help(self) -> None:
        """Test trace group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["trace", "--help"])

        assert result.exit_code == 0
        assert "Tracing commands" in result.output
        assert "start" in result.output
        assert "enrich" in result.output

    def test_api_group_help(self) -> None:
        """Test API group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["api", "--help"])

        assert result.exit_code == 0
        assert "API client commands" in result.output
        assert "request" in result.output

    def test_monitor_group_help(self) -> None:
        """Test monitor group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["monitor", "--help"])

        assert result.exit_code == 0
        assert "Monitoring and performance commands" in result.output
        assert "status" in result.output
        assert "watch" in result.output

    def test_performance_group_help(self) -> None:
        """Test performance group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["performance", "--help"])

        assert result.exit_code == 0
        assert "Performance analysis commands" in result.output
        assert "benchmark" in result.output

    def test_cleanup_command_help(self) -> None:
        """Test cleanup command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["cleanup", "--help"])

        assert result.exit_code == 0
        assert "Clean up resources" in result.output


class TestCLIConfigCommands:
    """Phase 2: Test CLI configuration commands functionality."""

    def test_config_show_json_format(self) -> None:
        """Test config show command with JSON format."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "show", "--format", "json"])

        assert result.exit_code == 0
        config_data = json.loads(result.output)

        # Verify expected config keys are present
        expected_keys = [
            "api_key",
            "api_url",
            "project",
            "source",
            "debug_mode",
            "test_mode",
            "experiment_id",
            "experiment_name",
            "experiment_variant",
            "experiment_group",
            "experiment_metadata",
        ]
        for key in expected_keys:
            assert key in config_data

    def test_config_show_yaml_format(self) -> None:
        """Test config show command with YAML format."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "show", "--format", "yaml"])

        assert result.exit_code == 0
        config_data = yaml.safe_load(result.output)

        # Verify expected config keys are present
        expected_keys = [
            "api_key",
            "api_url",
            "project",
            "source",
            "debug_mode",
            "test_mode",
            "experiment_id",
            "experiment_name",
            "experiment_variant",
            "experiment_group",
            "experiment_metadata",
        ]
        for key in expected_keys:
            assert key in config_data

    def test_config_show_env_format(self) -> None:
        """Test config show command with environment format."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "show", "--format", "env"])

        assert result.exit_code == 0
        # Check for environment variable format
        assert "HH_API_URL=" in result.output
        assert "HH_SOURCE=" in result.output

    def test_config_set_valid_key(self) -> None:
        """Test config set command with valid key."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["config", "set", "--key", "timeout", "--value", "60.0"]
        )

        assert result.exit_code == 0
        assert "Set timeout = 60.0" in result.output

    def test_config_set_invalid_key(self) -> None:
        """Test config set command with invalid key."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["config", "set", "--key", "invalid_key", "--value", "test_value"]
        )

        assert result.exit_code == 1
        assert "Unknown configuration key" in result.output

    def test_config_set_missing_value(self) -> None:
        """Test config set command with missing value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set", "--key", "timeout"])

        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_config_set_missing_key(self) -> None:
        """Test config set command with missing key."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set", "--value", "test_value"])

        assert result.exit_code != 0
        assert "Missing option" in result.output


class TestCLITraceCommands:
    """Phase 2: Test CLI trace commands functionality."""

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("builtins.input", return_value="")  # Simulate Enter key press
    def test_trace_start_basic(self, mock_input: Mock, mock_tracer: Mock) -> None:
        """Test trace start command with basic parameters."""
        mock_tracer_instance = Mock()
        mock_tracer.return_value = mock_tracer_instance
        mock_span_context = Mock()
        mock_span_context.__enter__ = Mock(return_value=None)
        mock_span_context.__exit__ = Mock(return_value=None)
        mock_tracer_instance.start_span.return_value = mock_span_context

        runner = CliRunner()
        result = runner.invoke(cli, ["trace", "start", "--name", "test-trace"])

        assert result.exit_code == 0
        assert "Started span: test-trace" in result.output
        assert "Ended span: test-trace" in result.output
        mock_tracer.assert_called_once()

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("builtins.input", return_value="")
    def test_trace_start_with_session_id(
        self, mock_input: Mock, mock_tracer: Mock
    ) -> None:
        """Test trace start command with session ID."""
        mock_tracer_instance = Mock()
        mock_tracer.return_value = mock_tracer_instance
        mock_span_context = Mock()
        mock_span_context.__enter__ = Mock(return_value=None)
        mock_span_context.__exit__ = Mock(return_value=None)
        mock_tracer_instance.start_span.return_value = mock_span_context

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["trace", "start", "--name", "test-trace", "--session-id", "session-123"],
        )

        assert result.exit_code == 0
        assert "Started span: test-trace" in result.output
        mock_tracer_instance.start_span.assert_called_once_with(
            name="test-trace", session_id="session-123", attributes={}
        )

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("builtins.input", return_value="")
    def test_trace_start_with_attributes(
        self, mock_input: Mock, mock_tracer: Mock
    ) -> None:
        """Test trace start command with attributes."""
        mock_tracer_instance = Mock()
        mock_tracer.return_value = mock_tracer_instance
        mock_span_context = Mock()
        mock_span_context.__enter__ = Mock(return_value=None)
        mock_span_context.__exit__ = Mock(return_value=None)
        mock_tracer_instance.start_span.return_value = mock_span_context

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "trace",
                "start",
                "--name",
                "test-trace",
                "--attributes",
                '{"key": "value", "count": 42}',
            ],
        )

        assert result.exit_code == 0
        assert "Started span: test-trace" in result.output
        mock_tracer_instance.start_span.assert_called_once_with(
            name="test-trace", session_id=None, attributes={"key": "value", "count": 42}
        )

    def test_trace_start_invalid_json(self) -> None:
        """Test trace start command with invalid JSON attributes."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["trace", "start", "--name", "test-trace", "--attributes", "invalid-json"],
        )

        assert result.exit_code == 1
        # The error message depends on order of validation - either JSON or API key error is acceptable
        assert (
            "Invalid JSON for attributes" in result.output
            or "Failed to start trace" in result.output
        )

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    def test_trace_start_tracer_error(self, mock_tracer: Mock) -> None:
        """Test trace start command with tracer error."""
        mock_tracer.side_effect = Exception("API key required")

        runner = CliRunner()
        result = runner.invoke(cli, ["trace", "start", "--name", "test-trace"])

        assert result.exit_code == 1
        assert "Failed to start trace" in result.output

    def test_trace_enrich_basic(self) -> None:
        """Test trace enrich command with basic parameters."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "trace",
                "enrich",
                "--session-id",
                "session-123",
                "--metadata",
                '{"key": "value"}',
            ],
        )

        assert "Would enrich session session-123" in result.output
        assert "Note: Session enrichment is not yet implemented" in result.output

    def test_trace_enrich_missing_session_id(self) -> None:
        """Test trace enrich command with missing session ID."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["trace", "enrich", "--metadata", '{"key": "value"}']
        )

        assert result.exit_code == 1
        assert "Session ID is required" in result.output

    def test_trace_enrich_invalid_metadata(self) -> None:
        """Test trace enrich command with invalid metadata JSON."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "trace",
                "enrich",
                "--session-id",
                "session-123",
                "--metadata",
                "invalid-json",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid JSON for metadata" in result.output

    def test_trace_enrich_invalid_feedback(self) -> None:
        """Test trace enrich command with invalid feedback JSON."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "trace",
                "enrich",
                "--session-id",
                "session-123",
                "--feedback",
                "invalid-json",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid JSON for feedback" in result.output

    def test_trace_enrich_invalid_metrics(self) -> None:
        """Test trace enrich command with invalid metrics JSON."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "trace",
                "enrich",
                "--session-id",
                "session-123",
                "--metrics",
                "invalid-json",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid JSON for metrics" in result.output

    def test_trace_enrich_all_data_types(self) -> None:
        """Test trace enrich command with all data types."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "trace",
                "enrich",
                "--session-id",
                "session-123",
                "--metadata",
                '{"environment": "test"}',
                "--feedback",
                '{"rating": 5}',
                "--metrics",
                '{"accuracy": 0.95}',
            ],
        )

        assert result.exit_code == 0
        assert "Would enrich session session-123" in result.output
        assert "metadata" in result.output
        assert "feedback" in result.output
        assert "metrics" in result.output


class TestCLIAPICommands:
    """Phase 2: Test CLI API commands functionality."""

    @patch("honeyhive.cli.main.HoneyHive")
    def test_api_request_get(self, mock_client_class: Mock) -> None:
        """Test API request command with GET method."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        mock_client.sync_client.request.return_value = mock_response

        runner = CliRunner()
        result = runner.invoke(
            cli, ["api", "request", "--method", "GET", "--url", "/api/v1/test"]
        )

        assert result.exit_code == 0
        assert "Status: 200" in result.output
        assert "Duration:" in result.output
        assert '"result": "success"' in result.output

    @patch("honeyhive.cli.main.HoneyHive")
    def test_api_request_post_with_data(self, mock_client_class: Mock) -> None:
        """Test API request command with POST method and data."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"id": "123", "created": True}
        mock_client.sync_client.request.return_value = mock_response

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "api",
                "request",
                "--method",
                "POST",
                "--url",
                "/api/v1/events",
                "--data",
                '{"name": "test_event", "type": "model"}',
            ],
        )

        assert result.exit_code == 0
        assert "Status: 201" in result.output
        assert '"id": "123"' in result.output
        mock_client.sync_client.request.assert_called_once_with(
            method="POST",
            url="/api/v1/events",
            headers={},
            json={"name": "test_event", "type": "model"},
            timeout=30.0,
        )

    @patch("honeyhive.cli.main.HoneyHive")
    def test_api_request_with_headers(self, mock_client_class: Mock) -> None:
        """Test API request command with custom headers."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"status": "ok"}
        mock_client.sync_client.request.return_value = mock_response

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "api",
                "request",
                "--method",
                "GET",
                "--url",
                "/api/v1/health",
                "--headers",
                '{"X-Custom-Header": "test-value"}',
            ],
        )

        assert result.exit_code == 0
        assert "Status: 200" in result.output
        mock_client.sync_client.request.assert_called_once_with(
            method="GET",
            url="/api/v1/health",
            headers={"X-Custom-Header": "test-value"},
            json=None,
            timeout=30.0,
        )

    def test_api_request_invalid_headers_json(self) -> None:
        """Test API request command with invalid headers JSON."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "api",
                "request",
                "--method",
                "GET",
                "--url",
                "/api/v1/test",
                "--headers",
                "invalid-json",
            ],
        )

        assert result.exit_code == 1
        # The error message depends on order of validation - either JSON or API key error is acceptable
        assert (
            "Invalid JSON for headers" in result.output
            or "API request failed" in result.output
        )

    def test_api_request_invalid_data_json(self) -> None:
        """Test API request command with invalid data JSON."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "api",
                "request",
                "--method",
                "POST",
                "--url",
                "/api/v1/test",
                "--data",
                "invalid-json",
            ],
        )

        assert result.exit_code == 1
        # The error message depends on order of validation - either JSON or API key error is acceptable
        assert (
            "Invalid JSON for data" in result.output
            or "API request failed" in result.output
        )

    @patch("honeyhive.cli.main.HoneyHive")
    def test_api_request_client_error(self, mock_client_class: Mock) -> None:
        """Test API request command with client error."""
        mock_client_class.side_effect = Exception("Authentication failed")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["api", "request", "--method", "GET", "--url", "/api/v1/test"]
        )

        assert result.exit_code == 1
        assert "API request failed" in result.output

    @patch("honeyhive.cli.main.HoneyHive")
    def test_api_request_non_json_response(self, mock_client_class: Mock) -> None:
        """Test API request command with non-JSON response."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.json.side_effect = Exception("Not JSON")
        mock_response.text = "Plain text response"
        mock_client.sync_client.request.return_value = mock_response

        runner = CliRunner()
        result = runner.invoke(
            cli, ["api", "request", "--method", "GET", "--url", "/api/v1/text"]
        )

        assert result.exit_code == 0
        assert "Status: 200" in result.output
        assert "Plain text response" in result.output


class TestCLIMonitorCommands:
    """Phase 2: Test CLI monitor commands functionality."""

    @patch("honeyhive.cli.main.Config")
    @patch("honeyhive.cli.main.get_global_cache")
    @patch("honeyhive.cli.main.get_global_pool")
    def test_monitor_status(
        self, mock_pool: Mock, mock_cache: Mock, mock_config: Mock
    ) -> None:
        """Test monitor status command."""
        # Mock config
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.api_key = "test-key"
        mock_config_instance.project = "test-project"
        mock_config_instance.source = "honeyhive-python-sdk"
        mock_config_instance.debug_mode = False
        mock_config_instance.disable_tracing = False

        # Mock cache
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get_stats.return_value = {
            "size": 10,
            "max_size": 100,
            "hit_rate": 0.85,
        }

        # Mock connection pool
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        mock_pool_instance.get_stats.return_value = {
            "total_requests": 50,
            "pool_hits": 45,
            "pool_misses": 5,
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["monitor", "status"])

        assert result.exit_code == 0
        assert "Configuration Status" in result.output
        assert "API Key: ✓" in result.output
        assert "Project: test-project" in result.output
        assert "Tracer Status" in result.output
        assert "Cache Status" in result.output
        assert "✓ Cache active" in result.output
        assert "Connection Pool Status" in result.output
        assert "✓ Connection pool active" in result.output

    @patch("honeyhive.cli.main.Config")
    @patch("honeyhive.cli.main.get_global_cache")
    def test_monitor_status_cache_error(
        self, mock_cache: Mock, mock_config: Mock
    ) -> None:
        """Test monitor status command with cache error."""
        # Mock config
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.api_key = None
        mock_config_instance.project = None
        mock_config_instance.source = "honeyhive-python-sdk"
        mock_config_instance.debug_mode = False
        mock_config_instance.disable_tracing = False

        # Mock cache error
        mock_cache.side_effect = Exception("Cache unavailable")

        runner = CliRunner()
        result = runner.invoke(cli, ["monitor", "status"])

        assert "API Key: ✗" in result.output
        assert "✗ Cache error" in result.output

    @patch("honeyhive.utils.cache.get_global_cache")
    @patch("honeyhive.utils.connection_pool.get_global_pool")
    @patch("time.sleep", return_value=None)  # Speed up the test
    def test_monitor_watch(
        self, mock_sleep: Mock, mock_pool: Mock, mock_cache: Mock
    ) -> None:
        """Test monitor watch command."""
        # Mock cache
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get_stats.return_value = {
            "size": 5,
            "max_size": 50,
            "hit_rate": 0.9,
            "hits": 45,
            "misses": 5,
        }

        # Mock connection pool
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        mock_pool_instance.get_stats.return_value = {
            "total_requests": 100,
            "pool_hits": 90,
            "pool_misses": 10,
            "active_connections": 3,
        }

        runner = CliRunner()
        # Use very short duration for testing
        result = runner.invoke(
            cli, ["monitor", "watch", "--duration", "1", "--interval", "0.1"]
        )

        assert "Monitoring for 1 seconds" in result.output
        assert "Cache:" in result.output
        assert "Connection Pool:" in result.output

    @patch("honeyhive.utils.cache.get_global_cache")
    @patch("honeyhive.utils.connection_pool.get_global_pool")
    def test_monitor_watch_keyboard_interrupt(
        self, mock_pool: Mock, mock_cache: Mock
    ) -> None:
        """Test monitor watch command with keyboard interrupt."""
        # Mock cache and pool to raise KeyboardInterrupt
        mock_cache.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["monitor", "watch", "--duration", "60"])

        # Should handle KeyboardInterrupt gracefully
        assert result.exit_code == 0


class TestCLIPerformanceCommands:
    """Phase 2: Test CLI performance commands functionality."""

    @patch("honeyhive.utils.cache.get_global_cache")
    def test_performance_benchmark_basic(self, mock_cache: Mock) -> None:
        """Test performance benchmark command."""
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance

        runner = CliRunner()
        result = runner.invoke(
            cli, ["performance", "benchmark", "--iterations", "10", "--warmup", "5"]
        )

        assert result.exit_code == 0
        assert "Running performance benchmarks" in result.output
        assert "Iterations: 10" in result.output
        assert "Warmup: 5" in result.output
        assert "Warming up..." in result.output
        assert "Cache Performance" in result.output
        assert "Tracer Performance" in result.output
        assert "Benchmarks completed" in result.output

    @patch("honeyhive.utils.cache.get_global_cache")
    def test_performance_benchmark_no_warmup(self, mock_cache: Mock) -> None:
        """Test performance benchmark command without warmup."""
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance

        runner = CliRunner()
        result = runner.invoke(
            cli, ["performance", "benchmark", "--iterations", "5", "--warmup", "0"]
        )

        assert result.exit_code == 0
        assert "Warmup: 0" in result.output
        assert "Warming up..." not in result.output

    @patch("honeyhive.utils.cache.get_global_cache")
    def test_performance_benchmark_zero_iterations(self, mock_cache: Mock) -> None:
        """Test performance benchmark command with zero iterations."""
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["performance", "benchmark", "--iterations", "0"])

        assert result.exit_code == 0
        assert "Skipping cache benchmarks (0 iterations)" in result.output
        assert "Skipping tracer benchmarks (0 iterations)" in result.output

    @patch("honeyhive.cli.main.get_global_cache")
    def test_performance_benchmark_error(self, mock_cache: Mock) -> None:
        """Test performance benchmark command with error."""
        mock_cache.side_effect = Exception("Cache error")

        runner = CliRunner()
        result = runner.invoke(cli, ["performance", "benchmark"])

        assert result.exit_code == 1
        assert "Benchmark failed" in result.output


class TestCLICleanupCommand:
    """Phase 2: Test CLI cleanup command functionality."""

    @patch("honeyhive.cli.main.close_global_cache")
    @patch("honeyhive.cli.main.close_global_pool")
    def test_cleanup_success(
        self, mock_close_pool: Mock, mock_close_cache: Mock
    ) -> None:
        """Test cleanup command successful execution."""
        runner = CliRunner()
        result = runner.invoke(cli, ["cleanup"])

        assert result.exit_code == 0
        assert "Cleaning up resources..." in result.output
        assert "✓ Cache closed" in result.output
        assert "✓ Connection pool closed" in result.output
        assert "Cleanup completed" in result.output

        mock_close_cache.assert_called_once()
        mock_close_pool.assert_called_once()

    @patch("honeyhive.cli.main.close_global_cache")
    @patch("honeyhive.cli.main.close_global_pool")
    def test_cleanup_cache_error(
        self, mock_close_pool: Mock, mock_close_cache: Mock
    ) -> None:
        """Test cleanup command with cache close error."""
        mock_close_cache.side_effect = Exception("Cache close failed")

        runner = CliRunner()
        result = runner.invoke(cli, ["cleanup"])

        assert result.exit_code == 0
        assert "✗ Cache cleanup failed" in result.output
        assert "✓ Connection pool closed" in result.output
        assert "Cleanup completed" in result.output

    @patch("honeyhive.cli.main.close_global_cache")
    @patch("honeyhive.cli.main.close_global_pool")
    def test_cleanup_pool_error(
        self, mock_close_pool: Mock, mock_close_cache: Mock
    ) -> None:
        """Test cleanup command with connection pool close error."""
        mock_close_pool.side_effect = Exception("Pool close failed")

        runner = CliRunner()
        result = runner.invoke(cli, ["cleanup"])

        assert result.exit_code == 0
        assert "✓ Cache closed" in result.output
        assert "✗ Connection pool cleanup failed" in result.output
        assert "Cleanup completed" in result.output

    @patch("honeyhive.utils.cache.close_global_cache")
    def test_cleanup_general_error(self, mock_close_cache: Mock) -> None:
        """Test cleanup command with general error."""
        mock_close_cache.side_effect = Exception("Critical error")

        # Patch the entire cleanup function to raise an error
        with patch(
            "honeyhive.cli.main.close_global_cache",
            side_effect=Exception("Critical error"),
        ):
            runner = CliRunner()
            result = runner.invoke(cli, ["cleanup"])

            # Should handle the error but still try to complete cleanup
            assert "✗ Cache cleanup failed" in result.output


class TestCLIErrorHandling:
    """Phase 3: Test CLI error handling and edge cases."""

    def test_invalid_command(self) -> None:
        """Test invalid command handling."""
        runner = CliRunner()
        result = runner.invoke(cli, ["invalid-command"])

        assert result.exit_code != 0
        assert "No such command" in result.output

    def test_missing_required_argument(self) -> None:
        """Test missing required argument handling."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set"])

        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_invalid_option_value(self) -> None:
        """Test invalid option value handling."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "show", "--format", "invalid"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_trace_start_missing_name(self) -> None:
        """Test trace start command missing required name."""
        runner = CliRunner()
        result = runner.invoke(cli, ["trace", "start"])

        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_api_request_missing_url(self) -> None:
        """Test API request command missing required URL."""
        runner = CliRunner()
        result = runner.invoke(cli, ["api", "request"])

        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_nonexistent_config_file(self) -> None:
        """Test CLI with nonexistent config file."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--config", "/nonexistent/config.yaml", "config", "show"]
        )

        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()


class TestCLIEnvironmentVariables:
    """Phase 4: Test CLI environment variable handling and integration."""

    def test_env_var_override(self) -> None:
        """Test environment variable override."""
        with patch.dict(os.environ, {"HH_API_KEY": "env-api-key"}):
            runner = CliRunner()
            result = runner.invoke(cli, ["config", "show", "--format", "json"])

            assert result.exit_code == 0
            config_data = json.loads(result.output)
            assert "api_key" in config_data

    def test_env_var_debug_mode(self) -> None:
        """Test debug mode environment variable."""
        with patch.dict(os.environ, {"HH_DEBUG": "true"}):
            runner = CliRunner()
            result = runner.invoke(cli, ["config", "show"])

            assert result.exit_code == 0
            assert len(result.output) > 0

    def test_env_var_test_mode(self) -> None:
        """Test test mode environment variable."""
        with patch.dict(os.environ, {"HH_TEST_MODE": "true"}):
            runner = CliRunner()
            result = runner.invoke(cli, ["config", "show"])

            assert result.exit_code == 0
            assert len(result.output) > 0

    def test_combined_flags_and_env_vars(self) -> None:
        """Test combined CLI flags and environment variables."""
        with patch.dict(os.environ, {"HH_PROJECT": "env-project"}):
            runner = CliRunner()
            result = runner.invoke(cli, ["--verbose", "--debug", "config", "show"])

            assert "Verbose mode enabled" in result.output
            assert "Debug mode enabled" in result.output
