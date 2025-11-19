"""Unit tests for honeyhive.cli.main.

This module contains comprehensive unit tests for the HoneyHive CLI main module,
covering all CLI commands, configuration management, tracing, API interactions,
monitoring, performance benchmarking, and resource cleanup functionality.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

import json
from io import StringIO
from unittest.mock import Mock, patch

import yaml
from click.testing import CliRunner

from honeyhive.cli.main import (
    api,
    benchmark,
    cleanup,
    cli,
    config,
    enrich,
    monitor,
    performance,
    request,
    set_config,
    show,
    start,
    status,
    trace,
    watch,
)


class TestCLIMain:
    """Test suite for CLI main entry point."""

    def test_cli_basic_invocation(self) -> None:
        """Test basic CLI invocation without arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "HoneyHive CLI" in result.output

    def test_cli_with_verbose_flag(self) -> None:
        """Test CLI with verbose flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "--help"])

        assert result.exit_code == 0
        assert "HoneyHive CLI" in result.output

    def test_cli_with_debug_flag(self) -> None:
        """Test CLI with debug flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--debug", "--help"])

        assert result.exit_code == 0
        assert "HoneyHive CLI" in result.output

    def test_cli_with_config_file(self) -> None:
        """Test CLI with config file option."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a test config file
            with open("test_config.yaml", "w", encoding="utf-8") as f:
                yaml.dump({"api_key": "test-key"}, f)

            result = runner.invoke(cli, ["--config", "test_config.yaml", "--help"])

            assert result.exit_code == 0
            assert "HoneyHive CLI" in result.output

    def test_cli_with_all_flags(self) -> None:
        """Test CLI with all flags combined."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("test_config.yaml", "w", encoding="utf-8") as f:
                yaml.dump({"api_key": "test-key"}, f)

            result = runner.invoke(
                cli, ["--verbose", "--debug", "--config", "test_config.yaml", "--help"]
            )

            assert result.exit_code == 0
            assert "HoneyHive CLI" in result.output


class TestConfigCommands:
    """Test suite for configuration management commands."""

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    def test_config_show_json_format(self, mock_tracer_class: Mock) -> None:
        """Test config show command with JSON format."""
        # Setup mock tracer instance
        mock_tracer = Mock()
        mock_tracer.config = {
            "api_key": "test-key-123",
            "server_url": "https://api.honeyhive.ai",
            "project": "test-project",
            "source": "dev",
            "verbose": False,
            "test_mode": True,
        }
        mock_tracer.shutdown = Mock()
        mock_tracer_class.return_value = mock_tracer

        runner = CliRunner()
        result = runner.invoke(show, ["--format", "json"])

        assert result.exit_code == 0
        output_data = json.loads(result.output)
        assert output_data["api_key"] == "test-key-123"
        assert output_data["project"] == "test-project"
        mock_tracer.shutdown.assert_called_once()

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    def test_config_show_yaml_format(self, mock_tracer_class: Mock) -> None:
        """Test config show command with YAML format."""
        mock_tracer = Mock()
        mock_tracer.config = {
            "api_key": "test-key-456",
            "server_url": "https://api.honeyhive.ai",
            "project": "yaml-project",
            "source": "prod",
            "verbose": True,
            "test_mode": False,
        }
        mock_tracer.shutdown = Mock()
        mock_tracer_class.return_value = mock_tracer

        runner = CliRunner()
        result = runner.invoke(show, ["--format", "yaml"])

        assert result.exit_code == 0
        assert "api_key: test-key-456" in result.output
        assert "project: yaml-project" in result.output
        mock_tracer.shutdown.assert_called_once()

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    def test_config_show_env_format(self, mock_tracer_class: Mock) -> None:
        """Test config show command with environment variable format."""
        mock_tracer = Mock()
        mock_tracer.config = {
            "api_key": "test-env-key",
            "server_url": "https://custom.api.url",
            "project": "env-project",
            "source": "staging",
            "verbose": False,
            "test_mode": True,
        }
        mock_tracer.shutdown = Mock()
        mock_tracer_class.return_value = mock_tracer

        runner = CliRunner()
        result = runner.invoke(show, ["--format", "env"])

        assert result.exit_code == 0
        assert "HH_API_KEY=test-env-key" in result.output
        assert "HH_API_URL=https://custom.api.url" in result.output
        assert "HH_PROJECT=env-project" in result.output
        mock_tracer.shutdown.assert_called_once()

    @patch("honeyhive.cli.main.TracerConfig")
    @patch("honeyhive.cli.main.HoneyHiveTracer")
    def test_config_show_fallback_to_tracer_config(
        self, mock_tracer_class: Mock, mock_tracer_config_class: Mock
    ) -> None:
        """Test config show falls back to TracerConfig when tracer creation fails."""
        # Make tracer creation fail
        mock_tracer_class.side_effect = Exception("Tracer creation failed")

        # Setup fallback config with proper attributes
        mock_config = Mock()
        mock_config.api_key = "fallback-key"
        mock_config.server_url = None
        mock_config.project = "fallback-project"
        mock_config.source = "fallback"
        mock_config.verbose = False
        mock_config.test_mode = True
        # Add experiment attributes that might be accessed
        mock_config.experiment_id = None
        mock_config.experiment_name = None
        mock_config.experiment_variant = None
        mock_config.experiment_group = None
        mock_config.experiment_metadata = None
        mock_tracer_config_class.return_value = mock_config

        runner = CliRunner()
        result = runner.invoke(show, ["--format", "json"])

        assert result.exit_code == 0
        output_data = json.loads(result.output)
        assert output_data["api_key"] == "fallback-key"
        assert (
            output_data["server_url"] == "https://api.honeyhive.ai"
        )  # Default fallback
        assert output_data["project"] == "fallback-project"

    def test_config_show_logging_suppression(self) -> None:
        """Test that config show suppresses logging during tracer creation."""
        with (
            patch("honeyhive.cli.main.logging") as mock_logging,
            patch("honeyhive.cli.main.sys") as mock_sys,
            patch("honeyhive.cli.main.HoneyHiveTracer") as mock_tracer_class,
        ):

            mock_tracer = Mock()
            mock_tracer.config = {
                "api_key": "test",
                "server_url": "https://api.honeyhive.ai",
            }
            mock_tracer.shutdown = Mock()
            mock_tracer_class.return_value = mock_tracer

            mock_stdout = Mock()
            mock_sys.stdout = mock_stdout

            runner = CliRunner()
            result = runner.invoke(show, ["--format", "json"])

            assert result.exit_code == 0
            # Verify logging was suppressed and restored
            mock_logging.root.setLevel.assert_called()
            mock_tracer.shutdown.assert_called_once()

    def test_set_config_command(self) -> None:
        """Test set config command shows appropriate message."""
        runner = CliRunner()
        result = runner.invoke(set_config, ["--key", "api_key", "--value", "new-key"])

        assert result.exit_code == 0
        assert "Configuration modification not supported" in result.output
        assert "export HH_API_KEY=new-key" in result.output
        assert "tracer = HoneyHiveTracer(api_key='new-key')" in result.output


class TestTraceCommands:
    """Test suite for tracing commands."""

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("builtins.input", return_value="")
    def test_trace_start_basic(
        self, _mock_input: Mock, mock_tracer_class: Mock
    ) -> None:
        """Test basic trace start command."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer_class.return_value = mock_tracer

        runner = CliRunner()
        result = runner.invoke(start, ["--name", "test-span"])

        assert result.exit_code == 0
        assert "Started span: test-span" in result.output
        assert "Ended span: test-span" in result.output
        mock_tracer.start_span.assert_called_once_with(name="test-span", attributes={})

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("builtins.input", return_value="")
    def test_trace_start_with_session_id(
        self, _mock_input: Mock, mock_tracer_class: Mock
    ) -> None:
        """Test trace start command with session ID."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer_class.return_value = mock_tracer

        runner = CliRunner()
        result = runner.invoke(
            start, ["--name", "test-span", "--session-id", "session-123"]
        )

        assert result.exit_code == 0
        expected_attributes = {"session_id": "session-123"}
        mock_tracer.start_span.assert_called_once_with(
            name="test-span", attributes=expected_attributes
        )

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("builtins.input", return_value="")
    def test_trace_start_with_attributes(
        self, _mock_input: Mock, mock_tracer_class: Mock
    ) -> None:
        """Test trace start command with JSON attributes."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer_class.return_value = mock_tracer

        attributes_json = '{"key1": "value1", "key2": 42}'
        runner = CliRunner()
        result = runner.invoke(
            start, ["--name", "test-span", "--attributes", attributes_json]
        )

        assert result.exit_code == 0
        expected_attributes = {"key1": "value1", "key2": 42}
        mock_tracer.start_span.assert_called_once_with(
            name="test-span", attributes=expected_attributes
        )

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    def test_trace_start_invalid_json_attributes(self, mock_tracer_class: Mock) -> None:
        """Test trace start command with invalid JSON attributes."""
        mock_tracer_class.return_value = Mock()

        runner = CliRunner()
        result = runner.invoke(
            start, ["--name", "test-span", "--attributes", "invalid-json"]
        )

        assert result.exit_code == 1
        assert "Invalid JSON for attributes" in result.output

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    def test_trace_start_exception_handling(self, mock_tracer_class: Mock) -> None:
        """Test trace start command exception handling."""
        mock_tracer_class.side_effect = Exception("Tracer creation failed")

        runner = CliRunner()
        result = runner.invoke(start, ["--name", "test-span"])

        assert result.exit_code == 1
        assert "Failed to start trace: Tracer creation failed" in result.output

    def test_trace_enrich_missing_session_id(self) -> None:
        """Test trace enrich command without session ID."""
        runner = CliRunner()
        result = runner.invoke(enrich, ["--metadata", '{"key": "value"}'])

        assert result.exit_code == 1
        assert "Session ID is required" in result.output

    def test_trace_enrich_with_metadata(self) -> None:
        """Test trace enrich command with metadata."""
        runner = CliRunner()
        result = runner.invoke(
            enrich,
            ["--session-id", "session-123", "--metadata", '{"experiment": "test-exp"}'],
        )

        assert result.exit_code == 0
        assert "Would enrich session session-123" in result.output
        assert "experiment" in result.output

    def test_trace_enrich_with_feedback(self) -> None:
        """Test trace enrich command with feedback."""
        runner = CliRunner()
        result = runner.invoke(
            enrich,
            [
                "--session-id",
                "session-456",
                "--feedback",
                '{"rating": 5, "comment": "excellent"}',
            ],
        )

        assert result.exit_code == 0
        assert "Would enrich session session-456" in result.output
        assert "rating" in result.output

    def test_trace_enrich_with_metrics(self) -> None:
        """Test trace enrich command with metrics."""
        runner = CliRunner()
        result = runner.invoke(
            enrich,
            [
                "--session-id",
                "session-789",
                "--metrics",
                '{"accuracy": 0.95, "latency": 120}',
            ],
        )

        assert result.exit_code == 0
        assert "Would enrich session session-789" in result.output
        assert "accuracy" in result.output

    def test_trace_enrich_invalid_metadata_json(self) -> None:
        """Test trace enrich command with invalid metadata JSON."""
        runner = CliRunner()
        result = runner.invoke(
            enrich, ["--session-id", "session-123", "--metadata", "invalid-json"]
        )

        assert result.exit_code == 1
        assert "Invalid JSON for metadata" in result.output

    def test_trace_enrich_invalid_feedback_json(self) -> None:
        """Test trace enrich command with invalid feedback JSON."""
        runner = CliRunner()
        result = runner.invoke(
            enrich, ["--session-id", "session-123", "--feedback", "invalid-json"]
        )

        assert result.exit_code == 1
        assert "Invalid JSON for feedback" in result.output

    def test_trace_enrich_invalid_metrics_json(self) -> None:
        """Test trace enrich command with invalid metrics JSON."""
        runner = CliRunner()
        result = runner.invoke(
            enrich, ["--session-id", "session-123", "--metrics", "invalid-json"]
        )

        assert result.exit_code == 1
        assert "Invalid JSON for metrics" in result.output

    def test_trace_enrich_exception_handling(self) -> None:
        """Test trace enrich command exception handling."""
        with patch(
            "honeyhive.cli.main.json.loads", side_effect=Exception("JSON error")
        ):
            runner = CliRunner()
            result = runner.invoke(
                enrich,
                ["--session-id", "session-123", "--metadata", '{"key": "value"}'],
            )

            assert result.exit_code == 1
            assert "Failed to enrich session: JSON error" in result.output


class TestAPICommands:
    """Test suite for API client commands."""

    @patch("honeyhive.cli.main.HoneyHive")
    @patch("honeyhive.cli.main.time")
    def test_api_request_get(self, mock_time: Mock, mock_client_class: Mock) -> None:
        """Test API request command with GET method."""
        # Setup time mocking
        mock_time.time.side_effect = [1000.0, 1000.5]  # 0.5 second duration

        # Setup client and response mocking
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_client.sync_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(
            request, ["--method", "GET", "--url", "https://api.honeyhive.ai/test"]
        )

        assert result.exit_code == 0
        assert "Status: 200" in result.output
        assert "Duration: 0.500s" in result.output
        assert '"success": true' in result.output
        mock_client.sync_client.request.assert_called_once_with(
            method="GET",
            url="https://api.honeyhive.ai/test",
            headers={},
            json=None,
            timeout=30.0,
        )

    @patch("honeyhive.cli.main.HoneyHive")
    @patch("honeyhive.cli.main.time")
    def test_api_request_post_with_data(
        self, mock_time: Mock, mock_client_class: Mock
    ) -> None:
        """Test API request command with POST method and data."""
        mock_time.time.side_effect = [2000.0, 2001.2]  # 1.2 second duration

        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"id": "created-123"}
        mock_client.sync_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(
            request,
            [
                "--method",
                "POST",
                "--url",
                "https://api.honeyhive.ai/events",
                "--headers",
                '{"Authorization": "Bearer token123"}',
                "--data",
                '{"name": "test-event", "type": "click"}',
                "--timeout",
                "60",
            ],
        )

        assert result.exit_code == 0
        assert "Status: 201" in result.output
        assert "Duration: 1.200s" in result.output
        assert '"id": "created-123"' in result.output
        mock_client.sync_client.request.assert_called_once_with(
            method="POST",
            url="https://api.honeyhive.ai/events",
            headers={"Authorization": "Bearer token123"},
            json={"name": "test-event", "type": "click"},
            timeout=60.0,
        )

    @patch("honeyhive.cli.main.HoneyHive")
    def test_api_request_invalid_headers_json(self, mock_client_class: Mock) -> None:
        """Test API request command with invalid headers JSON."""
        mock_client_class.return_value = Mock()

        runner = CliRunner()
        result = runner.invoke(
            request,
            [
                "--method",
                "GET",
                "--url",
                "https://api.honeyhive.ai/test",
                "--headers",
                "invalid-json",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid JSON for headers" in result.output

    @patch("honeyhive.cli.main.HoneyHive")
    def test_api_request_invalid_data_json(self, mock_client_class: Mock) -> None:
        """Test API request command with invalid data JSON."""
        mock_client_class.return_value = Mock()

        runner = CliRunner()
        result = runner.invoke(
            request,
            [
                "--method",
                "POST",
                "--url",
                "https://api.honeyhive.ai/test",
                "--data",
                "invalid-json",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid JSON for data" in result.output

    @patch("honeyhive.cli.main.HoneyHive")
    @patch("honeyhive.cli.main.time")
    def test_api_request_non_json_response(
        self, mock_time: Mock, mock_client_class: Mock
    ) -> None:
        """Test API request command with non-JSON response."""
        mock_time.time.side_effect = [3000.0, 3000.1]

        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        mock_response.text = "Plain text response"
        mock_client.sync_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(
            request, ["--method", "GET", "--url", "https://api.honeyhive.ai/health"]
        )

        assert result.exit_code == 0
        assert "Status: 200" in result.output
        assert "Response: Plain text response" in result.output

    @patch("honeyhive.cli.main.HoneyHive")
    def test_api_request_exception_handling(self, mock_client_class: Mock) -> None:
        """Test API request command exception handling."""
        mock_client_class.side_effect = Exception("Client creation failed")

        runner = CliRunner()
        result = runner.invoke(
            request, ["--method", "GET", "--url", "https://api.honeyhive.ai/test"]
        )

        assert result.exit_code == 1
        assert "API request failed: Client creation failed" in result.output


class TestMonitorCommands:
    """Test suite for monitoring commands."""

    @patch("honeyhive.cli.main.TracerConfig")
    @patch("honeyhive.cli.main.get_global_cache")
    @patch("honeyhive.cli.main.get_global_pool")
    def test_monitor_status_success(
        self, mock_get_pool: Mock, mock_get_cache: Mock, mock_tracer_config_class: Mock
    ) -> None:
        """Test monitor status command with successful status retrieval."""
        # Setup tracer config
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.project = "test-project"
        mock_config.source = "test"
        mock_config.verbose = True
        mock_config.disable_http_tracing = False
        mock_tracer_config_class.return_value = mock_config

        # Setup cache stats
        mock_cache = Mock()
        mock_cache.get_stats.return_value = {
            "size": 50,
            "max_size": 100,
            "hit_rate": 0.75,
            "hits": 150,
            "misses": 50,
        }
        mock_get_cache.return_value = mock_cache

        # Setup pool stats
        mock_pool = Mock()
        mock_pool.get_stats.return_value = {
            "total_requests": 1000,
            "pool_hits": 800,
            "pool_misses": 200,
            "active_connections": 5,
        }
        mock_get_pool.return_value = mock_pool

        runner = CliRunner()
        result = runner.invoke(status)

        assert result.exit_code == 0
        assert "=== Configuration Status ===" in result.output
        assert "API Key: ✓" in result.output
        assert "Project: test-project" in result.output
        assert "Source: test" in result.output
        assert "Verbose Mode: True" in result.output
        assert "HTTP Tracing Disabled: False" in result.output
        assert "=== Tracer Status ===" in result.output
        assert "✓ Multi-instance architecture enabled" in result.output
        assert "=== Cache Status ===" in result.output
        assert "✓ Cache active" in result.output
        assert "Size: 50/100" in result.output
        assert "Hit Rate: 75.00%" in result.output
        assert "=== Connection Pool Status ===" in result.output
        assert "✓ Connection pool active" in result.output
        assert "Total Requests: 1000" in result.output

    @patch("honeyhive.cli.main.TracerConfig")
    @patch("honeyhive.cli.main.get_global_cache")
    @patch("honeyhive.cli.main.get_global_pool")
    def test_monitor_status_with_errors(
        self, mock_get_pool: Mock, mock_get_cache: Mock, mock_tracer_config_class: Mock
    ) -> None:
        """Test monitor status command with component errors."""
        # Setup tracer config
        mock_config = Mock()
        mock_config.api_key = None  # No API key
        mock_config.project = None  # No project
        mock_config.source = "dev"
        mock_config.verbose = False
        mock_config.disable_http_tracing = True
        mock_tracer_config_class.return_value = mock_config

        # Make cache fail
        mock_get_cache.side_effect = Exception("Cache error")

        # Make pool fail
        mock_get_pool.side_effect = Exception("Pool error")

        runner = CliRunner()
        result = runner.invoke(status)

        assert result.exit_code == 0
        assert "API Key: ✗" in result.output
        assert "Project: Not set" in result.output
        assert "✗ Cache error: Cache error" in result.output
        assert "✗ Connection pool error: Pool error" in result.output

    @patch("honeyhive.cli.main.TracerConfig")
    def test_monitor_status_exception_handling(
        self, mock_tracer_config_class: Mock
    ) -> None:
        """Test monitor status command exception handling."""
        mock_tracer_config_class.side_effect = Exception("Config creation failed")

        runner = CliRunner()
        result = runner.invoke(status)

        assert result.exit_code == 1
        assert "Failed to get status: Config creation failed" in result.output

    @patch("honeyhive.cli.main.get_global_cache")
    @patch("honeyhive.cli.main.get_global_pool")
    @patch("honeyhive.cli.main.time")
    def test_monitor_watch_basic(
        self, mock_time: Mock, mock_get_pool: Mock, mock_get_cache: Mock
    ) -> None:
        """Test monitor watch command basic functionality."""
        # Setup time progression to exit loop quickly
        mock_time.time.side_effect = [
            1000.0,
            1001.0,
            1002.0,
            1010.0,
        ]  # Exit after 3 iterations
        mock_time.strftime.return_value = "12:34:56"
        mock_time.sleep = Mock()

        # Setup cache stats
        mock_cache = Mock()
        mock_cache.get_stats.return_value = {
            "size": 25,
            "max_size": 50,
            "hit_rate": 0.80,
            "hits": 80,
            "misses": 20,
        }
        mock_get_cache.return_value = mock_cache

        # Setup pool stats
        mock_pool = Mock()
        mock_pool.get_stats.return_value = {
            "total_requests": 500,
            "pool_hits": 400,
            "pool_misses": 100,
            "active_connections": 3,
        }
        mock_get_pool.return_value = mock_pool

        runner = CliRunner()
        result = runner.invoke(watch, ["--duration", "5", "--interval", "1"])

        assert result.exit_code == 0
        assert "Monitoring for 5 seconds" in result.output
        assert "=== HoneyHive Monitor (12:34:56) ===" in result.output
        assert "Size: 25/50" in result.output
        assert "Hit Rate: 80.00%" in result.output
        assert "Total Requests: 500" in result.output
        assert "Monitoring completed" in result.output

    @patch("honeyhive.cli.main.get_global_cache")
    @patch("honeyhive.cli.main.get_global_pool")
    @patch("honeyhive.cli.main.time")
    def test_monitor_watch_with_stats_error(
        self, mock_time: Mock, mock_get_pool: Mock, mock_get_cache: Mock
    ) -> None:
        """Test monitor watch command with stats retrieval error."""
        mock_time.time.side_effect = [2000.0, 2001.0, 2010.0]  # Exit after 1 iteration
        mock_time.sleep = Mock()

        # Make stats retrieval fail
        mock_get_cache.side_effect = Exception("Stats error")
        mock_get_pool.side_effect = Exception("Pool stats error")

        runner = CliRunner()
        result = runner.invoke(watch, ["--duration", "2", "--interval", "1"])

        assert result.exit_code == 0
        assert "Error getting stats: Stats error" in result.output

    @patch("honeyhive.cli.main.get_global_cache")
    def test_monitor_watch_exception_handling(self, _mock_get_cache: Mock) -> None:
        """Test monitor watch command exception handling."""
        # Make the exception occur during the main try block
        with patch(
            "honeyhive.cli.main.time.time", side_effect=Exception("Watch setup failed")
        ):
            runner = CliRunner()
            result = runner.invoke(watch, ["--duration", "1"])

            assert result.exit_code == 1
            assert "Failed to start monitoring: Watch setup failed" in result.output


class TestPerformanceCommands:
    """Test suite for performance analysis commands."""

    @patch("honeyhive.cli.main.get_global_cache")
    @patch("honeyhive.cli.main.time")
    def test_performance_benchmark_basic(
        self, mock_time: Mock, mock_get_cache: Mock
    ) -> None:
        """Test performance benchmark command basic functionality."""
        # Setup cache
        mock_cache = Mock()
        mock_cache.set = Mock()
        mock_cache.get = Mock(return_value="cached_value")
        mock_get_cache.return_value = mock_cache

        # Setup time for duration measurement
        mock_time.time.side_effect = [
            1000.0,
            1001.0,  # Set operations: 1 second
            2000.0,
            2000.5,  # Get operations: 0.5 seconds
        ]

        runner = CliRunner()
        result = runner.invoke(benchmark, ["--iterations", "100", "--warmup", "10"])

        assert result.exit_code == 0
        assert "Running performance benchmarks..." in result.output
        assert "Iterations: 100" in result.output
        assert "Warmup: 10" in result.output
        assert "Warming up..." in result.output
        assert "Warmup completed" in result.output
        assert "=== Cache Performance ===" in result.output
        assert "Set operations: 100 ops/s" in result.output
        assert "Get operations: 200 ops/s" in result.output
        assert "=== Tracer Performance ===" in result.output
        assert "Multi-instance mode enabled" in result.output
        assert "Benchmarks completed" in result.output

        # Verify cache operations were called
        assert mock_cache.set.call_count == 100
        assert mock_cache.get.call_count == 100

    @patch("honeyhive.cli.main.get_global_cache")
    def test_performance_benchmark_zero_iterations(self, mock_get_cache: Mock) -> None:
        """Test performance benchmark command with zero iterations."""
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache

        runner = CliRunner()
        result = runner.invoke(benchmark, ["--iterations", "0", "--warmup", "0"])

        assert result.exit_code == 0
        assert "Skipping cache benchmarks (0 iterations)" in result.output
        assert "Skipping tracer benchmarks (0 iterations)" in result.output

        # Verify no cache operations were called
        mock_cache.set.assert_not_called()
        mock_cache.get.assert_not_called()

    @patch("honeyhive.cli.main.get_global_cache")
    def test_performance_benchmark_exception_handling(
        self, mock_get_cache: Mock
    ) -> None:
        """Test performance benchmark command exception handling."""
        mock_get_cache.side_effect = Exception("Benchmark setup failed")

        runner = CliRunner()
        result = runner.invoke(benchmark, ["--iterations", "10"])

        assert result.exit_code == 1
        assert "Benchmark failed: Benchmark setup failed" in result.output


class TestCleanupCommand:
    """Test suite for cleanup command."""

    @patch("honeyhive.cli.main.close_global_cache")
    @patch("honeyhive.cli.main.close_global_pool")
    def test_cleanup_success(
        self, mock_close_pool: Mock, mock_close_cache: Mock
    ) -> None:
        """Test cleanup command successful execution."""
        runner = CliRunner()
        result = runner.invoke(cleanup)

        assert result.exit_code == 0
        assert "Cleaning up resources..." in result.output
        assert "✓ Cache closed" in result.output
        assert "✓ Connection pool closed" in result.output
        assert "Cleanup completed" in result.output

        mock_close_cache.assert_called_once()
        mock_close_pool.assert_called_once()

    @patch("honeyhive.cli.main.close_global_cache")
    @patch("honeyhive.cli.main.close_global_pool")
    def test_cleanup_with_cache_error(
        self, _mock_close_pool: Mock, mock_close_cache: Mock
    ) -> None:
        """Test cleanup command with cache cleanup error."""
        mock_close_cache.side_effect = Exception("Cache cleanup failed")

        runner = CliRunner()
        result = runner.invoke(cleanup)

        assert result.exit_code == 0
        assert "✗ Cache cleanup failed: Cache cleanup failed" in result.output
        assert "✓ Connection pool closed" in result.output
        assert "Cleanup completed" in result.output

    @patch("honeyhive.cli.main.close_global_cache")
    @patch("honeyhive.cli.main.close_global_pool")
    def test_cleanup_with_pool_error(
        self, mock_close_pool: Mock, _mock_close_cache: Mock
    ) -> None:
        """Test cleanup command with pool cleanup error."""
        mock_close_pool.side_effect = Exception("Pool cleanup failed")

        runner = CliRunner()
        result = runner.invoke(cleanup)

        assert result.exit_code == 0
        assert "✓ Cache closed" in result.output
        assert "✗ Connection pool cleanup failed: Pool cleanup failed" in result.output
        assert "Cleanup completed" in result.output

    @patch("honeyhive.cli.main.close_global_cache")
    def test_cleanup_exception_handling(self, mock_close_cache: Mock) -> None:
        """Test cleanup command exception handling."""
        # Test that cleanup handles exceptions gracefully
        mock_close_cache.side_effect = Exception("Cleanup setup failed")

        runner = CliRunner()
        result = runner.invoke(cleanup)

        # Cleanup command catches exceptions and continues
        assert result.exit_code == 0
        assert "Cache cleanup failed: Cleanup setup failed" in result.output


class TestPrivateHelperFunctions:
    """Test suite for private helper functions."""

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("honeyhive.cli.main.logging")
    @patch("honeyhive.cli.main.sys")
    def test_get_config_dict_success(
        self, mock_sys: Mock, mock_logging: Mock, mock_tracer_class: Mock
    ) -> None:
        """Test _get_config_dict helper function success path."""
        # Setup tracer mock
        mock_tracer = Mock()
        mock_tracer.config = {
            "api_key": "helper-test-key",
            "server_url": "https://custom.server.url",
            "project": "helper-project",
            "source": "helper-source",
            "verbose": True,
            "test_mode": False,
        }
        mock_tracer.shutdown = Mock()
        mock_tracer_class.return_value = mock_tracer

        # Setup logging and stdout mocking
        mock_stdout = StringIO()
        mock_sys.stdout = mock_stdout
        mock_logging.root.level = 20  # INFO level
        mock_logging.root.handlers = [Mock(), Mock()]

        runner = CliRunner()
        result = runner.invoke(show, ["--format", "json"])

        assert result.exit_code == 0
        output_data = json.loads(result.output)
        assert output_data["api_key"] == "helper-test-key"
        assert output_data["server_url"] == "https://custom.server.url"
        assert output_data["project"] == "helper-project"

        # Verify logging was suppressed and restored
        mock_logging.root.setLevel.assert_called()
        mock_tracer.shutdown.assert_called_once()

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("honeyhive.cli.main.TracerConfig")
    @patch("honeyhive.cli.main.logging")
    @patch("honeyhive.cli.main.sys")
    def test_get_config_dict_fallback(
        self,
        _mock_sys: Mock,
        _mock_logging: Mock,
        mock_tracer_config_class: Mock,
        mock_tracer_class: Mock,
    ) -> None:
        """Test _get_config_dict helper function fallback path."""
        # Make tracer creation fail
        mock_tracer_class.side_effect = Exception("Tracer init failed")

        # Setup fallback config
        mock_config = Mock()
        mock_config.api_key = "fallback-helper-key"
        mock_config.server_url = "https://fallback.url"
        mock_config.project = "fallback-helper-project"
        mock_config.source = "fallback-source"
        mock_config.verbose = False
        mock_config.test_mode = True
        # Add experiment attributes
        for attr in [
            "experiment_id",
            "experiment_name",
            "experiment_variant",
            "experiment_group",
            "experiment_metadata",
        ]:
            setattr(mock_config, attr, f"fallback-{attr}")
        mock_tracer_config_class.return_value = mock_config

        runner = CliRunner()
        result = runner.invoke(show, ["--format", "json"])

        assert result.exit_code == 0
        output_data = json.loads(result.output)
        assert output_data["api_key"] == "fallback-helper-key"
        assert output_data["server_url"] == "https://fallback.url"
        assert output_data["project"] == "fallback-helper-project"


class TestEdgeCasesAndErrorHandling:
    """Test suite for edge cases and comprehensive error handling."""

    def test_cli_version_option(self) -> None:
        """Test CLI version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        # Version option should exit with code 0 and show version info
        assert result.exit_code == 0

    def test_config_command_help(self) -> None:
        """Test config command help."""
        runner = CliRunner()
        result = runner.invoke(config, ["--help"])

        assert result.exit_code == 0
        assert "Configuration management commands" in result.output

    def test_trace_command_help(self) -> None:
        """Test trace command help."""
        runner = CliRunner()
        result = runner.invoke(trace, ["--help"])

        assert result.exit_code == 0
        assert "Tracing commands" in result.output

    def test_api_command_help(self) -> None:
        """Test API command help."""
        runner = CliRunner()
        result = runner.invoke(api, ["--help"])

        assert result.exit_code == 0
        assert "API client commands" in result.output

    def test_monitor_command_help(self) -> None:
        """Test monitor command help."""
        runner = CliRunner()
        result = runner.invoke(monitor, ["--help"])

        assert result.exit_code == 0
        assert "Monitoring and performance commands" in result.output

    def test_performance_command_help(self) -> None:
        """Test performance command help."""
        runner = CliRunner()
        result = runner.invoke(performance, ["--help"])

        assert result.exit_code == 0
        assert "Performance analysis commands" in result.output

    @patch("honeyhive.cli.main.HoneyHiveTracer")
    @patch("builtins.input", side_effect=KeyboardInterrupt())
    def test_trace_start_keyboard_interrupt(
        self, _mock_input: Mock, mock_tracer_class: Mock
    ) -> None:
        """Test trace start command with keyboard interrupt."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer_class.return_value = mock_tracer

        runner = CliRunner()
        result = runner.invoke(start, ["--name", "interrupt-test"])

        # Should handle KeyboardInterrupt gracefully
        assert "Started span: interrupt-test" in result.output

    @patch("honeyhive.cli.main.get_global_cache")
    @patch("honeyhive.cli.main.get_global_pool")
    @patch("honeyhive.cli.main.time")
    def test_monitor_watch_keyboard_interrupt(
        self, mock_time: Mock, mock_get_pool: Mock, mock_get_cache: Mock
    ) -> None:
        """Test monitor watch command with keyboard interrupt."""
        # Setup mocks to simulate KeyboardInterrupt during monitoring
        mock_time.time.side_effect = [3000.0, 3001.0]
        mock_time.sleep.side_effect = KeyboardInterrupt()

        mock_cache = Mock()
        mock_cache.get_stats.return_value = {
            "size": 0,
            "max_size": 100,
            "hit_rate": 0.0,
            "hits": 0,
            "misses": 0,
        }
        mock_get_cache.return_value = mock_cache

        mock_pool = Mock()
        mock_pool.get_stats.return_value = {
            "total_requests": 0,
            "pool_hits": 0,
            "pool_misses": 0,
            "active_connections": 0,
        }
        mock_get_pool.return_value = mock_pool

        runner = CliRunner()
        result = runner.invoke(watch, ["--duration", "10", "--interval", "1"])

        # Monitor watch handles KeyboardInterrupt gracefully
        assert result.exit_code in (0, 1)  # Either is acceptable for interrupt handling

    def test_config_show_env_format_with_none_values(self) -> None:
        """Test config show env format handling None values correctly."""
        with patch("honeyhive.cli.main.HoneyHiveTracer") as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer.config = {
                "api_key": None,  # None value should be skipped
                "server_url": "https://api.honeyhive.ai",
                "project": None,  # None value should be skipped
                "source": "dev",
                "verbose": False,
                "test_mode": True,
            }
            mock_tracer.shutdown = Mock()
            mock_tracer_class.return_value = mock_tracer

            runner = CliRunner()
            result = runner.invoke(show, ["--format", "env"])

            assert result.exit_code == 0
            # Should only show non-None values
            assert "HH_API_URL=https://api.honeyhive.ai" in result.output
            assert "HH_SOURCE=dev" in result.output
            assert "HH_VERBOSE=False" in result.output
            # Should not show None values
            assert (
                "HH_API_KEY=" not in result.output
                or "HH_API_KEY=None" not in result.output
            )
            assert (
                "HH_PROJECT=" not in result.output
                or "HH_PROJECT=None" not in result.output
            )
