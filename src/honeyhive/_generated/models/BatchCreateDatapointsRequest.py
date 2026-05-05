from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .BatchDateRange import BatchDateRange
from .CheckState import CheckState
from .DatapointMapping import DatapointMapping

__all__ = ["BatchCreateDatapointsRequest"]


class BatchCreateDatapointsRequest(BaseModel):
    """
    BatchCreateDatapointsRequest model
        Request body for POST /datapoints/batch
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    events: Optional[List[str]] = Field(validation_alias="events", default=None)

    mapping: Optional[DatapointMapping] = Field(
        validation_alias="mapping", default=None
    )

    filters: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        validation_alias="filters", default=None
    )

    dateRange: Optional[BatchDateRange] = Field(
        validation_alias="dateRange", default=None
    )

    checkState: Optional[CheckState] = Field(
        validation_alias="checkState", default=None
    )

    selectAll: Optional[bool] = Field(validation_alias="selectAll", default=None)

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)
