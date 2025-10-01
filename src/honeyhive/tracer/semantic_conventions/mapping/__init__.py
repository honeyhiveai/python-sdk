"""Modular semantic convention mapping system.

This module provides a clean, maintainable architecture for semantic convention
processing by separating concerns into focused components:

- rule_engine: Dynamic rule creation and coordination
- transforms: Data transformation functions
- patterns: Pattern matching utilities
- rule_applier: Rule application logic

The modular design enables easier testing, better performance, and simplified
maintenance compared to the previous monolithic approach.
"""

from .patterns import PatternMatcher, pattern_matcher
from .rule_applier import RuleApplier, rule_applier

# Core components
from .rule_engine import MappingRule, RuleEngine
from .transforms import TransformRegistry

__all__ = [
    # Core classes
    "RuleEngine",
    "MappingRule",
    "TransformRegistry",
    "PatternMatcher",
    "RuleApplier",
    # Global instances (only for stateless components)
    "pattern_matcher",
    "rule_applier",
]
