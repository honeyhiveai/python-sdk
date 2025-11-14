"""
Configuration system for Ouroboros MCP Server.

Provides type-safe, validated configuration using Pydantic v2. All configuration
is loaded from a single YAML file (.praxis-os/config/mcp.yaml) with fail-fast
validation at server startup.

Key Features:
    - Single source of truth (config/mcp.yaml)
    - Fail-fast validation (errors at startup, not runtime)
    - Type-safe access (config.indexes.standards.vector.model)
    - Clear error messages (field paths with actionable remediation)
    - IDE autocomplete (full IntelliSense support)

Usage:
    >>> from ouroboros.config import load_config
    >>> config = load_config(".praxis-os/config/mcp.yaml")
    >>> print(config.indexes.standards.vector.model)
    'BAAI/bge-small-en-v1.5'

Modules:
    schemas: Pydantic v2 models for all config sections
    loader: Config loading and validation logic

See Also:
    - schemas.base: Base models and shared validation
    - schemas.mcp: Root MCPConfig model
"""

from ouroboros.config.schemas.base import BaseConfig, EnvType

__all__ = [
    "BaseConfig",
    "EnvType",
]

