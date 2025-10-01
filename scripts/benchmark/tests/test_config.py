"""
Unit tests for benchmark configuration module.

Tests the BenchmarkConfig dataclass validation and default values.
"""

import pytest
from ..core.config import BenchmarkConfig


class TestBenchmarkConfig:
    """Test cases for BenchmarkConfig dataclass."""
    
    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        config = BenchmarkConfig()
        
        assert config.operations == 50
        assert config.concurrent_threads == 4
        assert config.warmup_operations == 10
        assert config.openai_model == "gpt-4o"
        assert config.anthropic_model == "claude-sonnet-4-20250514"
        assert config.span_size_mode == "mixed"
        assert config.max_tokens == 100
        assert config.temperature == 0.7
        assert config.timeout == 30.0
        assert config.conversation_mode is True
        assert config.seed is None
        assert config.include_traceloop is False
        assert config.enabled_providers is None
    
    def test_custom_values(self):
        """Test configuration with custom values."""
        config = BenchmarkConfig(
            operations=100,
            concurrent_threads=8,
            openai_model="gpt-3.5-turbo",
            span_size_mode="large",
            include_traceloop=True,
            enabled_providers=["openinference_openai"]
        )
        
        assert config.operations == 100
        assert config.concurrent_threads == 8
        assert config.openai_model == "gpt-3.5-turbo"
        assert config.span_size_mode == "large"
        assert config.include_traceloop is True
        assert config.enabled_providers == ["openinference_openai"]
    
    def test_validation_valid_span_size_mode(self):
        """Test that valid span size modes are accepted."""
        valid_modes = ["small", "medium", "large", "mixed"]
        
        for mode in valid_modes:
            config = BenchmarkConfig(span_size_mode=mode)
            # Should not raise an exception
            config.__post_init__()
    
    def test_validation_invalid_span_size_mode(self):
        """Test that invalid span size modes raise ValueError."""
        with pytest.raises(ValueError, match="span_size_mode must be one of"):
            config = BenchmarkConfig(span_size_mode="invalid")
            config.__post_init__()
    
    def test_validation_negative_operations(self):
        """Test that negative operations raise ValueError."""
        with pytest.raises(ValueError, match="operations must be positive"):
            config = BenchmarkConfig(operations=-1)
            config.__post_init__()
    
    def test_validation_zero_operations(self):
        """Test that zero operations raise ValueError."""
        with pytest.raises(ValueError, match="operations must be positive"):
            config = BenchmarkConfig(operations=0)
            config.__post_init__()
    
    def test_validation_negative_threads(self):
        """Test that negative concurrent threads raise ValueError."""
        with pytest.raises(ValueError, match="concurrent_threads must be positive"):
            config = BenchmarkConfig(concurrent_threads=-1)
            config.__post_init__()
    
    def test_validation_zero_threads(self):
        """Test that zero concurrent threads raise ValueError."""
        with pytest.raises(ValueError, match="concurrent_threads must be positive"):
            config = BenchmarkConfig(concurrent_threads=0)
            config.__post_init__()
    
    def test_validation_negative_warmup(self):
        """Test that negative warmup operations raise ValueError."""
        with pytest.raises(ValueError, match="warmup_operations must be non-negative"):
            config = BenchmarkConfig(warmup_operations=-1)
            config.__post_init__()
    
    def test_validation_zero_warmup_allowed(self):
        """Test that zero warmup operations are allowed."""
        config = BenchmarkConfig(warmup_operations=0)
        # Should not raise an exception
        config.__post_init__()
