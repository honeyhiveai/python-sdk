"""
Pydantic v2 configuration schemas for Ouroboros.

This package contains all configuration models using Pydantic v2 for
type-safe, validated configuration. Schemas are organized by subsystem:

Modules:
    base: Base models, enums, and shared validation logic
    indexes: RAG index configurations (Standards, Code, AST, Graph)
    workflow: Workflow subsystem configuration
    browser: Browser subsystem configuration
    mcp: Root MCPConfig that composes all subsystem configs

Schema Design Principles:
    1. Fail-Fast: Invalid config crashes at startup with clear errors
    2. Type-Safe: All access via dot-notation (config.field.subfield)
    3. Self-Documenting: Field descriptions for all fields
    4. Validated: Field constraints (ge, le, pattern) enforced
    5. Immutable: Frozen after load (prevents runtime mutation)

Example:
    >>> from ouroboros.config.schemas.base import BaseConfig, EnvType
    >>> from ouroboros.config.schemas.indexes import StandardsIndexConfig
    >>> 
    >>> class MyConfig(BaseConfig):
    ...     name: str = Field(description="Service name")
    ...     port: int = Field(ge=1024, le=65535, default=8080)
"""

from ouroboros.config.schemas.base import BaseConfig, EnvType

__all__ = [
    "BaseConfig",
    "EnvType",
]

