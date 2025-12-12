from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunsQuery(BaseModel):
    """
    GetExperimentRunsQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)

    page: Optional[int] = Field(validation_alias="page", default=None)

    limit: Optional[int] = Field(validation_alias="limit", default=None)

    run_ids: Optional[List[str]] = Field(validation_alias="run_ids", default=None)

    name: Optional[str] = Field(validation_alias="name", default=None)

    status: Optional[str] = Field(validation_alias="status", default=None)

    dateRange: Optional[Union[str, Dict[str, Any]]] = Field(
        validation_alias="dateRange", default=None
    )

    sort_by: Optional[str] = Field(validation_alias="sort_by", default=None)

    sort_order: Optional[str] = Field(validation_alias="sort_order", default=None)
