from typing import *

from pydantic import BaseModel, Field


class GetConfigurationsResponse(BaseModel):
    """
    GetConfigurationsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}
