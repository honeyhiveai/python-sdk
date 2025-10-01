"""
Anthropic Provider Module

Handles Anthropic API calls with optional instrumentation support.
Supports multiple instrumentors (OpenInference, Traceloop) and A/B testing.
Uses the universal instrumentor interface following documented patterns.
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional, Any, Dict

import anthropic
from .universal_instrumentor import UniversalInstrumentor

logger = logging.getLogger(__name__)


@dataclass
class AnthropicResponse:
    """Response from Anthropic API call."""
    success: bool
    latency_ms: float
    tokens_used: int
    response_text: str
    model_used: str
    error_message: Optional[str] = None
    raw_response: Optional[Any] = None


class AnthropicProvider:
    """Anthropic provider with universal instrumentation support.
    
    Follows the documented pattern:
    - Traced workloads (default): Uses UniversalInstrumentor
    - Untraced workloads (A/B testing): Pure Anthropic client
    
    Supports all instrumentor types seamlessly.
    """
    
    def __init__(self, model: str = "claude-sonnet-4-20250514", instrumentor_type: Optional[str] = None, project: Optional[str] = None, enable_tracing: bool = True):
        """Initialize Anthropic provider.
        
        :param model: Anthropic model to use
        :param instrumentor_type: Type of instrumentor ("openinference", "traceloop", None)
        :param project: HoneyHive project name
        :param enable_tracing: Whether to enable tracing (False for A/B testing)
        """
        self.model = model
        self.client = None
        self.instrumentor = None
        self.network_analyzer = None  # For network analysis integration
        
        # Initialize client
        self._initialize_client()
        
        # Initialize instrumentation using universal interface
        if instrumentor_type and enable_tracing:
            self.instrumentor = UniversalInstrumentor(
                instrumentor_type=instrumentor_type,
                provider_type="anthropic",
                project=project,
                enable_tracing=enable_tracing
            )
    
    def _initialize_client(self) -> None:
        """Initialize Anthropic client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.debug(f"✅ Anthropic client initialized (model: {self.model})")
    
    def is_traced(self) -> bool:
        """Check if this provider is currently traced.
        
        :return: True if tracing is active
        """
        return self.instrumentor is not None and self.instrumentor.is_traced()
    
    def get_tracer(self) -> Optional[Any]:
        """Get the HoneyHive tracer instance.
        
        :return: Tracer instance or None if not traced
        """
        return self.instrumentor.get_tracer() if self.instrumentor else None
    
    def set_network_analyzer(self, network_analyzer) -> None:
        """Set the network analyzer for this provider instance.
        
        :param network_analyzer: NetworkIOAnalyzer instance
        :type network_analyzer: NetworkIOAnalyzer
        """
        self.network_analyzer = network_analyzer
        logger.debug(f"🌐 Network analyzer set on provider: {network_analyzer is not None}")
    
    def make_call(self, prompt: str, operation_id: int, max_tokens: int = 500, temperature: float = 0.1, network_analyzer=None) -> AnthropicResponse:
        """Make Anthropic API call with optional tracing and network analysis.
        
        :param prompt: Input prompt
        :param operation_id: Unique operation identifier
        :param max_tokens: Maximum tokens to generate
        :param temperature: Sampling temperature
        :param network_analyzer: Optional NetworkIOAnalyzer for tracking LLM network I/O
        :return: Response with timing and token information
        """
        # Use instance network analyzer (set by AB testing harness) or parameter fallback
        active_network_analyzer = self.network_analyzer or network_analyzer
        logger.debug(f"🌐 make_call using network_analyzer: {active_network_analyzer is not None} (instance: {self.network_analyzer is not None}, param: {network_analyzer is not None})")
        
        start_time = time.perf_counter()
        
        try:
            # Make the API call (instrumentation happens automatically if enabled)
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract response data
            response_text = ""
            if response.content and len(response.content) > 0:
                response_text = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            
            tokens_used = getattr(response.usage, 'input_tokens', 0) + getattr(response.usage, 'output_tokens', 0) if response.usage else 0
            
            # Record network I/O for analysis if analyzer provided
            if active_network_analyzer:
                request_size, response_size = active_network_analyzer.estimate_llm_payload_sizes(
                    prompt=prompt,
                    response=response_text,
                    model=self.model
                )
                active_network_analyzer.record_llm_operation(
                    request_size_bytes=request_size,
                    response_size_bytes=response_size,
                    latency_ms=latency_ms
                )
                logger.debug(f"🌐 Recorded LLM network I/O: req={request_size}B, resp={response_size}B, latency={latency_ms:.1f}ms")
            else:
                logger.debug("🌐 No network analyzer available for make_call")
            
            logger.debug(f"✅ Anthropic call completed (op_id={operation_id}, {latency_ms:.1f}ms, {tokens_used} tokens)")
            
            return AnthropicResponse(
                success=True,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                response_text=response_text,
                model_used=self.model,
                raw_response=response
            )
            
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            logger.error(f"❌ Anthropic call failed (op_id={operation_id}): {e}")
            
            return AnthropicResponse(
                success=False,
                latency_ms=latency_ms,
                tokens_used=0,
                response_text="",
                model_used=self.model,
                error_message=str(e)
            )
    
    def cleanup(self) -> None:
        """Clean up instrumentation."""
        if self.instrumentor:
            self.instrumentor.cleanup()
            logger.debug("🧹 Anthropic instrumentation cleaned up")


# Factory functions for easy A/B testing and setup
def create_untraced_anthropic(model: str = "claude-sonnet-4-20250514") -> AnthropicProvider:
    """Create untraced Anthropic provider for A/B testing."""
    return AnthropicProvider(model=model, instrumentor_type=None, enable_tracing=False)


def create_openinference_anthropic(model: str = "claude-sonnet-4-20250514", project: Optional[str] = None) -> AnthropicProvider:
    """Create OpenInference-instrumented Anthropic provider."""
    return AnthropicProvider(model=model, instrumentor_type="openinference", project=project, enable_tracing=True)


def create_traceloop_anthropic(model: str = "claude-sonnet-4-20250514", project: Optional[str] = None) -> AnthropicProvider:
    """Create Traceloop-instrumented Anthropic provider."""
    return AnthropicProvider(model=model, instrumentor_type="traceloop", project=project, enable_tracing=True)


# Convenience functions matching documentation examples
def setup_anthropic_tracing(instrumentor: str = "openinference", model: str = "claude-sonnet-4-20250514", project: Optional[str] = None) -> AnthropicProvider:
    """Set up Anthropic tracing following documentation patterns.
    
    :param instrumentor: Instrumentor type ("openinference" or "traceloop")
    :param model: Anthropic model to use
    :param project: HoneyHive project name
    :return: Configured Anthropic provider with tracing
    """
    return AnthropicProvider(model=model, instrumentor_type=instrumentor, project=project, enable_tracing=True)
