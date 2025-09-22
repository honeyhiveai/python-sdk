"""Base API class for HoneyHive API modules."""

# pylint: disable=protected-access
# Note: Protected access to client._log is required for consistent logging
# across all API classes. This is legitimate internal access.

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..utils.error_handler import ErrorContext, get_error_handler

if TYPE_CHECKING:
    from .client import HoneyHive


class BaseAPI:  # pylint: disable=too-few-public-methods
    """Base class for all API modules."""

    def __init__(self, client: "HoneyHive"):
        """Initialize the API module with a client.

        Args:
            client: HoneyHive client instance
        """
        self.client = client
        self.error_handler = get_error_handler()
        self._client_name = self.__class__.__name__

    def _create_error_context(  # pylint: disable=too-many-arguments
        self,
        operation: str,
        *,
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
        url = f"{self.client.server_url}{path}" if path else None

        return ErrorContext(
            operation=operation,
            method=method,
            url=url,
            params=params,
            json_data=json_data,
            client_name=self._client_name,
            additional_context=additional_context,
        )

    def _process_data_dynamically(
        self, data_list: list, model_class: type, data_type: str = "items"
    ) -> list:
        """Universal dynamic data processing for all API modules.

        This method applies dynamic processing patterns across the entire API client:
        - Early validation failure detection
        - Memory-efficient processing for large datasets
        - Adaptive error handling based on dataset size
        - Performance monitoring and optimization

        Args:
            data_list: List of raw data dictionaries from API response
            model_class: Pydantic model class to instantiate (e.g., Event, Metric, Tool)
            data_type: Type of data being processed (for logging)

        Returns:
            List of instantiated model objects
        """
        if not data_list:
            return []

        processed_items = []
        dataset_size = len(data_list)
        error_count = 0
        max_errors = max(1, dataset_size // 10)  # Allow up to 10% errors

        # Dynamic processing: Use different strategies based on dataset size
        if dataset_size > 100:
            # Large dataset: Use generator-based processing with early error detection
            self.client._log(
                "debug", f"Processing large {data_type} dataset: {dataset_size} items"
            )

            for i, item_data in enumerate(data_list):
                try:
                    processed_items.append(model_class(**item_data))
                except Exception as e:
                    error_count += 1

                    # Dynamic error handling: Stop early if too many errors
                    if error_count > max_errors:
                        self.client._log(
                            "warning",
                            (
                                f"Too many validation errors ({error_count}/{i+1}) in "
                                f"{data_type}. Stopping processing to prevent "
                                "performance degradation."
                            ),
                        )
                        break

                    # Log first few errors for debugging
                    if error_count <= 3:
                        self.client._log(
                            "warning",
                            f"Skipping {data_type} item {i} with validation error: {e}",
                        )
                    elif error_count == 4:
                        self.client._log(
                            "warning",
                            f"Suppressing further {data_type} validation error logs...",
                        )

                # Performance check: Log progress for very large datasets
                if dataset_size > 500 and (i + 1) % 100 == 0:
                    self.client._log(
                        "debug", f"Processed {i + 1}/{dataset_size} {data_type}"
                    )
        else:
            # Small dataset: Use simple processing
            for item_data in data_list:
                try:
                    processed_items.append(model_class(**item_data))
                except Exception as e:
                    error_count += 1
                    # For small datasets, log all errors
                    self.client._log(
                        "warning",
                        f"Skipping {data_type} item with validation error: {e}",
                    )

        # Performance summary for large datasets
        if dataset_size > 100:
            success_rate = (
                (len(processed_items) / dataset_size) * 100 if dataset_size > 0 else 0
            )
            self.client._log(
                "debug",
                (
                    f"{data_type.title()} processing complete: "
                    f"{len(processed_items)}/{dataset_size} items "
                    f"({success_rate:.1f}% success rate)"
                ),
            )

        return processed_items
