"""
OpenAI Provider Module

Handles OpenAI API calls with optional instrumentation support.
Supports multiple instrumentors (OpenInference, Traceloop) and A/B testing.
Uses the universal instrumentor interface following documented patterns.
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional, Any, Dict

import openai
from .universal_instrumentor import UniversalInstrumentor

logger = logging.getLogger(__name__)


@dataclass
class OpenAIResponse:
    """Response from OpenAI API call."""
    success: bool
    latency_ms: float
    tokens_used: int
    response_text: str
    model_used: str
    error_message: Optional[str] = None
    raw_response: Optional[Any] = None


class OpenAIProvider:
    """OpenAI provider with universal instrumentation support.
    
    Follows the documented pattern:
    - Traced workloads (default): Uses UniversalInstrumentor
    - Untraced workloads (A/B testing): Pure OpenAI client
    
    Supports all instrumentor types seamlessly.
    """
    
    def __init__(self, model: str = "gpt-4o", instrumentor_type: Optional[str] = None, project: Optional[str] = None, enable_tracing: bool = True):
        """Initialize OpenAI provider.
        
        :param model: OpenAI model to use
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
                provider_type="openai",
                project=project,
                enable_tracing=enable_tracing
            )
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = openai.OpenAI(api_key=api_key)
        logger.debug(f"✅ OpenAI client initialized (model: {self.model})")
    
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
    
    def make_call(self, prompt: str, operation_id: int, max_tokens: int = 500, temperature: float = 0.1, network_analyzer=None) -> OpenAIResponse:
        """Make OpenAI API call with optional tracing and network analysis.
        
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract response data
            response_text = response.choices[0].message.content or ""
            tokens_used = getattr(response.usage, 'total_tokens', 0) if response.usage else 0
            
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
            
            logger.debug(f"✅ OpenAI call completed (op_id={operation_id}, {latency_ms:.1f}ms, {tokens_used} tokens)")
            
            return OpenAIResponse(
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
            
            logger.error(f"❌ OpenAI call failed (op_id={operation_id}): {e}")
            
            return OpenAIResponse(
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
            logger.debug("🧹 OpenAI instrumentation cleaned up")


# Factory functions for easy A/B testing and setup
def create_untraced_openai(model: str = "gpt-4o") -> OpenAIProvider:
    """Create untraced OpenAI provider for A/B testing."""
    return OpenAIProvider(model=model, instrumentor_type=None, enable_tracing=False)


def create_openinference_openai(model: str = "gpt-4o", project: Optional[str] = None) -> OpenAIProvider:
    """Create OpenInference-instrumented OpenAI provider."""
    return OpenAIProvider(model=model, instrumentor_type="openinference", project=project, enable_tracing=True)


def create_traceloop_openai(model: str = "gpt-4o", project: Optional[str] = None) -> OpenAIProvider:
    """Create Traceloop-instrumented OpenAI provider."""
    return OpenAIProvider(model=model, instrumentor_type="traceloop", project=project, enable_tracing=True)


# Convenience functions matching documentation examples
def setup_openai_tracing(instrumentor: str = "openinference", model: str = "gpt-4o", project: Optional[str] = None) -> OpenAIProvider:
    """Set up OpenAI tracing following documentation patterns.
    
    :param instrumentor: Instrumentor type ("openinference" or "traceloop")
    :param model: OpenAI model to use
    :param project: HoneyHive project name
    :return: Configured OpenAI provider with tracing
    """
    return OpenAIProvider(model=model, instrumentor_type=instrumentor, project=project, enable_tracing=True)
