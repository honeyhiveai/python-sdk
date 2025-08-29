"""Base API class for HoneyHive API modules."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import HoneyHive


class BaseAPI:
    """Base class for all API modules."""

    def __init__(self, client: "HoneyHive"):
        """Initialize the API module with a client.

        Args:
            client: HoneyHive client instance
        """
        self.client = client
