"""
Bundle Types for Universal LLM Discovery Engine v4.0

Contains the data structures used for compiled provider bundles.
This module ensures consistent imports for pickle serialization/deserialization.
"""

from typing import Dict, Any, Set, FrozenSet, List, Optional, Tuple, Callable

from pydantic import BaseModel, Field, ConfigDict


class CompiledProviderBundle(BaseModel):
    """
    Compiled provider bundle structure optimized for true O(1) operations.

    Version 4.0.1 introduces inverted signature index for genuine O(1) exact match lookups,
    addressing the O(n) scaling issues identified in performance analysis.
    """

    model_config = ConfigDict(
        # Allow arbitrary types for frozensets and callables
        arbitrary_types_allowed=True,
        # Validate assignment to catch runtime errors
        validate_assignment=True,
        # Extra fields forbidden to catch typos
        extra="forbid",
    )

    # Forward index: provider → [signatures] (for subset matching fallback)
    provider_signatures: Dict[str, List[FrozenSet[str]]] = Field(
        description="Provider signature patterns for subset matching fallback (O(log n))"
    )

    # NEW: Inverted index: signature → (provider, confidence) (for exact matching)
    signature_to_provider: Dict[FrozenSet[str], Tuple[str, float]] = Field(
        default_factory=dict,
        description="Inverted signature index for O(1) exact match lookups",
    )

    # Compiled extraction functions as executable code strings
    extraction_functions: Dict[str, str] = Field(
        description="Compiled extraction functions as executable Python code strings"
    )

    # Field mappings for HoneyHive schema conversion
    field_mappings: Dict[str, Dict[str, Any]] = Field(
        description="Field mappings for converting to HoneyHive 4-section schema"
    )

    # Transform function registry
    transform_registry: Dict[str, Dict[str, Any]] = Field(
        description="Transform function registry for data processing"
    )

    # Validation rules for runtime checking
    validation_rules: Dict[str, Any] = Field(
        description="Validation rules for runtime data integrity checking"
    )

    # Build metadata for debugging and versioning
    build_metadata: Dict[str, Any] = Field(
        description="Build metadata including timestamps, versions, and compilation info"
    )

    def get_provider_count(self) -> int:
        """Get the number of compiled providers."""
        return len(self.provider_signatures)

    def get_signature_count(self) -> int:
        """Get the total number of signature patterns."""
        return sum(len(sigs) for sigs in self.provider_signatures.values())

    def get_extraction_function_count(self) -> int:
        """Get the number of compiled extraction functions."""
        return len(self.extraction_functions)

    def validate_bundle_integrity(self) -> bool:
        """Validate that the bundle is internally consistent."""
        # Check that all providers have signatures
        for provider in self.provider_signatures.keys():
            if provider not in self.extraction_functions:
                return False
            if provider not in self.field_mappings:
                return False

        return True
