"""DSL (Domain Specific Language) tooling for provider configuration.

This module provides the compilation system for converting YAML provider
configurations into optimized runtime bundles.
"""

from config.dsl.compiler import ProviderCompiler

__all__ = ["ProviderCompiler"]
