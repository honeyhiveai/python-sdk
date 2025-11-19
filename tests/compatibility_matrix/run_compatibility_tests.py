#!/usr/bin/env python3
"""
Compatibility Test Runner for HoneyHive SDK

Runs all model provider compatibility tests and generates a comprehensive report.
"""

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_env_file() -> None:
    """Load environment variables from .env file if it exists."""
    # Look for .env file in project root
    env_file = Path(__file__).parent.parent.parent / ".env"

    if env_file.exists():
        print(f"📄 Loading environment variables from {env_file}")
        with open(env_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE format
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not already in environment
                    if key and not os.getenv(key):
                        os.environ[key] = value
                else:
                    print(
                        f"⚠️  Warning: Invalid line format in .env file (line {line_num}): {line}"
                    )
    else:
        print(f"ℹ️  No .env file found at {env_file}")
        print(
            "   Set environment variables manually or create .env file from env.example"
        )


@dataclass
class TestResult:
    """Result of a compatibility test."""

    provider: str
    instrumentor: str
    status: str  # "PASSED", "FAILED", "SKIPPED"
    duration: float
    error_message: Optional[str] = None
    notes: Optional[str] = None


class CompatibilityTestRunner:
    """Runs compatibility tests for all model providers."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results: List[TestResult] = []

        # Map test files to provider info - Updated to match actual file names
        self.test_configs = {
            # OpenInference Instrumentor Tests
            "test_openinference_openai.py": {
                "provider": "OpenAI",
                "instrumentor": "openinference-instrumentation-openai",
                "category": "openinference",
                "required_env": ["OPENAI_API_KEY"],
            },
            "test_openinference_azure_openai.py": {
                "provider": "Azure OpenAI",
                "instrumentor": "openinference-instrumentation-openai",
                "category": "openinference",
                "required_env": [
                    "AZURE_OPENAI_ENDPOINT",
                    "AZURE_OPENAI_API_KEY",
                    "AZURE_OPENAI_DEPLOYMENT_NAME",
                ],
            },
            "test_openinference_anthropic.py": {
                "provider": "Anthropic",
                "instrumentor": "openinference-instrumentation-anthropic",
                "category": "openinference",
                "required_env": ["ANTHROPIC_API_KEY"],
            },
            "test_openinference_google_ai.py": {
                "provider": "Google Generative AI",
                "instrumentor": "openinference-instrumentation-google-generativeai",
                "category": "openinference",
                "required_env": ["GOOGLE_API_KEY"],
            },
            "test_openinference_google_adk.py": {
                "provider": "Google Agent Development Kit",
                "instrumentor": "openinference-instrumentation-google-adk",
                "category": "openinference",
                "required_env": ["GOOGLE_ADK_API_KEY"],
            },
            "test_openinference_bedrock.py": {
                "provider": "AWS Bedrock",
                "instrumentor": "openinference-instrumentation-bedrock",
                "category": "openinference",
                "required_env": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
            },
            "test_openinference_mcp.py": {
                "provider": "Model Context Protocol",
                "instrumentor": "openinference-instrumentation-mcp",
                "category": "openinference",
                "required_env": [],  # MCP may not require external API keys
            },
            # Traceloop (OpenTelemetry) Instrumentor Tests
            "test_traceloop_openai.py": {
                "provider": "OpenAI (Traceloop)",
                "instrumentor": "opentelemetry-instrumentation-openai",
                "category": "traceloop",
                "required_env": ["OPENAI_API_KEY"],
            },
            "test_traceloop_azure_openai.py": {
                "provider": "Azure OpenAI (Traceloop)",
                "instrumentor": "opentelemetry-instrumentation-openai",
                "category": "traceloop",
                "required_env": [
                    "AZURE_OPENAI_ENDPOINT",
                    "AZURE_OPENAI_API_KEY",
                    "AZURE_OPENAI_DEPLOYMENT_NAME",
                ],
            },
            "test_traceloop_anthropic.py": {
                "provider": "Anthropic (Traceloop)",
                "instrumentor": "opentelemetry-instrumentation-anthropic",
                "category": "traceloop",
                "required_env": ["ANTHROPIC_API_KEY"],
            },
            "test_traceloop_google_ai.py": {
                "provider": "Google AI (Traceloop)",
                "instrumentor": "opentelemetry-instrumentation-google-generativeai",
                "category": "traceloop",
                "required_env": ["GOOGLE_API_KEY"],
            },
            "test_traceloop_bedrock.py": {
                "provider": "AWS Bedrock (Traceloop)",
                "instrumentor": "opentelemetry-instrumentation-bedrock",
                "category": "traceloop",
                "required_env": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
            },
            "test_traceloop_mcp.py": {
                "provider": "Model Context Protocol (Traceloop)",
                "instrumentor": "opentelemetry-instrumentation-mcp",
                "category": "traceloop",
                "required_env": [],
            },
            # Framework Integration Tests
            "test_strands_integration.py": {
                "provider": "AWS Strands",
                "instrumentor": "strands-agents",
                "category": "framework",
                "required_env": [],  # Strands is optional - test will skip if not available
            },
        }

    def check_base_requirements(self) -> bool:
        """Check if base HoneyHive requirements are met."""
        required_vars = ["HH_API_KEY", "HH_PROJECT"]
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            print("❌ Missing base HoneyHive environment variables:")
            for var in missing:
                print(f"   - {var}")
            return False

        return True

    def check_test_requirements(self, test_file: str) -> Tuple[bool, List[str]]:
        """Check if requirements for a specific test are met."""
        config = self.test_configs.get(test_file, {})
        required_env = config.get("required_env", [])

        missing = [var for var in required_env if not os.getenv(var)]
        return len(missing) == 0, missing

    def run_test(self, test_file: str) -> TestResult:
        """Run a single compatibility test."""
        config = self.test_configs[test_file]
        provider = config["provider"]
        instrumentor = config["instrumentor"]

        print(f"\n🧪 Testing {provider}...")
        print(f"   Instrumentor: {instrumentor}")

        # Check requirements
        can_run, missing_env = self.check_test_requirements(test_file)

        if not can_run:
            print(
                f"   ⏭️  Skipping - missing environment variables: {', '.join(missing_env)}"
            )
            return TestResult(
                provider=provider,
                instrumentor=instrumentor,
                status="SKIPPED",
                duration=0.0,
                notes=f"Missing env vars: {', '.join(missing_env)}",
            )

        # Run the test
        test_path = self.test_dir / test_file
        start_time = time.time()

        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                print(f"   ✅ PASSED ({duration:.1f}s)")
                return TestResult(
                    provider=provider,
                    instrumentor=instrumentor,
                    status="PASSED",
                    duration=duration,
                )
            else:
                print(f"   ❌ FAILED ({duration:.1f}s)")
                print(f"   Error: {result.stderr.strip()}")
                return TestResult(
                    provider=provider,
                    instrumentor=instrumentor,
                    status="FAILED",
                    duration=duration,
                    error_message=result.stderr.strip(),
                )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   ⏰ TIMEOUT ({duration:.1f}s)")
            return TestResult(
                provider=provider,
                instrumentor=instrumentor,
                status="FAILED",
                duration=duration,
                error_message="Test timed out after 120 seconds",
            )

        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 ERROR ({duration:.1f}s): {e}")
            return TestResult(
                provider=provider,
                instrumentor=instrumentor,
                status="FAILED",
                duration=duration,
                error_message=str(e),
            )

    def run_all_tests(self) -> List[TestResult]:
        """Run all compatibility tests."""
        print("🚀 HoneyHive Model Provider Compatibility Test Suite")
        print("=" * 60)

        # Check base requirements
        if not self.check_base_requirements():
            print("\n❌ Cannot run tests - missing base requirements")
            return []

        print(f"✓ Base requirements met")
        print(f"✓ Found {len(self.test_configs)} test configurations")

        # Run each test
        results = []
        for test_file in sorted(self.test_configs.keys()):
            result = self.run_test(test_file)
            results.append(result)
            self.results.append(result)

        return results

    def print_summary(self):
        """Print test summary."""
        if not self.results:
            print("\n❌ No test results available")
            return

        passed = [r for r in self.results if r.status == "PASSED"]
        failed = [r for r in self.results if r.status == "FAILED"]
        skipped = [r for r in self.results if r.status == "SKIPPED"]

        print(f"\n📊 TEST SUMMARY")
        print("=" * 40)
        print(f"Total Tests:    {len(self.results)}")
        print(f"✅ Passed:      {len(passed)}")
        print(f"❌ Failed:      {len(failed)}")
        print(f"⏭️  Skipped:     {len(skipped)}")

        if passed:
            print(f"\n✅ PASSED TESTS:")
            for result in passed:
                print(f"   • {result.provider} ({result.duration:.1f}s)")

        if failed:
            print(f"\n❌ FAILED TESTS:")
            for result in failed:
                print(f"   • {result.provider}: {result.error_message}")

        if skipped:
            print(f"\n⏭️  SKIPPED TESTS:")
            for result in skipped:
                print(f"   • {result.provider}: {result.notes}")

        # Overall status
        if failed:
            print(
                f"\n❌ OVERALL: SOME TESTS FAILED ({len(failed)}/{len(self.results)})"
            )
        elif skipped and not passed:
            print(f"\n⚠️  OVERALL: ALL TESTS SKIPPED")
        else:
            print(f"\n✅ OVERALL: ALL AVAILABLE TESTS PASSED")

    def generate_matrix_report(self, output_file: Optional[str] = None):
        """Generate compatibility matrix report."""
        if not self.results:
            print("❌ No results to generate matrix from")
            return

        # Get Python version info
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        lines = []
        lines.append("# HoneyHive Model Provider Compatibility Matrix")
        lines.append("")
        lines.append(f"**Python Version**: {python_version}")
        lines.append(f"**HoneyHive SDK**: Compatible (requires Python >=3.11)")
        lines.append("")

        # Summary statistics
        passed = len([r for r in self.results if r.status == "PASSED"])
        failed = len([r for r in self.results if r.status == "FAILED"])
        skipped = len([r for r in self.results if r.status == "SKIPPED"])

        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Tests**: {len(self.results)}")
        lines.append(f"- **✅ Passed**: {passed}")
        lines.append(f"- **❌ Failed**: {failed}")
        lines.append(f"- **⏭️ Skipped**: {skipped}")
        lines.append("")

        # Detailed results
        lines.append("## Detailed Results")
        lines.append("")
        lines.append("| Provider | Instrumentor | Status | Duration | Notes |")
        lines.append("|----------|-------------|---------|----------|-------|")

        for result in self.results:
            status_emoji = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭️"}.get(
                result.status, "❓"
            )

            duration_str = f"{result.duration:.1f}s" if result.duration > 0 else "N/A"
            notes = result.notes or result.error_message or ""
            if len(notes) > 50:
                notes = notes[:47] + "..."

            lines.append(
                f"| {result.provider} | `{result.instrumentor}` | {status_emoji} {result.status} | {duration_str} | {notes} |"
            )

        lines.append("")

        # Python version compatibility notes
        lines.append("## Python Version Compatibility")
        lines.append("")
        if python_version in ["3.11", "3.12", "3.13"]:
            lines.append(
                f"✅ Python {python_version} is fully supported by HoneyHive SDK"
            )
        else:
            lines.append(f"⚠️ Python {python_version} compatibility not verified")

        lines.append("")
        lines.append("**Instrumentor Compatibility Notes:**")
        lines.append(
            "- OpenInference instrumentors: Generally compatible with Python 3.11+"
        )
        lines.append("- Traceloop SDK: Compatible with Python 3.11+")
        lines.append("- Some instrumentors may have Python version restrictions")
        lines.append("")

        lines.append(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        report_content = "\n".join(lines)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"📄 Matrix report saved to: {output_file}")
        else:
            print("\n📄 COMPATIBILITY MATRIX:")
            print(report_content)


def main():
    """Main entry point."""
    # Load environment variables from .env file first
    load_env_file()

    runner = CompatibilityTestRunner()

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Run HoneyHive compatibility tests")
    parser.add_argument("--output", "-o", help="Output file for matrix report")
    parser.add_argument("--test", "-t", help="Run specific test file only")
    args = parser.parse_args()

    try:
        if args.test:
            # Run specific test
            if args.test not in runner.test_configs:
                print(f"❌ Unknown test: {args.test}")
                print(f"Available tests: {', '.join(runner.test_configs.keys())}")
                sys.exit(1)

            result = runner.run_test(args.test)
            runner.results = [result]
        else:
            # Run all tests
            runner.run_all_tests()

        # Print summary
        runner.print_summary()

        # Generate matrix report
        runner.generate_matrix_report(args.output)

        # Exit with appropriate code
        failed_tests = [r for r in runner.results if r.status == "FAILED"]
        sys.exit(len(failed_tests))

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
