"""
Base Provider Module

This module provides the abstract base class and common interfaces for
LLM provider implementations. Follows Agent OS production code standards.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from ..core.config import BenchmarkConfig

logger = logging.getLogger(__name__)


@dataclass
class ProviderResponse:
    """Standardized response from LLM provider calls.
    
    :param provider_name: Name of the LLM provider (openai, anthropic)
    :type provider_name: str
    :param operation_id: Unique identifier for this operation
    :type operation_id: int
    :param success: Whether the operation completed successfully
    :type success: bool
    :param latency_ms: Total operation latency in milliseconds
    :type latency_ms: float
    :param tokens_used: Total tokens consumed (input + output)
    :type tokens_used: int
    :param response_text: Generated response text
    :type response_text: str
    :param response_length: Length of response text in characters
    :type response_length: int
    :param model_used: Actual model used for the request
    :type model_used: str
    :param error_message: Error message if operation failed
    :type error_message: Optional[str]
    :param raw_response: Raw provider response for detailed analysis
    :type raw_response: Optional[Any]
    :param span_processing_time_ms: Time spent on span processing
    :type span_processing_time_ms: Optional[float]
    
    Example:
        >>> response = ProviderResponse(
        ...     provider_name="openai",
        ...     operation_id=42,
        ...     success=True,
        ...     latency_ms=1250.5,
        ...     tokens_used=150,
        ...     response_text="Hello, world!"
        ... )
        >>> print(f"{response.provider_name}: {response.latency_ms:.1f}ms")
        openai: 1250.5ms
    """
    provider_name: str
    operation_id: int
    success: bool
    latency_ms: float
    tokens_used: int
    response_text: str
    response_length: int
    model_used: str
    error_message: Optional[str] = None
    raw_response: Optional[Any] = None
    span_processing_time_ms: Optional[float] = None


class BaseProvider(ABC):
    """Abstract base class for LLM provider implementations.
    
    Defines the common interface that all provider implementations must follow
    to ensure consistent behavior and measurement across different LLM services.
    
    :param config: Benchmark configuration parameters
    :type config: BenchmarkConfig
    :param tracer: HoneyHive tracer instance for this provider
    :type tracer: Any
    
    Example:
        >>> class MyProvider(BaseProvider):
        ...     def make_call(self, prompt, operation_id):
        ...         # Implementation here
        ...         pass
        >>> provider = MyProvider(config, tracer)
    """
    
    def __init__(self, config: BenchmarkConfig, tracer: Optional[Any]) -> None:
        """Initialize base provider.
        
        :param config: Benchmark configuration
        :type config: BenchmarkConfig
        :param tracer: HoneyHive tracer instance (None for untraced mode)
        :type tracer: Optional[Any]
        """
        self.config = config
        self.tracer = tracer
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        self.call_count = 0
        self.total_latency = 0.0
        self.total_tokens = 0
        self.error_count = 0
        
        logger.debug(f"🤖 {self.provider_name} provider initialized")
    
    @abstractmethod
    def make_call(self, prompt: str, operation_id: int) -> ProviderResponse:
        """Make a call to the LLM provider.
        
        :param prompt: The prompt to send to the LLM
        :type prompt: str
        :param operation_id: Unique identifier for this operation
        :type operation_id: int
        :return: Standardized provider response
        :rtype: ProviderResponse
        :raises NotImplementedError: Must be implemented by subclasses
        
        Example:
            >>> provider = MyProvider(config, tracer)
            >>> response = provider.make_call("Hello", 42)
            >>> print(f"Success: {response.success}")
        """
        raise NotImplementedError("Subclasses must implement make_call")
    
    @abstractmethod
    def initialize_client(self) -> None:
        """Initialize the provider-specific client.
        
        :raises NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement initialize_client")
    
    @abstractmethod
    def initialize_instrumentor(self) -> None:
        """Initialize the provider-specific instrumentor.
        
        :raises NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement initialize_instrumentor")
    
    @abstractmethod
    def cleanup_instrumentor(self) -> None:
        """Clean up the provider-specific instrumentor.
        
        :raises NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement cleanup_instrumentor")
    
    def record_call_metrics(self, response: ProviderResponse) -> None:
        """Record metrics from a provider call.
        
        :param response: The provider response to record
        :type response: ProviderResponse
        """
        self.call_count += 1
        self.total_latency += response.latency_ms
        self.total_tokens += response.tokens_used
        
        if not response.success:
            self.error_count += 1
        
        logger.debug(
            f"🤖 {self.provider_name} call recorded: "
            f"latency={response.latency_ms:.1f}ms, "
            f"tokens={response.tokens_used}, "
            f"success={response.success}"
        )
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get accumulated statistics for this provider.
        
        :return: Dictionary containing provider statistics
        :rtype: Dict[str, Any]
        
        Example:
            >>> provider = MyProvider(config, tracer)
            >>> # ... make calls ...
            >>> stats = provider.get_provider_statistics()
            >>> print(f"Average latency: {stats['avg_latency_ms']:.1f}ms")
        """
        avg_latency = self.total_latency / max(self.call_count, 1)
        avg_tokens = self.total_tokens / max(self.call_count, 1)
        success_rate = ((self.call_count - self.error_count) / max(self.call_count, 1)) * 100
        
        return {
            'provider_name': self.provider_name,
            'total_calls': self.call_count,
            'total_latency_ms': self.total_latency,
            'total_tokens': self.total_tokens,
            'error_count': self.error_count,
            'avg_latency_ms': avg_latency,
            'avg_tokens_per_call': avg_tokens,
            'success_rate_percent': success_rate,
        }
    
    def reset_statistics(self) -> None:
        """Reset provider statistics counters."""
        self.call_count = 0
        self.total_latency = 0.0
        self.total_tokens = 0
        self.error_count = 0
        logger.debug(f"🤖 {self.provider_name} statistics reset")
    
    def validate_configuration(self) -> bool:
        """Validate provider configuration.
        
        :return: True if configuration is valid
        :rtype: bool
        """
        if not self.config:
            logger.error("No configuration provided")
            return False
        
        if not self.tracer:
            logger.error("No tracer provided")
            return False
        
        return True
    
    def get_model_name(self) -> str:
        """Get the model name for this provider.
        
        :return: Model name from configuration
        :rtype: str
        """
        if self.provider_name == "openai":
            return self.config.openai_model
        elif self.provider_name == "anthropic":
            return self.config.anthropic_model
        else:
            return "unknown"
    
    def create_error_response(self, operation_id: int, error_message: str, latency_ms: float = 0.0) -> ProviderResponse:
        """Create a standardized error response.
        
        :param operation_id: Operation identifier
        :type operation_id: int
        :param error_message: Error description
        :type error_message: str
        :param latency_ms: Time spent before error occurred
        :type latency_ms: float
        :return: Error response object
        :rtype: ProviderResponse
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            operation_id=operation_id,
            success=False,
            latency_ms=latency_ms,
            tokens_used=0,
            response_text="",
            response_length=0,
            model_used=self.get_model_name(),
            error_message=error_message,
        )
    
    def measure_span_processing_time(self) -> float:
        """Measure span processing overhead by timing span creation and attribute setting.
        
        :return: Span processing time in milliseconds
        :rtype: float
        """
        span_start = time.perf_counter()
        
        # Simulate actual span processing work
        # This represents the overhead of creating spans and setting attributes
        dummy_attributes = {
            "honeyhive.event_type": "model",
            "operation.name": "llm_call",
            "model.name": self.get_model_name(),
            "provider": self.provider_name,
            "timestamp": time.time(),
        }
        
        # Simulate attribute processing overhead
        for key, value in dummy_attributes.items():
            _ = f"{key}={value}"  # String formatting overhead
        
        span_end = time.perf_counter()
        
        processing_time_ms = (span_end - span_start) * 1000
        logger.debug(f"🤖 Span processing time: {processing_time_ms:.2f}ms")
        return processing_time_ms
