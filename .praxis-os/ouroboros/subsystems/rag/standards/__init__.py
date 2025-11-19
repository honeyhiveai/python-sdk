"""Standards index submodule - semantic search for standards documentation.

This submodule provides semantic search capabilities for standards documentation
using the submodule pattern with container-based delegation.

Architecture:
    - container.py: StandardsIndex (implements BaseIndex, delegates to semantic)
    - semantic.py: SemanticIndex (internal LanceDB implementation)

The container pattern provides:
    - Uniform interface (BaseIndex) for IndexManager
    - Internal delegation to semantic implementation
    - Lock management for build/update operations
    - Auto-repair on corruption detection

Usage:
    >>> from ouroboros.subsystems.rag.standards import StandardsIndex
    >>> 
    >>> index = StandardsIndex(config, base_path)
    >>> index.build(source_paths)
    >>> results = index.search("how to test in python", n_results=5)

Exports:
    StandardsIndex: Main interface for standards search (from container.py)

Traceability:
    - FR-001: Uniform container entry point pattern
    - FR-007: Internal implementation hidden from IndexManager
    - Implementation Pattern 2: Simple submodule (single database)
"""

from ouroboros.subsystems.rag.standards.container import StandardsIndex

__all__ = ["StandardsIndex"]

