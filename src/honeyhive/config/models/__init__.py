"""Domain-specific configuration models for HoneyHive SDK.

This package provides Pydantic models for different domains within the SDK
to reduce constructor argument count while maintaining backwards compatibility.

The hybrid approach allows both old and new usage patterns:

## Tracer Configuration

Old Usage (Backwards Compatible):
    >>> tracer = HoneyHiveTracer(api_key="...", project="...", verbose=True)

New Usage (Recommended):
    >>> from honeyhive.config.models import TracerConfig
    >>> config = TracerConfig(api_key="...", project="...", verbose=True)
    >>> tracer = HoneyHiveTracer(config=config)

## API Client Configuration (Future)

Old Usage (Current):
    >>> client = HoneyHive(bearer_auth="...", server_url="...", timeout_ms=30000)

New Usage (Future):
    >>> from honeyhive.config.models import APIClientConfig
    >>> config = APIClientConfig(api_key="...", server_url="...", timeout=30.0)
    >>> client = HoneyHive(config=config)

## Architecture

The models are organized by domain:
- base.py: BaseHoneyHiveConfig with common fields (api_key, project, etc.)
- tracer.py: TracerConfig, SessionConfig, EvaluationConfig
- api_client.py: APIClientConfig for API client initialization

All models inherit from BaseHoneyHiveConfig to avoid field duplication
while maintaining type safety and validation consistency.
"""

# API client configurations
from .api_client import APIClientConfig

# Base configuration
from .base import BaseHoneyHiveConfig

# Experiment configurations
from .experiment import ExperimentConfig

# HTTP client configurations
from .http_client import HTTPClientConfig

# OTLP configurations
from .otlp import OTLPConfig

# Tracer configurations
from .tracer import EvaluationConfig, SessionConfig, TracerConfig

# Note: TracingConfig merged into TracerConfig to eliminate duplication

__all__ = [
    # Base
    "BaseHoneyHiveConfig",
    # Tracer domain
    "TracerConfig",
    "SessionConfig",
    "EvaluationConfig",
    # API client domain
    "APIClientConfig",
    # HTTP client domain
    "HTTPClientConfig",
    # OTLP domain
    "OTLPConfig",
    # Experiment domain
    "ExperimentConfig",
    # Note: TracingConfig merged into TracerConfig
]
