#!/usr/bin/env python3
"""
Validate Agent OS file size constraints.

This is a QUALITY IMPROVEMENT TOOL, not a blocking pre-commit gate.
Use during Agent OS retrospective/improvement sessions, not on every commit.

Usage:
    python .agent-os/scripts/validate-file-sizes.py           # Summary report
    python .agent-os/scripts/validate-file-sizes.py --verbose # Detailed analysis
    python .agent-os/scripts/validate-file-sizes.py --strict  # Exit 1 on violations
    
Philosophy:
    - Agent OS documentation is a living, iterative improvement process
    - File size targets are quality goals, not commit blockers
    - Production code quality gates block commits; meta-docs improve continuously
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Tier 1: Side-loaded context files (optimal AI processing)
TIER_1_DIRS = [
    ".agent-os/standards/ai-assistant/code-generation/tests/v3/phases",
    ".agent-os/standards/ai-assistant/code-generation/tests/v3/tasks",
    ".agent-os/standards/ai-assistant/code-generation/tests/v3/core",
]
TIER_1_TARGET = 100
TIER_1_PRACTICAL = 150  # Reality check: some files need more context

# Tier 2: Active read files (focused reading sessions)
TIER_2_DIRS = [
    ".agent-os/standards/ai-assistant/code-generation/tests/v3",
    ".agent-os/standards/ai-assistant/code-generation/production/v2",
]
TIER_2_TARGET = 500


def analyze_file_sizes(strict_mode: bool = False) -> Tuple[List[str], Dict[str, List[Tuple[Path, int]]]]:
    """
    Analyze Agent OS file sizes against targets.
    
    Args:
        strict_mode: Use strict 100-line limit vs practical 150-line limit
        
    Returns:
        Tuple of (violations, analysis_by_tier)
    """
    violations: List[str] = []
    analysis: Dict[str, List[Tuple[Path, int]]] = {
        "tier_1_compliant": [],
        "tier_1_over_target": [],
        "tier_1_violations": [],
        "tier_2_compliant": [],
        "tier_2_violations": [],
    }
    
    tier_1_limit = TIER_1_TARGET if strict_mode else TIER_1_PRACTICAL
    
    # Analyze Tier 1 files
    for dir_path in TIER_1_DIRS:
        full_dir = Path(__file__).parent.parent / dir_path
        if not full_dir.exists():
            continue
            
        for file_path in full_dir.rglob("*.md"):
            line_count = len(file_path.read_text().splitlines())
            relative_path = file_path.relative_to(Path(__file__).parent.parent)
            
            if line_count <= TIER_1_TARGET:
                analysis["tier_1_compliant"].append((relative_path, line_count))
            elif line_count <= tier_1_limit:
                analysis["tier_1_over_target"].append((relative_path, line_count))
            else:
                analysis["tier_1_violations"].append((relative_path, line_count))
                violations.append(
                    f"  - {relative_path}: {line_count} lines "
                    f"(target ≤{TIER_1_TARGET}, practical ≤{tier_1_limit})"
                )
    
    # Analyze Tier 2 files
    for dir_path in TIER_2_DIRS:
        full_dir = Path(__file__).parent.parent / dir_path
        if not full_dir.exists():
            continue
            
        for file_path in full_dir.rglob("*.md"):
            # Skip Tier 1 files already counted
            if any(str(file_path.relative_to(Path(__file__).parent.parent)).startswith(t1) 
                   for t1 in TIER_1_DIRS):
                continue
                
            line_count = len(file_path.read_text().splitlines())
            relative_path = file_path.relative_to(Path(__file__).parent.parent)
            
            if line_count <= TIER_2_TARGET:
                analysis["tier_2_compliant"].append((relative_path, line_count))
            else:
                analysis["tier_2_violations"].append((relative_path, line_count))
                violations.append(
                    f"  - {relative_path}: {line_count} lines (target ≤{TIER_2_TARGET})"
                )
    
    return violations, analysis


def print_summary_report(violations: List[str], analysis: Dict[str, List[Tuple[Path, int]]]) -> None:
    """Print summary report of file size analysis."""
    print("\n" + "="*80)
    print("📊 Agent OS File Size Analysis - Quality Improvement Report")
    print("="*80)
    
    # Tier 1 Summary
    tier_1_total = (
        len(analysis["tier_1_compliant"]) + 
        len(analysis["tier_1_over_target"]) + 
        len(analysis["tier_1_violations"])
    )
    tier_1_compliant = len(analysis["tier_1_compliant"])
    tier_1_over = len(analysis["tier_1_over_target"])
    tier_1_violations = len(analysis["tier_1_violations"])
    
    print(f"\n📁 TIER 1 (Side-Loaded Context Files):")
    print(f"   Target: ≤100 lines (optimal AI processing)")
    print(f"   Practical: ≤150 lines (acceptable)")
    print(f"   Total Files: {tier_1_total}")
    print(f"   ✅ Within target (≤100): {tier_1_compliant} files")
    print(f"   ⚠️  Over target (101-150): {tier_1_over} files")
    print(f"   🔴 Exceeds practical (>150): {tier_1_violations} files")
    
    if tier_1_violations > 0:
        print(f"\n   🔴 Files Exceeding Practical Limit:")
        for path, lines in sorted(analysis["tier_1_violations"], key=lambda x: x[1], reverse=True):
            print(f"      - {path}: {lines} lines")
    
    # Tier 2 Summary
    tier_2_total = len(analysis["tier_2_compliant"]) + len(analysis["tier_2_violations"])
    tier_2_compliant = len(analysis["tier_2_compliant"])
    tier_2_violations = len(analysis["tier_2_violations"])
    
    print(f"\n📚 TIER 2 (Active Read Files):")
    print(f"   Target: ≤500 lines (focused reading)")
    print(f"   Total Files: {tier_2_total}")
    print(f"   ✅ Within target: {tier_2_compliant} files")
    print(f"   🔴 Exceeds target: {tier_2_violations} files")
    
    if tier_2_violations > 0:
        print(f"\n   🔴 Files Exceeding Target:")
        for path, lines in sorted(analysis["tier_2_violations"], key=lambda x: x[1], reverse=True):
            print(f"      - {path}: {lines} lines")
    
    # Overall Assessment
    print(f"\n{'='*80}")
    if violations:
        print(f"⚠️  {len(violations)} file size improvement opportunities identified")
        print("\nℹ️  These are QUALITY IMPROVEMENT targets, not blocking issues")
        print("ℹ️  Address during Agent OS retrospective/improvement sessions")
    else:
        print("✅ All files within size targets - excellent file organization!")
    print(f"{'='*80}\n")


def print_verbose_report(analysis: Dict[str, List[Tuple[Path, int]]]) -> None:
    """Print detailed verbose report."""
    print("\n" + "="*80)
    print("📊 DETAILED FILE SIZE ANALYSIS")
    print("="*80)
    
    # Tier 1 Compliant
    if analysis["tier_1_compliant"]:
        print(f"\n✅ TIER 1 COMPLIANT (≤100 lines): {len(analysis['tier_1_compliant'])} files")
        for path, lines in sorted(analysis["tier_1_compliant"], key=lambda x: x[1]):
            print(f"   {lines:3d} lines - {path}")
    
    # Tier 1 Over Target
    if analysis["tier_1_over_target"]:
        print(f"\n⚠️  TIER 1 OVER TARGET (101-150 lines): {len(analysis['tier_1_over_target'])} files")
        for path, lines in sorted(analysis["tier_1_over_target"], key=lambda x: x[1], reverse=True):
            print(f"   {lines:3d} lines - {path}")
    
    # Tier 1 Violations
    if analysis["tier_1_violations"]:
        print(f"\n🔴 TIER 1 VIOLATIONS (>150 lines): {len(analysis['tier_1_violations'])} files")
        for path, lines in sorted(analysis["tier_1_violations"], key=lambda x: x[1], reverse=True):
            print(f"   {lines:3d} lines - {path} (consider splitting)")
    
    # Tier 2 Compliant
    if analysis["tier_2_compliant"]:
        print(f"\n✅ TIER 2 COMPLIANT (≤500 lines): {len(analysis['tier_2_compliant'])} files")
        for path, lines in sorted(analysis["tier_2_compliant"], key=lambda x: x[1]):
            print(f"   {lines:3d} lines - {path}")
    
    # Tier 2 Violations
    if analysis["tier_2_violations"]:
        print(f"\n🔴 TIER 2 VIOLATIONS (>500 lines): {len(analysis['tier_2_violations'])} files")
        for path, lines in sorted(analysis["tier_2_violations"], key=lambda x: x[1], reverse=True):
            print(f"   {lines:3d} lines - {path} (consider refactoring)")
    
    print()


def main() -> int:
    """Execute file size validation."""
    parser = argparse.ArgumentParser(
        description="Validate Agent OS file size constraints (quality improvement tool)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed file-by-file analysis"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use strict 100-line limit and exit 1 on violations (for Agent OS improvement sessions)"
    )
    
    args = parser.parse_args()
    
    # Analyze file sizes
    violations, analysis = analyze_file_sizes(strict_mode=args.strict)
    
    # Print reports
    print_summary_report(violations, analysis)
    
    if args.verbose:
        print_verbose_report(analysis)
    
    # Exit code logic
    if args.strict and violations:
        print("❌ STRICT MODE: Violations found - exit code 1")
        print("   (Use without --strict for non-blocking quality improvement mode)")
        return 1
    else:
        print("✅ EXIT CODE 0: Quality improvement opportunities identified")
        print("   (Agent OS improvements are iterative, not blocking)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
