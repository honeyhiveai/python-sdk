"""
Component Helpers for Cascading Health Check Architecture.

This module provides core abstractions for the fractal component registry pattern
used throughout the RAG subsystem. The pattern is self-similar (fractal), meaning
the same abstractions (ComponentDescriptor + dynamic_health_check) are used at
every level of the hierarchy: IndexManager, StandardsIndex, CodeIndex, GraphIndex,
and their sub-components. This creates a uniform, composable architecture where
parent indexes discover child component health dynamically without hardcoded logic.

Key Abstractions:
    - ComponentDescriptor: Declarative metadata for registering components
    - dynamic_health_check(): Generic helper to aggregate component health

Architectural Pattern:
    The fractal pattern eliminates O(N²) maintenance cost by using dynamic discovery.
    When a new component is added, parents automatically discover it via the registry,
    requiring zero code changes in parent classes. This self-similar pattern scales
    identically from the lowest level (AST/graph tables in GraphIndex) to the highest
    level (indexes in IndexManager).

Example Usage:
    ```python
    from ouroboros.subsystems.rag.utils.component_helpers import (
        ComponentDescriptor,
        dynamic_health_check,
    )
    from ouroboros.subsystems.rag.models import HealthStatus
    
    class MyIndex:
        def __init__(self):
            self.components = {
                "component_a": ComponentDescriptor(
                    name="component_a",
                    provides=["data_a"],
                    capabilities=["query_a"],
                    health_check=self._check_a_health,
                    rebuild=self._rebuild_a,
                    dependencies=[],
                ),
                "component_b": ComponentDescriptor(
                    name="component_b",
                    provides=["data_b"],
                    capabilities=["query_b"],
                    health_check=self._check_b_health,
                    rebuild=self._rebuild_b,
                    dependencies=["component_a"],
                ),
            }
        
        def health_check(self) -> HealthStatus:
            \"\"\"Delegate to dynamic helper for automatic aggregation.\"\"\"
            return dynamic_health_check(self.components)
    ```

See Also:
    - specs/2025-11-08-cascading-health-check-architecture/specs.md
    - specs/2025-11-08-cascading-health-check-architecture/implementation.md
"""

from dataclasses import dataclass
from typing import Dict, List, Callable, Any
import logging

logger = logging.getLogger(__name__)

# Import HealthStatus from base module
# Note: We import here to avoid circular dependencies
try:
    from ouroboros.subsystems.rag.base import HealthStatus
except ImportError:
    # Fallback for testing or when base is not available
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from ouroboros.subsystems.rag.base import HealthStatus


@dataclass
class ComponentDescriptor:
    """
    Declarative metadata for registering components in the fractal architecture.
    
    A ComponentDescriptor defines what a component provides, what capabilities it offers,
    how to check its health, how to rebuild it, and what dependencies it has. This
    abstraction enables dynamic discovery: parent indexes can aggregate child component
    health without hardcoded if/else logic.
    
    Attributes:
        name (str): Unique component identifier (e.g., "ast", "graph", "vector").
            Must be non-empty. Used as registry key and in health check output.
            
            Example: "ast", "semantic", "standards_vector"
        
        provides (List[str]): Data or resources this component provides.
            Must be non-empty list. Used for dependency resolution and documentation.
            
            Example: ["ast_nodes"], ["symbols", "relationships"], ["embeddings"]
        
        capabilities (List[str]): Query capabilities this component enables.
            Must be non-empty list. Used for capability discovery (e.g., can this
            index perform semantic search?).
            
            Example: ["search_ast"], ["find_callers", "find_dependencies"]
        
        health_check (Callable): Function that checks component health.
            Must be callable with no arguments, returning HealthStatus.
            Typically a bound method like `self._check_ast_health`.
            
            Example: `lambda: self._check_ast_health()`
        
        rebuild (Callable): Function that rebuilds component.
            Must be callable with no arguments, returning None or raising exception.
            Typically a bound method like `self._rebuild_ast`.
            
            Example: `lambda: self._rebuild_ast()`
        
        dependencies (List[str]): Component names this component depends on.
            Can be empty list (no dependencies). Used for rebuild ordering and
            health check interpretation (dependent component can't be healthy if
            dependency is unhealthy).
            
            Example: [], ["ast"], ["semantic", "graph"]
    
    Validation:
        - name must be non-empty string
        - provides must be non-empty list
        - capabilities must be non-empty list
        - health_check must be callable
        - rebuild must be callable
        - dependencies can be empty (no validation required)
    
    Raises:
        ValueError: If any validation check fails during __post_init__().
    
    Example:
        ```python
        from ouroboros.subsystems.rag.models import HealthStatus
        
        class MyIndex:
            def __init__(self):
                self.components = {
                    "ast": ComponentDescriptor(
                        name="ast",
                        provides=["ast_nodes"],
                        capabilities=["search_ast"],
                        health_check=self._check_ast_health,
                        rebuild=self._rebuild_ast,
                        dependencies=[],
                    ),
                }
            
            def _check_ast_health(self) -> HealthStatus:
                # ... check AST table ...
                return HealthStatus(healthy=True, details={})
            
            def _rebuild_ast(self) -> None:
                # ... rebuild AST index ...
                pass
        ```
    
    See Also:
        - dynamic_health_check(): Uses ComponentDescriptor to aggregate health
        - specs/2025-11-08-cascading-health-check-architecture/specs.md: Design rationale
    """
    
    name: str
    provides: List[str]
    capabilities: List[str]
    health_check: Callable
    rebuild: Callable
    dependencies: List[str]
    
    def __post_init__(self) -> None:
        """
        Validate ComponentDescriptor fields after initialization.
        
        Ensures all required fields are non-empty and callable fields are actually
        callable. This prevents registration errors at component setup time rather
        than at health check time.
        
        Raises:
            ValueError: If name is empty, provides is empty, capabilities is empty,
                       health_check is not callable, or rebuild is not callable.
        """
        if not self.name:
            raise ValueError(
                "ComponentDescriptor.name must be non-empty string. "
                "Received empty string. "
                "Example: name='ast', name='semantic', name='vector'"
            )
        
        if not self.provides:
            raise ValueError(
                f"ComponentDescriptor.provides must be non-empty list for component '{self.name}'. "
                "Received empty list. "
                "Example: provides=['ast_nodes'], provides=['symbols', 'relationships']"
            )
        
        if not self.capabilities:
            raise ValueError(
                f"ComponentDescriptor.capabilities must be non-empty list for component '{self.name}'. "
                "Received empty list. "
                "Example: capabilities=['search_ast'], capabilities=['find_callers', 'find_dependencies']"
            )
        
        if not callable(self.health_check):
            raise ValueError(
                f"ComponentDescriptor.health_check must be callable for component '{self.name}'. "
                f"Received {type(self.health_check).__name__}. "
                "Example: health_check=self._check_ast_health, health_check=lambda: HealthStatus(...)"
            )
        
        if not callable(self.rebuild):
            raise ValueError(
                f"ComponentDescriptor.rebuild must be callable for component '{self.name}'. "
                f"Received {type(self.rebuild).__name__}. "
                "Example: rebuild=self._rebuild_ast, rebuild=lambda: None"
            )


def dynamic_health_check(components: Dict[str, ComponentDescriptor]) -> "HealthStatus":
    """
    Aggregate health check across all registered components.
    
    This is the core helper function for the fractal architecture. It dynamically
    discovers all registered components, calls their health_check() functions,
    aggregates their health status, and builds a capability map. Parents use this
    to avoid hardcoded if/else logic - they just register components and delegate
    to this helper.
    
    The function is defensive: if a component's health_check() raises an exception,
    it's caught, logged, and treated as unhealthy (not crash). This prevents one
    broken component from crashing the entire health check cascade.
    
    Args:
        components (Dict[str, ComponentDescriptor]): Registry of components to check.
            Key is component name (e.g., "ast", "graph"), value is ComponentDescriptor.
            Can be empty dict (treated as healthy).
    
    Returns:
        HealthStatus: Aggregated health status with:
            - healthy (bool): True only if ALL components are healthy
            - message (str): Summary message (e.g., "2/2 components healthy")
            - details (dict): Contains:
                - "components" (dict): Per-component health {name: HealthStatus}
                - "capabilities" (dict): Capability map {capability: bool}
                - "component_count" (int): Total number of components
                - "healthy_count" (int): Number of healthy components
    
    Behavior:
        - Empty components dict: Returns HealthStatus(healthy=True, ...)
        - All components healthy: Returns HealthStatus(healthy=True, ...)
        - Any component unhealthy: Returns HealthStatus(healthy=False, ...)
        - Exception in health_check(): Caught, logged, treated as unhealthy
    
    Capability Map:
        Built by iterating all components and their capabilities. If component is
        healthy, its capabilities map to True. If unhealthy, map to False. This
        allows callers to query: "Can this index perform semantic search?" by
        checking capabilities["semantic_search"].
    
    Example:
        ```python
        components = {
            "ast": ComponentDescriptor(
                name="ast",
                provides=["ast_nodes"],
                capabilities=["search_ast"],
                health_check=lambda: HealthStatus(healthy=True, message="AST OK"),
                rebuild=lambda: None,
                dependencies=[],
            ),
            "graph": ComponentDescriptor(
                name="graph",
                provides=["symbols"],
                capabilities=["find_callers", "find_dependencies"],
                health_check=lambda: HealthStatus(healthy=False, message="Graph broken"),
                rebuild=lambda: None,
                dependencies=[],
            ),
        }
        
        result = dynamic_health_check(components)
        # result.healthy == False (one component unhealthy)
        # result.details["components"]["ast"].healthy == True
        # result.details["components"]["graph"].healthy == False
        # result.details["capabilities"] == {
        #     "search_ast": True,
        #     "find_callers": False,
        #     "find_dependencies": False
        # }
        ```
    
    See Also:
        - ComponentDescriptor: Defines component metadata
        - specs/2025-11-08-cascading-health-check-architecture/specs.md: Design
    """
    from ouroboros.subsystems.rag.base import HealthStatus
    
    # Handle empty components (treated as healthy)
    if not components:
        return HealthStatus(
            healthy=True,
            message="No components registered (healthy by default)",
            details={
                "components": {},
                "capabilities": {},
                "component_count": 0,
                "healthy_count": 0,
            },
        )
    
    # Aggregate component health
    component_health: Dict[str, Any] = {}
    capabilities: Dict[str, bool] = {}
    healthy_count = 0
    
    for name, descriptor in components.items():
        try:
            # Call component health_check() (may raise exception)
            status = descriptor.health_check()
            component_health[name] = status
            
            # Track healthy count
            if status.healthy:
                healthy_count += 1
            
            # Build capability map: healthy components → True, unhealthy → False
            for capability in descriptor.capabilities:
                capabilities[capability] = status.healthy
        
        except Exception as e:
            # Defensive: catch exceptions, treat as unhealthy
            logger.error(
                f"Component '{name}' health_check() raised exception: {type(e).__name__}: {e}",
                exc_info=True,
            )
            
            # Create error HealthStatus for this component
            error_status = HealthStatus(
                healthy=False,
                message=f"Health check raised exception: {type(e).__name__}: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
            )
            component_health[name] = error_status
            
            # Mark all capabilities as unavailable
            for capability in descriptor.capabilities:
                capabilities[capability] = False
    
    # Overall health: True only if ALL components healthy
    all_healthy = (healthy_count == len(components))
    
    # Build summary message
    if all_healthy:
        message = f"All {len(components)} components healthy"
    else:
        message = f"{healthy_count}/{len(components)} components healthy"
    
    return HealthStatus(
        healthy=all_healthy,
        message=message,
        details={
            "components": component_health,
            "capabilities": capabilities,
            "component_count": len(components),
            "healthy_count": healthy_count,
        },
    )

