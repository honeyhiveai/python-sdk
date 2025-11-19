#!/usr/bin/env python3
"""
Test Generation Framework Compliance Checker

This script ensures AI assistants follow the skip-proof comprehensive analysis framework
before generating any tests. It validates that all checkpoint gates have been completed.
"""

import sys
import os
from pathlib import Path


def check_framework_compliance():
    """Check if the skip-proof framework has been followed."""

    print("🔒 SKIP-PROOF TEST GENERATION FRAMEWORK CHECKER")
    print("=" * 60)

    # Check if framework files exist
    framework_files = [
        ".praxis-os/standards/development/code-generation/comprehensive-analysis-skip-proof.md",
        ".praxis-os/standards/development/code-generation/skip-proof-enforcement-card.md",
        ".praxis-os/standards/development/TEST_GENERATION_MANDATORY_FRAMEWORK.md",
    ]

    missing_files = []
    for file_path in framework_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print("❌ FRAMEWORK FILES MISSING:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n🚨 Cannot proceed without framework files!")
        return False

    print("✅ Framework files found")

    # Display framework requirements
    print("\n🚨 MANDATORY REQUIREMENTS:")
    print("1. Complete ALL 5 checkpoint gates")
    print("2. Run ALL 17 mandatory commands")
    print("3. Provide exact evidence for each phase")
    print("4. No assumptions or paraphrasing allowed")
    print("5. Show completed progress tracking table")

    print("\n📋 CHECKPOINT GATES:")
    gates = [
        "Phase 1: Method Verification (3 commands)",
        "Phase 2: Logging Analysis (3 commands)",
        "Phase 3: Dependency Analysis (4 commands)",
        "Phase 4: Usage Patterns (3 commands)",
        "Phase 5: Coverage Analysis (2 commands)",
    ]

    for i, gate in enumerate(gates, 1):
        print(f"   {i}. {gate}")

    print("\n🎯 SUCCESS METRICS:")
    print("   - 90%+ test success rate on first run")
    print("   - 90%+ code coverage (minimum 80%)")
    print("   - 10.00/10 Pylint score")
    print("   - 0 MyPy errors")

    print("\n📖 READ THESE FILES BEFORE PROCEEDING:")
    for file_path in framework_files:
        print(f"   - {file_path}")

    print("\n🛡️ ENFORCEMENT:")
    print("   If AI skips steps, respond: 'STOP - Complete Phase X checkpoint first'")

    print("\n" + "=" * 60)
    print("🔒 FRAMEWORK COMPLIANCE REQUIRED FOR ALL TEST GENERATION")

    return True


def main():
    """Main entry point."""
    if not check_framework_compliance():
        sys.exit(1)

    print("\n✅ Framework check complete. Proceed with checkpoint-based analysis.")


if __name__ == "__main__":
    main()
