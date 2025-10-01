"""Semantic convention processing for HoneyHive tracer.

This module provides comprehensive semantic convention support through a
config-driven architecture that dynamically discovers and processes:

- HoneyHive native attributes (honeyhive_*)
- OpenInference attributes (llm.*)
- Traceloop attributes (gen_ai.*)
- OpenLit attributes (gen_ai.usage.input_tokens patterns)

The system is designed for high performance with caching integration,
easy extensibility through versioned convention definitions, and
maintains 100% backward compatibility.

Architecture:
- Dynamic discovery of convention definitions
- Rule-based mapping from configuration
- Cached processing for optimal performance
- Versioned convention support for future growth
"""

from .central_mapper import CentralEventMapper, get_central_mapper

# Config-driven architecture (primary interface)
from .discovery import (
    ConventionDefinition,
    ConventionDiscovery,
    discover_semantic_conventions,
    get_discovery_instance,
)

# Centralized schema and mapping system
from .schema import (
    TARGET_SCHEMAS,
    ChatMessage,
    EventType,
    HoneyHiveEventSchema,
    LLMConfig,
    LLMInputs,
    LLMMetadata,
    LLMOutputs,
)

__all__ = [
    # Primary interface - CentralEventMapper with integrated rule engine
    "CentralEventMapper",
    "get_central_mapper",
    # Config-driven architecture components
    "ConventionDiscovery",
    "ConventionDefinition",
    "get_discovery_instance",
    "discover_semantic_conventions",
    # Schema and validation
    "HoneyHiveEventSchema",
    "EventType",
    "ChatMessage",
    "LLMInputs",
    "LLMOutputs",
    "LLMConfig",
    "LLMMetadata",
    "TARGET_SCHEMAS",
]
