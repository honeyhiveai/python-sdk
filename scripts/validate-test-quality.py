#!/usr/bin/env python3
"""
V3 Framework Quality Validator

Automated quality validation for generated test files.
Exit code 0: All quality gates passed
Exit code 1: Quality failures with detailed output
"""

import sys
import subprocess
import re
import argparse
from pathlib import Path


def validate_pylint_score(
    file_path: str, target_score: float = 10.0
) -> tuple[bool, float, str]:
    """Validate Pylint score meets target."""
    try:
        result = subprocess.run(
            ["tox", "-e", "lint", "--", file_path, "--score=y"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Extract score
        score_match = re.search(
            r"Your code has been rated at ([\d.-]+)/10", result.stdout
        )
        score = float(score_match.group(1)) if score_match else 0.0

        passed = score >= target_score
        status = f"Pylint: {score}/10 {'✅' if passed else '❌'}"
        if not passed:
            status += f" (Target: {target_score})"

        return passed, score, status

    except Exception as e:
        return False, 0.0, f"Pylint: ERROR - {e} ❌"


def validate_mypy_errors(file_path: str, max_errors: int = 0) -> tuple[bool, int, str]:
    """Validate MyPy has no type errors."""
    try:
        result = subprocess.run(
            ["tox", "-e", "mypy", "--", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Count errors
        error_count = len(re.findall(r"error:", result.stdout))
        passed = error_count <= max_errors

        status = f"MyPy: {error_count} errors {'✅' if passed else '❌'}"
        if not passed:
            status += f" (Target: {max_errors})"

        return passed, error_count, status

    except Exception as e:
        return False, 999, f"MyPy: ERROR - {e} ❌"


def validate_black_formatting(file_path: str) -> tuple[bool, str]:
    """Validate Black formatting compliance."""
    try:
        result = subprocess.run(
            ["tox", "-e", "format", "--", "--check", file_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        passed = result.returncode == 0
        status = f"Black: {'Formatted ✅' if passed else 'Not formatted ❌'}"

        return passed, status

    except Exception as e:
        return False, f"Black: ERROR - {e} ❌"


def validate_test_execution(file_path: str) -> tuple[bool, int, int, str]:
    """Validate test execution and pass rate."""
    try:
        # Determine test type from path
        test_env = "unit" if "unit" in file_path else "integration"

        result = subprocess.run(
            ["tox", "-e", test_env, "--", file_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Extract test counts
        passed_match = re.search(r"(\d+) passed", result.stdout)
        failed_match = re.search(r"(\d+) failed", result.stdout)

        passed_count = int(passed_match.group(1)) if passed_match else 0
        failed_count = int(failed_match.group(1)) if failed_match else 0
        total_count = passed_count + failed_count

        all_passed = failed_count == 0 and total_count > 0

        if total_count == 0:
            status = "Tests: No tests found ❌"
        else:
            status = f"Tests: {passed_count}/{total_count} passed {'✅' if all_passed else '❌'}"
            if failed_count > 0:
                status += f" ({failed_count} failed)"

        return all_passed, passed_count, failed_count, status

    except Exception as e:
        return False, 0, 999, f"Tests: ERROR - {e} ❌"


def validate_coverage(
    file_path: str, target_coverage: float = 90.0, minimum_coverage: float = 80.0
) -> tuple[bool, float, str]:
    """Validate test coverage (unit tests only)."""
    try:
        # Determine production file from test file
        test_path = Path(file_path)
        if "unit" not in str(test_path):
            return True, 0.0, "Coverage: N/A (integration test) ✅"

        # Extract production file path from test file name
        prod_file = str(test_path.name).replace("test_", "").replace(".py", ".py")
        prod_path = f"src/honeyhive/tracer/instrumentation/{prod_file}"

        # Use unit tox environment for coverage
        result = subprocess.run(
            [
                "tox",
                "-e",
                "unit",
                "--",
                file_path,
                f"--cov={prod_path}",
                "--cov-report=term-missing",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Extract coverage percentage
        coverage_match = re.search(r"TOTAL.*?(\d+)%", result.stdout)
        coverage = float(coverage_match.group(1)) if coverage_match else 0.0

        passed = coverage >= minimum_coverage
        status = f"Coverage: {coverage}% {'✅' if passed else '❌'}"
        if not passed:
            status += f" (Minimum: {minimum_coverage}%)"
        elif coverage < target_coverage:
            status += f" (Target: {target_coverage}%)"

        return passed, coverage, status

    except Exception as e:
        return False, 0.0, f"Coverage: ERROR - {e} ❌"


def main():
    parser = argparse.ArgumentParser(description="V3 Framework Quality Validator")
    parser.add_argument("file_path", help="Path to test file to validate")
    parser.add_argument(
        "--pylint-target", type=float, default=10.0, help="Pylint score target"
    )
    parser.add_argument(
        "--coverage-target",
        type=float,
        default=90.0,
        help="Coverage target for unit tests",
    )
    parser.add_argument(
        "--coverage-minimum",
        type=float,
        default=80.0,
        help="Coverage minimum accepted for unit tests",
    )

    args = parser.parse_args()

    if not Path(args.file_path).exists():
        print(f"❌ File not found: {args.file_path}")
        sys.exit(1)

    print("🔍 V3 FRAMEWORK QUALITY VALIDATION")
    print(f"📁 File: {args.file_path}")
    print()

    # Run all validations
    validations = []

    # Pylint validation
    pylint_passed, pylint_score, pylint_status = validate_pylint_score(
        args.file_path, args.pylint_target
    )
    validations.append((pylint_passed, pylint_status))

    # MyPy validation
    mypy_passed, mypy_errors, mypy_status = validate_mypy_errors(args.file_path)
    validations.append((mypy_passed, mypy_status))

    # Black validation
    black_passed, black_status = validate_black_formatting(args.file_path)
    validations.append((black_passed, black_status))

    # Test execution validation
    test_passed, passed_count, failed_count, test_status = validate_test_execution(
        args.file_path
    )
    validations.append((test_passed, test_status))

    # Coverage validation (unit tests only)
    coverage_passed, coverage_pct, coverage_status = validate_coverage(
        args.file_path, args.coverage_target, args.coverage_minimum
    )
    validations.append((coverage_passed, coverage_status))

    # Print results
    all_passed = all(passed for passed, _ in validations)

    if all_passed:
        print("✅ QUALITY VALIDATION PASSED")
    else:
        print("❌ QUALITY VALIDATION FAILED")

    print()
    for _, status in validations:
        print(status)

    print()
    if all_passed:
        print("🎉 All quality gates passed!")
        sys.exit(0)
    else:
        print("🔧 Fix the issues above and re-run validation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
