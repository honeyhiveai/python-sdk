"""HoneyHive API Client.

Usage:
    from honeyhive.api import HoneyHive

    client = HoneyHive(api_key="hh_...")
    configs = client.configurations.list()
"""

from ._base import MissingApiKeyError
from .client import (
    ConfigurationsAPI,
    DatapointsAPI,
    DatasetsAPI,
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
    "EventsAPI",
    "ExperimentsAPI",
    "MetricsAPI",
    "MetricVersionsAPI",
    "SessionsAPI",
    # Backwards compatible aliases
    "EvaluationsAPI",
    "SessionAPI",
]
