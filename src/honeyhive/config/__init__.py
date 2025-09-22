"""HoneyHive SDK Per-Instance Configuration Management.

This module provides per-instance configuration using Pydantic models for
the multi-instance architecture. Each tracer instance has its own configuration
that is thread-safe and process-safe.

## Architecture

- **models/**: Per-instance Pydantic models for configuration and validation
- **utils**: Configuration merging utilities for backwards compatibility

## Usage Patterns

### Per-Instance Configuration (Recommended)

    >>> from honeyhive.config import TracerConfig, SessionConfig
    >>> config = TracerConfig(api_key="...", project="...", verbose=True)
    >>> tracer = HoneyHiveTracer(config=config)

### Individual Parameters (Backwards Compatible)

    >>> tracer = HoneyHiveTracer(api_key="...", project="...", verbose=True)

### Multiple Independent Tracers

    >>> config1 = TracerConfig(api_key="key1", project="project1")
    >>> config2 = TracerConfig(api_key="key2", project="project2")
    >>> tracer1 = HoneyHiveTracer(config=config1)  # Independent instance
    >>> tracer2 = HoneyHiveTracer(config=config2)  # Independent instance

## Benefits

- **Multi-Instance Support**: Each tracer has independent configuration
- **Thread Safety**: No shared global state between instances
- **Process Safety**: Works correctly across process boundaries
- **Type Safety**: Pydantic validation with clear error messages
- **Environment Integration**: Automatic loading from HH_* environment variables
- **Backwards Compatibility**: Individual parameters still work
"""

# pylint: disable=duplicate-code
# Note: Export lists are intentionally similar across config modules
# for consistency in the public API interface.

# Global config removed - use per-instance configuration instead

# Domain-specific Pydantic models (with validation)
from .models import (
    APIClientConfig,
    BaseHoneyHiveConfig,
    EvaluationConfig,
    SessionConfig,
    TracerConfig,
)

# Utility functions
from .utils import create_unified_config, merge_configs_with_params

# Future: API client configuration
# from .api_config import APIClientConfig

__all__ = [
    # Per-instance configuration models (recommended approach)
    "BaseHoneyHiveConfig",
    "TracerConfig",
    "SessionConfig",
    "EvaluationConfig",
    "APIClientConfig",
    # Configuration utilities
    "merge_configs_with_params",
    "create_unified_config",
]
