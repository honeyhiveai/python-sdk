"""Graph submodule: AST and call graph analysis.

This submodule provides structural code analysis through:
- AST extraction: Parse code with tree-sitter, extract syntax nodes
- Graph traversal: Build and query call graphs (who calls what?)

Architecture:
- ast.py: Tree-sitter parsing, AST node extraction
- traversal.py: Graph queries (recursive CTEs, path finding)
- container.py: GraphIndex (orchestrates AST + graph)

Export:
- GraphIndex: Main container class (use this from parent module)
"""

from .container import GraphIndex

__all__ = ["GraphIndex"]

