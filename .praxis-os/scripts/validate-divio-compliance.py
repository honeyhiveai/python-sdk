#!/usr/bin/env python3
"""
Divio Documentation Compliance Validator

Validates documentation against Divio framework compliance criteria.

Usage:
    python validate-divio-compliance.py                    # Run validation, exit 0 if ≥90%
    python validate-divio-compliance.py --strict           # Require 100% compliance
    python validate-divio-compliance.py --report           # Generate markdown report
    python validate-divio-compliance.py --report --strict  # Both

Exit Codes:
    0: Compliance threshold met
    1: Compliance below threshold

Validation Rules:
    - Frontmatter: doc_type field must exist and be valid
    - Tutorials: Learning goals, step-by-step structure, "What You Learned" section
    - How-To: Goal statement, numbered steps, prerequisites
    - Reference: Structured information, minimal prose patterns
    - Explanation: Background, concepts, trade-offs discussions
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ANSI color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


@dataclass
class Violation:
    """Represents a compliance violation"""

    rule: str
    severity: str  # 'error' or 'warning'
    message: str
    line_number: Optional[int] = None
    remediation: Optional[str] = None


@dataclass
class FileResult:
    """Validation result for a single file"""

    file_path: str
    doc_type: Optional[str]
    compliance_score: float
    violations: List[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.compliance_score >= 90.0


class DivioValidator:
    """Validates documentation against Divio compliance criteria"""

    VALID_DOC_TYPES = {"tutorial", "how-to", "reference", "explanation"}

    def __init__(self, content_dir: str = "docs/content"):
        self.content_dir = Path(content_dir)
        self.results: List[FileResult] = []

    def validate_all(self) -> List[FileResult]:
        """Validate all markdown files in content directory"""
        if not self.content_dir.exists():
            print(
                f"{Colors.RED}Error: Content directory not found: {self.content_dir}{Colors.RESET}"
            )
            sys.exit(1)

        md_files = list(self.content_dir.rglob("*.md"))

        if not md_files:
            print(
                f"{Colors.YELLOW}Warning: No markdown files found in {self.content_dir}{Colors.RESET}"
            )
            return []

        for md_file in md_files:
            result = self.validate_file(md_file)
            self.results.append(result)

        return self.results

    def validate_file(self, file_path: Path) -> FileResult:
        """Validate a single markdown file"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        violations = []

        # Parse frontmatter
        frontmatter, doc_type = self._parse_frontmatter(content)

        # Validate frontmatter
        violations.extend(self._validate_frontmatter(frontmatter))

        # Validate content patterns based on doc type
        if doc_type:
            violations.extend(self._validate_content_patterns(content, doc_type))

        # Calculate compliance score
        total_checks = self._count_total_checks(doc_type)
        violations_count = len([v for v in violations if v.severity == "error"])
        compliance_score = (
            max(0, (total_checks - violations_count) / total_checks * 100)
            if total_checks > 0
            else 0
        )

        return FileResult(
            file_path=str(file_path.relative_to(self.content_dir.parent)),
            doc_type=doc_type,
            compliance_score=compliance_score,
            violations=violations,
        )

    def _parse_frontmatter(self, content: str) -> Tuple[Dict[str, str], Optional[str]]:
        """Extract frontmatter from markdown content"""
        frontmatter = {}
        doc_type = None

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                fm_content = parts[1]
                for line in fm_content.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        frontmatter[key] = value
                        if key == "doc_type":
                            doc_type = value

        return frontmatter, doc_type

    def _validate_frontmatter(self, frontmatter: Dict[str, str]) -> List[Violation]:
        """Validate frontmatter fields"""
        violations = []

        # Check doc_type exists
        if "doc_type" not in frontmatter:
            violations.append(
                Violation(
                    rule="frontmatter_doc_type",
                    severity="error",
                    message="Missing required frontmatter field: doc_type",
                    remediation='Add "doc_type: tutorial|how-to|reference|explanation" to frontmatter',
                )
            )
        elif frontmatter["doc_type"] not in self.VALID_DOC_TYPES:
            violations.append(
                Violation(
                    rule="frontmatter_doc_type_valid",
                    severity="error",
                    message=f"Invalid doc_type: {frontmatter['doc_type']}",
                    remediation=f'Use one of: {", ".join(self.VALID_DOC_TYPES)}',
                )
            )

        # Check sidebar_position (optional but recommended)
        if "sidebar_position" not in frontmatter:
            violations.append(
                Violation(
                    rule="frontmatter_sidebar_position",
                    severity="warning",
                    message="Missing recommended frontmatter field: sidebar_position",
                    remediation='Add "sidebar_position: N" to control sidebar ordering',
                )
            )

        return violations

    def _validate_content_patterns(
        self, content: str, doc_type: str
    ) -> List[Violation]:
        """Validate content patterns based on doc type"""
        if doc_type == "tutorial":
            return self._validate_tutorial(content)
        elif doc_type == "how-to":
            return self._validate_how_to(content)
        elif doc_type == "reference":
            return self._validate_reference(content)
        elif doc_type == "explanation":
            return self._validate_explanation(content)
        return []

    def _validate_tutorial(self, content: str) -> List[Violation]:
        """Validate tutorial-specific patterns"""
        violations = []

        # Check for learning goals/objectives
        if not re.search(
            r"(?i)(learning|learn|objectives?|goals?|you will learn)", content
        ):
            violations.append(
                Violation(
                    rule="tutorial_learning_goals",
                    severity="error",
                    message="Tutorial missing explicit learning goals/objectives",
                    remediation='Add section describing what users will learn (e.g., "What You\'ll Learn", "Learning Objectives")',
                )
            )

        # Check for step-by-step structure (numbered steps or clear progression)
        step_patterns = [
            r"##\s+Step \d+",
            r"\d+\.\s+",
            r"(?i)first|second|third|next|then|finally",
        ]
        has_steps = any(re.search(pattern, content) for pattern in step_patterns)
        if not has_steps:
            violations.append(
                Violation(
                    rule="tutorial_step_structure",
                    severity="error",
                    message="Tutorial missing clear step-by-step structure",
                    remediation="Structure tutorial with numbered steps or clear progression (Step 1, Step 2, etc.)",
                )
            )

        # Check for "What You Learned" or summary section
        if not re.search(
            r"(?i)(what (you|you\'ve) learned|summary|conclusion|recap)", content
        ):
            violations.append(
                Violation(
                    rule="tutorial_summary",
                    severity="warning",
                    message='Tutorial missing "What You Learned" or summary section',
                    remediation="Add summary section at end reinforcing what was learned",
                )
            )

        return violations

    def _validate_how_to(self, content: str) -> List[Violation]:
        """Validate how-to guide patterns"""
        violations = []

        # Check for goal statement (what problem this solves)
        if not re.search(
            r"(?i)(this (guide|how-to) (shows?|explains?|demonstrates?)|problem|solution|goal)",
            content[:500],
        ):
            violations.append(
                Violation(
                    rule="howto_goal_statement",
                    severity="error",
                    message="How-To guide missing clear goal/problem statement",
                    remediation="Add goal statement near top explaining what problem this solves",
                )
            )

        # Check for numbered steps
        if not re.search(r"\d+\.\s+\w+", content):
            violations.append(
                Violation(
                    rule="howto_numbered_steps",
                    severity="error",
                    message="How-To guide missing numbered steps",
                    remediation="Structure guide with numbered steps (1., 2., 3., etc.)",
                )
            )

        # Check for prerequisites
        if not re.search(
            r"(?i)(prerequisite|requirement|before you begin|you (will )?need)", content
        ):
            violations.append(
                Violation(
                    rule="howto_prerequisites",
                    severity="warning",
                    message="How-To guide missing prerequisites section",
                    remediation="Add section listing prerequisites or requirements",
                )
            )

        return violations

    def _validate_reference(self, content: str) -> List[Violation]:
        """Validate reference documentation patterns"""
        violations = []

        # Check for structured information (tables, lists, code blocks)
        has_structure = bool(
            re.search(r"\|.*\|", content)  # Tables
            or re.search(r"^[-*+]\s+", content, re.MULTILINE)  # Lists
            or re.search(r"```", content)  # Code blocks
        )
        if not has_structure:
            violations.append(
                Violation(
                    rule="reference_structured_info",
                    severity="error",
                    message="Reference doc missing structured information (tables, lists, code examples)",
                    remediation="Add tables, lists, or code examples to structure the reference information",
                )
            )

        # Check for excessive prose (reference should be information-dense)
        paragraphs = re.split(r"\n\n+", content)
        long_paragraphs = [
            p for p in paragraphs if len(p) > 500 and not p.startswith("```")
        ]
        if len(long_paragraphs) > 3:
            violations.append(
                Violation(
                    rule="reference_minimal_prose",
                    severity="warning",
                    message=f"Reference has {len(long_paragraphs)} long prose paragraphs (keep reference concise)",
                    remediation="Break long paragraphs into lists, tables, or shorter sections",
                )
            )

        return violations

    def _validate_explanation(self, content: str) -> List[Violation]:
        """Validate explanation documentation patterns"""
        violations = []

        # Check for background/context
        if not re.search(
            r"(?i)(background|context|why|history|motivation)", content[:1000]
        ):
            violations.append(
                Violation(
                    rule="explanation_background",
                    severity="error",
                    message="Explanation missing background/context section",
                    remediation="Add section providing background or context for the topic",
                )
            )

        # Check for concept explanations
        heading_count = len(re.findall(r"^#{2,4}\s+", content, re.MULTILINE))
        if heading_count < 3:
            violations.append(
                Violation(
                    rule="explanation_concepts",
                    severity="warning",
                    message=f"Explanation has only {heading_count} concept sections (expected 3+)",
                    remediation="Break explanation into multiple concept sections with headings",
                )
            )

        # Check for trade-offs/comparisons
        if not re.search(
            r"(?i)(trade-?off|advantage|disadvantage|benefit|drawback|comparison|versus|vs\.)",
            content,
        ):
            violations.append(
                Violation(
                    rule="explanation_tradeoffs",
                    severity="warning",
                    message="Explanation missing discussion of trade-offs or comparisons",
                    remediation="Add section discussing trade-offs, benefits, or comparisons",
                )
            )

        return violations

    def _count_total_checks(self, doc_type: Optional[str]) -> int:
        """Count total validation checks for a doc type"""
        base_checks = 2  # frontmatter checks
        if doc_type == "tutorial":
            return base_checks + 3
        elif doc_type == "how-to":
            return base_checks + 3
        elif doc_type == "reference":
            return base_checks + 2
        elif doc_type == "explanation":
            return base_checks + 3
        return base_checks

    def print_results(self, strict: bool = False):
        """Print validation results to console"""
        if not self.results:
            print(f"{Colors.YELLOW}No files validated{Colors.RESET}")
            return

        # Sort by compliance score
        self.results.sort(key=lambda r: r.compliance_score)

        # Print per-file results
        print(f"\n{Colors.BOLD}Divio Compliance Validation Results{Colors.RESET}")
        print("=" * 80)

        for result in self.results:
            score_color = (
                Colors.GREEN
                if result.compliance_score >= 90
                else Colors.YELLOW if result.compliance_score >= 70 else Colors.RED
            )
            print(f"\n{Colors.BOLD}{result.file_path}{Colors.RESET}")
            print(f"  Doc Type: {result.doc_type or 'MISSING'}")
            print(
                f"  Compliance: {score_color}{result.compliance_score:.1f}%{Colors.RESET}"
            )

            if result.violations:
                print(f"  Violations:")
                for v in result.violations:
                    severity_color = (
                        Colors.RED if v.severity == "error" else Colors.YELLOW
                    )
                    print(
                        f"    {severity_color}[{v.severity.upper()}]{Colors.RESET} {v.message}"
                    )
                    if v.remediation:
                        print(f"      → {v.remediation}")

        # Print summary
        print(f"\n{Colors.BOLD}Summary{Colors.RESET}")
        print("=" * 80)

        total_files = len(self.results)
        passed_files = len([r for r in self.results if r.passed])
        avg_compliance = sum(r.compliance_score for r in self.results) / total_files

        summary_color = (
            Colors.GREEN
            if avg_compliance >= 90
            else Colors.YELLOW if avg_compliance >= 70 else Colors.RED
        )

        print(f"Total Files: {total_files}")
        print(f"Passed (≥90%): {passed_files}")
        print(f"Failed (<90%): {total_files - passed_files}")
        print(f"Average Compliance: {summary_color}{avg_compliance:.1f}%{Colors.RESET}")

        threshold = 100.0 if strict else 90.0
        threshold_met = avg_compliance >= threshold

        print(
            f"\nThreshold: {threshold:.0f}% ({'STRICT' if strict else 'NORMAL'} mode)"
        )
        print(
            f"Status: {Colors.GREEN if threshold_met else Colors.RED}{'PASS' if threshold_met else 'FAIL'}{Colors.RESET}"
        )

    def generate_report(self, output_path: str = "divio-compliance-report.md"):
        """Generate markdown compliance report"""
        with open(output_path, "w") as f:
            f.write("# Divio Documentation Compliance Report\n\n")
            f.write(f"**Generated:** {self._get_timestamp()}\n\n")

            # Summary
            total_files = len(self.results)
            passed_files = len([r for r in self.results if r.passed])
            avg_compliance = (
                sum(r.compliance_score for r in self.results) / total_files
                if total_files > 0
                else 0
            )

            f.write("## Summary\n\n")
            f.write(f"- **Total Files:** {total_files}\n")
            f.write(f"- **Passed (≥90%):** {passed_files}\n")
            f.write(f"- **Failed (<90%):** {total_files - passed_files}\n")
            f.write(f"- **Average Compliance:** {avg_compliance:.1f}%\n\n")

            # Files by compliance
            f.write("## Files by Compliance\n\n")
            for result in sorted(
                self.results, key=lambda r: r.compliance_score, reverse=True
            ):
                status = "✅" if result.passed else "❌"
                f.write(
                    f"{status} **{result.file_path}** - {result.compliance_score:.1f}%\n"
                )

            # Detailed violations
            f.write("\n## Detailed Violations\n\n")
            for result in self.results:
                if result.violations:
                    f.write(f"### {result.file_path}\n\n")
                    f.write(f"**Compliance:** {result.compliance_score:.1f}%\n\n")
                    for v in result.violations:
                        f.write(f"- **[{v.severity.upper()}]** {v.message}\n")
                        if v.remediation:
                            f.write(f"  - *Remediation:* {v.remediation}\n")
                    f.write("\n")

        print(f"\n{Colors.GREEN}Report generated: {output_path}{Colors.RESET}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    parser = argparse.ArgumentParser(
        description="Validate documentation against Divio compliance criteria",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--strict", action="store_true", help="Require 100%% compliance (default: 90%%)"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate markdown compliance report"
    )
    parser.add_argument(
        "--content-dir",
        default="docs/content",
        help="Content directory to validate (default: docs/content)",
    )

    args = parser.parse_args()

    validator = DivioValidator(content_dir=args.content_dir)
    validator.validate_all()
    validator.print_results(strict=args.strict)

    if args.report:
        validator.generate_report()

    # Exit with appropriate code
    if validator.results:
        total_files = len(validator.results)
        avg_compliance = (
            sum(r.compliance_score for r in validator.results) / total_files
        )
        threshold = 100.0 if args.strict else 90.0
        sys.exit(0 if avg_compliance >= threshold else 1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
