"""HoneyHive API Client Module - Public Facade.

This module re-exports from the underlying client implementation (_v0 or _v1).
Only one implementation will be present in a published package.
"""

try:
    # Prefer v1 if available
    from honeyhive._v1.client.client import Client as HoneyHive
    from honeyhive._v1.client.client import Client as HoneyHiveClient

    __api_version__ = "v1"
except ImportError:
    # Fall back to v0
    from honeyhive._v0.api.client import HoneyHive
    from honeyhive._v0.api.configurations import ConfigurationsAPI
    from honeyhive._v0.api.datapoints import DatapointsAPI
    from honeyhive._v0.api.datasets import DatasetsAPI
    from honeyhive._v0.api.evaluations import EvaluationsAPI
    from honeyhive._v0.api.events import EventsAPI, UpdateEventRequest
    from honeyhive._v0.api.metrics import MetricsAPI
    from honeyhive._v0.api.projects import ProjectsAPI
    from honeyhive._v0.api.session import SessionAPI
    from honeyhive._v0.api.tools import ToolsAPI

    # Alias for consistency
    HoneyHiveClient = HoneyHive

    __api_version__ = "v0"

__all__ = [
    "HoneyHive",
    "HoneyHiveClient",
    "SessionAPI",
    "EventsAPI",
    "ToolsAPI",
    "DatapointsAPI",
    "DatasetsAPI",
    "ConfigurationsAPI",
    "ProjectsAPI",
    "MetricsAPI",
    "EvaluationsAPI",
    "UpdateEventRequest",
    "__api_version__",
]
