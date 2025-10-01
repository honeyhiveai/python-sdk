"""Provider-specific implementations for different LLM services."""

from .openinference_openai_provider import OpenInferenceOpenAIProvider
from .openinference_anthropic_provider import OpenInferenceAnthropicProvider
from .base_provider import BaseProvider, ProviderResponse

# Traceloop providers (optional imports)
try:
    from .traceloop_openai_provider import TraceloopOpenAIProvider
    from .traceloop_anthropic_provider import TraceloopAnthropicProvider
    _TRACELOOP_AVAILABLE = True
except ImportError:
    _TRACELOOP_AVAILABLE = False

__all__ = ["BaseProvider", "OpenInferenceOpenAIProvider", "OpenInferenceAnthropicProvider", "ProviderResponse"]

if _TRACELOOP_AVAILABLE:
    __all__.extend(["TraceloopOpenAIProvider", "TraceloopAnthropicProvider"])
