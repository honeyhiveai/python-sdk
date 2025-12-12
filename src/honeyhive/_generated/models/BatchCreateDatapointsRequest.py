from typing import *

from pydantic import BaseModel, Field


class BatchCreateDatapointsRequest(BaseModel):
    """
    BatchCreateDatapointsRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    events: Optional[List[str]] = Field(validation_alias="events", default=None)

    mapping: Optional[Dict[str, Any]] = Field(validation_alias="mapping", default=None)

    filters: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        validation_alias="filters", default=None
    )

    dateRange: Optional[Dict[str, Any]] = Field(
        validation_alias="dateRange", default=None
    )

    checkState: Optional[Dict[str, Any]] = Field(
        validation_alias="checkState", default=None
    )

    selectAll: Optional[bool] = Field(validation_alias="selectAll", default=None)

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)
