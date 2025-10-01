"""
Universal Instrumentor Interface

Provides a consistent interface for all instrumentors following the documented pattern:
1. HoneyHiveTracer.init() 
2. instrumentor.instrument(tracer_provider=tracer.provider)
3. Use LLM client normally (automatically traced)

Supports A/B testing by allowing traced vs untraced modes.
"""

import logging
import os
from typing import Optional, Any, Dict, Union

logger = logging.getLogger(__name__)


class UniversalInstrumentor:
    """Universal instrumentor interface for seamless tracing across all LLM providers.
    
    Follows the documented pattern:
    - Traced workloads (default): Initialize tracer + instrumentor
    - Untraced workloads (A/B testing): Skip instrumentation
    
    Supports all instrumentor types: OpenInference, Traceloop, etc.
    """
    
    def __init__(self, 
                 instrumentor_type: str,
                 provider_type: str,
                 project: Optional[str] = None,
                 enable_tracing: bool = True):
        """Initialize universal instrumentor.
        
        :param instrumentor_type: Type of instrumentor ("openinference", "traceloop")
        :param provider_type: LLM provider ("openai", "anthropic", "bedrock", etc.)
        :param project: HoneyHive project name (uses HH_PROJECT env var if None)
        :param enable_tracing: Whether to enable tracing (False for A/B testing untraced workloads)
        """
        self.instrumentor_type = instrumentor_type.lower()
        self.provider_type = provider_type.lower()
        self.project = project or os.getenv("HH_PROJECT", f"benchmark-{self.provider_type}")
        self.enable_tracing = enable_tracing
        
        self.tracer = None
        self.instrumentor = None
        
        # Initialize tracing if enabled
        if self.enable_tracing:
            self._initialize_tracing()
    
    def _initialize_tracing(self) -> None:
        """Initialize tracing following the universal pattern from docs."""
        try:
            # Step 1: Initialize HoneyHive tracer first (without instrumentors)
            from honeyhive import HoneyHiveTracer
            
            self.tracer = HoneyHiveTracer.init(
                project=self.project  # Uses HH_API_KEY from environment
            )
            
            logger.debug(f"✅ HoneyHive tracer initialized (project: {self.project})")
            
            # Step 2: Initialize instrumentor separately with tracer_provider
            self._initialize_instrumentor()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize tracing: {e}")
            self.tracer = None
            self.instrumentor = None
    
    def _initialize_instrumentor(self) -> None:
        """Initialize the specific instrumentor based on type and provider."""
        if not self.tracer:
            logger.warning("⚠️ No tracer available for instrumentation")
            return
        
        try:
            if self.instrumentor_type == "openinference":
                self._initialize_openinference()
            elif self.instrumentor_type == "traceloop":
                self._initialize_traceloop()
            else:
                logger.error(f"❌ Unknown instrumentor type: {self.instrumentor_type}")
        
        except ImportError as e:
            logger.error(f"❌ {self.instrumentor_type} not available for {self.provider_type}: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.instrumentor_type} instrumentor: {e}")
    
    def _initialize_openinference(self) -> None:
        """Initialize OpenInference instrumentor for the specific provider."""
        if self.provider_type == "openai":
            from openinference.instrumentation.openai import OpenAIInstrumentor
            self.instrumentor = OpenAIInstrumentor()
        elif self.provider_type == "anthropic":
            from openinference.instrumentation.anthropic import AnthropicInstrumentor
            self.instrumentor = AnthropicInstrumentor()
        elif self.provider_type == "bedrock":
            from openinference.instrumentation.bedrock import BedrockInstrumentor
            self.instrumentor = BedrockInstrumentor()
        else:
            raise ValueError(f"OpenInference not supported for provider: {self.provider_type}")
        
        # Universal instrumentation call
        self.instrumentor.instrument(tracer_provider=self.tracer.provider)
        logger.debug(f"✅ OpenInference {self.provider_type} instrumentor initialized")
    
    def _initialize_traceloop(self) -> None:
        """Initialize Traceloop instrumentor."""
        import traceloop
        
        # Traceloop uses a global initialization pattern
        traceloop.init(
            api_key=os.getenv("HH_API_KEY"),
            disable_batch=True
        )
        
        # Note: Traceloop doesn't return an instrumentor object
        self.instrumentor = "traceloop_global"
        logger.debug(f"✅ Traceloop instrumentor initialized for {self.provider_type}")
    
    def is_traced(self) -> bool:
        """Check if tracing is currently enabled.
        
        :return: True if tracing is active
        """
        return self.enable_tracing and self.tracer is not None
    
    def get_tracer(self) -> Optional[Any]:
        """Get the HoneyHive tracer instance.
        
        :return: Tracer instance or None if tracing disabled
        """
        return self.tracer
    
    def cleanup(self) -> None:
        """Clean up instrumentor and tracer resources."""
        if self.instrumentor and hasattr(self.instrumentor, 'uninstrument'):
            try:
                self.instrumentor.uninstrument()
                logger.debug(f"🧹 {self.instrumentor_type} {self.provider_type} instrumentor cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Error cleaning up instrumentor: {e}")
        
        if self.tracer and hasattr(self.tracer, 'shutdown'):
            try:
                self.tracer.shutdown()
                logger.debug("🧹 HoneyHive tracer shut down")
            except Exception as e:
                logger.warning(f"⚠️ Error shutting down tracer: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the current instrumentor setup.
        
        :return: Dictionary with instrumentor information
        """
        return {
            "instrumentor_type": self.instrumentor_type,
            "provider_type": self.provider_type,
            "project": self.project,
            "tracing_enabled": self.enable_tracing,
            "tracer_active": self.tracer is not None,
            "instrumentor_active": self.instrumentor is not None,
            "name": f"{self.instrumentor_type}_{self.provider_type}"
        }


# Factory functions for easy creation
def create_traced_instrumentor(instrumentor_type: str, provider_type: str, project: Optional[str] = None) -> UniversalInstrumentor:
    """Create a traced instrumentor (default mode).
    
    :param instrumentor_type: Type of instrumentor ("openinference", "traceloop")
    :param provider_type: LLM provider ("openai", "anthropic", etc.)
    :param project: HoneyHive project name
    :return: Configured instrumentor with tracing enabled
    """
    return UniversalInstrumentor(
        instrumentor_type=instrumentor_type,
        provider_type=provider_type,
        project=project,
        enable_tracing=True
    )


def create_untraced_instrumentor(provider_type: str) -> UniversalInstrumentor:
    """Create an untraced instrumentor for A/B testing.
    
    :param provider_type: LLM provider ("openai", "anthropic", etc.)
    :return: Configured instrumentor with tracing disabled
    """
    return UniversalInstrumentor(
        instrumentor_type="none",
        provider_type=provider_type,
        project=None,
        enable_tracing=False
    )


# Convenience functions matching documentation examples
def setup_openinference_openai(project: Optional[str] = None) -> UniversalInstrumentor:
    """Set up OpenInference + OpenAI tracing (matches docs example)."""
    return create_traced_instrumentor("openinference", "openai", project)


def setup_openinference_anthropic(project: Optional[str] = None) -> UniversalInstrumentor:
    """Set up OpenInference + Anthropic tracing (matches docs example)."""
    return create_traced_instrumentor("openinference", "anthropic", project)


def setup_traceloop_openai(project: Optional[str] = None) -> UniversalInstrumentor:
    """Set up Traceloop + OpenAI tracing."""
    return create_traced_instrumentor("traceloop", "openai", project)


def setup_traceloop_anthropic(project: Optional[str] = None) -> UniversalInstrumentor:
    """Set up Traceloop + Anthropic tracing."""
    return create_traced_instrumentor("traceloop", "anthropic", project)
