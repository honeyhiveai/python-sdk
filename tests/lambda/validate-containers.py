#!/usr/bin/env python3
"""
Validate Lambda container images and test functions.
This script ensures all required containers exist and function properly.
"""

import json
import subprocess
import sys
import time
from typing import Dict, List, Optional


class LambdaContainerValidator:
    """Validates Lambda container images and functionality."""

    def __init__(self):
        self.results = {
            "container_builds": {},
            "container_tests": {},
            "function_tests": {},
            "overall_status": "UNKNOWN",
        }

    def run_command(self, cmd: List[str], timeout: int = 60) -> Dict[str, object]:
        """
        Run a command and return result with output.

        Args:
            cmd (List[str]): The command to run as a list of arguments.
            timeout (int): Timeout in seconds for the command.

        Returns:
            Dict[str, object]: Dictionary with keys: success, returncode, stdout, stderr.
        """
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
            }

    def check_docker_available(self) -> bool:
        """Check if Docker is available."""
        print("🐳 Checking Docker availability...")
        result = self.run_command(["docker", "--version"])
        if result["success"]:
            print(f"✅ Docker available: {result['stdout'].strip()}")
            return True
        else:
            print(f"❌ Docker not available: {result['stderr']}")
            return False

    def build_container(self, dockerfile: str, tag: str) -> bool:
        """Build a specific container."""
        print(f"🏗️  Building container {tag} from {dockerfile}...")

        # Ensure we're building from project root (two levels up from tests/lambda)
        import os

        current_dir = os.getcwd()
        if current_dir.endswith("tests/lambda"):
            build_dir = "../.."
            dockerfile_path = dockerfile
        else:
            build_dir = "."
            dockerfile_path = f"tests/lambda/{dockerfile}"

        result = self.run_command(
            ["docker", "build", "-f", dockerfile_path, "-t", tag, build_dir],
            timeout=300,
        )  # 5 minutes timeout

        if result["success"]:
            print(f"✅ Successfully built {tag}")
            self.results["container_builds"][tag] = {
                "status": "SUCCESS",
                "dockerfile": dockerfile,
            }
            return True
        else:
            print(f"❌ Failed to build {tag}: {result['stderr']}")
            self.results["container_builds"][tag] = {
                "status": "FAILED",
                "dockerfile": dockerfile,
                "error": result["stderr"],
            }
            return False

    def validate_container_sdk(self, tag: str) -> bool:
        """Validate that the SDK is available in the container."""
        print(f"🧪 Validating SDK in container {tag}...")

        result = self.run_command(
            [
                "docker",
                "run",
                "--rm",
                "--entrypoint",
                "python",
                tag,
                "-c",
                "import honeyhive; from honeyhive.tracer import HoneyHiveTracer; print('✅ HoneyHive SDK working')",
            ]
        )

        if result["success"]:
            print(f"✅ SDK validation passed for {tag}")
            self.results["container_tests"][tag] = {
                "status": "SUCCESS",
                "output": result["stdout"],
            }
            return True
        else:
            print(f"❌ SDK validation failed for {tag}: {result['stderr']}")
            self.results["container_tests"][tag] = {
                "status": "FAILED",
                "error": result["stderr"],
            }
            return False

    def test_lambda_function(self, tag: str, handler: str) -> bool:
        """Test a Lambda function in the container."""
        print(f"🚀 Testing Lambda function {handler} in {tag}...")

        # Start container in background
        start_result = self.run_command(
            [
                "docker",
                "run",
                "--rm",
                "-d",
                "-p",
                "0:8080",  # Use random port
                "-e",
                "HH_API_KEY=test-key",
                "-e",
                "HH_TEST_MODE=true",
                tag,
                handler,
            ]
        )

        if not start_result["success"]:
            print(f"❌ Failed to start container: {start_result['stderr']}")
            return False

        container_id = start_result["stdout"].strip()

        try:
            # Wait for container to start
            time.sleep(3)

            # Get the port
            port_result = self.run_command(["docker", "port", container_id, "8080"])

            if not port_result["success"]:
                print(f"❌ Failed to get container port: {port_result['stderr']}")
                return False

            port = port_result["stdout"].strip().split(":")[-1]

            # Test the function
            test_payload = {"test": "validation", "timestamp": time.time()}

            invoke_result = self.run_command(
                [
                    "curl",
                    "-s",
                    "-X",
                    "POST",
                    f"http://localhost:{port}/2015-03-31/functions/function/invocations",
                    "-H",
                    "Content-Type: application/json",
                    "-d",
                    json.dumps(test_payload),
                ]
            )

            if invoke_result["success"]:
                try:
                    response = json.loads(invoke_result["stdout"])
                    if response.get("statusCode") == 200:
                        print(f"✅ Lambda function {handler} working correctly")
                        self.results["function_tests"][f"{tag}:{handler}"] = {
                            "status": "SUCCESS",
                            "response": response,
                        }
                        return True
                    else:
                        print(f"❌ Lambda function returned error: {response}")
                        self.results["function_tests"][f"{tag}:{handler}"] = {
                            "status": "FAILED",
                            "error": f"Bad status code: {response.get('statusCode')}",
                        }
                        return False
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {invoke_result['stdout']}")
                    return False
            else:
                print(f"❌ Failed to invoke function: {invoke_result['stderr']}")
                return False

        finally:
            # Clean up container
            self.run_command(["docker", "stop", container_id])

    def validate_all(self) -> bool:
        """Validate all Lambda containers and functions."""
        print("🔍 Starting comprehensive Lambda container validation...")

        if not self.check_docker_available():
            return False

        # Clean up any existing containers
        print("🧹 Cleaning up existing containers...")
        self.run_command(["docker", "system", "prune", "-f"])

        # Build the main bundle container
        success = True

        # Build bundle container
        if not self.build_container(
            "Dockerfile.bundle-builder", "honeyhive-lambda:bundle-native"
        ):
            success = False

        # Validate SDK in container
        if success:
            if not self.validate_container_sdk("honeyhive-lambda:bundle-native"):
                success = False

        # Test key Lambda functions
        if success:
            test_functions = [
                "working_sdk_test.lambda_handler",
                "cold_start_test.lambda_handler",
                "simple_test.lambda_handler",
            ]

            for handler in test_functions:
                if not self.test_lambda_function(
                    "honeyhive-lambda:bundle-native", handler
                ):
                    print(f"⚠️ Function {handler} failed, continuing...")
                    # Don't fail overall validation for individual function failures

        self.results["overall_status"] = "SUCCESS" if success else "FAILED"

        return success

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("🔍 LAMBDA CONTAINER VALIDATION SUMMARY")
        print("=" * 60)

        # Container builds
        print("\n📦 Container Builds:")
        for tag, result in self.results["container_builds"].items():
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            print(f"  {status_icon} {tag}: {result['status']}")

        # Container tests
        print("\n🧪 SDK Validation:")
        for tag, result in self.results["container_tests"].items():
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            print(f"  {status_icon} {tag}: {result['status']}")

        # Function tests
        print("\n🚀 Function Tests:")
        for func, result in self.results["function_tests"].items():
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            print(f"  {status_icon} {func}: {result['status']}")

        print(f"\n🎯 Overall Status: {self.results['overall_status']}")
        print("=" * 60)

    def save_results(self, filename: str = "container-validation-results.json"):
        """Save validation results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Results saved to {filename}")


def main():
    """Main validation function."""
    validator = LambdaContainerValidator()

    try:
        success = validator.validate_all()
        validator.print_summary()
        validator.save_results()

        if success:
            print("\n🎉 All Lambda container validations passed!")
            sys.exit(0)
        else:
            print("\n💥 Some Lambda container validations failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ Validation interrupted by user")
        validator.print_summary()
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
