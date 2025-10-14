"""
Workflow Structure Validator.

Validates workflow directories against workflow-construction-standards.md.
Enforces:
- Standard directory structure
- File naming conventions (phase.md, task-N-name.md)
- File size guidelines (phase.md ~80 lines, task files 100-170 lines)
- Required metadata.json presence
"""

# pylint: disable=broad-exception-caught,missing-raises-doc
# Justification: Validator uses broad exceptions for robustness,
# standard exception documentation in docstrings

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class WorkflowValidator:
    """Validates workflow structure against Agent OS standards."""

    # File size guidelines from workflow-construction-standards.md
    PHASE_FILE_TARGET = 80
    PHASE_FILE_MAX = 90
    TASK_FILE_TARGET_MAX = 100  # Target: keep under 100 if possible
    TASK_FILE_ACCEPTABLE_MAX = 150  # Acceptable: 100-150 lines
    TASK_FILE_ABSOLUTE_MAX = 170  # Hard limit: must split if exceeded

    def __init__(self, workflow_path: Path):
        """
        Initialize validator.

        :param workflow_path: Path to workflow directory
            (e.g., universal/workflows/my_workflow_v1)
        """
        self.workflow_path = Path(workflow_path)
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []

    def validate(self) -> Dict[str, Any]:
        """
        Validate workflow structure comprehensively.

        :returns: Validation report with compliance status and issues
        """
        self.issues = []
        self.warnings = []

        # Core validations
        self._validate_workflow_exists()
        self._validate_metadata_json()
        self._validate_phase_structure()
        self._validate_file_naming()
        self._validate_file_sizes()

        # Calculate compliance score
        total_checks = len(self.issues) + len(self.warnings)
        compliance_score = (
            100
            if total_checks == 0
            else max(0, 100 - (len(self.issues) * 10 + len(self.warnings) * 3))
        )

        return {
            "workflow_path": str(self.workflow_path),
            "compliant": len(self.issues) == 0,
            "compliance_score": compliance_score,
            "issues": self.issues,
            "warnings": self.warnings,
            "summary": self._generate_summary(),
        }

    def _validate_workflow_exists(self) -> None:
        """Validate workflow directory exists."""
        if not self.workflow_path.exists():
            self.issues.append(
                {
                    "type": "missing_directory",
                    "severity": "critical",
                    "message": (
                        f"Workflow directory does not exist: {self.workflow_path}"
                    ),
                }
            )
        elif not self.workflow_path.is_dir():
            self.issues.append(
                {
                    "type": "not_directory",
                    "severity": "critical",
                    "message": (
                        f"Path exists but is not a directory: {self.workflow_path}"
                    ),
                }
            )

    def _validate_metadata_json(self) -> None:
        """Validate metadata.json exists and is valid."""
        metadata_path = self.workflow_path / "metadata.json"

        if not metadata_path.exists():
            self.issues.append(
                {
                    "type": "missing_metadata",
                    "severity": "critical",
                    "path": "metadata.json",
                    "message": "Required metadata.json file is missing",
                }
            )
            return

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Validate required fields
            required_fields = [
                "workflow_type",
                "version",
                "description",
                "total_phases",
                "estimated_duration",
                "primary_outputs",
                "phases",
            ]

            for field in required_fields:
                if field not in metadata:
                    self.issues.append(
                        {
                            "type": "missing_metadata_field",
                            "severity": "error",
                            "path": "metadata.json",
                            "field": field,
                            "message": (
                                f"Required field '{field}' missing in metadata.json"
                            ),
                        }
                    )

            # Validate phases array matches total_phases
            if "phases" in metadata and "total_phases" in metadata:
                if len(metadata["phases"]) != metadata["total_phases"]:
                    self.issues.append(
                        {
                            "type": "phase_count_mismatch",
                            "severity": "error",
                            "path": "metadata.json",
                            "expected": metadata["total_phases"],
                            "actual": len(metadata["phases"]),
                            "message": (
                                f"total_phases ({metadata['total_phases']}) doesn't "
                                f"match phases array length ({len(metadata['phases'])})"
                            ),
                        }
                    )

        except json.JSONDecodeError as e:
            self.issues.append(
                {
                    "type": "invalid_json",
                    "severity": "critical",
                    "path": "metadata.json",
                    "message": f"Invalid JSON in metadata.json: {str(e)}",
                }
            )

    def _validate_phase_structure(self) -> None:
        """Validate phase directory structure."""
        phases_dir = self.workflow_path / "phases"

        if not phases_dir.exists():
            self.issues.append(
                {
                    "type": "missing_phases_dir",
                    "severity": "critical",
                    "path": "phases/",
                    "message": "Required phases/ directory is missing",
                }
            )
            return

        # Check for phase directories (0, 1, 2, etc.)
        phase_dirs = [
            d for d in phases_dir.iterdir() if d.is_dir() and d.name.isdigit()
        ]

        if not phase_dirs:
            self.issues.append(
                {
                    "type": "no_phase_directories",
                    "severity": "error",
                    "path": "phases/",
                    "message": (
                        "No phase directories found "
                        "(expected phases/0/, phases/1/, etc.)"
                    ),
                }
            )
            return

        # Validate each phase directory
        for phase_dir in sorted(phase_dirs, key=lambda d: int(d.name)):
            self._validate_phase_directory(phase_dir)

    def _validate_phase_directory(self, phase_dir: Path) -> None:
        """
        Validate individual phase directory.

        :param phase_dir: Path to phase directory (e.g., phases/0/)
        """
        phase_num = phase_dir.name
        phase_md = phase_dir / "phase.md"

        # Check for phase.md (standard) vs README.md (non-standard)
        if not phase_md.exists():
            readme_md = phase_dir / "README.md"
            if readme_md.exists():
                self.issues.append(
                    {
                        "type": "wrong_phase_filename",
                        "severity": "error",
                        "path": str(readme_md.relative_to(self.workflow_path)),
                        "expected": f"phases/{phase_num}/phase.md",
                        "actual": f"phases/{phase_num}/README.md",
                        "message": (
                            f"Phase {phase_num} uses README.md instead of phase.md "
                            f"(violates workflow-construction-standards.md)"
                        ),
                    }
                )
            else:
                self.issues.append(
                    {
                        "type": "missing_phase_file",
                        "severity": "error",
                        "path": f"phases/{phase_num}/",
                        "message": f"Phase {phase_num} missing required phase.md file",
                    }
                )

        # Check for task files
        task_files = list(phase_dir.glob("task-*.md"))
        if not task_files:
            self.warnings.append(
                {
                    "type": "no_task_files",
                    "severity": "warning",
                    "path": f"phases/{phase_num}/",
                    "message": (
                        f"Phase {phase_num} has no task files "
                        f"(expected task-1-*.md, task-2-*.md, etc.)"
                    ),
                }
            )

    def _validate_file_naming(self) -> None:
        """Validate file naming conventions."""
        phases_dir = self.workflow_path / "phases"

        if not phases_dir.exists():
            return

        # Check for monolithic phase files (anti-pattern)
        monolithic_files = list(phases_dir.glob("*.md"))
        for monolithic_file in monolithic_files:
            self.issues.append(
                {
                    "type": "monolithic_phase_file",
                    "severity": "error",
                    "path": str(monolithic_file.relative_to(self.workflow_path)),
                    "message": (
                        f"Found monolithic phase file {monolithic_file.name}. "
                        f"Should use phases/N/ directories with phase.md instead."
                    ),
                    "fix": (
                        "Split into phases/N/phase.md + "
                        "phases/N/task-N-name.md files"
                    ),
                }
            )

        # Validate task file naming
        for phase_dir in phases_dir.glob("*/"):
            if not phase_dir.is_dir() or not phase_dir.name.isdigit():
                continue

            for task_file in phase_dir.glob("*.md"):
                if task_file.name == "phase.md":
                    continue

                # Task files must follow task-N-name.md pattern
                if not task_file.name.startswith("task-"):
                    self.warnings.append(
                        {
                            "type": "non_standard_task_name",
                            "severity": "warning",
                            "path": str(task_file.relative_to(self.workflow_path)),
                            "message": (
                                f"Task file {task_file.name} doesn't follow "
                                f"task-N-name.md convention"
                            ),
                        }
                    )

    def _validate_file_sizes(self) -> None:
        """Validate file sizes against guidelines."""
        phases_dir = self.workflow_path / "phases"

        if not phases_dir.exists():
            return

        for phase_dir in phases_dir.glob("*/"):
            if not phase_dir.is_dir() or not phase_dir.name.isdigit():
                continue

            phase_num = phase_dir.name

            # Check phase.md size
            phase_md = phase_dir / "phase.md"
            if phase_md.exists():
                line_count = len(phase_md.read_text().splitlines())

                if line_count > self.PHASE_FILE_MAX:
                    self.warnings.append(
                        {
                            "type": "phase_file_too_large",
                            "severity": "warning",
                            "path": str(phase_md.relative_to(self.workflow_path)),
                            "lines": line_count,
                            "target": self.PHASE_FILE_TARGET,
                            "max": self.PHASE_FILE_MAX,
                            "message": (
                                f"phase.md in Phase {phase_num} has {line_count} lines "
                                f"(target ~{self.PHASE_FILE_TARGET}, "
                                f"max {self.PHASE_FILE_MAX})"
                            ),
                            "recommendation": (
                                "Consider splitting tasks into separate files or "
                                "reducing overview content"
                            ),
                        }
                    )

            # Check task file sizes
            for task_file in phase_dir.glob("task-*.md"):
                line_count = len(task_file.read_text().splitlines())

                if line_count > self.TASK_FILE_ABSOLUTE_MAX:
                    # ERROR: Exceeds absolute maximum - must split
                    self.issues.append(
                        {
                            "type": "task_file_exceeds_limit",
                            "severity": "error",
                            "path": str(task_file.relative_to(self.workflow_path)),
                            "lines": line_count,
                            "max": self.TASK_FILE_ABSOLUTE_MAX,
                            "message": (
                                f"Task file {task_file.name} has {line_count} lines "
                                f"(absolute max {self.TASK_FILE_ABSOLUTE_MAX})"
                            ),
                            "fix": (
                                "MUST split into multiple smaller task files "
                                "(horizontal scaling required)"
                            ),
                        }
                    )
                elif line_count > self.TASK_FILE_ACCEPTABLE_MAX:
                    # WARNING: In 150-170 range - at the limit
                    self.warnings.append(
                        {
                            "type": "task_file_at_limit",
                            "severity": "warning",
                            "path": str(task_file.relative_to(self.workflow_path)),
                            "lines": line_count,
                            "acceptable_max": self.TASK_FILE_ACCEPTABLE_MAX,
                            "absolute_max": self.TASK_FILE_ABSOLUTE_MAX,
                            "message": (
                                f"Task file {task_file.name} has {line_count} lines "
                                f"(acceptable max {self.TASK_FILE_ACCEPTABLE_MAX}, "
                                f"absolute max {self.TASK_FILE_ABSOLUTE_MAX})"
                            ),
                            "recommendation": (
                                f"Consider splitting if approaching "
                                f"{self.TASK_FILE_ABSOLUTE_MAX} lines"
                            ),
                        }
                    )
                elif line_count > self.TASK_FILE_TARGET_MAX:
                    # INFO: In 100-150 range - acceptable but could be smaller
                    self.warnings.append(
                        {
                            "type": "task_file_large",
                            "severity": "info",
                            "path": str(task_file.relative_to(self.workflow_path)),
                            "lines": line_count,
                            "target_max": self.TASK_FILE_TARGET_MAX,
                            "message": (
                                f"Task file {task_file.name} has {line_count} lines "
                                f"(target <{self.TASK_FILE_TARGET_MAX}, "
                                f"acceptable up to {self.TASK_FILE_ACCEPTABLE_MAX})"
                            ),
                            "note": (
                                "Acceptable size, but consider simplifying if possible"
                            ),
                        }
                    )
                # Files ≤100 lines: Perfect! No warning needed

    def _generate_summary(self) -> str:
        """Generate human-readable summary."""
        if not self.issues and not self.warnings:
            return "✅ Workflow structure is fully compliant with standards"

        summary_parts = []

        if self.issues:
            summary_parts.append(f"❌ {len(self.issues)} critical issue(s) found")

        if self.warnings:
            summary_parts.append(f"⚠️  {len(self.warnings)} warning(s) found")

        return " | ".join(summary_parts)

    def print_report(self, report: Optional[Dict] = None) -> None:
        """
        Print formatted validation report to console.

        :param report: Validation report (if None, runs validation)
        """
        if report is None:
            report = self.validate()

        print(f"\n{'='*70}")
        print("Workflow Structure Validation Report")
        print(f"{'='*70}")
        print(f"Workflow: {report['workflow_path']}")
        print(f"Compliance Score: {report['compliance_score']}/100")
        print(
            f"Status: {'✅ COMPLIANT' if report['compliant'] else '❌ NON-COMPLIANT'}"
        )
        print(f"{'='*70}\n")

        if report["issues"]:
            print(f"🚨 CRITICAL ISSUES ({len(report['issues'])}):\n")
            for issue in report["issues"]:
                print(f"  [{issue['severity'].upper()}] {issue['type']}")
                print(f"  Path: {issue.get('path', 'N/A')}")
                print(f"  {issue['message']}")
                if "fix" in issue:
                    print(f"  Fix: {issue['fix']}")
                print()

        if report["warnings"]:
            print(f"⚠️  WARNINGS ({len(report['warnings'])}):\n")
            for warning in report["warnings"]:
                print(f"  [{warning['severity'].upper()}] {warning['type']}")
                print(f"  Path: {warning.get('path', 'N/A')}")
                print(f"  {warning['message']}")
                if "recommendation" in warning:
                    print(f"  Recommendation: {warning['recommendation']}")
                print()

        if not report["issues"] and not report["warnings"]:
            print("✅ No issues found - workflow structure is fully compliant!\n")

        print(f"{'='*70}\n")


def validate_workflow(workflow_path: str) -> Dict[str, Any]:
    """
    Validate workflow structure (convenience function).

    :param workflow_path: Path to workflow directory
    :returns: Validation report
    """
    validator = WorkflowValidator(Path(workflow_path))
    return validator.validate()
