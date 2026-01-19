from typing import *

from pydantic import BaseModel, Field


class GetMetricsResponse(BaseModel):
    """
    GetMetricsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}
