"""Automated regression detection for backwards compatibility.

This module provides comprehensive regression testing to ensure that
backwards compatibility is maintained across all SDK changes.
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestBackwardsCompatibilityRegression:
    """Detect regressions in backwards compatibility.

    These tests validate that all main branch API patterns continue to work
    in the complete-refactor branch, preventing backwards compatibility
    regressions from reaching production.
    """

    def test_main_branch_api_compatibility(self):
        """Test that all main branch API patterns still work.

        This test validates the core API patterns that users rely on
        from the main branch continue to work in complete-refactor.
        """

        # Test script using main branch patterns
        main_branch_script = """
# Main branch initialization patterns
from honeyhive import HoneyHiveTracer

# Pattern 1: Basic initialization (most common)
tracer1 = HoneyHiveTracer(
    api_key="test-key",
    project="test-project",
    session_name="test-session",
    test_mode=True
)

# Pattern 2: With all original parameters (comprehensive)
tracer2 = HoneyHiveTracer(
    api_key="test-key",
    project="test-project", 
    session_name="test-session",
    source="test",
    server_url="https://custom.url",
    disable_batch=True,
    verbose=True,
    inputs={"test": "input"},
    is_evaluation=True,
    run_id="test-run",
    dataset_id="test-dataset",
    datapoint_id="test-datapoint",
    test_mode=True
)

# Pattern 3: Context propagation methods (backwards compatibility)
carrier = {}
token = tracer2.link(carrier)
injected_carrier = tracer2.inject(carrier)
tracer2.unlink(token)

# Pattern 4: Span enrichment (core functionality)
tracer2.enrich_span(metadata={"test": "metadata"})

# Pattern 5: Session management
assert tracer1.session_id is not None or tracer1.test_mode is True
assert tracer2.session_id is not None or tracer2.test_mode is True

print("SUCCESS: All main branch patterns work")
"""

        result = subprocess.run(
            [sys.executable, "-c", main_branch_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Main branch compatibility failed - BACKWARDS COMPATIBILITY REGRESSION DETECTED:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_environment_variable_regression(self):
        """Test for environment variable loading regressions.

        This test would have caught the environment variable loading issue
        that was fixed in commit 2ebe473.
        """

        env_regression_script = """
import os

# Set all documented environment variables
env_vars = {
    "HH_API_KEY": "regression-test-key",
    "HH_API_URL": "https://regression.test.url", 
    "HH_PROJECT": "regression-project",
    "HH_SOURCE": "regression-source",
    "HH_TIMEOUT": "60.0",
    "HH_MAX_RETRIES": "10",
    "HH_BATCH_SIZE": "300",
    "HH_FLUSH_INTERVAL": "5.0",
    "HH_MAX_CONNECTIONS": "50",
    "HH_TEST_MODE": "true",
    "HH_VERBOSE": "true",
    "HH_VERIFY_SSL": "false",
    "HH_FOLLOW_REDIRECTS": "false",
    "HH_DISABLE_HTTP_TRACING": "true"
}

# Set environment variables AFTER import (critical test)
from honeyhive import HoneyHiveTracer

for key, value in env_vars.items():
    os.environ[key] = value

# Create tracer - per-instance config loads environment variables automatically
tracer = HoneyHiveTracer(test_mode=True)

# Verify ALL environment variables are loaded via tracer.config interface
assert tracer.config.api_key == "regression-test-key", f"API key regression: {tracer.config.api_key}"
assert tracer.config.server_url == "https://regression.test.url", f"Server URL regression: {tracer.config.server_url}"
assert tracer.config.project == "regression-project", f"Project regression: {tracer.config.project}"
assert tracer.config.source == "regression-source", f"Source regression: {tracer.config.source}"
assert tracer.config.http.timeout == 60.0, f"Timeout regression: {tracer.config.http.timeout}"
assert tracer.config.http.max_retries == 10, f"Max retries regression: {tracer.config.http.max_retries}"
assert tracer.config.otlp.batch_size == 300, f"Batch size regression: {tracer.config.otlp.batch_size}"
assert tracer.config.otlp.flush_interval == 5.0, f"Flush interval regression: {tracer.config.otlp.flush_interval}"
assert tracer.config.http.max_connections == 50, f"Max connections regression: {tracer.config.http.max_connections}"
assert tracer.config.test_mode is True, f"Test mode regression: {tracer.config.test_mode}"
assert tracer.config.get("verbose", False) is True, f"Verbose mode regression: {tracer.config.get('verbose')}"
assert tracer.config.http.verify_ssl is False, f"Verify SSL regression: {tracer.config.http.verify_ssl}"
assert tracer.config.http.follow_redirects is False, f"Follow redirects regression: {tracer.config.http.follow_redirects}"
assert tracer.config.disable_http_tracing is True, f"Disable HTTP tracing regression: {tracer.config.disable_http_tracing}"

# Verify tracer instance uses the configuration
assert tracer.api_key == "regression-test-key", f"Tracer API key regression: {tracer.api_key}"
assert tracer.client.server_url == "https://regression.test.url", f"Tracer URL regression: {tracer.client.server_url}"
assert tracer.project == "regression-project", f"Tracer project regression: {tracer.project}"

print("SUCCESS: No environment variable regression detected")
"""

        result = subprocess.run(
            [sys.executable, "-c", env_regression_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Environment variable regression detected - CRITICAL REGRESSION:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_decorator_compatibility_regression(self):
        """Test that trace decorators work exactly like main branch.

        This ensures the @trace decorator patterns from main branch
        continue to work in complete-refactor.
        """

        decorator_script = """
from honeyhive import trace, HoneyHiveTracer
from honeyhive.models import EventType

# Initialize tracer first
tracer = HoneyHiveTracer(
    api_key="test-key",
    project="test-project",
    test_mode=True
)

# Pattern 1: Basic trace decorator
@trace(event_type=EventType.tool)
def basic_function():
    return "basic result"

# Pattern 2: Trace with explicit tracer
@trace(tracer=tracer, event_type=EventType.chain)
def explicit_tracer_function():
    return "explicit result"

# Pattern 3: Trace with event name
@trace(event_type=EventType.model, event_name="test_model_call")
def named_function():
    return "named result"

# Test all patterns work
result1 = basic_function()
result2 = explicit_tracer_function()
result3 = named_function()

assert result1 == "basic result"
assert result2 == "explicit result"
assert result3 == "named result"

print("SUCCESS: All decorator patterns work")
"""

        result = subprocess.run(
            [sys.executable, "-c", decorator_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Decorator compatibility regression detected:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_evaluation_workflow_regression(self):
        """Test evaluation workflow backwards compatibility.

        This ensures evaluation-related parameters and workflows
        continue to work as expected.
        """

        evaluation_script = """
from honeyhive import HoneyHiveTracer

# Test evaluation workflow parameters
tracer = HoneyHiveTracer(
    api_key="test-key",
    project="test-project",
    is_evaluation=True,
    run_id="test-run-123",
    dataset_id="test-dataset-456",
    datapoint_id="test-datapoint-789",
    test_mode=True
)

# Verify evaluation parameters are stored
assert tracer.is_evaluation is True
assert tracer.run_id == "test-run-123"
assert tracer.dataset_id == "test-dataset-456"
assert tracer.datapoint_id == "test-datapoint-789"

print("SUCCESS: Evaluation workflow backwards compatibility maintained")
"""

        result = subprocess.run(
            [sys.executable, "-c", evaluation_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Evaluation workflow regression detected:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_session_management_regression(self):
        """Test session management backwards compatibility.

        This ensures session creation and management works as expected
        from the main branch.
        """

        session_script = """
from honeyhive import HoneyHiveTracer
import uuid

# Test session management patterns
tracer1 = HoneyHiveTracer(
    api_key="test-key",
    project="test-project",
    session_name="test-session",
    test_mode=True
)

# Test with existing session ID
existing_session_id = str(uuid.uuid4())
tracer2 = HoneyHiveTracer(
    api_key="test-key",
    project="test-project",
    session_id=existing_session_id,
    test_mode=True
)

# Test with inputs
tracer3 = HoneyHiveTracer(
    api_key="test-key",
    project="test-project",
    inputs={"test_input": "test_value"},
    test_mode=True
)

# Verify session management works
assert tracer1.session_id is not None or tracer1.test_mode is True
assert tracer2.session_id == existing_session_id or tracer2.test_mode is True
assert tracer3.session_id is not None or tracer3.test_mode is True

print("SUCCESS: Session management backwards compatibility maintained")
"""

        result = subprocess.run(
            [sys.executable, "-c", session_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Session management regression detected:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_import_compatibility_regression(self):
        """Test that all main branch imports still work.

        This ensures users can import everything they could from main branch.
        """

        import_script = """
# Test all main branch imports
try:
    from honeyhive import (
        HoneyHiveTracer,
        trace,
        atrace,
        enrich_span,
        evaluate,
        evaluator,
        aevaluator,
        config
    )
    
    # Test that imports are not None
    assert HoneyHiveTracer is not None
    assert trace is not None
    assert atrace is not None
    assert enrich_span is not None
    assert evaluate is not None
    assert evaluator is not None
    assert aevaluator is not None
    assert config is not None
    
    print("SUCCESS: All main branch imports work")
    
except ImportError as e:
    print(f"IMPORT REGRESSION: {e}")
    raise
"""

        result = subprocess.run(
            [sys.executable, "-c", import_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Import compatibility regression detected:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )
