from typing import *

from pydantic import BaseModel, Field


class CreateDatapointRequest(BaseModel):
    """
    CreateDatapointRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}
