from typing import *

from pydantic import BaseModel, Field


class RunMetricRequest(BaseModel):
    """
    RunMetricRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    metric: Dict[str, Any] = Field(validation_alias="metric")

    event: Optional[Any] = Field(validation_alias="event", default=None)
