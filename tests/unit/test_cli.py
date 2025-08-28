"""Unit tests for HoneyHive CLI."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
import os

from honeyhive.cli.main import cli


class TestCLI:
    """Test CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "HoneyHive CLI" in result.output

    def test_config_show(self):
        """Test config show command."""
        with patch('honeyhive.utils.config.config') as mock_config:
            mock_config.api_key = "test-key"
            mock_config.api_url = "https://api.honeyhive.ai"
            mock_config.project = "test-project"
            mock_config.__dict__ = {
                'api_key': 'test-key',
                'api_url': 'https://api.honeyhive.ai',
                'project': 'test-project'
            }
            
            result = self.runner.invoke(cli, ['config', 'show'])
            assert result.exit_code == 0
            assert "test-key" in result.output

    def test_config_set(self):
        """Test config set command."""
        with patch('honeyhive.cli.main.config') as mock_config, \
             patch('honeyhive.utils.config.reload_config') as mock_reload:
            
            mock_config.api_key = "test-key"
            mock_config.__dict__ = {'api_key': 'test-key'}
            
            result = self.runner.invoke(cli, ['config', 'set', '--key', 'api_key', '--value', 'new-key'])
            assert result.exit_code == 0
            assert "Set api_key = new-key" in result.output

    def test_trace_start(self):
        """Test trace start command."""
        with patch('honeyhive.cli.main.HoneyHiveTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_span.__enter__ = Mock()
            mock_span.__exit__ = Mock()
            mock_tracer.start_span.return_value = mock_span
            mock_tracer_class.return_value = mock_tracer
            
            result = self.runner.invoke(cli, ['trace', 'start', '--name', 'test-span'])
            assert result.exit_code == 0
            assert "Started span: test-span" in result.output

    def test_trace_enrich(self):
        """Test trace enrich command."""
        with patch('honeyhive.tracer.get_tracer') as mock_get_tracer:
            mock_tracer = Mock()
            mock_get_tracer.return_value = mock_tracer
            
            result = self.runner.invoke(cli, ['trace', 'enrich', '--session-id', 'test-session'])
            assert result.exit_code == 0
            assert "Would enrich session test-session" in result.output

    def test_api_request(self):
        """Test API request command."""
        with patch('honeyhive.cli.main.HoneyHiveClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'application/json'}
            mock_response.json.return_value = {"result": "success"}
            mock_client.sync_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = self.runner.invoke(cli, ['api', 'request', '--method', 'GET', '--url', 'https://api.honeyhive.ai/test'])
            assert result.exit_code == 0
            assert "Status: 200" in result.output
            assert "success" in result.output

    def test_monitor_status(self):
        """Test monitor status command."""
        with patch('honeyhive.api.client.HoneyHiveClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_health.return_value = {"status": "healthy"}
            mock_client_class.return_value = mock_client
            
            result = self.runner.invoke(cli, ['monitor', 'status'])
            assert result.exit_code == 0
            assert "Configuration Status" in result.output
            assert "Tracer Status" in result.output
            assert "Cache Status" in result.output
            assert "Connection Pool Status" in result.output

    def test_monitor_watch(self):
        """Test monitor watch command."""
        with patch('honeyhive.api.client.HoneyHiveClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_health.return_value = {"status": "healthy"}
            mock_client_class.return_value = mock_client
            
            # Test with --duration 1 to avoid long wait
            result = self.runner.invoke(cli, ['monitor', 'watch', '--duration', '1'])
            assert result.exit_code == 0
            assert "Monitoring for 1 seconds" in result.output

    def test_performance_benchmark(self):
        """Test performance benchmark command."""
        with patch('honeyhive.tracer.get_tracer') as mock_get_tracer:
            mock_tracer = Mock()
            mock_tracer.start_span.return_value.__enter__ = Mock()
            mock_tracer.start_span.return_value.__exit__ = Mock()
            mock_get_tracer.return_value = mock_tracer
            
            result = self.runner.invoke(cli, ['performance', 'benchmark', '--iterations', '5'])
            assert result.exit_code == 0
            assert "Benchmarks completed" in result.output

    def test_cleanup(self):
        """Test cleanup command."""
        with patch('honeyhive.cli.main.close_global_pool') as mock_close_pool, \
             patch('honeyhive.cli.main.close_global_cache') as mock_close_cache:
            
            result = self.runner.invoke(cli, ['cleanup'])
            assert result.exit_code == 0
            assert "Cleanup completed" in result.output
            mock_close_pool.assert_called_once()
            mock_close_cache.assert_called_once()

    def test_config_set_invalid_key(self):
        """Test config set with invalid key."""
        result = self.runner.invoke(cli, ['config', 'set', '--invalid-key', 'value'])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_trace_start_missing_name(self):
        """Test trace start without name."""
        result = self.runner.invoke(cli, ['trace', 'start'])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_api_request_invalid_method(self):
        """Test API request with invalid method."""
        result = self.runner.invoke(cli, ['api', 'request', '--method', 'INVALID', '--endpoint', '/test'])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_monitor_watch_invalid_count(self):
        """Test monitor watch with invalid count."""
        result = self.runner.invoke(cli, ['monitor', 'watch', '--count', '0'])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_performance_benchmark_invalid_iterations(self):
        """Test performance benchmark with 0 iterations (should be handled gracefully)."""
        result = self.runner.invoke(cli, ['performance', 'benchmark', '--iterations', '0'])
        # 0 iterations should be handled gracefully (no error)
        assert result.exit_code == 0
        # The output should contain benchmark information
        assert "Iterations: 0" in result.output
        assert "Benchmarks completed" in result.output

    def test_config_set_multiple_values(self):
        """Test config set with multiple values."""
        with patch('honeyhive.utils.config.get_config') as mock_get_config, \
             patch('honeyhive.utils.config.reload_config') as mock_reload:
            
            mock_config = Mock()
            mock_get_config.return_value = mock_config
            
            result = self.runner.invoke(cli, [
                'config', 'set',
                '--key', 'api_key',
                '--value', 'new-key'
            ])
            assert result.exit_code == 0
            assert "Set api_key = new-key" in result.output

    def test_trace_start_with_attributes(self):
        """Test trace start with attributes."""
        with patch('honeyhive.cli.main.HoneyHiveTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_span.__enter__ = Mock()
            mock_span.__exit__ = Mock()
            mock_tracer.start_span.return_value = mock_span
            mock_tracer_class.return_value = mock_tracer
            
            result = self.runner.invoke(cli, [
                'trace', 'start',
                '--name', 'test-span',
                '--attributes', '{"key1": "value1", "key2": "value2"}'
            ])
            assert result.exit_code == 0
            assert "Started span: test-span" in result.output

    def test_api_request_with_headers(self):
        """Test API request with custom headers."""
        with patch('honeyhive.cli.main.HoneyHiveClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'application/json'}
            mock_response.json.return_value = {"result": "success"}
            mock_client.sync_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = self.runner.invoke(cli, [
                'api', 'request',
                '--method', 'POST',
                '--url', 'https://api.honeyhive.ai/test',
                '--headers', '{"Content-Type": "application/json"}',
                '--data', '{"key": "value"}'
            ])
            assert result.exit_code == 0
            assert "success" in result.output

    def test_monitor_status_with_format(self):
        """Test monitor status command."""
        with patch('honeyhive.api.client.HoneyHiveClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_health.return_value = {"status": "healthy", "version": "1.0.0"}
            mock_client_class.return_value = mock_client
            
            result = self.runner.invoke(cli, ['monitor', 'status'])
            assert result.exit_code == 0
            assert "Configuration Status" in result.output
            assert "Tracer Status" in result.output
            assert "Cache Status" in result.output
            assert "Connection Pool Status" in result.output

    def test_performance_benchmark_with_metrics(self):
        """Test performance benchmark command."""
        with patch('honeyhive.cli.main.HoneyHiveTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_span.__enter__ = Mock()
            mock_span.__exit__ = Mock()
            mock_tracer.start_span.return_value = mock_span
            mock_tracer_class.return_value = mock_tracer
            
            result = self.runner.invoke(cli, [
                'performance', 'benchmark',
                '--iterations', '10'
            ])
            assert result.exit_code == 0
            assert "Benchmarks completed" in result.output

    def test_cleanup_with_options(self):
        """Test cleanup command."""
        with patch('honeyhive.cli.main.close_global_pool') as mock_close_pool, \
             patch('honeyhive.cli.main.close_global_cache') as mock_close_cache:
            
            result = self.runner.invoke(cli, ['cleanup'])
            assert result.exit_code == 0
            assert "Cleanup completed" in result.output
            mock_close_pool.assert_called_once()
            mock_close_cache.assert_called_once()

    def test_cli_with_environment_variables(self):
        """Test CLI with environment variables."""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'env-key',
            'HH_PROJECT': 'env-project'
        }):
            with patch('honeyhive.utils.config.config') as mock_config:
                mock_config.api_key = "env-key"
                mock_config.project = "env-project"
                mock_config.__dict__ = {
                    'api_key': 'env-key',
                    'project': 'env-project'
                }
                
                result = self.runner.invoke(cli, ['config', 'show'])
                assert result.exit_code == 0
                assert "env-key" in result.output
                assert "env-project" in result.output

    def test_cli_error_handling(self):
        """Test CLI error handling."""
        # Test with invalid JSON in trace start
        result = self.runner.invoke(cli, ['trace', 'start', '--name', 'test', '--attributes', 'invalid-json'])
        assert result.exit_code != 0
        assert "Invalid JSON" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_cli_verbose_mode(self):
        """Test CLI verbose mode."""
        with patch('honeyhive.utils.config.config') as mock_config:
            mock_config.api_key = "test-key"
            mock_config.__dict__ = {'api_key': 'test-key'}
            
            result = self.runner.invoke(cli, ['--verbose', 'config', 'show'])
            assert result.exit_code == 0
            assert "Verbose mode enabled" in result.output
            assert "test-key" in result.output

    def test_cli_quiet_mode(self):
        """Test CLI debug mode."""
        with patch('honeyhive.utils.config.config') as mock_config:
            mock_config.api_key = "test-key"
            mock_config.__dict__ = {'api_key': 'test-key'}
            
            result = self.runner.invoke(cli, ['--debug', 'config', 'show'])
            assert result.exit_code == 0
            assert "Debug mode enabled" in result.output
            assert "test-key" in result.output
