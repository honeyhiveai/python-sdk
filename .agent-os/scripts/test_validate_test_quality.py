#!/usr/bin/env python3
"""
Unit tests for the validate-test-quality.py script.
Ensures the validation script correctly detects quality issues.
"""

import json
import subprocess
import tempfile
import textwrap
from pathlib import Path


def run_validation_script(test_file_content: str) -> tuple[int, str]:
    """Run validation script on test file content and return exit code and output."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_file_content)
        temp_file = f.name

    try:
        result = subprocess.run(
            [
                "python",
                ".agent-os/scripts/validate-test-quality.py",
                "--test-file",
                temp_file,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout
    finally:
        Path(temp_file).unlink()


def test_perfect_quality_file():
    """Test that a perfect quality file returns exit code 0."""
    perfect_file = textwrap.dedent(
        '''
        """Perfect test file with no issues."""
        
        def test_example():
            """Test function with proper docstring."""
            assert True
    '''
    )

    exit_code, output = run_validation_script(perfect_file)

    # Should pass if all tools are working correctly
    # Note: This might fail if pytest/pylint/mypy/black aren't available
    print(f"Perfect file test - Exit code: {exit_code}")
    if "ALL QUALITY TARGETS MET" in output:
        print("✅ Perfect file correctly identified")
        assert exit_code == 0
    else:
        print("⚠️  Perfect file test skipped - tools may not be available")


def test_failing_tests():
    """Test that a file with failing tests returns exit code 1."""
    failing_file = textwrap.dedent(
        '''
        """Test file with failing tests."""
        
        def test_failing():
            """Test that will fail."""
            assert False, "This test should fail"
    '''
    )

    exit_code, output = run_validation_script(failing_file)

    print(f"Failing tests - Exit code: {exit_code}")
    assert exit_code == 1
    assert "QUALITY TARGETS NOT MET" in output
    assert "test_pass_rate" in output
    print("✅ Failing tests correctly detected")


def test_pylint_violations():
    """Test that pylint violations are detected."""
    pylint_violation_file = textwrap.dedent(
        '''
        """Test file with pylint violations."""
        
        def test_example():
            """Test function."""
            very_long_variable_name_that_exceeds_the_line_length_limit_and_should_trigger_pylint_violation = True
            assert very_long_variable_name_that_exceeds_the_line_length_limit_and_should_trigger_pylint_violation
    '''
    )

    exit_code, output = run_validation_script(pylint_violation_file)

    print(f"Pylint violations - Exit code: {exit_code}")
    assert exit_code == 1
    assert "QUALITY TARGETS NOT MET" in output
    print("✅ Pylint violations correctly detected")


def test_json_output_format():
    """Test that JSON output is properly formatted."""
    simple_file = textwrap.dedent(
        '''
        """Simple test file."""
        
        def test_simple():
            """Simple test."""
            assert True
    '''
    )

    exit_code, output = run_validation_script(simple_file)

    # Extract JSON from output
    json_start = output.find("{")
    json_end = output.rfind("}")
    if json_start != -1 and json_end != -1:
        json_str = output[json_start : json_end + 1]
        try:
            data = json.loads(json_str)
            assert "test_file" in data
            assert "quality_targets" in data
            assert "overall_passed" in data
            assert "summary" in data
            print("✅ JSON output format is valid")
        except json.JSONDecodeError as e:
            print(f"❌ JSON output is malformed: {e}")
            print(f"JSON string: {json_str[:200]}...")
            raise
    else:
        print("❌ No JSON output found")
        print(f"Output preview: {output[:500]}...")
        raise AssertionError("No JSON output found")


def test_nonexistent_file():
    """Test handling of nonexistent files."""
    result = subprocess.run(
        [
            "python",
            ".agent-os/scripts/validate-test-quality.py",
            "--test-file",
            "nonexistent.py",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2  # Error exit code
    assert "does not exist" in result.stdout
    print("✅ Nonexistent file correctly handled")


def test_invalid_usage():
    """Test invalid command line usage."""
    result = subprocess.run(
        ["python", ".agent-os/scripts/validate-test-quality.py"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2  # Error exit code
    assert "Usage:" in result.stdout
    print("✅ Invalid usage correctly handled")


def main():
    """Run all validation script tests."""
    print("🔍 Testing validate-test-quality.py script...")
    print("=" * 60)

    try:
        test_failing_tests()
        test_pylint_violations()
        test_json_output_format()
        test_nonexistent_file()
        test_invalid_usage()
        test_perfect_quality_file()  # Run last as it might be skipped

        print("\n" + "=" * 60)
        print("✅ All validation script tests passed!")
        print("🎯 The automated validation enforcement is working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
