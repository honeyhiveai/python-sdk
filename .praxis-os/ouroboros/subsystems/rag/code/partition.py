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
from ouroboros.subsystems.rag.base import BaseIndex, SearchResult, HealthStatus, BuildStatus
from ouroboros.subsystems.rag.utils.component_helpers import (
    ComponentDescriptor,
    dynamic_build_status,
    dynamic_health_check,
)
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
        
        # Register components for fractal health checks and build status
        # This follows the same pattern as StandardsIndex and CodeIndex
        self.components: Dict[str, ComponentDescriptor] = {}
        
        # Register semantic component (if exists)
        if self.semantic:
            self.components["semantic"] = ComponentDescriptor(
                name="semantic",
                provides=["code_chunks", "embeddings", "fts_index"],
                capabilities=["search"],
                health_check=lambda idx=self.semantic: idx.health_check(),
                build_status_check=lambda idx=self.semantic: idx.build_status(),
                rebuild=lambda: None,  # Rebuild not implemented yet
                dependencies=[],
            )
        
        # Register graph component (if exists)
        if self.graph:
            self.components["graph"] = ComponentDescriptor(
                name="graph",
                provides=["ast_nodes", "symbols", "relationships"],
                capabilities=["search_ast", "find_callers", "find_dependencies", "find_call_paths"],
                health_check=lambda idx=self.graph: idx.health_check(),
                build_status_check=lambda idx=self.graph: idx.build_status(),
                rebuild=lambda: None,  # Rebuild not implemented yet
                dependencies=[],
            )
        
        logger.info(
            "CodePartition '%s' initialized: path=%s, domains=%s, components=%s",
            partition_name,
            self.path,
            list(self.domains.keys()),
            list(self.components.keys())
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
    
    def build_status(self) -> BuildStatus:
        """Aggregate build status from all sub-indexes using fractal pattern.
        
        Delegates to dynamic_build_status() for automatic aggregation across
        registered components (semantic, graph). This follows the same pattern
        as StandardsIndex and CodeIndex.
        
        The fractal helper automatically:
        - Calls build_status_check() on each registered component
        - Aggregates using priority-based selection (worst state wins)
        - Calculates average progress across all components
        - Handles exceptions defensively (treats as FAILED)
        - Builds summary message with component counts
        
        Returns:
            BuildStatus with aggregated state, message, and progress:
            - state: Worst state from all sub-indexes (BUILT, BUILDING, FAILED, etc.)
            - message: Summary of partition build status
            - progress_percent: Average progress across sub-indexes
            - details: Sub-component build statuses
        
        Example:
            >>> status = partition.build_status()
            >>> print(status.state)  # IndexBuildState.BUILT
            >>> print(status.progress_percent)  # 100.0
            >>> print(status.details["components"].keys())  # dict_keys(['semantic', 'graph'])
        """
        return dynamic_build_status(self.components)
    
    def health_check(self) -> HealthStatus:
        """Aggregate health check from all sub-indexes using fractal pattern.
        
        Delegates to dynamic_health_check() for automatic aggregation across
        registered components (semantic, graph). This follows the same pattern
        as StandardsIndex and CodeIndex.
        
        The fractal helper automatically:
        - Calls health_check() on each registered component
        - Aggregates health (all healthy = True, any unhealthy = False)
        - Builds capability map from component capabilities
        - Handles exceptions defensively (treats as unhealthy)
        - Provides component-level diagnostics in details
        
        Returns:
            HealthStatus with aggregated health from all sub-indexes:
            - healthy (bool): True only if ALL sub-indexes healthy
            - message (str): Summary of health status
            - details (dict): Contains:
                - "components" (dict): Per-component health {name: HealthStatus}
                - "capabilities" (dict): Capability map {capability: bool}
                - "component_count" (int): Total number of components
                - "healthy_count" (int): Number of healthy components
        
        Example:
            >>> health = partition.health_check()
            >>> print(health.healthy)  # True
            >>> print(health.details["component_count"])  # 2 (semantic, graph)
            >>> print(health.details["capabilities"])  # {"search": True, "find_callers": True, ...}
        """
        return dynamic_health_check(self.components)

