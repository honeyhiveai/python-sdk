from typing import *

from pydantic import BaseModel, Field


class ExperimentComparisonResponse(BaseModel):
    """
    ExperimentComparisonResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    metrics: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="metrics", default=None
    )

    commonDatapoints: Optional[List[str]] = Field(
        validation_alias="commonDatapoints", default=None
    )

    event_details: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="event_details", default=None
    )

    old_run: Optional[Dict[str, Any]] = Field(validation_alias="old_run", default=None)

    new_run: Optional[Dict[str, Any]] = Field(validation_alias="new_run", default=None)
