"""
OpenInference OpenAI Provider Module

This module provides OpenInference OpenAI-specific implementation for tracer 
performance benchmarks using OpenInference semantic conventions. 
Follows Agent OS production code standards.
"""

import logging
import os
import time
from typing import Optional, Any
import openai
import httpx
from openinference.instrumentation.openai import OpenAIInstrumentor

from .base_provider import BaseProvider, ProviderResponse
from ..core.config import BenchmarkConfig

logger = logging.getLogger(__name__)


class OpenInferenceOpenAIProvider(BaseProvider):
    """OpenInference OpenAI provider implementation for benchmark testing.
    
    Handles OpenAI-specific API calls using OpenInference instrumentors for
    tracer performance benchmarks. Automatically instruments OpenAI calls
    with HoneyHive tracing via OpenInference semantic conventions.
    
    :param config: Benchmark configuration parameters
    :type config: BenchmarkConfig
    :param tracer: HoneyHive tracer instance for OpenAI
    :type tracer: Any
    
    Example:
        >>> provider = OpenAIProvider(config, tracer)
        >>> provider.initialize_client()
        >>> provider.initialize_instrumentor()
        >>> response = provider.make_call("Hello", 42)
        >>> print(f"OpenAI response: {response.response_text}")
    """
    
    def __init__(self, config: BenchmarkConfig, tracer: Any) -> None:
        """Initialize OpenAI provider.
        
        :param config: Benchmark configuration
        :type config: BenchmarkConfig
        :param tracer: HoneyHive tracer instance
        :type tracer: Any
        """
        super().__init__(config, tracer)
        self.client: Optional[openai.OpenAI] = None
        self.instrumentor: Optional[OpenAIInstrumentor] = None
        self.network_analyzer = None  # Will be set by subprocess
        
        logger.debug("🤖 OpenInference OpenAI provider initialized")
    
    def initialize_client(self) -> None:
        """Initialize OpenAI client with API key and connection pooling."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Create httpx client with connection pooling for reduced latency variability
        # Configuration based on HoneyHive SDK's optimized connection pooling
        http_client = httpx.Client(
            limits=httpx.Limits(
                max_connections=16,      # Total connection pool size
                max_keepalive_connections=12,  # Keep-alive connections
                keepalive_expiry=30.0    # Keep connections alive for 30s
            ),
            timeout=httpx.Timeout(
                connect=10.0,            # Connection timeout
                read=30.0,               # Read timeout
                write=10.0,              # Write timeout
                pool=5.0                 # Pool acquisition timeout
            ),
            follow_redirects=True
            # Note: HTTP/2 disabled to avoid h2 dependency requirement
        )
        
        self.client = openai.OpenAI(
            api_key=api_key,
            http_client=http_client
        )
        logger.debug("✅ OpenInference OpenAI client initialized with connection pooling (16 max connections, 12 keepalive)")
    
    def initialize_instrumentor(self) -> None:
        """Initialize OpenAI instrumentor with HoneyHive tracer."""
        if not self.tracer:
            logger.debug("🚫 No tracer provided - skipping instrumentation (untraced mode)")
            return
        
        self.instrumentor = OpenAIInstrumentor()
        self.instrumentor.instrument(tracer_provider=self.tracer.provider)
        logger.debug("✅ OpenInference OpenAI instrumentor initialized with HoneyHive tracer")
    
    def cleanup_instrumentor(self) -> None:
        """Clean up OpenAI instrumentor."""
        if self.instrumentor:
            self.instrumentor.uninstrument()
            logger.debug("🧹 OpenInference OpenAI instrumentor cleaned up")
    
    def set_network_analyzer(self, network_analyzer) -> None:
        """Set the network analyzer for this provider instance.
        
        :param network_analyzer: NetworkIOAnalyzer instance
        :type network_analyzer: NetworkIOAnalyzer
        """
        self.network_analyzer = network_analyzer
        logger.debug(f"🌐 Network analyzer set on provider: {network_analyzer is not None}")
    
    def make_call(self, prompt: str, operation_id: int, network_analyzer=None) -> ProviderResponse:
        """Make an OpenAI API call with tracing and performance measurement.
        
        :param prompt: The prompt to send to OpenAI
        :type prompt: str
        :param operation_id: Unique identifier for this operation
        :type operation_id: int
        :param network_analyzer: Optional NetworkIOAnalyzer for tracking network I/O
        :type network_analyzer: Optional[NetworkIOAnalyzer]
        :return: Standardized provider response
        :rtype: ProviderResponse
        
        Example:
            >>> provider = OpenAIProvider(config, tracer)
            >>> provider.initialize_client()
            >>> response = provider.make_call("Explain AI", 42)
            >>> print(f"Tokens used: {response.tokens_used}")
        """
        # Use instance network analyzer (set by subprocess) or parameter fallback
        active_network_analyzer = self.network_analyzer or network_analyzer
        logger.debug(f"🌐 make_call using network_analyzer: {active_network_analyzer is not None} (instance: {self.network_analyzer is not None}, param: {network_analyzer is not None})")
        
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        start_time = time.perf_counter()
        
        try:
            # Measure span processing time
            span_processing_time_ms = self.measure_span_processing_time()
            
            # Make the API call - automatically instrumented by OpenAIInstrumentor
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.timeout,
            )
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract response data
            response_text = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Record network I/O for analysis if analyzer provided
            if active_network_analyzer:
                request_size, response_size = active_network_analyzer.estimate_llm_payload_sizes(
                    prompt=prompt,
                    response=response_text,
                    model=self.config.openai_model
                )
                active_network_analyzer.record_llm_operation(
                    request_size_bytes=request_size,
                    response_size_bytes=response_size,
                    latency_ms=latency_ms
                )
                logger.debug(f"🌐 Recorded LLM network I/O: req={request_size}B, resp={response_size}B, latency={latency_ms:.1f}ms")
            else:
                logger.debug("🌐 No network analyzer available for make_call")
            
            # Create standardized response
            provider_response = ProviderResponse(
                provider_name="openinference_openai",
                operation_id=operation_id,
                success=True,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                response_text=response_text,
                response_length=len(response_text),
                model_used=self.config.openai_model,
                raw_response=response,
                span_processing_time_ms=span_processing_time_ms,
            )
            
            # Record metrics
            self.record_call_metrics(provider_response)
            
            logger.debug(
                f"🤖 OpenInference OpenAI call completed: op_id={operation_id}, "
                f"latency={latency_ms:.1f}ms, tokens={tokens_used}"
            )
            
            return provider_response
            
        except openai.APITimeoutError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            error_msg = f"OpenInference OpenAI API timeout: {str(e)}"
            logger.error(error_msg)
            
            error_response = self.create_error_response(operation_id, error_msg, latency_ms)
            self.record_call_metrics(error_response)
            return error_response
            
        except openai.RateLimitError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            error_msg = f"OpenInference OpenAI rate limit exceeded: {str(e)}"
            logger.error(error_msg)
            
            error_response = self.create_error_response(operation_id, error_msg, latency_ms)
            self.record_call_metrics(error_response)
            return error_response
            
        except openai.APIError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            error_msg = f"OpenInference OpenAI API error: {str(e)}"
            logger.error(error_msg)
            
            error_response = self.create_error_response(operation_id, error_msg, latency_ms)
            self.record_call_metrics(error_response)
            return error_response
            
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            error_msg = f"Unexpected OpenInference OpenAI error: {str(e)}"
            logger.error(error_msg)
            
            error_response = self.create_error_response(operation_id, error_msg, latency_ms)
            self.record_call_metrics(error_response)
            return error_response
    
    def validate_configuration(self) -> bool:
        """Validate OpenAI-specific configuration.
        
        :return: True if configuration is valid
        :rtype: bool
        """
        if not super().validate_configuration():
            return False
        
        # Check OpenAI-specific configuration
        if not self.config.openai_model:
            logger.error("No OpenInference OpenAI model specified in configuration")
            return False
        
        # Check API key
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable not set")
            return False
        
        return True
    
    def get_provider_info(self) -> dict[str, Any]:
        """Get OpenAI provider information.
        
        :return: Dictionary with provider details
        :rtype: dict[str, Any]
        """
        return {
            'provider_name': 'openai',
            'model': self.config.openai_model,
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature,
            'timeout': self.config.timeout,
            'client_initialized': self.client is not None,
            'instrumentor_initialized': self.instrumentor is not None,
        }
    
    def test_connection(self) -> bool:
        """Test connection to OpenAI API.
        
        :return: True if connection successful
        :rtype: bool
        """
        if not self.client:
            logger.error("OpenInference OpenAI client not initialized")
            return False
        
        try:
            # Make a simple test call
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
                timeout=10.0,
            )
            
            logger.debug("✅ OpenInference OpenAI connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenInference OpenAI connection test failed: {e}")
            return False
