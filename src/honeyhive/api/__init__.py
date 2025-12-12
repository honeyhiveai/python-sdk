"""HoneyHive API Client.

Usage:
    from honeyhive.api import HoneyHive

    client = HoneyHive(api_key="hh_...")
    configs = client.configurations.list()
"""

from .client import HoneyHive

__all__ = ["HoneyHive"]
