"""Core HoneyHive tracer implementation with dynamic composition.

This module provides the main HoneyHiveTracer class composed from multiple
mixins using dynamic inheritance patterns. It maintains full backward
compatibility while providing a clean, modular architecture.
"""

from .base import NoOpSpan
from .tracer import HoneyHiveTracer

# Export the main class and utilities for backward compatibility
__all__ = [
    "HoneyHiveTracer",
    "NoOpSpan",
]
