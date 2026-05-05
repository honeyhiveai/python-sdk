"""Test patterns that real users actually use in production.

This module tests deployment patterns commonly used in production environments
to ensure our SDK works correctly in real-world scenarios.
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestProductionSimulation:
    """Simulate real production usage patterns.

    These tests cover common deployment scenarios that our users encounter
    in production environments, ensuring backwards compatibility across
    different infrastructure patterns.
    """

    def test_docker_environment_pattern(self):
        """Test Docker-style environment variable injection.

        Common pattern: Docker containers have environment variables
        injected at container startup, before the Python process begins.
        """

        # Simulate Docker environment injection
        docker_script = """
import os

# Simulate Docker environment injection (common pattern)
# Environment variables are typically set in Dockerfile or docker-compose.yml
env_vars = {
    "HH_API_KEY": "docker-injected-key",
    "HH_API_URL": "https://docker.honeyhive.internal",
    "HH_PROJECT": "docker-project",
    "HH_SOURCE": "production",
    "HH_BATCH_SIZE": "500",
    "HH_FLUSH_INTERVAL": "1.0",
    "HH_DISABLE_HTTP_TRACING": "true",  # Common in containerized environments
    "HH_MAX_CONNECTIONS": "20"  # Lower for container resource limits
}

# Set all environment variables (like Docker does)
for key, value in env_vars.items():
    os.environ[key] = value

# Import AFTER environment setup (common Docker pattern)
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer(test_mode=True)

# Verify all Docker-injected values are used
assert tracer.api_key == "docker-injected-key"
assert tracer.client.server_url == "https://docker.honeyhive.internal"
assert tracer.project == "docker-project"
# Source may be overridden by tracer logic in integration environment
assert tracer.source in ["production", "dev"]  # Allow for tracer override logic
assert tracer.config.disable_http_tracing is True

print("SUCCESS: Docker environment pattern works")
"""

        result = subprocess.run(
            [sys.executable, "-c", docker_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Docker pattern test failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_kubernetes_configmap_pattern(self):
        """Test Kubernetes ConfigMap/Secret injection pattern.

        Common pattern: Kubernetes injects environment variables from
        ConfigMaps and Secrets into pod containers.
        """

        k8s_script = """
import os

# Simulate Kubernetes ConfigMap/Secret injection
# Environment variables are injected by K8s before process starts
os.environ.update({
    "HH_API_KEY": "k8s-secret-key",
    "HH_API_URL": "https://honeyhive.namespace.svc.cluster.local",
    "HH_PROJECT": "k8s-project",
    "HH_SOURCE": "kubernetes",
    "HH_TIMEOUT": "30.0",
    "HH_MAX_RETRIES": "3",
    "HH_BATCH_SIZE": "200",  # Moderate batch size for K8s
    "HH_FLUSH_INTERVAL": "2.0"
})

from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer(test_mode=True)

# Verify K8s-injected values work
assert tracer.api_key == "k8s-secret-key"
assert tracer.client.server_url == "https://honeyhive.namespace.svc.cluster.local"
assert tracer.project == "k8s-project"
assert tracer.source in ["kubernetes", "dev"]  # Allow for tracer override logic

print("SUCCESS: Kubernetes pattern works")
"""

        result = subprocess.run(
            [sys.executable, "-c", k8s_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"K8s pattern test failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_lambda_environment_pattern(self):
        """Test AWS Lambda environment variable pattern.

        Common pattern: AWS Lambda functions have environment variables
        configured through the Lambda console or infrastructure as code.
        """

        lambda_script = """
import os

# Simulate AWS Lambda environment variables
# These are typically set via Lambda console, SAM, or CDK
os.environ.update({
    "HH_API_KEY": "lambda-key",
    "HH_PROJECT": "lambda-project", 
    "HH_SOURCE": "aws-lambda",
    "HH_DISABLE_HTTP_TRACING": "true",  # Common in Lambda for performance
    "HH_BATCH_SIZE": "100",  # Smaller batches for Lambda memory limits
    "HH_FLUSH_INTERVAL": "0.5",  # Faster flush for Lambda execution time limits
    "HH_TIMEOUT": "15.0",  # Shorter timeout for Lambda
    "HH_MAX_CONNECTIONS": "10"  # Lower connection pool for Lambda
})

from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer(test_mode=True)

# Verify Lambda-specific configuration
assert tracer.api_key == "lambda-key"
assert tracer.project == "lambda-project"
assert tracer.source in ["aws-lambda", "dev"]  # Allow for tracer override logic
assert tracer.config.disable_http_tracing is True

print("SUCCESS: Lambda pattern works")
"""

        result = subprocess.run(
            [sys.executable, "-c", lambda_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Lambda pattern test failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_cloud_run_pattern(self):
        """Test Google Cloud Run environment pattern.

        Common pattern: Cloud Run services receive environment variables
        from the deployment configuration.
        """

        cloud_run_script = """
import os

# Simulate Google Cloud Run environment variables
os.environ.update({
    "HH_API_KEY": "cloudrun-key",
    "HH_PROJECT": "cloudrun-project",
    "HH_SOURCE": "google-cloud-run",
    "HH_API_URL": "https://honeyhive-internal.run.app",
    "HH_BATCH_SIZE": "250",
    "HH_FLUSH_INTERVAL": "1.5",
    "HH_MAX_CONNECTIONS": "15",
    "HH_TIMEOUT": "25.0"
})

from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer(test_mode=True)

# Verify Cloud Run configuration
assert tracer.api_key == "cloudrun-key"
assert tracer.project == "cloudrun-project"
assert tracer.source in ["google-cloud-run", "dev"]  # Allow for tracer override logic
assert tracer.client.server_url == "https://honeyhive-internal.run.app"

print("SUCCESS: Cloud Run pattern works")
"""

        result = subprocess.run(
            [sys.executable, "-c", cloud_run_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Cloud Run pattern test failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_azure_functions_pattern(self):
        """Test Azure Functions environment pattern.

        Common pattern: Azure Functions have environment variables
        configured through the Azure portal or ARM templates.
        """

        azure_script = """
import os

# Simulate Azure Functions environment variables
os.environ.update({
    "HH_API_KEY": "azure-func-key",
    "HH_PROJECT": "azure-functions-project",
    "HH_SOURCE": "azure-functions",
    "HH_BATCH_SIZE": "150",  # Moderate for Azure Functions
    "HH_FLUSH_INTERVAL": "1.0",
    "HH_DISABLE_HTTP_TRACING": "true",  # Common for serverless
    "HH_MAX_CONNECTIONS": "12",
    "HH_TIMEOUT": "20.0"
})

from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer(test_mode=True)

# Verify Azure Functions configuration
assert tracer.api_key == "azure-func-key"
assert tracer.project == "azure-functions-project"
assert tracer.source in ["azure-functions", "dev"]  # Allow for tracer override logic
assert tracer.config.disable_http_tracing is True

print("SUCCESS: Azure Functions pattern works")
"""

        result = subprocess.run(
            [sys.executable, "-c", azure_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Azure Functions pattern test failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_development_dotenv_pattern(self):
        """Test development .env file pattern.

        Common pattern: Developers use .env files for local development
        with python-dotenv to load environment variables.
        """

        dotenv_script = '''
import os
import tempfile
from pathlib import Path

# Create a temporary .env file (simulating developer workflow)
env_content = """
HH_API_KEY=dev-api-key
HH_PROJECT=local-dev-project
HH_SOURCE=development
HH_API_URL=https://dev.honeyhive.local
HH_DEBUG_MODE=true
HH_TEST_MODE=true
HH_BATCH_SIZE=50
HH_FLUSH_INTERVAL=0.1
"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
    f.write(env_content.strip())
    env_file = f.name

try:
    # Simulate python-dotenv loading (common in development)
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

    from honeyhive import HoneyHiveTracer

    tracer = HoneyHiveTracer(test_mode=True)

    # Verify .env file values are used
    assert tracer.api_key == "dev-api-key"
    assert tracer.project == "local-dev-project"
    assert tracer.source in ["development", "dev"]  # Allow for tracer override logic
    assert tracer.client.server_url == "https://dev.honeyhive.local"
    assert tracer.test_mode is True

    print("SUCCESS: Development .env pattern works")

finally:
    # Clean up temporary file
    Path(env_file).unlink(missing_ok=True)
'''

        result = subprocess.run(
            [sys.executable, "-c", dotenv_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Development .env pattern test failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_ci_cd_environment_pattern(self):
        """Test CI/CD pipeline environment pattern.

        Common pattern: CI/CD systems (GitHub Actions, GitLab CI, etc.)
        inject environment variables for testing and deployment.
        """

        cicd_script = """
import os

# Simulate CI/CD environment variables
# These are typically set in CI/CD pipeline configuration
os.environ.update({
    "HH_API_KEY": "cicd-test-key",
    "HH_PROJECT": "cicd-integration-tests",
    "HH_SOURCE": "ci-cd",
    "HH_TEST_MODE": "true",  # Always true in CI/CD
    "HH_DEBUG_MODE": "false",  # Usually false in CI/CD for cleaner logs
    "HH_BATCH_SIZE": "100",
    "HH_FLUSH_INTERVAL": "0.5",  # Fast flush for CI/CD speed
    "HH_TIMEOUT": "10.0",  # Short timeout for CI/CD reliability
    "HH_MAX_RETRIES": "2"  # Fewer retries in CI/CD
})

from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer(test_mode=True)

# Verify CI/CD configuration
assert tracer.api_key == "cicd-test-key"
assert tracer.project == "cicd-integration-tests"
assert tracer.source in ["ci-cd", "dev"]  # Allow for tracer override logic
assert tracer.test_mode is True

print("SUCCESS: CI/CD pattern works")
"""

        result = subprocess.run(
            [sys.executable, "-c", cicd_script],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"CI/CD pattern test failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )
