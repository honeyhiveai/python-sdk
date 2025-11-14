"""Code partition container for multi-repo code intelligence.

A CodePartition represents a single repository with multiple domains (code, tests, docs).
Each partition contains 3 sub-indexes (semantic, AST, graph) that work together.

Architecture:
- 1 partition = 1 repository (simple 1:1 mapping)
- Multiple domains per partition (code, tests, docs, instrumentors, etc.)
- Domain metadata for query filtering (framework, type, provider, etc.)
- Fractal health checks (partition → indexes → components)

Mission: Enable flexible multi-repo code search with explicit metadata filtering.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

from ouroboros.config.schemas.indexes import PartitionConfig
from ouroboros.subsystems.rag.base import BaseIndex, SearchResult, HealthStatus
from ouroboros.utils.errors import ActionableError

if TYPE_CHECKING:
    from ouroboros.subsystems.rag.code.semantic import SemanticIndex
    from ouroboros.subsystems.rag.code.graph.container import GraphIndex

logger = logging.getLogger(__name__)


class CodePartition:
    """Container for a single repository partition with 3 sub-indexes.
    
    Wraps semantic, AST, and graph indexes for a single repository.
    Provides unified search interface and health check aggregation.
    
    Attributes:
        name: Partition name (typically repo name)
        path: Repository path relative to base_path
        domains: Domain configurations (code, tests, docs, etc.)
        base_path: Base path for resolving relative paths
        semantic: SemanticIndex instance
        ast: ASTIndex instance (via GraphIndex)
        graph: GraphIndex instance
    
    Example:
        >>> from pathlib import Path
        >>> from ouroboros.config.schemas.indexes import PartitionConfig, DomainConfig
        >>> 
        >>> config = PartitionConfig(
        ...     path="../",
        ...     domains={
        ...         "code": DomainConfig(include_paths=["src/"])
        ...     }
        ... )
        >>> 
        >>> partition = CodePartition(
        ...     partition_name="my-repo",
        ...     partition_config=config,
        ...     base_path=Path(".praxis-os")
        ... )
        >>> 
        >>> # Search across all indexes in this partition
        >>> results = partition.search(
        ...     query="authentication logic",
        ...     action="search_code"
        ... )
    """
    
    def __init__(
        self,
        partition_name: str,
        partition_config: PartitionConfig,
        base_path: Path,
        semantic_index: Optional["SemanticIndex"] = None,
        graph_index: Optional["GraphIndex"] = None
    ):
        """Initialize code partition with sub-indexes.
        
        Args:
            partition_name: Partition identifier (e.g., "praxis-os", "python-sdk")
            partition_config: Partition configuration with path and domains
            base_path: Base path for resolving relative repository paths
            semantic_index: Optional pre-initialized SemanticIndex (for dependency injection)
            graph_index: Optional pre-initialized GraphIndex (for dependency injection)
        
        Raises:
            ActionableError: If partition initialization fails
        """
        self.name = partition_name
        self.config = partition_config
        self.base_path = base_path
        
        # Repository path (resolved relative to base_path)
        self.path = (base_path / partition_config.path).resolve()
        
        # Domain configurations (code, tests, docs, etc.)
        self.domains = partition_config.domains
        
        # Sub-indexes (injected or None for now)
        self.semantic = semantic_index
        self.graph = graph_index  # Contains both AST and graph functionality
        
        logger.info(
            "CodePartition '%s' initialized: path=%s, domains=%s",
            partition_name,
            self.path,
            list(self.domains.keys())
        )
    
    def search(
        self,
        query: str,
        action: str,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Union[List[SearchResult], List[Dict[str, Any]], List[List[str]]]:
        """Search across partition indexes with optional filtering.
        
        Routes search requests to the appropriate sub-index based on action:
        - search_code → semantic index (vector + FTS + hybrid)
        - search_ast → AST index (structural patterns)
        - find_callers/find_dependencies/find_call_paths → graph index
        
        FRACTAL INTERFACE PATTERN:
        This method preserves the same `filters` dict interface as SemanticIndex
        and GraphIndex for consistent delegation throughout the stack.
        
        Args:
            query: Search query or symbol name
            action: Search action type (search_code, search_ast, find_callers, etc.)
            filters: Optional filters dict (domain, metadata keys, etc.)
            **kwargs: Additional search parameters (n_results, max_depth, etc.)
        
        Returns:
            List of search results from appropriate index
        
        Raises:
            ActionableError: If action is invalid or index is not initialized
        
        Example:
            >>> # Search all code in partition
            >>> results = partition.search(
            ...     query="authentication logic",
            ...     action="search_code"
            ... )
            >>> 
            >>> # Search only in tests domain
            >>> results = partition.search(
            ...     query="test fixtures",
            ...     action="search_code",
            ...     filters={"domain": "tests"}
            ... )
            >>> 
            >>> # Search with metadata filter
            >>> results = partition.search(
            ...     query="span attributes",
            ...     action="search_code",
            ...     filters={"framework": "openai", "type": "instrumentor"}
            ... )
        """
        # Build filters for this partition (add partition name to filters)
        partition_filters = filters.copy() if filters else {}
        partition_filters["partition"] = self.name
        
        # Route to appropriate index (FRACTAL DELEGATION - same interface preserved)
        if action == "search_code":
            if self.semantic is None:
                raise ActionableError(
                    what_failed=f"Search partition '{self.name}'",
                    why_failed="SemanticIndex not initialized",
                    how_to_fix="Initialize partition with semantic_index parameter"
                )
            return self.semantic.search(query=query, filters=partition_filters, **kwargs)
        
        elif action in ("search_ast", "find_callers", "find_dependencies", "find_call_paths"):
            if self.graph is None:
                raise ActionableError(
                    what_failed=f"Search partition '{self.name}'",
                    why_failed="GraphIndex not initialized",
                    how_to_fix="Initialize partition with graph_index parameter"
                )
            
            # Route to specific graph method based on action (FRACTAL DELEGATION)
            if action == "search_ast":
                # FRACTAL COMPLIANCE: GraphIndex.search_ast() expects 'pattern', not 'query'
                n_results = kwargs.get("n_results", 5)
                return self.graph.search_ast(pattern=query, n_results=n_results, filters=partition_filters)
            elif action == "find_callers":
                # Extract max_depth from kwargs, default to 10
                max_depth = kwargs.get("max_depth", 10)
                return self.graph.find_callers(symbol_name=query, max_depth=max_depth)
            elif action == "find_dependencies":
                max_depth = kwargs.get("max_depth", 10)
                return self.graph.find_dependencies(symbol_name=query, max_depth=max_depth)
            elif action == "find_call_paths":
                max_depth = kwargs.get("max_depth", 10)
                to_symbol = kwargs.get("to_symbol")
                if not to_symbol:
                    raise ActionableError(
                        what_failed=f"Find call paths in partition '{self.name}'",
                        why_failed="Missing required 'to_symbol' parameter",
                        how_to_fix="Provide to_symbol parameter for call path search"
                    )
                return self.graph.find_call_paths(from_symbol=query, to_symbol=to_symbol, max_depth=max_depth)
            else:
                # Should never reach here as action is validated above
                raise ActionableError(
                    what_failed=f"Search partition '{self.name}'",
                    why_failed=f"Unexpected graph action '{action}'",
                    how_to_fix="Use search_ast, find_callers, find_dependencies, or find_call_paths"
                )
        
        else:
            raise ActionableError(
                what_failed=f"Search partition '{self.name}'",
                why_failed=f"Invalid action '{action}'",
                how_to_fix=f"Use one of: search_code, search_ast, find_callers, find_dependencies, find_call_paths"
            )
    
    def health_check(self) -> HealthStatus:
        """Aggregate health check from all sub-indexes.
        
        Returns fractal ComponentDescriptor showing:
        - Partition-level status (healthy if all sub-indexes healthy)
        - Sub-index statuses (semantic, AST, graph)
        - Chunk counts per domain
        - Query latency p95
        
        Returns:
            ComponentDescriptor dict with 3-level hierarchy:
            {
                "name": "partition:praxis-os",
                "status": "healthy",
                "metadata": {
                    "path": "../",
                    "domains": ["code", "tests"],
                    "repo_name": "praxis-os"
                },
                "sub_components": [
                    {"name": "semantic", "status": "healthy", ...},
                    {"name": "ast", "status": "healthy", ...},
                    {"name": "graph", "status": "healthy", ...}
                ]
            }
        
        Example:
            >>> health = partition.health_check()
            >>> print(health["status"])  # "healthy"
            >>> print(len(health["sub_components"]))  # 3 (semantic, ast, graph)
        """
        # Aggregate sub-index health checks
        sub_components = []
        all_healthy = True
        
        if self.semantic:
            semantic_health = self.semantic.health_check()
            sub_components.append(semantic_health)
            if not semantic_health.healthy:
                all_healthy = False
        
        if self.graph:
            graph_health = self.graph.health_check()
            sub_components.append(graph_health)
            if not graph_health.healthy:
                all_healthy = False
        
        # Partition-level health (return HealthStatus object, not dict)
        from ouroboros.subsystems.rag.base import HealthStatus
        
        return HealthStatus(
            healthy=all_healthy,
            message=f"Partition '{self.name}': {len(sub_components)} sub-components ({'healthy' if all_healthy else 'degraded'})",
            details={
                "name": f"partition:{self.name}",
                "path": str(self.path),
                "domains": list(self.domains.keys()),
                "domain_count": len(self.domains),
                "repo_name": self.name,
                "sub_components": sub_components
            }
        )

