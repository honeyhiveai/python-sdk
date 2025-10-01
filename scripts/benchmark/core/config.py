"""
Benchmark Configuration Module

This module provides configuration dataclasses for the HoneyHive tracer
performance benchmark suite, following Agent OS production code standards.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class BenchmarkConfig:
    """Configuration parameters for tracer performance benchmarks.
    
    This dataclass encapsulates all configuration options for running
    comprehensive performance benchmarks across multiple LLM providers.
    
    :param operations: Number of operations to perform per provider per mode
    :type operations: int
    :param warmup_operations: Number of warmup operations before benchmarking
    :type warmup_operations: int
    :param concurrent_threads: Number of concurrent threads for parallel testing
    :type concurrent_threads: int
    :param openai_model: OpenAI model identifier for testing
    :type openai_model: str
    :param anthropic_model: Anthropic model identifier for testing
    :type anthropic_model: str
    :param max_tokens: Maximum tokens per API response
    :type max_tokens: int
    :param temperature: Temperature parameter for LLM responses
    :type temperature: float
    :param timeout: Request timeout in seconds
    :type timeout: float
    :param verbose: Enable verbose logging output
    :type verbose: bool
    :param span_size_mode: Span size testing mode (small/medium/large/mixed)
    :type span_size_mode: str
    :param conversation_mode: Enable conversation simulation
    :type conversation_mode: bool
    :param seed: Random seed for deterministic testing
    :type seed: Optional[int]
    
    Example:
        >>> config = BenchmarkConfig(
        ...     operations=50,
        ...     openai_model="gpt-4o",
        ...     anthropic_model="claude-sonnet-4-20250514"
        ... )
        >>> print(f"Testing {config.operations} operations per provider")
        Testing 50 operations per provider
    """
    
    # Core benchmark parameters
    operations: int = 50
    warmup_operations: int = 10
    concurrent_threads: int = 4
    
    # LLM model configuration
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 10000  # Will be overridden by dynamic detection
    temperature: float = 0.7
    timeout: float = 30.0
    
    # Output and debugging
    verbose: bool = False
    
    # Advanced testing features
    span_size_mode: str = "mixed"  # small, medium, large, mixed
    conversation_mode: bool = True
    seed: Optional[int] = None
    include_traceloop: bool = False  # Include Traceloop instrumentors for comparison
    enabled_providers: Optional[List[str]] = None  # Specific providers to enable (None = all available)
    
    def __post_init__(self) -> None:
        """Validate configuration parameters after initialization.
        
        :raises ValueError: If any configuration parameter is invalid
        """
        if self.operations <= 0:
            raise ValueError("operations must be positive")
        if self.warmup_operations < 0:
            raise ValueError("warmup_operations must be non-negative")
        if self.concurrent_threads <= 0:
            raise ValueError("concurrent_threads must be positive")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.span_size_mode not in ["small", "medium", "large", "mixed"]:
            raise ValueError("span_size_mode must be one of: small, medium, large, mixed")
