"""OpenTelemetry resource attribute building and management."""

import os
import sys
from typing import Any, Dict, Optional

from ...utils.logger import safe_log
from .environment import EnvironmentDetector


def build_otel_resources(tracer_instance: Optional[Any] = None) -> Dict[str, Any]:
    """Build comprehensive OpenTelemetry resource attributes.

    This function uses the EnvironmentDetector to create a complete set of
    OpenTelemetry-compliant resource attributes.

    Args:
        tracer_instance: Optional tracer instance for logging and context

    Returns:
        Dictionary containing OpenTelemetry resource attributes
    """
    resources = {}

    try:
        # Use the comprehensive environment detector
        detector = EnvironmentDetector(tracer_instance)

        # Process information (always available)
        resources.update(
            {
                "process.pid": os.getpid(),
                "process.runtime.name": "python",
                "process.runtime.version": _get_python_version(),
            }
        )

        # Service information
        resources.update(
            {
                "service.name": _detect_service_name(tracer_instance),
                "service.version": _detect_service_version(),
                "service.instance.id": (
                    str(id(tracer_instance)) if tracer_instance else "unknown"
                ),
            }
        )

        # System information from environment detector
        system_info = detector.detect_system_info()
        resources.update(system_info)

        # Container information
        container_info = detector.detect_container_environment()
        resources.update(container_info)

        # Cloud provider information
        cloud_info = detector.detect_cloud_environment()
        resources.update(cloud_info)

        if tracer_instance:
            safe_log(
                tracer_instance,
                "debug",
                f"Built {len(resources)} OpenTelemetry resource attributes",
            )

    except Exception as e:
        # Graceful degradation - provide minimal resource set
        if tracer_instance:
            safe_log(
                tracer_instance, "warning", f"Error during resource detection: {e}"
            )

        resources = {
            "service.name": "unknown",
            "service.instance.id": (
                str(id(tracer_instance)) if tracer_instance else "unknown"
            ),
            "process.pid": os.getpid(),
        }

    return resources


def _detect_service_name(tracer_instance: Optional[Any] = None) -> str:
    """Detect service name from various sources."""
    # Priority order for service name detection
    sources = [
        ("OTEL_SERVICE_NAME", lambda: os.getenv("OTEL_SERVICE_NAME")),
        ("HH_SERVICE_NAME", lambda: os.getenv("HH_SERVICE_NAME")),
        ("SERVICE_NAME", lambda: os.getenv("SERVICE_NAME")),
        (
            "project_name",
            lambda: (
                getattr(tracer_instance, "project", None) if tracer_instance else None
            ),
        ),
        ("lambda_function", lambda: os.getenv("AWS_LAMBDA_FUNCTION_NAME")),
        ("k8s_app", lambda: os.getenv("K8S_APP_NAME")),
        ("default", lambda: "honeyhive-service"),
    ]

    for _, detector in sources:
        try:
            value = detector()
            if value:
                if tracer_instance:
                    safe_log(
                        tracer_instance,
                        "debug",
                        f"Service name detected: {value}",
                    )
                return str(value)
        except Exception:
            continue

    return "honeyhive-service"


def _detect_service_version() -> str:
    """Detect service version from various sources."""
    # Priority order for version detection
    sources = [
        ("OTEL_SERVICE_VERSION", lambda: os.getenv("OTEL_SERVICE_VERSION")),
        ("HH_SERVICE_VERSION", lambda: os.getenv("HH_SERVICE_VERSION")),
        ("SERVICE_VERSION", lambda: os.getenv("SERVICE_VERSION")),
        (
            "GIT_COMMIT",
            lambda: (
                os.getenv("GIT_COMMIT", "")[:8] if os.getenv("GIT_COMMIT") else None
            ),
        ),
        ("BUILD_NUMBER", lambda: os.getenv("BUILD_NUMBER")),
        ("default", lambda: "unknown"),
    ]

    for _, detector in sources:
        try:
            value = detector()
            if value:
                return str(value)
        except Exception:
            continue

    return "unknown"


def _get_python_version() -> str:
    """Get Python runtime version.

    Returns:
        Python version string
    """
    try:
        return (
            f"{sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )
    except Exception:
        return "unknown"
