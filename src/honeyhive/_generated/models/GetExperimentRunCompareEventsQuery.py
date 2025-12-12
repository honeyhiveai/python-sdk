from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunCompareEventsQuery(BaseModel):
    """
    GetExperimentRunCompareEventsQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    run_id_1: str = Field(validation_alias="run_id_1")

    run_id_2: str = Field(validation_alias="run_id_2")

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    filter: Optional[Union[str, Dict[str, Any]]] = Field(
        validation_alias="filter", default=None
    )

    limit: Optional[int] = Field(validation_alias="limit", default=None)

    page: Optional[int] = Field(validation_alias="page", default=None)
