"""HoneyHive API Client.

Usage:
    from honeyhive.api import HoneyHive

    client = HoneyHive(api_key="hh_...")
    configs = client.configurations.list()
"""

from .client import (
    ConfigurationsAPI,
    DatapointsAPI,
    DatasetsAPI,
    EventsAPI,
    ExperimentsAPI,
    HoneyHive,
    MetricsAPI,
    ProjectsAPI,
    SessionsAPI,
    ToolsAPI,
)

# Backwards compatible aliases
EvaluationsAPI = ExperimentsAPI
SessionAPI = SessionsAPI

__all__ = [
    "HoneyHive",
    # API classes
    "ConfigurationsAPI",
    "DatapointsAPI",
    "DatasetsAPI",
    "EventsAPI",
    "ExperimentsAPI",
    "MetricsAPI",
    "ProjectsAPI",
    "SessionsAPI",
    "ToolsAPI",
    # Backwards compatible aliases
    "EvaluationsAPI",
    "SessionAPI",
]
