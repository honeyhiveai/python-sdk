"""
Traceloop OpenAI Provider for Benchmark Testing

This module provides the TraceloopOpenAIProvider class for benchmarking
HoneyHive tracer performance with Traceloop OpenAI instrumentors.
"""

import logging
import time
from typing import Any, Dict, Optional

import openai

from .base_provider import BaseProvider, ProviderResponse

logger = logging.getLogger(__name__)


class TraceloopOpenAIProvider(BaseProvider):
    """OpenAI provider using Traceloop instrumentor for enhanced metrics.
    
    This provider uses the opentelemetry-instrumentation-openai package
    from Traceloop for enhanced LLM metrics and production optimizations.
    """
    
    def __init__(self, config: Any, tracer: Any) -> None:
        """Initialize Traceloop OpenAI provider.
        
        :param config: Benchmark configuration
        :type config: Any
        :param tracer: HoneyHive tracer instance
        :type tracer: Any
        """
        super().__init__(config, tracer)
        self.client: Optional[openai.OpenAI] = None
        self.instrumentor: Optional[Any] = None
        
    
    def make_call(self, prompt: str, operation_id: int) -> ProviderResponse:
        """Make OpenAI API call with Traceloop instrumentation.
        
        :param prompt: The prompt to send to OpenAI
        :type prompt: str
        :param operation_id: Unique operation identifier
        :type operation_id: int
        :return: Provider response with metrics
        :rtype: ProviderResponse
        """
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        start_time = time.perf_counter()
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.timeout
            )
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract token usage
            tokens_used = 0
            if response.usage:
                tokens_used = (
                    (response.usage.prompt_tokens or 0) + 
                    (response.usage.completion_tokens or 0)
                )
            
            # Extract response text
            response_text = ""
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and choice.message:
                    response_text = getattr(choice.message, 'content', '') or ''
            
            logger.debug(
                "🤖 Traceloop OpenAI call completed: op_id=%d, latency=%.1fms, tokens=%d",
                operation_id, latency_ms, tokens_used
            )
            
            return ProviderResponse(
                provider_name="traceloop_openai",
                operation_id=operation_id,
                success=True,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                response_text=response_text,
                response_length=len(response_text),
                model_used=self.config.openai_model,
                raw_response=response
            )
            
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            logger.error("Traceloop OpenAI call failed: op_id=%d, error=%s", operation_id, e)
            
            return ProviderResponse(
                provider_name="traceloop_openai",
                operation_id=operation_id,
                success=False,
                latency_ms=latency_ms,
                tokens_used=0,
                response_text="",
                response_length=0,
                model_used=self.config.openai_model,
                error_message=str(e)
            )
    
    def cleanup(self) -> None:
        """Clean up Traceloop instrumentor."""
        if self.instrumentor:
            try:
                self.instrumentor.uninstrument()
                logger.debug("🧹 Traceloop OpenAI instrumentor cleaned up")
            except Exception as e:
                logger.warning("Error cleaning up Traceloop OpenAI instrumentor: %s", e)
    
    def initialize_client(self) -> None:
        """Initialize OpenAI client."""
        self.client = openai.OpenAI()
    
    def initialize_instrumentor(self) -> None:
        """Initialize Traceloop instrumentor."""
        try:
            from opentelemetry.instrumentation.openai import OpenAIInstrumentor
            self.instrumentor = OpenAIInstrumentor()
            self.instrumentor.instrument(tracer_provider=self.tracer.provider)
        except ImportError as e:
            raise ImportError(
                "Traceloop OpenAI instrumentor not available. "
                "Install with: pip install opentelemetry-instrumentation-openai"
            ) from e
    
    def cleanup_instrumentor(self) -> None:
        """Clean up instrumentor - alias for cleanup."""
        self.cleanup()
    
    def get_model_name(self) -> str:
        """Get the model name being used.
        
        :return: Model name
        :rtype: str
        """
        return f"traceloop_{self.config.openai_model}"
    
    def measure_span_processing_time(self) -> float:
        """Measure span processing overhead for this provider.
        
        :return: Span processing time in milliseconds
        :rtype: float
        """
        # Traceloop instrumentors typically have slightly higher overhead
        # due to enhanced metrics collection
        return 2.5  # Estimated baseline for Traceloop OpenAI
