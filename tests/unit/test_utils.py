"""Unit tests for HoneyHive utilities."""

import pytest
from unittest.mock import patch

from honeyhive.utils.config import Config
from honeyhive.utils.retry import RetryConfig, BackoffStrategy
from honeyhive.utils.dotdict import dotdict


class TestConfig:
    """Test configuration utilities."""
    
    def test_config_defaults(self, monkeypatch):
        """Test configuration default values."""
        # Clear test environment variables for this test
        monkeypatch.delenv("HH_API_KEY", raising=False)
        monkeypatch.delenv("HH_PROJECT", raising=False)
        monkeypatch.delenv("HH_TEST_MODE", raising=False)
        monkeypatch.delenv("HH_DISABLE_TRACING", raising=False)
        monkeypatch.delenv("HH_DISABLE_HTTP_TRACING", raising=False)
        monkeypatch.delenv("HH_SOURCE", raising=False)
        monkeypatch.delenv("HH_OTLP_ENABLED", raising=False)
        monkeypatch.delenv("HH_DEBUG_MODE", raising=False)
        
        # Create a new config instance with cleared environment
        config = Config()
        
        assert config.api_url == "https://api.honeyhive.ai"
        assert config.source == "production"
        assert config.disable_tracing is False
        assert config.disable_http_tracing is False
        assert config.test_mode is False
        assert config.otlp_enabled is True
        assert config.version == "0.1.0"
        assert config.timeout == 30.0
        assert config.max_retries == 3
    
    def test_config_env_vars(self, monkeypatch):
        """Test configuration with environment variables."""
        monkeypatch.setenv("HH_API_KEY", "test-key")
        monkeypatch.setenv("HH_PROJECT", "test-project")
        monkeypatch.setenv("HH_SOURCE", "staging")
        monkeypatch.setenv("HH_API_URL", "https://test-api.honeyhive.ai")
        monkeypatch.setenv("HH_DISABLE_TRACING", "true")
        monkeypatch.setenv("HH_DISABLE_HTTP_TRACING", "true")
        monkeypatch.setenv("HH_TEST_MODE", "true")
        monkeypatch.setenv("HH_OTLP_ENABLED", "false")
        monkeypatch.setenv("HH_OTLP_ENDPOINT", "https://test-otlp:4318")
        monkeypatch.setenv("HH_OTLP_HEADERS", '{"test": "header"}')
        
        config = Config()
        
        assert config.api_key == "test-key"
        assert config.project == "test-project"
        assert config.source == "staging"
        assert config.api_url == "https://test-api.honeyhive.ai"
        assert config.disable_tracing is True
        assert config.disable_http_tracing is True
        assert config.test_mode is True
        assert config.otlp_enabled is False
        assert config.otlp_endpoint == "https://test-otlp:4318"
        assert config.otlp_headers == {"test": "header"}


class TestBackoffStrategy:
    """Test backoff strategy."""
    
    def test_backoff_strategy_defaults(self):
        """Test backoff strategy default values."""
        strategy = BackoffStrategy()
        
        assert strategy.initial_delay == 1.0
        assert strategy.max_delay == 60.0
        assert strategy.multiplier == 2.0
        assert strategy.jitter == 0.1
    
    def test_backoff_strategy_get_delay(self):
        """Test backoff strategy delay calculation."""
        strategy = BackoffStrategy(
            initial_delay=1.0,
            max_delay=10.0,
            multiplier=2.0,
            jitter=0.0
        )
        
        # First attempt (attempt 0) should return 0
        assert strategy.get_delay(0) == 0
        
        # Second attempt (attempt 1) should return initial_delay
        assert strategy.get_delay(1) == 1.0
        
        # Third attempt (attempt 2) should return initial_delay * multiplier
        assert strategy.get_delay(2) == 2.0
        
        # Fourth attempt (attempt 3) should return initial_delay * multiplier^2
        assert strategy.get_delay(3) == 4.0
        
        # Should not exceed max_delay
        assert strategy.get_delay(10) == 10.0
    
    def test_backoff_strategy_with_jitter(self):
        """Test backoff strategy with jitter."""
        strategy = BackoffStrategy(
            initial_delay=1.0,
            max_delay=10.0,
            multiplier=2.0,
            jitter=0.1
        )
        
        # With jitter, delay should be within expected range
        delay = strategy.get_delay(1)
        assert 0.9 <= delay <= 1.1


class TestRetryConfig:
    """Test retry configuration."""
    
    def test_retry_config_defaults(self):
        """Test retry configuration default values."""
        config = RetryConfig()
        
        assert config.strategy == "exponential"
        assert config.max_retries == 3
        assert config.retry_on_status_codes == {408, 429, 500, 502, 503, 504}
        assert config.backoff_strategy is not None
    
    def test_retry_config_exponential(self):
        """Test exponential retry configuration."""
        config = RetryConfig.exponential(
            initial_delay=2.0,
            max_delay=20.0,
            multiplier=3.0,
            max_retries=5
        )
        
        assert config.strategy == "exponential"
        assert config.max_retries == 5
        assert config.backoff_strategy.initial_delay == 2.0
        assert config.backoff_strategy.max_delay == 20.0
        assert config.backoff_strategy.multiplier == 3.0
    
    def test_retry_config_linear(self):
        """Test linear retry configuration."""
        config = RetryConfig.linear(delay=1.5, max_retries=4)
        
        assert config.strategy == "linear"
        assert config.max_retries == 4
        assert config.backoff_strategy.initial_delay == 1.5
        assert config.backoff_strategy.max_delay == 1.5
        assert config.backoff_strategy.multiplier == 1.0
    
    def test_retry_config_constant(self):
        """Test constant retry configuration."""
        config = RetryConfig.constant(delay=0.5, max_retries=2)
        
        assert config.strategy == "constant"
        assert config.max_retries == 2
        assert config.backoff_strategy.initial_delay == 0.5
        assert config.backoff_strategy.max_delay == 0.5
        assert config.backoff_strategy.multiplier == 1.0
    
    def test_should_retry_status_codes(self):
        """Test should_retry with status codes."""
        config = RetryConfig()
        
        # Should retry on retryable status codes
        mock_response = type('MockResponse', (), {'status_code': 429})()
        assert config.should_retry(mock_response) is True
        
        # Should not retry on non-retryable status codes
        mock_response = type('MockResponse', (), {'status_code': 200})()
        assert config.should_retry(mock_response) is False
        
        # Should retry on connection errors (status_code 0)
        mock_response = type('MockResponse', (), {'status_code': 0})()
        assert config.should_retry(mock_response) is True


class TestDotDict:
    """Test dotdict utility."""
    
    def test_dotdict_initialization(self):
        """Test dotdict initialization."""
        data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        d = dotdict(data)
        
        assert d.a == 1
        assert d.b.c == 2
        assert d.b.d.e == 3
    
    def test_dotdict_attribute_access(self):
        """Test dotdict attribute access."""
        d = dotdict({"key": "value"})
        
        assert d.key == "value"
        assert d["key"] == "value"
        
        with pytest.raises(AttributeError):
            _ = d.nonexistent
    
    def test_dotdict_attribute_setting(self):
        """Test dotdict attribute setting."""
        d = dotdict()
        
        d.key = "value"
        assert d["key"] == "value"
        
        d.nested = {"inner": "value"}
        assert isinstance(d.nested, dotdict)
        assert d.nested.inner == "value"
    
    def test_dotdict_dot_notation_access(self):
        """Test dotdict dot notation access."""
        d = dotdict({"a": {"b": {"c": "value"}}})
        
        assert d["a.b.c"] == "value"
        assert d.get("a.b.c") == "value"
        assert d.get("a.b.nonexistent", "default") == "default"
    
    def test_dotdict_dot_notation_setting(self):
        """Test dotdict dot notation setting."""
        d = dotdict()
        
        d["a.b.c"] = "value"
        assert d.a.b.c == "value"
        
        d["x.y.z"] = "nested"
        assert d.x.y.z == "nested"
    
    def test_dotdict_update(self):
        """Test dotdict update."""
        d = dotdict({"a": 1})
        
        d.update({"b": 2, "c": 3})
        assert d.a == 1
        assert d.b == 2
        assert d.c == 3
        
        d.update(d=4, e=5)
        assert d.d == 4
        assert d.e == 5
    
    def test_dotdict_to_dict(self):
        """Test dotdict to_dict conversion."""
        data = {"a": 1, "b": {"c": 2}}
        d = dotdict(data)
        
        result = d.to_dict()
        assert result == data
        assert isinstance(result, dict)
        assert not isinstance(result["b"], dotdict)
    
    def test_dotdict_copy(self):
        """Test dotdict copy."""
        original = dotdict({"a": 1, "b": {"c": 2}})
        copied = original.copy()
        
        assert copied is not original
        assert copied.a == original.a
        assert copied.b is not original.b  # Should be a new dotdict
    
    def test_dotdict_deepcopy(self):
        """Test dotdict deepcopy."""
        original = dotdict({"a": 1, "b": {"c": 2}})
        deep_copied = original.deepcopy()
        
        assert deep_copied is not original
        assert deep_copied.a == original.a
        assert deep_copied.b is not original.b
        assert deep_copied.b.c == original.b.c
