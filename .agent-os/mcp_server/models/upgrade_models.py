"""
Data Models for Agent OS Upgrade Workflow.

Provides type-safe data structures for workflow evidence and state.
"""

# pylint: disable=too-many-instance-attributes
# Justification: Evidence dataclasses require many attributes to capture comprehensive
# upgrade workflow evidence for each phase (9-14 attributes per phase). This ensures
# complete checkpoint validation and audit trails.

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Phase0Evidence:
    """
    Evidence required to pass Phase 0 checkpoint.

    Phase 0: Pre-Flight Checks
    """

    source_path: str
    source_version: str
    source_commit: str
    source_git_clean: bool
    target_exists: bool
    target_structure_valid: bool
    disk_space_available: str
    disk_space_required: str
    no_concurrent_workflows: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Phase0Evidence":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Phase1Evidence:
    """
    Evidence required to pass Phase 1 checkpoint.

    Phase 1: Backup & Preparation
    """

    backup_path: str
    backup_timestamp: str
    files_backed_up: int
    backup_size_bytes: int
    backup_manifest: str
    integrity_verified: bool
    lock_acquired: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Phase1Evidence":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Phase2Evidence:
    """
    Evidence required to pass Phase 2 checkpoint.

    Phase 2: Content Upgrade
    """

    safe_upgrade_executed: bool
    dry_run_preview: Dict
    actual_upgrade: Dict
    version_updated: str
    update_log_appended: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Phase2Evidence":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Phase3Evidence:
    """
    Evidence required to pass Phase 3 checkpoint.

    Phase 3: MCP Server Upgrade (Critical - server restart)
    """

    mcp_server_copied: bool
    files_copied: int
    checksums_verified: bool
    dependencies_installed: bool
    post_install_steps: List[Dict]
    server_restarted: bool
    server_restart_time: float
    server_health_check: str  # "passed" | "failed"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Phase3Evidence":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Phase4Evidence:
    """
    Evidence required to pass Phase 4 checkpoint.

    Phase 4: Post-Upgrade Validation
    """

    server_version: str
    tools_registered: int
    expected_tools: int
    browser_tools_enabled: bool
    browser_smoke_test: str
    rag_search_test: str
    workflow_engine_test: str
    file_watchers_active: bool
    rag_index_current: bool
    unit_tests_passed: bool
    validation_report: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Phase4Evidence":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Phase5Evidence:
    """
    Evidence required to pass Phase 5 checkpoint.

    Phase 5: Cleanup & Documentation
    """

    lock_released: bool
    old_backups_archived: int
    upgrade_summary: str
    installation_summary_updated: bool
    update_log_appended: bool
    git_changes_committed: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Phase5Evidence":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class BackupManifest:
    """
    Manifest of backed-up files with checksums.

    Used by BackupManager to verify backup integrity.
    """

    backup_path: str
    timestamp: str
    files: Dict[str, str]  # path -> SHA256 hash
    total_size_bytes: int

    def to_json(self) -> Dict:
        """Serialize to dictionary for JSON file."""
        return {
            "backup_path": self.backup_path,
            "timestamp": self.timestamp,
            "files": self.files,
            "total_size_bytes": self.total_size_bytes,
        }

    @classmethod
    def from_json(cls, data: Dict) -> "BackupManifest":
        """Deserialize from JSON file."""
        return cls(
            backup_path=data["backup_path"],
            timestamp=data["timestamp"],
            files=data["files"],
            total_size_bytes=data["total_size_bytes"],
        )


@dataclass
class UpgradeReport:
    """
    Summary of upgrade operation.

    Used by ReportGenerator to create human-readable reports.
    """

    session_id: str
    workflow_type: str
    started_at: str
    completed_at: str
    duration_seconds: float
    from_version: str
    to_version: str
    phases_completed: List[int]
    phase_summaries: Dict[int, str] = field(default_factory=dict)
    issues_encountered: List[str] = field(default_factory=list)
    rollback_performed: bool = False
    success: bool = True

    def to_markdown(self) -> str:
        """
        Generate human-readable markdown report.

        Returns:
            Formatted markdown string
        """
        lines = [
            "# Agent OS Upgrade Report",
            "",
            f"**Session ID:** {self.session_id}",
            f"**Workflow:** {self.workflow_type}",
            f"**Started:** {self.started_at}",
            f"**Completed:** {self.completed_at}",
            f"**Duration:** {self.duration_seconds:.2f} seconds",
            "",
            "## Upgrade Summary",
            "",
            f"- **From Version:** {self.from_version}",
            f"- **To Version:** {self.to_version}",
            f"- **Status:** {'✅ Success' if self.success else '❌ Failed'}",
            f"- **Rollback Performed:** {'Yes' if self.rollback_performed else 'No'}",
            "",
            "## Phases Completed",
            "",
        ]

        for phase_num in self.phases_completed:
            summary = self.phase_summaries.get(phase_num, "Completed")
            lines.append(f"- **Phase {phase_num}:** {summary}")

        if self.issues_encountered:
            lines.extend(
                [
                    "",
                    "## Issues Encountered",
                    "",
                ]
            )
            for issue in self.issues_encountered:
                lines.append(f"- {issue}")

        lines.extend(
            [
                "",
                "---",
                "",
                f"_Report generated: {datetime.now().isoformat()}_",
            ]
        )

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "UpgradeReport":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class UpgradeWorkflowSession:
    """
    Complete workflow session state for agent_os_upgrade_v1.

    Extends base WorkflowState with upgrade-specific fields.
    """

    session_id: str
    workflow_type: str
    target_file: str
    current_phase: int
    completed_phases: List[int]
    phase_artifacts: Dict[int, Dict]

    # Upgrade-specific fields
    source_path: str
    dry_run: bool = False
    auto_restart: bool = True

    # Timestamps
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Status
    status: str = "in_progress"  # in_progress | completed | failed | rolled_back
    rollback_reason: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "UpgradeWorkflowSession":
        """Create from dictionary."""
        return cls(**data)

    def get_backup_path(self) -> Optional[str]:
        """
        Get backup path from Phase 1 artifacts.

        Returns:
            Backup path if Phase 1 completed, None otherwise
        """
        if 1 in self.completed_phases:
            phase1_artifacts = self.phase_artifacts.get(1, {})
            return phase1_artifacts.get("backup_path")
        return None

    def get_source_version(self) -> Optional[str]:
        """
        Get source version from Phase 0 artifacts.

        Returns:
            Source version if Phase 0 completed, None otherwise
        """
        if 0 in self.completed_phases:
            phase0_artifacts = self.phase_artifacts.get(0, {})
            return phase0_artifacts.get("source_version")
        return None

    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return self.status == "completed" and self.current_phase > 5

    def needs_rollback(self) -> bool:
        """Check if workflow needs rollback."""
        return self.status == "failed" and self.current_phase >= 2
