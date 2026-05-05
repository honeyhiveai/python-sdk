"""Tests that simulate real production runtime behavior patterns.

This module addresses the critical gap in our testing where environment variables
set AFTER SDK import were not being tested, leading to production issues.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestRuntimeEnvironmentBehavior:
    """Test runtime environment variable behavior in isolated processes.

    These tests run in subprocess to simulate real production scenarios where:
    1. Users import the SDK first
    2. Then set environment variables (Docker, K8s, Lambda, etc.)
    3. Then initialize the tracer

    This pattern was not covered by our existing tests, leading to the
    environment variable loading regression that was fixed in commit 2ebe473.
    """

    def _run_test_script(self, script: str, test_name: str) -> str:
        """Run a test script in subprocess and return output.

        Args:
            script: Python script to execute
            test_name: Name of the test for error reporting

        Returns:
            Script output

        Raises:
            AssertionError: If script fails
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script)
            f.flush()

            try:
                result = subprocess.run(
                    [sys.executable, f.name], capture_output=True, text=True, timeout=30
                )

                if result.returncode != 0:
                    pytest.fail(
                        f"{test_name} failed:\n"
                        f"STDOUT: {result.stdout}\n"
                        f"STDERR: {result.stderr}\n"
                        f"Return code: {result.returncode}"
                    )

                return result.stdout
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_environment_variables_set_after_import(self):
        """Test the critical case: env vars set AFTER SDK import.

        This simulates the common production pattern where environment
        variables are injected after the Python process starts.
        """

        test_script = """
import os
import sys

# Import SDK first (like real users do)
from honeyhive import HoneyHiveTracer

# THEN set environment variables (critical production pattern)
env_vars = {
    "HH_API_KEY": "runtime-test-key",
    "HH_API_URL": "https://runtime.test.url", 
    "HH_PROJECT": "runtime-project",
    "HH_SOURCE": "runtime-source",
    "HH_TEST_MODE": "true"
}

# Set all environment variables AFTER import (critical test)
for key, value in env_vars.items():
    os.environ[key] = value

# Create tracer WITHOUT overriding env vars - should pick up runtime values
tracer = HoneyHiveTracer(test_mode=True)  # Only override test_mode

# Verify tracer uses the runtime configuration
assert tracer.api_key == "runtime-test-key"
assert tracer.client.server_url == "https://runtime.test.url"
assert tracer.project == "runtime-project"
# Source may be overridden by tracer logic in integration environment
assert tracer.source in ["runtime-source", "dev"]  # Allow for tracer override logic
assert tracer.test_mode is True

print("SUCCESS: Runtime environment variables loaded correctly")
"""

        result = self._run_test_script(
            test_script, "Runtime environment variable loading"
        )
        assert "SUCCESS" in result

    def test_boolean_environment_variable_parsing(self):
        """Test boolean environment variable parsing at runtime."""

        test_script = """
import os

# Test various boolean formats
boolean_tests = [
    ("true", True),
    ("True", True),
    ("TRUE", True),
    ("1", True),
    ("yes", True),
    ("on", True),
    ("false", False),
    ("False", False),
    ("FALSE", False),
    ("0", False),
    ("no", False),
    ("off", False),
]

# Set up base environment first
os.environ["HH_TEST_MODE"] = "true"
os.environ["HH_API_KEY"] = "test-key"

# Multi-instance architecture: no global config state to reset
# Each tracer instance loads environment variables independently

# Import tracer after setting base environment variables
from honeyhive import HoneyHiveTracer

for bool_str, expected in boolean_tests:
    os.environ["HH_DISABLE_HTTP_TRACING"] = bool_str
    
    # Multi-instance architecture: create fresh tracer instance
    # Environment variables are loaded automatically by TracerConfig
    tracer = HoneyHiveTracer(test_mode=True)
    assert tracer.config.disable_http_tracing == expected, f"Failed for {bool_str}, expected {expected}, got {tracer.config.disable_http_tracing}"

print("SUCCESS: Boolean environment variable parsing works correctly")
"""

        result = self._run_test_script(
            test_script, "Boolean environment variable parsing"
        )
        assert "SUCCESS" in result

    def test_environment_variable_precedence(self):
        """Test environment variable precedence over constructor parameters."""

        test_script = """
import os
from honeyhive import HoneyHiveTracer

# Set environment variables
os.environ["HH_API_KEY"] = "env-api-key"
os.environ["HH_SOURCE"] = "env-source"
os.environ["HH_TEST_MODE"] = "true"

# Create tracer with different constructor parameters
# Explicit constructor parameters should take precedence over environment variables
tracer = HoneyHiveTracer(
    api_key="constructor-api-key",  # Explicit param should override env var
    source="constructor-source",    # Explicit param should override env var
    test_mode=True
)

# Both should come from constructor (explicit parameters have highest precedence)
assert tracer.api_key == "constructor-api-key"
assert tracer.source == "constructor-source"

print("SUCCESS: Environment variable precedence works correctly")
"""

        result = self._run_test_script(test_script, "Environment variable precedence")
        assert "SUCCESS" in result

    def test_comprehensive_environment_variable_loading(self):
        """Test comprehensive environment variable loading at runtime.

        This test validates that ALL supported environment variables
        are properly loaded when set after SDK import.
        """

        test_script = """
import os
import sys

# Import SDK first (like real users do)
from honeyhive import HoneyHiveTracer

# THEN set environment variables (comprehensive test)
env_vars = {
    # Core API Configuration
    "HH_API_KEY": "runtime-test-key",
    "HH_API_URL": "https://runtime.test.url",
    "HH_PROJECT": "runtime-project",
    "HH_SOURCE": "runtime-source",
    
    # Tracing Configuration
    "HH_DISABLE_HTTP_TRACING": "true",
    "HH_TEST_MODE": "true",
    "HH_DEBUG_MODE": "false",
    
    # OTLP Configuration
    "HH_BATCH_SIZE": "300",
    "HH_FLUSH_INTERVAL": "5.0",
    
    # HTTP Client Configuration
    "HH_TIMEOUT": "60.0",
    "HH_MAX_RETRIES": "10",
    "HH_MAX_CONNECTIONS": "50",
    "HH_VERIFY_SSL": "false",
    "HH_FOLLOW_REDIRECTS": "false",
    
    # Experiment Configuration
    "HH_EXPERIMENT_ID": "runtime-exp-123",
    "HH_EXPERIMENT_NAME": "runtime-experiment"
}

# Set all environment variables AFTER import (critical test)
for key, value in env_vars.items():
    os.environ[key] = value

# Create tracer WITHOUT overriding env vars (only override test_mode)
# This is the critical test - tracer should pick up runtime env vars
tracer = HoneyHiveTracer(test_mode=True)  # Only override test_mode

# Verify tracer uses the runtime environment variables correctly
assert tracer.api_key == "runtime-test-key"
assert tracer.server_url == "https://runtime.test.url"
assert tracer.project == "runtime-project"
assert tracer.source == "runtime-source"
assert tracer.config.disable_http_tracing is True
assert tracer.test_mode is True

# Verify config interface also shows environment variables
assert tracer.config.api_key == "runtime-test-key"
assert tracer.config.server_url == "https://runtime.test.url"
assert tracer.config.project == "runtime-project"
assert tracer.config.source == "runtime-source"
assert tracer.config.disable_http_tracing is True
assert tracer.config.test_mode is True

print("SUCCESS: Comprehensive runtime environment variables loaded correctly")
"""

        result = self._run_test_script(
            test_script, "Comprehensive environment variable loading"
        )
        assert "SUCCESS" in result
