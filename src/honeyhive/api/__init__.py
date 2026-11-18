"""HoneyHive API Client.

Usage:
    from honeyhive.api import HoneyHive

    client = HoneyHive(data_plane_api_key="hh_fgdp_...")
    configs = client.configurations.list(project_id="your-project-id")
"""

from ._base import MissingApiKeyError
from .client import (
    ConfigurationsAPI,
    DatapointsAPI,
    DatasetsAPI,
    EvaluatorsAPI,
    EventsAPI,
    ExperimentsAPI,
    HoneyHive,
    MetricsAPI,
    MetricVersionsAPI,
    SessionsAPI,
)

# Backwards compatible aliases
EvaluationsAPI = ExperimentsAPI
SessionAPI = SessionsAPI

__all__ = [
    "HoneyHive",
    "MissingApiKeyError",
    # API classes
    "ConfigurationsAPI",
    "DatapointsAPI",
    "DatasetsAPI",
    "EvaluatorsAPI",
    "EventsAPI",
    "ExperimentsAPI",
    "MetricsAPI",
    "MetricVersionsAPI",
    "SessionsAPI",
    # Backwards compatible aliases
    "EvaluationsAPI",
    "SessionAPI",
]
