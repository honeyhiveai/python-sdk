"""
OpenLit OpenAI Provider Module

Provider implementation for OpenLit instrumentor with OpenAI, capturing
OpenLit-specific semantic conventions and attribute formats.
"""

import logging
import os
import time
from typing import Optional, Any
import openai
import httpx

from .base_provider import BaseProvider, ProviderResponse
from ..core.config import BenchmarkConfig

logger = logging.getLogger(__name__)


class OpenLitOpenAIProvider(BaseProvider):
    """OpenLit OpenAI provider implementation for benchmark testing.
    
    Handles OpenAI API calls using OpenLit instrumentor to capture
    OpenLit-specific semantic conventions and attribute formats.
    
    :param config: Benchmark configuration parameters
    :type config: BenchmarkConfig
    :param tracer: HoneyHive tracer instance for OpenAI
    :type tracer: Any
    
    Example:
        >>> provider = OpenLitOpenAIProvider(config, tracer)
        >>> provider.initialize_client()
        >>> provider.initialize_instrumentor()
        >>> response = provider.make_call("Hello", 42)
    """
    
    def __init__(self, config: BenchmarkConfig, tracer: Any) -> None:
        """Initialize OpenLit OpenAI provider.
        
        :param config: Benchmark configuration
        :type config: BenchmarkConfig
        :param tracer: HoneyHive tracer instance
        :type tracer: Any
        """
        super().__init__(config, tracer)
        self.client: Optional[openai.OpenAI] = None
        self.instrumentor: Optional[Any] = None
        self.network_analyzer = None
        
        logger.debug("🔥 OpenLit OpenAI provider initialized")
    
    def initialize_client(self) -> None:
        """Initialize OpenAI client with API key and connection pooling."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        http_client = httpx.Client(
            limits=httpx.Limits(
                max_connections=16,
                max_keepalive_connections=12,
                keepalive_expiry=30.0
            ),
            timeout=httpx.Timeout(
                connect=10.0,
                read=30.0,
                write=10.0,
                pool=5.0
            ),
            follow_redirects=True
        )
        
        self.client = openai.OpenAI(
            api_key=api_key,
            http_client=http_client
        )
        logger.debug("✅ OpenLit OpenAI client initialized")
    
    def initialize_instrumentor(self) -> None:
        """Initialize OpenLit instrumentor with HoneyHive tracer."""
        if not self.tracer:
            logger.debug("🚫 No tracer provided - skipping instrumentation")
            return
        
        try:
            # Import OpenLit instrumentor
            import openlit
            
            # Initialize OpenLit with HoneyHive tracer provider
            openlit.init(
                otlp_endpoint=None,  # Don't send to OpenLit backend
                tracer_provider=self.tracer.provider  # Use HoneyHive's provider
            )
            
            self.instrumentor = openlit  # Store reference
            logger.debug("✅ OpenLit instrumentor initialized with HoneyHive tracer")
            
        except ImportError:
            logger.warning(
                "⚠️  OpenLit not installed - install with: pip install openlit"
            )
            raise
    
    def cleanup_instrumentor(self) -> None:
        """Clean up OpenLit instrumentor."""
        if self.instrumentor:
            # OpenLit doesn't have explicit uninstrumentation
            logger.debug("🧹 OpenLit instrumentor cleanup (no-op)")
    
    def set_network_analyzer(self, network_analyzer) -> None:
        """Set the network analyzer for this provider instance.
        
        :param network_analyzer: NetworkIOAnalyzer instance
        :type network_analyzer: NetworkIOAnalyzer
        """
        self.network_analyzer = network_analyzer
        logger.debug(f"🌐 Network analyzer set on OpenLit provider: {network_analyzer is not None}")
    
    def make_call(
        self,
        prompt: str,
        operation_id: int,
        network_analyzer=None
    ) -> ProviderResponse:
        """Make an OpenAI API call with OpenLit tracing.
        
        :param prompt: The prompt to send to OpenAI
        :type prompt: str
        :param operation_id: Unique identifier for this operation
        :type operation_id: int
        :param network_analyzer: Optional NetworkIOAnalyzer
        :type network_analyzer: Optional[NetworkIOAnalyzer]
        :return: Standardized provider response
        :rtype: ProviderResponse
        """
        active_network_analyzer = self.network_analyzer or network_analyzer
        
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        start_time = time.perf_counter()
        
        try:
            span_processing_time_ms = self.measure_span_processing_time()
            
            # Make the API call - automatically instrumented by OpenLit
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
            
            response_text = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Record network I/O
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
            
            provider_response = ProviderResponse(
                provider_name="openlit_openai",
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
            
            self.record_call_metrics(provider_response)
            
            logger.debug(
                f"🔥 OpenLit OpenAI call completed: op_id={operation_id}, "
                f"latency={latency_ms:.1f}ms, tokens={tokens_used}"
            )
            
            return provider_response
            
        except openai.APITimeoutError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            error_msg = f"OpenLit OpenAI API timeout: {str(e)}"
            logger.error(error_msg)
            
            error_response = self.create_error_response(operation_id, error_msg, latency_ms)
            self.record_call_metrics(error_response)
            return error_response
            
        except openai.RateLimitError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            error_msg = f"OpenLit OpenAI rate limit exceeded: {str(e)}"
            logger.error(error_msg)
            
            error_response = self.create_error_response(operation_id, error_msg, latency_ms)
            self.record_call_metrics(error_response)
            return error_response
            
        except openai.APIError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            error_msg = f"OpenLit OpenAI API error: {str(e)}"
            logger.error(error_msg)
            
            error_response = self.create_error_response(operation_id, error_msg, latency_ms)
            self.record_call_metrics(error_response)
            return error_response
            
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            error_msg = f"Unexpected OpenLit OpenAI error: {str(e)}"
            logger.error(error_msg)
            
            error_response = self.create_error_response(operation_id, error_msg, latency_ms)
            self.record_call_metrics(error_response)
            return error_response
    
    def validate_configuration(self) -> bool:
        """Validate OpenLit OpenAI configuration.
        
        :return: True if configuration is valid
        :rtype: bool
        """
        if not super().validate_configuration():
            return False
        
        if not self.config.openai_model:
            logger.error("No OpenAI model specified in configuration")
            return False
        
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable not set")
            return False
        
        return True
    
    def get_provider_info(self) -> dict[str, Any]:
        """Get OpenLit OpenAI provider information.
        
        :return: Dictionary with provider details
        :rtype: dict[str, Any]
        """
        return {
            'provider_name': 'openlit_openai',
            'model': self.config.openai_model,
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature,
            'timeout': self.config.timeout,
            'client_initialized': self.client is not None,
            'instrumentor_initialized': self.instrumentor is not None,
        }
    
    def test_connection(self) -> bool:
        """Test connection to OpenAI API with OpenLit instrumentation.
        
        :return: True if connection successful
        :rtype: bool
        """
        if not self.client:
            logger.error("OpenLit OpenAI client not initialized")
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
                timeout=10.0,
            )
            
            logger.debug("✅ OpenLit OpenAI connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenLit OpenAI connection test failed: {e}")
            return False
