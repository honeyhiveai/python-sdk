"""Base API class for HoneyHive API modules."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..utils.error_handler import ErrorContext, get_error_handler, handle_api_errors

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
        self.error_handler = get_error_handler()
        self._client_name = self.__class__.__name__

    def _create_error_context(
        self,
        operation: str,
        method: Optional[str] = None,
        path: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **additional_context: Any,
    ) -> ErrorContext:
        """Create error context for an operation.

        Args:
            operation: Name of the operation being performed
            method: HTTP method
            path: API path
            params: Request parameters
            json_data: JSON data being sent
            **additional_context: Additional context information

        Returns:
            ErrorContext instance
        """
        url = f"{self.client.base_url}{path}" if path else None

        return ErrorContext(
            operation=operation,
            method=method,
            url=url,
            params=params,
            json_data=json_data,
            client_name=self._client_name,
            additional_context=additional_context,
        )
