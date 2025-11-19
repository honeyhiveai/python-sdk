"""Declarative partition reconciliation for config-as-desired-state pattern.

The PartitionReconciler implements a Kubernetes/Terraform-style declarative
infrastructure pattern where the config file defines the desired state and
the system automatically reconciles to match it on startup.

Reconciliation Pattern:
    1. User edits mcp.yaml (defines desired state)
    2. User restarts MCP server
    3. PartitionReconciler.reconcile() runs:
       - Scans filesystem for actual state (indexes/ directory)
       - Reads config for desired state (partitions in mcp.yaml)
       - Creates missing partitions
       - Deletes removed partitions
    4. System now matches config automatically

Philosophy:
    "Config as desired state, restart to apply - true lazy nirvana" - Josh
    No manual commands needed. Edit config, restart, done.
    Indexes are ephemeral cache - deletion is safe, can rebuild from source.

Example:
    >>> # User edits mcp.yaml, removes 'openlit' partition
    >>> # User restarts MCP server
    >>> reconciler = PartitionReconciler(base_path, config)
    >>> report = reconciler.reconcile()
    >>> # Report: deleted=['openlit'], created=[]
    >>> # openlit directory deleted (can rebuild from source if re-added)

Mission: Enable GitOps-style partition management with zero manual intervention.
"""

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

from ouroboros.config.schemas.indexes import CodeIndexConfig

logger = logging.getLogger(__name__)


@dataclass
class ReconciliationReport:
    """Report of partition reconciliation actions taken.
    
    Provides full audit trail of what changed during reconciliation.
    Enables logging, monitoring, and alerting on partition lifecycle.
    
    Attributes:
        created: List of partition names that were created
        deleted: List of partition names that were deleted (removed from config)
        errors: List of error messages encountered during reconciliation
        
    Example:
        >>> report = ReconciliationReport(
        ...     created=['new-instrumentor'],
        ...     deleted=['old-repo'],
        ...     errors=[]
        ... )
        >>> print(f"Created {len(report.created)}, deleted {len(report.deleted)} partitions")
    """
    created: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def has_changes(self) -> bool:
        """Check if any reconciliation actions were taken.
        
        Returns:
            True if any partitions were created or deleted
        """
        return bool(self.created or self.deleted)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for logging/monitoring.
        
        Returns:
            Dictionary representation of the report
        """
        return {
            "created": self.created,
            "deleted": self.deleted,
            "errors": self.errors,
            "total_changes": len(self.created) + len(self.deleted),
            "has_errors": len(self.errors) > 0,
        }


class PartitionReconciler:
    """Declarative partition reconciler (Kubernetes/Terraform pattern).
    
    Reconciles partition filesystem state with config-defined desired state.
    Runs automatically on MCP server startup to ensure system matches config.
    
    Reconciliation Actions:
        - **Create:** Partition in config but not in filesystem → create directory
        - **Delete:** Partition in filesystem but not in config → delete directory
    
    Design Principles:
        - **Declarative:** Config is source of truth (not imperative commands)
        - **Idempotent:** Running reconcile() multiple times is safe
        - **Ephemeral indexes:** Indexes are derived cache, can be rebuilt from source
        - **Simple:** No archival, no orphan detection - just create/delete
    
    Attributes:
        base_path: Base directory for index storage
        config: CodeIndexConfig with partition definitions
        indexes_dir: Path to indexes/ directory (actual state)
    
    Example:
        >>> config = MCPConfig().rag.code
        >>> reconciler = PartitionReconciler(Path("/data"), config)
        >>> report = reconciler.reconcile()
        >>> logger.info(f"Reconciliation: {report.to_dict()}")
    """
    
    def __init__(self, base_path: Path, config: CodeIndexConfig):
        """Initialize partition reconciler.
        
        Args:
            base_path: Base directory for index storage
            config: CodeIndexConfig with partition definitions from mcp.yaml
        """
        self.base_path = base_path
        self.config = config
        self.indexes_dir = base_path / ".cache" / "indexes" / "code"
        
        # Ensure base directory exists
        self.indexes_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "PartitionReconciler initialized (indexes=%s)",
            self.indexes_dir
        )
    
    def reconcile(self) -> ReconciliationReport:
        """Reconcile partition state (desired vs actual).
        
        This is the main entry point for declarative reconciliation.
        Compares config-defined partitions with filesystem state and
        takes actions to make filesystem match config.
        
        Reconciliation Flow:
            1. Scan filesystem for actual partitions (indexes/ directory)
            2. Read config for desired partitions (mcp.yaml)
            3. Create missing partitions (in config but not in filesystem)
            4. Delete removed partitions (in filesystem but not in config)
            5. Return report of actions taken
        
        Returns:
            ReconciliationReport with lists of created and deleted partitions
        
        Example:
            >>> report = reconciler.reconcile()
            >>> if report.has_changes():
            ...     logger.info(f"Reconciled: {report.to_dict()}")
        """
        logger.info("🔄 Starting partition reconciliation (config as desired state)")
        report = ReconciliationReport()
        
        try:
            # Get desired and actual partition sets
            desired = self._get_desired_partitions()
            actual = self._scan_actual_partitions()
            
            logger.info(
                "Partition state: desired=%s, actual=%s",
                sorted(desired),
                sorted(actual)
            )
            
            # Determine reconciliation actions
            to_create = desired - actual  # In config but not filesystem
            to_delete = actual - desired  # In filesystem but not config
            
            # Execute reconciliation actions
            if to_create:
                created = self._create_missing(to_create)
                report.created.extend(created)
            
            if to_delete:
                deleted = self._delete_removed(to_delete)
                report.deleted.extend(deleted)
            
            # Log reconciliation summary
            if report.has_changes():
                logger.info(
                    "✅ Reconciliation complete: created=%d, deleted=%d",
                    len(report.created),
                    len(report.deleted)
                )
            else:
                logger.info("✅ Reconciliation complete: no changes needed (system matches config)")
        
        except Exception as e:
            error_msg = f"Reconciliation failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            report.errors.append(error_msg)
        
        return report
    
    def _get_desired_partitions(self) -> Set[str]:
        """Get desired partition names from config.
        
        Reads partition names from mcp.yaml config. This is the "desired state"
        that the system should match.
        
        Returns:
            Set of partition names defined in config
        
        Example:
            >>> desired = reconciler._get_desired_partitions()
            >>> # {'praxis-os', 'openlit', 'instrumentor'}
        """
        if not hasattr(self.config, 'partitions') or not self.config.partitions:
            logger.warning("No partitions defined in config (single-repo mode)")
            return set()
        
        partition_names = set(self.config.partitions.keys())
        logger.debug("Desired partitions from config: %s", sorted(partition_names))
        return partition_names
    
    def _scan_actual_partitions(self) -> Set[str]:
        """Scan filesystem for actual partition directories.
        
        Scans indexes/ directory to find existing partition directories.
        This is the "actual state" that needs to match the config.
        
        Excludes:
            - .archive/ directory (not an active partition)
            - Hidden directories (start with .)
            - Files (not directories)
        
        Returns:
            Set of partition names found in indexes/ directory
        
        Example:
            >>> actual = reconciler._scan_actual_partitions()
            >>> # {'praxis-os', 'old-repo'}
        """
        if not self.indexes_dir.exists():
            logger.debug("Indexes directory doesn't exist yet: %s", self.indexes_dir)
            return set()
        
        actual = set()
        
        for item in self.indexes_dir.iterdir():
            # Skip archive directory and hidden directories
            if item.name.startswith('.'):
                continue
            
            # Only include directories (not files)
            if item.is_dir():
                actual.add(item.name)
        
        logger.debug("Actual partitions in filesystem: %s", sorted(actual))
        return actual
    
    def _create_missing(self, partition_names: Set[str]) -> List[str]:
        """Create missing partition directories (in config but not filesystem).
        
        Creates directory structure for new partitions that appear in config.
        Directory creation is lightweight - actual index initialization happens
        when CodePartition is first used.
        
        Args:
            partition_names: Set of partition names to create
        
        Returns:
            List of successfully created partition names
        
        Example:
            >>> created = reconciler._create_missing({'new-instrumentor'})
            >>> # Creates indexes/new-instrumentor/ directory
        """
        created = []
        
        for partition_name in partition_names:
            try:
                partition_dir = self.indexes_dir / partition_name
                partition_dir.mkdir(parents=True, exist_ok=True)
                
                logger.info(
                    "✅ Created partition directory: %s (from config)",
                    partition_name
                )
                created.append(partition_name)
            
            except Exception as e:
                error_msg = f"Failed to create partition '{partition_name}': {e}"
                logger.error(error_msg)
                # Continue with other partitions (graceful degradation)
        
        return created
    
    def _delete_removed(self, partition_names: Set[str]) -> List[str]:
        """Delete removed partitions (hard delete - indexes are ephemeral cache).
        
        Deletes partition directories when removed from config.
        Indexes are derived cache from source code, can be rebuilt anytime.
        
        Philosophy:
            - Indexes = ephemeral cache (not source of truth)
            - Source of truth = actual code repos (on disk)
            - Rebuilding single partition is fast (not full multi-repo set)
            - No archival needed (same as Kubernetes pods - gone when deleted)
        
        Restore Process (if needed):
            1. Add partition back to mcp.yaml config
            2. Restart MCP server
            3. Reconciler creates directory
            4. Index rebuild happens automatically on first use
        
        Args:
            partition_names: Set of partition names to delete
        
        Returns:
            List of successfully deleted partition names
        
        Example:
            >>> deleted = reconciler._delete_removed({'old-repo'})
            >>> # Deletes indexes/old-repo/ (and all contents)
        """
        deleted = []
        
        for partition_name in partition_names:
            try:
                partition_dir = self.indexes_dir / partition_name
                
                if not partition_dir.exists():
                    logger.warning(
                        "Partition '%s' marked for deletion but directory doesn't exist",
                        partition_name
                    )
                    continue
                
                # Delete directory and all contents
                shutil.rmtree(partition_dir)
                
                logger.info(
                    "🗑️  Deleted partition '%s' (removed from config, can rebuild from source)",
                    partition_name
                )
                deleted.append(partition_name)
            
            except Exception as e:
                error_msg = f"Failed to delete partition '{partition_name}': {e}"
                logger.error(error_msg)
                # Continue with other partitions (graceful degradation)
        
        return deleted

