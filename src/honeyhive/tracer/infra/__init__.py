"""Infrastructure detection and resource management for HoneyHive tracer.

This module provides comprehensive infrastructure detection capabilities including:
- Host and OS detection
- Container environment detection (Docker, Kubernetes)
- Cloud provider detection (AWS, GCP, Azure)
- Service information resolution
- Performance characteristics based on environment
- Resource constraints and optimization settings
"""

from .environment import (
    EnvironmentDetector,
    get_comprehensive_environment_analysis,
    get_environment_type,
    get_performance_characteristics,
    get_resource_constraints,
)
from .resources import build_otel_resources

__all__ = [
    "EnvironmentDetector",
    "get_comprehensive_environment_analysis",
    "get_environment_type",
    "get_performance_characteristics",
    "get_resource_constraints",
    "build_otel_resources",
]
