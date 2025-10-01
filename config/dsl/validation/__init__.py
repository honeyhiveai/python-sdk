"""
DSL Validation Module.

This module provides validation utilities for the Provider DSL system,
including YAML schema validation, signature collision detection,
bundle compilation verification, and performance regression detection.

Quality Gates:
- Gate 12: YAML Schema Validation (yaml_schema.py)
- Gate 13: Signature Collision Detection (signature_collisions.py)
- Gate 14: Bundle Compilation Verification (bundle_verification.py)
- Gate 15: Performance Regression Detection (performance_benchmarks.py)

Usage:
    >>> from config.dsl.validation import validate_yaml_schema
    >>> is_valid, errors, count = validate_yaml_schema([Path("config.yaml")])
"""

from .yaml_schema import validate_yaml_schema, validate_yaml_file
from .signature_collisions import check_signature_collisions, check_collisions
from .bundle_verification import verify_bundle_compilation
from .performance_benchmarks import (
    check_performance_regression,
    run_performance_checks,
)

__all__ = [
    # Main library functions
    "validate_yaml_schema",
    "validate_yaml_file",
    "check_signature_collisions",
    "check_collisions",
    "verify_bundle_compilation",
    "check_performance_regression",
    "run_performance_checks",
]
