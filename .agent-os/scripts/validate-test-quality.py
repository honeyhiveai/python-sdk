#!/usr/bin/env python3
"""
Automated test quality validation script for Agent OS framework.
Returns exit code 0 only when ALL quality targets are met.

This script enforces the framework's quality gates and prevents
AI assistants from bypassing Phase 8 completion requirements.
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any


def run_command(cmd: list, timeout: int = 60) -> tuple[int, str, str]:
    """Run command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return 1, "", str(e)


def validate_test_pass_rate(test_file: str) -> Dict[str, Any]:
    """Validate test pass rate - must be 100%."""
    result = {"target": 100.0, "actual": 0.0, "passed": False, "details": ""}

    exit_code, stdout, stderr = run_command(["pytest", test_file, "-v", "--tb=no"])

    if exit_code == 0:
        # All tests passed
        result["actual"] = 100.0
        result["passed"] = True
        result["details"] = "All tests passed"
    else:
        # Parse pytest output for failure details
        if "failed" in stdout.lower():
            # Extract failure count
            failed_match = re.search(r"(\d+) failed", stdout)
            passed_match = re.search(r"(\d+) passed", stdout)

            if failed_match and passed_match:
                failed = int(failed_match.group(1))
                passed = int(passed_match.group(1))
                total = failed + passed
                result["actual"] = (passed / total) * 100.0 if total > 0 else 0.0
            else:
                result["actual"] = 0.0
        else:
            result["actual"] = 0.0

        result["details"] = f"Tests failed. Exit code: {exit_code}"

    return result


def validate_pylint_score(test_file: str) -> Dict[str, Any]:
    """Validate pylint score - must be 10.0/10."""
    result = {"target": 10.0, "actual": 0.0, "passed": False, "details": ""}

    exit_code, stdout, stderr = run_command(["pylint", test_file, "--score=yes"])

    # Parse pylint score
    score_match = re.search(r"Your code has been rated at ([\d.]+)/10", stdout)
    if score_match:
        score = float(score_match.group(1))
        result["actual"] = score
        result["passed"] = score >= 10.0
        result["details"] = f"Pylint score: {score}/10"
    else:
        result["details"] = f"Could not parse pylint score. Exit code: {exit_code}"

    return result


def validate_mypy_errors(test_file: str) -> Dict[str, Any]:
    """Validate mypy errors - must be 0."""
    result = {"target": 0, "actual": 999, "passed": False, "details": ""}

    exit_code, stdout, stderr = run_command(["mypy", test_file])

    # Count errors
    error_count = stdout.count("error:")
    result["actual"] = error_count
    result["passed"] = error_count == 0

    if error_count == 0:
        result["details"] = "No mypy errors"
    else:
        result["details"] = f"{error_count} mypy errors found"

    return result


def validate_black_formatting(test_file: str) -> Dict[str, Any]:
    """Validate black formatting - must be clean."""
    result = {"target": True, "actual": False, "passed": False, "details": ""}

    exit_code, stdout, stderr = run_command(["black", "--check", test_file])

    result["actual"] = exit_code == 0
    result["passed"] = exit_code == 0

    if exit_code == 0:
        result["details"] = "Code is properly formatted"
    else:
        result["details"] = "Code needs formatting"

    return result


def validate_test_quality(test_file: str) -> Dict[str, Any]:
    """Validate all quality targets for generated test file."""

    # Initialize results structure
    results = {
        "test_file": test_file,
        "timestamp": "",
        "quality_targets": {
            "test_pass_rate": validate_test_pass_rate(test_file),
            "pylint_score": validate_pylint_score(test_file),
            "mypy_errors": validate_mypy_errors(test_file),
            "black_formatting": validate_black_formatting(test_file),
        },
        "overall_passed": False,
        "summary": {"targets_met": 0, "targets_total": 4, "blocking_issues": []},
    }

    # Calculate overall pass status
    targets_met = 0
    blocking_issues = []

    for target_name, target_data in results["quality_targets"].items():
        if target_data["passed"]:
            targets_met += 1
        else:
            blocking_issues.append(f"{target_name}: {target_data['details']}")

    results["summary"]["targets_met"] = targets_met
    results["summary"]["blocking_issues"] = blocking_issues
    results["overall_passed"] = targets_met == 4

    # Add timestamp
    from datetime import datetime

    results["timestamp"] = datetime.now().isoformat()

    return results


def print_results(results: Dict[str, Any]) -> None:
    """Print formatted results."""
    print("🔍 AGENT OS FRAMEWORK - TEST QUALITY VALIDATION")
    print("=" * 60)
    print(f"📁 Test File: {results['test_file']}")
    print(f"⏰ Timestamp: {results['timestamp']}")
    print()

    print("📊 QUALITY TARGETS:")
    for target_name, target_data in results["quality_targets"].items():
        status = "✅" if target_data["passed"] else "❌"
        print(
            f"  {status} {target_name.replace('_', ' ').title()}: {target_data['details']}"
        )

    print()
    print(
        f"📈 SUMMARY: {results['summary']['targets_met']}/{results['summary']['targets_total']} targets met"
    )

    if results["overall_passed"]:
        print("\n✅ ALL QUALITY TARGETS MET - Framework completion authorized")
        print("🎯 Phase 8 quality gate: PASSED")
    else:
        print("\n❌ QUALITY TARGETS NOT MET - Framework completion BLOCKED")
        print("🚫 Phase 8 quality gate: FAILED")
        print("\n🔧 Blocking Issues:")
        for issue in results["summary"]["blocking_issues"]:
            print(f"  • {issue}")
        print("\n💡 Fix all blocking issues and re-run validation to proceed.")


def main():
    """Main validation function."""
    if len(sys.argv) != 3 or sys.argv[1] != "--test-file":
        print("Usage: validate-test-quality.py --test-file <test_file>")
        print("\nThis script validates test quality for Agent OS framework Phase 8.")
        print("Returns exit code 0 only when ALL quality targets are met.")
        sys.exit(2)

    test_file = sys.argv[2]
    test_path = Path(test_file)

    if not test_path.exists():
        print(f"❌ Error: Test file {test_file} does not exist")
        sys.exit(2)

    if not test_path.suffix == ".py":
        print(f"❌ Error: Test file {test_file} is not a Python file")
        sys.exit(2)

    # Run validation
    results = validate_test_quality(test_file)

    # Print human-readable results
    print_results(results)

    # Print JSON for programmatic use
    print("\n" + "=" * 60)
    print("📋 JSON OUTPUT (for metrics collection):")
    print(json.dumps(results, indent=2))

    # Exit with appropriate code
    if results["overall_passed"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
