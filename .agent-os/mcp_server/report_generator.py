"""
Report Generator for Agent OS Upgrade Workflow.

Generates upgrade reports and updates documentation.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates upgrade reports and updates documentation.

    Features:
    - Upgrade summary reports (markdown)
    - Validation reports (JSON)
    - Installation summary updates
    - Update log entries

    Example:
        generator = ReportGenerator()
        report_path = generator.generate_upgrade_summary(session_id, state)
        print(f"Report generated: {report_path}")
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize report generator.

        Args:
            base_path: Optional base path for .agent-os directory
        """
        self.base_path = base_path or Path.cwd()
        self.agent_os_dir = self.base_path / ".agent-os"
        self.cache_dir = self.agent_os_dir / ".cache"

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ReportGenerator initialized")

    def generate_upgrade_summary(self, session_id: str, state: Dict) -> str:
        """
        Generate human-readable upgrade summary in markdown.

        Args:
            session_id: Workflow session ID
            state: Workflow state dictionary

        Returns:
            Path to generated report (as string)
        """
        logger.info("Generating upgrade summary for session: %s", session_id)

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        report_path = self.cache_dir / f"upgrade-summary-{timestamp}.md"

        # Extract data from state
        workflow_type = state.get("workflow_type", "unknown")
        started_at = state.get("metadata", {}).get("started_at", "unknown")
        current_phase = state.get("current_phase", 0)
        completed_phases = state.get("completed_phases", [])
        phase_artifacts = state.get("phase_artifacts", {})

        # Build report content
        content = [
            "# Agent OS Upgrade Summary",
            "",
            f"**Session ID:** {session_id}",
            f"**Workflow:** {workflow_type}",
            f"**Started:** {started_at}",
            f"**Completed:** {datetime.now().isoformat()}",
            "",
            "## Status",
            "",
            f"- **Current Phase:** {current_phase}",
            f"- **Completed Phases:** {', '.join(map(str, completed_phases))}",
            "",
            "## Phase Results",
            "",
        ]

        # Add phase-specific results
        for phase_num, artifacts in phase_artifacts.items():
            content.append(f"### Phase {phase_num}")
            content.append("")

            # Format artifacts as bullet list
            for key, value in artifacts.items():
                content.append(f"- **{key}:** {value}")

            content.append("")

        # Add footer
        content.extend(
            [
                "---",
                "",
                f"_Report generated: {datetime.now().isoformat()}_",
            ]
        )

        # Write report
        report_path.write_text("\n".join(content))

        logger.info("Upgrade summary generated: %s", report_path)

        return str(report_path)

    def generate_validation_report(self, validation_results: Dict) -> str:
        """
        Generate JSON validation report.

        Args:
            validation_results: Dictionary of validation results

        Returns:
            Path to generated report (as string)
        """
        logger.info("Generating validation report")

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        report_path = self.cache_dir / f"upgrade-validation-{timestamp}.json"

        # Add timestamp to results
        report = {
            "generated_at": datetime.now().isoformat(),
            "validation_results": validation_results,
        }

        # Write report
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info("Validation report generated: %s", report_path)

        return str(report_path)

    def update_installation_summary(self, upgrade_info: Dict) -> None:
        """
        Update INSTALLATION_SUMMARY.md with upgrade details.

        Args:
            upgrade_info: Dictionary with upgrade information
        """
        logger.info("Updating installation summary")

        summary_path = self.agent_os_dir / "INSTALLATION_SUMMARY.md"

        # Create upgrade entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        from_version = upgrade_info.get("from_version", "unknown")
        to_version = upgrade_info.get("to_version", "unknown")

        entry = [
            "",
            f"## Upgrade: {timestamp}",
            "",
            f"- **From Version:** {from_version}",
            f"- **To Version:** {to_version}",
            f"- **Status:** {upgrade_info.get('status', 'completed')}",
            "",
        ]

        # Append to file (or create if doesn't exist)
        if summary_path.exists():
            content = summary_path.read_text()
            content += "\n".join(entry)
        else:
            content = "# Agent OS Installation Summary\n\n" + "\n".join(entry)

        summary_path.write_text(content)

        logger.info("Installation summary updated")

    def append_to_update_log(self, version: str, changes: Dict) -> None:
        """
        Append timestamped entry to UPDATE_LOG.txt.

        Args:
            version: Version being upgraded to
            changes: Dictionary of changes made
        """
        logger.info("Appending to update log: version %s", version)

        log_path = self.agent_os_dir / "UPDATE_LOG.txt"

        # Create log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = [
            "",
            f"=== Upgrade to {version} - {timestamp} ===",
            "",
        ]

        # Add change details
        if "new_files" in changes:
            entry.append(f"New files: {changes['new_files']}")
        if "updated_files" in changes:
            entry.append(f"Updated files: {changes['updated_files']}")
        if "conflicts_resolved" in changes:
            entry.append(f"Conflicts resolved: {changes['conflicts_resolved']}")

        entry.append("")

        # Append to file
        if log_path.exists():
            content = log_path.read_text()
            content += "\n".join(entry)
        else:
            content = "Agent OS Update Log\n\n" + "\n".join(entry)

        log_path.write_text(content)

        logger.info("Update log appended")
