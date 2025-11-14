#!/usr/bin/env python3
"""
Validation script to detect mocks in integration tests.

This script enforces the no-mock rule for integration tests to prevent
critical bugs like the ProxyTracerProvider issue from going undetected.

Usage:
    python scripts/validate-no-mocks-integration.py
    python scripts/validate-no-mocks-integration.py --fix

Exit codes:
    0: No mocks found in integration tests
    1: Mocks found in integration tests
    2: Script error
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def find_mock_usage(integration_dir: Path) -> List[Tuple[str, int, str]]:
    """
    Find all mock usage in integration tests.

    Returns:
        List of (file_path, line_number, line_content) tuples
    """
    mock_patterns = [
        r"unittest\.mock",
        r"from unittest\.mock",
        r"@patch",
        r"Mock\(",
        r"MagicMock\(",
        r"mock\.patch",
        r"patch\.object",
        r"with patch",
        r"mock_\w+",  # Variables starting with mock_
        r"test_mode\s*=\s*True",  # Also catch test_mode=True which defeats integration testing
    ]

    violations = []

    for py_file in integration_dir.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    for pattern in mock_patterns:
                        if re.search(pattern, line):
                            violations.append((str(py_file), line_num, line.strip()))
                            break  # Only report one violation per line
        except Exception as e:
            print(f"⚠️  Error reading {py_file}: {e}")

    return violations


def suggest_fixes(violations: List[Tuple[str, int, str]]) -> None:
    """Print suggestions for fixing mock violations."""
    print("\n💡 **SOLUTIONS FOR FIXING MOCK VIOLATIONS:**")
    print()
    print("1. **Move heavily mocked tests to unit tests:**")
    print("   mv tests/integration/test_heavily_mocked.py tests/unit/")
    print()
    print("2. **Replace mocks with real API calls:**")
    print("   # ❌ WRONG (mocked)")
    print("   @patch('openai.chat.completions.create')")
    print("   def test_openai_integration(mock_create):")
    print("       mock_create.return_value = Mock()")
    print()
    print("   # ✅ CORRECT (real API)")
    print("   def test_openai_integration():")
    print("       api_key = os.getenv('OPENAI_API_KEY')")
    print("       if not api_key:")
    print("           pytest.skip('OPENAI_API_KEY required')")
    print("       client = openai.OpenAI(api_key=api_key)")
    print("       response = client.chat.completions.create(...)")
    print()
    print("3. **Use real HoneyHive API (NO test_mode):**")
    print("   # ❌ WRONG")
    print("   tracer = HoneyHiveTracer.init(api_key='key', test_mode=True)")
    print()
    print("   # ✅ CORRECT")
    print("   api_key = os.getenv('HH_API_KEY')")
    print("   if not api_key:")
    print("       pytest.skip('HH_API_KEY required for integration tests')")
    print("   tracer = HoneyHiveTracer.init(api_key=api_key, test_mode=False)")
    print()
    print("4. **Environment setup for real API testing:**")
    print("   export HH_API_KEY='your-honeyhive-api-key'")
    print("   export OPENAI_API_KEY='your-openai-api-key'")
    print("   export ANTHROPIC_API_KEY='your-anthropic-api-key'")


def move_files_to_unit(
    violations: List[Tuple[str, int, str]], dry_run: bool = True
) -> None:
    """Suggest or perform moving heavily mocked files to unit tests."""
    # Group violations by file
    file_violations = {}
    for file_path, line_num, line_content in violations:
        if file_path not in file_violations:
            file_violations[file_path] = []
        file_violations[file_path].append((line_num, line_content))

    # Find files with heavy mock usage (>5 violations)
    heavily_mocked_files = {
        file_path: violations_list
        for file_path, violations_list in file_violations.items()
        if len(violations_list) > 5
    }

    if heavily_mocked_files:
        print(f"\n📁 **FILES WITH HEAVY MOCK USAGE (>5 violations):**")
        print()
        for file_path, file_violations_list in heavily_mocked_files.items():
            rel_path = os.path.relpath(file_path)
            unit_path = rel_path.replace("tests/integration/", "tests/unit/")
            print(f"  {rel_path} ({len(file_violations_list)} violations)")

            if dry_run:
                print(f"    💡 Suggested move: mv {rel_path} {unit_path}")
            else:
                try:
                    os.makedirs(os.path.dirname(unit_path), exist_ok=True)
                    os.rename(file_path, unit_path)
                    print(f"    ✅ Moved to: {unit_path}")
                except Exception as e:
                    print(f"    ❌ Failed to move: {e}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Validate no mocks in integration tests"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix violations by moving heavily mocked files to unit tests",
    )
    parser.add_argument(
        "--integration-dir",
        type=Path,
        default=Path("tests/integration"),
        help="Path to integration tests directory",
    )

    args = parser.parse_args()

    # Check if integration directory exists
    if not args.integration_dir.exists():
        print(f"❌ Integration tests directory not found: {args.integration_dir}")
        return 2

    print("🔍 **CHECKING FOR MOCKS IN INTEGRATION TESTS**")
    print(f"📁 Directory: {args.integration_dir}")
    print()

    # Find all mock violations
    violations = find_mock_usage(args.integration_dir)

    if not violations:
        print("✅ **NO MOCKS FOUND IN INTEGRATION TESTS**")
        print("Integration tests are properly using real systems and real APIs.")
        return 0

    # Report violations
    print(f"❌ **FOUND {len(violations)} MOCK VIOLATIONS IN INTEGRATION TESTS**")
    print()
    print("🚨 **CRITICAL: NO MOCKS ALLOWED IN INTEGRATION TESTS**")
    print("Integration tests must use real systems and real APIs to catch bugs")
    print("like the ProxyTracerProvider issue that mocked tests missed.")
    print()

    # Group and display violations by file
    file_violations = {}
    for file_path, line_num, line_content in violations:
        rel_path = os.path.relpath(file_path)
        if rel_path not in file_violations:
            file_violations[rel_path] = []
        file_violations[rel_path].append((line_num, line_content))

    print("📋 **VIOLATIONS BY FILE:**")
    for file_path, file_violations_list in sorted(file_violations.items()):
        print(f"\n  📄 {file_path} ({len(file_violations_list)} violations)")
        for line_num, line_content in file_violations_list[:3]:  # Show first 3
            print(f"    Line {line_num}: {line_content}")
        if len(file_violations_list) > 3:
            print(f"    ... and {len(file_violations_list) - 3} more")

    # Suggest fixes
    suggest_fixes(violations)

    # Offer to move heavily mocked files
    move_files_to_unit(violations, dry_run=not args.fix)

    print("\n🎯 **NEXT STEPS:**")
    print("1. Run with --fix to automatically move heavily mocked files to unit tests")
    print("2. Manually refactor remaining tests to use real APIs")
    print("3. Set up real API credentials for integration testing")
    print("4. Re-run this script to verify all violations are fixed")
    print()
    print("📚 **DOCUMENTATION:**")
    print(
        "- Integration Testing Guide: docs/development/testing/integration-testing.rst"
    )
    print(
        "- praxis OS Spec: .praxis-os/specs/completed/2025-09-06-integration-testing-consolidation/"
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())
